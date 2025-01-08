"""Tests unitaires pour le collecteur d'actualités."""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from sadie.data.collectors.news import NewsCollector

@pytest.fixture
def sample_article():
    """Crée un article de test."""
    return {
        'title': 'Bitcoin reaches new all-time high',
        'description': 'BTC breaks previous records as institutional adoption grows',
        'url': 'https://example.com/article',
        'source': {'name': 'CryptoNews'},
        'publishedAt': '2024-01-20T12:00:00Z'
    }

@pytest.fixture
def collector():
    """Crée une instance du collecteur pour les tests."""
    collector = NewsCollector(
        api_key="test_api_key",
        window_size=100,
        update_interval=60
    )
    return collector

@pytest.mark.asyncio
async def test_initialization(collector):
    """Teste l'initialisation du collecteur."""
    assert collector.api_key == "test_api_key"
    assert collector.window_size == 100
    assert collector.update_interval == 60
    assert not collector._running
    assert isinstance(collector.articles, dict)
    assert isinstance(collector.languages, list)
    assert "en" in collector.languages
    assert "fr" in collector.languages

@pytest.mark.asyncio
async def test_start_stop_stream(collector):
    """Teste le démarrage et l'arrêt du stream."""
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
async def test_get_historical_news(collector, sample_article):
    """Teste la récupération des actualités historiques."""
    mock_response = {
        'status': 'ok',
        'articles': [sample_article]
    }
    
    # Simuler la réponse de l'API
    mock_session = AsyncMock()
    mock_session.get.return_value.__aenter__.return_value.status = 200
    mock_session.get.return_value.__aenter__.return_value.json = AsyncMock(
        return_value=mock_response
    )
    
    with patch('aiohttp.ClientSession', return_value=mock_session):
        start_time = datetime.now() - timedelta(days=1)
        articles = await collector.get_historical_news(
            symbol="BTC/USDT",
            start_time=start_time,
            limit=10
        )
        
        assert len(articles) == 1
        assert articles[0]['title'] == sample_article['title']
        assert 'polarity' in articles[0]
        assert 'subjectivity' in articles[0]

@pytest.mark.asyncio
async def test_maintain_stream(collector, sample_article):
    """Teste le maintien du stream d'actualités."""
    mock_response = {
        'status': 'ok',
        'articles': [sample_article]
    }
    
    # Simuler la réponse de l'API
    mock_session = AsyncMock()
    mock_session.get.return_value.__aenter__.return_value.status = 200
    mock_session.get.return_value.__aenter__.return_value.json = AsyncMock(
        return_value=mock_response
    )
    
    with patch('aiohttp.ClientSession', return_value=mock_session):
        collector._running = True
        callback = AsyncMock()
        
        # Exécuter le stream pendant un court moment
        task = asyncio.create_task(collector._maintain_stream("BTC/USDT", callback))
        await asyncio.sleep(0.1)
        collector._running = False
        await task
        
        # Vérifier que le callback a été appelé
        callback.assert_called()
        assert "BTC/USDT" in collector.articles

@pytest.mark.asyncio
async def test_get_news_metrics(collector):
    """Teste le calcul des métriques d'actualités."""
    # Ajouter des articles de test
    collector.articles["BTC/USDT"] = [
        {
            'title': 'Very bullish on Bitcoin',
            'description': 'Analysis suggests upward trend',
            'url': 'https://example.com/1',
            'source': 'Source1',
            'published_at': datetime.utcnow(),
            'polarity': 0.8,
            'subjectivity': 0.6
        },
        {
            'title': 'Market uncertainty for BTC',
            'description': 'Mixed signals in crypto market',
            'url': 'https://example.com/2',
            'source': 'Source2',
            'published_at': datetime.utcnow() - timedelta(hours=2),
            'polarity': 0.0,
            'subjectivity': 0.4
        },
        {
            'title': 'Bitcoin faces resistance',
            'description': 'Technical analysis shows resistance',
            'url': 'https://example.com/3',
            'source': 'Source1',
            'published_at': datetime.utcnow() - timedelta(minutes=30),
            'polarity': -0.3,
            'subjectivity': 0.7
        }
    ]
    
    # Calculer les métriques
    metrics = await collector.get_news_metrics("BTC/USDT")
    
    assert 'average_polarity' in metrics
    assert 'average_subjectivity' in metrics
    assert 'article_count' in metrics
    assert 'source_diversity' in metrics
    assert 'bullish_ratio' in metrics
    assert 'hourly_volume' in metrics
    assert metrics['article_count'] == 3
    assert metrics['source_diversity'] == pytest.approx(0.667, rel=0.01)
    assert metrics['bullish_ratio'] == pytest.approx(0.333, rel=0.01)
    assert metrics['hourly_volume'] == 2

@pytest.mark.asyncio
async def test_error_handling(collector):
    """Teste la gestion des erreurs."""
    # Test avec une erreur d'API
    mock_session = AsyncMock()
    mock_session.get.return_value.__aenter__.return_value.status = 500
    
    with patch('aiohttp.ClientSession', return_value=mock_session):
        start_time = datetime.now() - timedelta(days=1)
        articles = await collector.get_historical_news(
            symbol="BTC/USDT",
            start_time=start_time
        )
        
        assert articles == []
        
    # Test avec un symbole invalide
    metrics = await collector.get_news_metrics("INVALID/PAIR")
    assert metrics['article_count'] == 0
    assert metrics['average_polarity'] == 0.0
    assert metrics['hourly_volume'] == 0.0

@pytest.mark.asyncio
async def test_language_configuration(collector):
    """Teste la configuration des langues."""
    # Test avec des langues personnalisées
    custom_languages = ["es", "de"]
    collector = NewsCollector(
        api_key="test_api_key",
        languages=custom_languages
    )
    
    assert collector.languages == custom_languages
    assert len(collector.languages) == 2
    
    # Test avec les langues par défaut
    collector = NewsCollector(
        api_key="test_api_key"
    )
    
    assert "en" in collector.languages
    assert "fr" in collector.languages 