"""Tests unitaires pour le collecteur Twitter."""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from sadie.data.collectors.twitter import TwitterCollector

@pytest.fixture
def sample_tweet():
    """Crée un tweet de test."""
    return {
        "id": "1234567890",
        "text": "Bitcoin is looking very bullish today! #BTC $BTC",
        "created_at": "2024-01-20T12:00:00Z",
        "public_metrics": {
            "retweet_count": 10,
            "like_count": 50,
            "reply_count": 5
        }
    }

@pytest.fixture
def collector():
    """Crée une instance du collecteur pour les tests."""
    collector = TwitterCollector(
        api_key="test_key",
        api_secret="test_secret",
        bearer_token="test_bearer",
        window_size=100
    )
    return collector

@pytest.mark.asyncio
async def test_initialization(collector):
    """Teste l'initialisation du collecteur."""
    assert collector.api_key == "test_key"
    assert collector.api_secret == "test_secret"
    assert collector.bearer_token == "test_bearer"
    assert collector.window_size == 100
    assert not collector._running
    assert isinstance(collector.tweets, dict)

@pytest.mark.asyncio
async def test_start_stop_stream(collector):
    """Teste le démarrage et l'arrêt du stream."""
    with patch('tweepy.StreamingClient', return_value=AsyncMock()) as mock_client:
        # Configurer le mock
        mock_client.return_value.add_rules = AsyncMock()
        mock_client.return_value.get_rules = AsyncMock(return_value=Mock(data=[Mock(id="1")]))
        mock_client.return_value.delete_rules = AsyncMock()
        
        # Démarrer le stream
        callback = AsyncMock()
        await collector.start_stream(["BTC/USDT"], callback)
        
        assert collector._running
        assert len(collector._stream_tasks) == 1
        mock_client.return_value.add_rules.assert_called_once()
        
        # Arrêter le stream
        await collector.stop_stream()
        
        assert not collector._running
        assert not collector._stream_tasks
        mock_client.return_value.delete_rules.assert_called_once()

@pytest.mark.asyncio
async def test_get_historical_tweets(collector, sample_tweet):
    """Teste la récupération des tweets historiques."""
    with patch('tweepy.Client', return_value=AsyncMock()) as mock_client:
        # Configurer le mock
        mock_response = Mock()
        mock_response.data = [Mock(**sample_tweet)]
        mock_client.return_value.search_recent_tweets = AsyncMock(return_value=mock_response)
        
        # Récupérer les tweets
        start_time = datetime.now() - timedelta(days=1)
        tweets = await collector.get_historical_tweets(
            symbol="BTC/USDT",
            start_time=start_time,
            limit=10
        )
        
        assert len(tweets) == 1
        assert tweets[0]['id'] == sample_tweet['id']
        assert tweets[0]['text'] == sample_tweet['text']
        assert 'polarity' in tweets[0]
        assert 'subjectivity' in tweets[0]

@pytest.mark.asyncio
async def test_maintain_stream(collector, sample_tweet):
    """Teste le maintien du stream de tweets."""
    # Créer un mock pour le stream
    mock_stream = AsyncMock()
    mock_stream.filter = AsyncMock()
    mock_stream.filter.return_value = [Mock(**sample_tweet)]
    
    collector.stream_client = mock_stream
    collector._running = True
    
    # Créer un callback de test
    callback = AsyncMock()
    
    # Exécuter le stream pendant un court moment
    task = asyncio.create_task(collector._maintain_stream("BTC/USDT", callback))
    await asyncio.sleep(0.1)
    collector._running = False
    await task
    
    # Vérifier que le callback a été appelé
    callback.assert_called()
    assert "BTC/USDT" in collector.tweets

@pytest.mark.asyncio
async def test_get_sentiment_metrics(collector):
    """Teste le calcul des métriques de sentiment."""
    # Ajouter des tweets de test
    collector.tweets["BTC/USDT"] = [
        {
            'id': '1',
            'text': 'Very bullish on BTC!',
            'polarity': 0.8,
            'subjectivity': 0.6
        },
        {
            'id': '2',
            'text': 'Not sure about BTC...',
            'polarity': 0.0,
            'subjectivity': 0.3
        },
        {
            'id': '3',
            'text': 'BTC looking bearish',
            'polarity': -0.6,
            'subjectivity': 0.7
        }
    ]
    
    # Calculer les métriques
    metrics = await collector.get_sentiment_metrics("BTC/USDT")
    
    assert 'average_polarity' in metrics
    assert 'average_subjectivity' in metrics
    assert 'tweet_count' in metrics
    assert 'bullish_ratio' in metrics
    assert metrics['tweet_count'] == 3
    assert metrics['bullish_ratio'] == pytest.approx(0.333, rel=0.01)

@pytest.mark.asyncio
async def test_error_handling(collector):
    """Teste la gestion des erreurs."""
    # Test avec une erreur d'API
    with patch('tweepy.Client', return_value=AsyncMock()) as mock_client:
        mock_client.return_value.search_recent_tweets = AsyncMock(
            side_effect=Exception("API Error")
        )
        
        start_time = datetime.now() - timedelta(days=1)
        tweets = await collector.get_historical_tweets(
            symbol="BTC/USDT",
            start_time=start_time
        )
        
        assert tweets == []
        
    # Test avec un symbole invalide
    metrics = await collector.get_sentiment_metrics("INVALID/PAIR")
    assert metrics['tweet_count'] == 0
    assert metrics['average_polarity'] == 0.0 