"""Tests unitaires pour le collecteur Reddit."""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from sadie.data.collectors.reddit import RedditCollector

@pytest.fixture
def sample_submission():
    """Crée une soumission Reddit de test."""
    submission = Mock()
    submission.id = "abc123"
    submission.title = "Bitcoin breaking new highs! BTC to the moon!"
    submission.selftext = "Technical analysis suggests BTC will reach new ATH soon."
    submission.created_utc = datetime.now().timestamp()
    submission.subreddit = Mock(display_name="CryptoCurrency")
    submission.score = 100
    submission.upvote_ratio = 0.85
    submission.num_comments = 50
    return submission

@pytest.fixture
def collector():
    """Crée une instance du collecteur pour les tests."""
    collector = RedditCollector(
        client_id="test_id",
        client_secret="test_secret",
        user_agent="test_agent",
        window_size=100
    )
    return collector

@pytest.mark.asyncio
async def test_initialization(collector):
    """Teste l'initialisation du collecteur."""
    assert collector.api_key == "test_id"
    assert collector.api_secret == "test_secret"
    assert collector.user_agent == "test_agent"
    assert collector.window_size == 100
    assert not collector._running
    assert isinstance(collector.posts, dict)
    assert isinstance(collector.subreddits, list)
    assert "CryptoCurrency" in collector.subreddits

@pytest.mark.asyncio
async def test_start_stop_stream(collector):
    """Teste le démarrage et l'arrêt du stream."""
    with patch('praw.Reddit', return_value=Mock()) as mock_client:
        # Démarrer le stream
        callback = AsyncMock()
        await collector.start_stream(["BTC/USDT"], callback)
        
        assert collector._running
        assert len(collector._stream_tasks) == 1
        
        # Arrêter le stream
        await collector.stop_stream()
        
        assert not collector._running
        assert not collector._stream_tasks

@pytest.mark.asyncio
async def test_get_historical_posts(collector, sample_submission):
    """Teste la récupération des posts historiques."""
    with patch('praw.Reddit', return_value=Mock()) as mock_client:
        # Configurer le mock
        mock_subreddit = Mock()
        mock_subreddit.search.return_value = [sample_submission]
        mock_client.return_value.subreddit.return_value = mock_subreddit
        
        # Récupérer les posts
        start_time = datetime.now() - timedelta(days=1)
        posts = await collector.get_historical_posts(
            symbol="BTC/USDT",
            start_time=start_time,
            limit=10
        )
        
        assert len(posts) == 1
        assert posts[0]['id'] == sample_submission.id
        assert posts[0]['title'] == sample_submission.title
        assert 'polarity' in posts[0]
        assert 'subjectivity' in posts[0]

@pytest.mark.asyncio
async def test_maintain_stream(collector, sample_submission):
    """Teste le maintien du stream de posts."""
    # Configurer le mock
    mock_subreddit = Mock()
    mock_subreddit.stream.submissions.return_value = [sample_submission]
    
    with patch('praw.Reddit', return_value=Mock()) as mock_client:
        mock_client.return_value.subreddit.return_value = mock_subreddit
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
        assert "BTC/USDT" in collector.posts

@pytest.mark.asyncio
async def test_get_community_metrics(collector):
    """Teste le calcul des métriques communautaires."""
    # Ajouter des posts de test
    collector.posts["BTC/USDT"] = [
        {
            'id': '1',
            'title': 'Very bullish on BTC!',
            'text': 'Analysis suggests upward trend',
            'polarity': 0.8,
            'subjectivity': 0.6,
            'score': 100,
            'num_comments': 50
        },
        {
            'id': '2',
            'title': 'Not sure about BTC...',
            'text': 'Market seems uncertain',
            'polarity': 0.0,
            'subjectivity': 0.3,
            'score': 50,
            'num_comments': 25
        },
        {
            'id': '3',
            'title': 'BTC looking bearish',
            'text': 'Technical indicators suggest downtrend',
            'polarity': -0.6,
            'subjectivity': 0.7,
            'score': 75,
            'num_comments': 35
        }
    ]
    
    # Calculer les métriques
    metrics = await collector.get_community_metrics("BTC/USDT")
    
    assert 'average_polarity' in metrics
    assert 'average_subjectivity' in metrics
    assert 'post_count' in metrics
    assert 'average_score' in metrics
    assert 'average_comments' in metrics
    assert 'bullish_ratio' in metrics
    assert 'engagement_rate' in metrics
    assert metrics['post_count'] == 3
    assert metrics['bullish_ratio'] == pytest.approx(0.333, rel=0.01)
    assert metrics['average_score'] == pytest.approx(75.0)
    assert metrics['average_comments'] == pytest.approx(36.67, rel=0.01)

@pytest.mark.asyncio
async def test_error_handling(collector):
    """Teste la gestion des erreurs."""
    with patch('praw.Reddit', return_value=Mock()) as mock_client:
        # Configurer le mock pour lever une exception
        mock_client.return_value.subreddit.side_effect = Exception("API Error")
        
        # Test avec une erreur d'API
        start_time = datetime.now() - timedelta(days=1)
        posts = await collector.get_historical_posts(
            symbol="BTC/USDT",
            start_time=start_time
        )
        
        assert posts == []
        
    # Test avec un symbole invalide
    metrics = await collector.get_community_metrics("INVALID/PAIR")
    assert metrics['post_count'] == 0
    assert metrics['average_polarity'] == 0.0
    assert metrics['engagement_rate'] == 0.0

@pytest.mark.asyncio
async def test_subreddit_configuration(collector):
    """Teste la configuration des subreddits."""
    # Test avec des subreddits personnalisés
    custom_subreddits = ["test1", "test2"]
    collector = RedditCollector(
        client_id="test_id",
        client_secret="test_secret",
        user_agent="test_agent",
        subreddits=custom_subreddits
    )
    
    assert collector.subreddits == custom_subreddits
    assert len(collector.subreddits) == 2
    
    # Test avec les subreddits par défaut
    collector = RedditCollector(
        client_id="test_id",
        client_secret="test_secret",
        user_agent="test_agent"
    )
    
    assert "CryptoCurrency" in collector.subreddits
    assert "Bitcoin" in collector.subreddits 