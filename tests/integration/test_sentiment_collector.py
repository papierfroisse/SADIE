"""Tests d'intégration pour le collecteur de sentiment."""

import json
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from SADIE.data.sentiment import SentimentCollector, SentimentSource, SentimentAnalyzer, SentimentScore

@pytest.fixture
def mock_twitter_data():
    """Crée des données mock pour Twitter."""
    return {
        "data": [
            {
                "text": "Bitcoin is amazing! #BTC",
                "public_metrics": {
                    "retweet_count": 10,
                    "reply_count": 5,
                    "like_count": 20,
                    "quote_count": 2
                }
            }
        ]
    }

@pytest.fixture
def mock_reddit_data():
    """Crée des données mock pour Reddit."""
    return {
        "data": {
            "children": [
                {
                    "data": {
                        "title": "ETH price analysis",
                        "selftext": "Ethereum looks bullish",
                        "score": 100,
                        "num_comments": 50,
                        "ups": 80
                    }
                }
            ]
        }
    }

@pytest.fixture
def mock_news_data():
    """Crée des données mock pour les actualités."""
    return {
        "status": "ok",
        "articles": [
            {
                "source": {"name": "Bloomberg"},
                "title": "Market Analysis",
                "description": "Positive trends in crypto",
                "content": "Markets show strength",
                "url": "https://bloomberg.com/article",
                "publishedAt": datetime.now(timezone.utc).isoformat()
            }
        ]
    }

@pytest_asyncio.fixture
async def collector():
    """Crée une instance du collecteur."""
    api_keys = {
        "twitter_api_key": "test_key",
        "twitter_api_secret": "test_secret",
        "twitter_bearer_token": "test_token",
        "reddit_client_id": "test_id",
        "reddit_client_secret": "test_secret",
        "reddit_username": "test_user",
        "newsapi_key": "test_key"
    }
    
    collector = SentimentCollector(
        name="test_collector",
        symbols=["BTC", "ETH"],
        sources=[
            SentimentSource.TWITTER,
            SentimentSource.REDDIT,
            SentimentSource.NEWS
        ],
        api_keys=api_keys
    )
    return collector

@pytest.mark.asyncio
async def test_collector_initialization(collector):
    """Teste l'initialisation du collecteur."""
    assert collector.name == "test_collector"
    assert len(collector.symbols) == 2
    assert len(collector.sources) == 3
    assert collector._twitter is not None
    assert collector._reddit is not None
    assert collector._news is not None

@pytest.mark.asyncio
async def test_collect_all_sources(
    collector,
    mock_twitter_data,
    mock_reddit_data,
    mock_news_data
):
    """Teste la collecte depuis toutes les sources."""
    # Mock des réponses API
    with patch("aiohttp.ClientSession.get") as mock_get, \
         patch("aiohttp.ClientSession.post") as mock_post:
        
        # Configuration des mocks
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_post.return_value.__aenter__.return_value.status = 200
        
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(side_effect=lambda: mock_twitter_data)
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value={"access_token": "test_token"})
        
        # Test de la collecte
        data = await collector.collect()
        
        # Vérifications
        assert "BTC" in data
        assert "ETH" in data
        
        for symbol in ["BTC", "ETH"]:
            assert "scores" in data[symbol]
            assert "aggregated" in data[symbol]
            
            scores = data[symbol]["scores"]
            assert len(scores) > 0
            
            # Vérification des scores par source
            for source in collector.sources:
                if source.value in scores:
                    score_data = scores[source.value]
                    assert "score" in score_data
                    assert "volume" in score_data
                    assert "timestamp" in score_data
                    assert "metadata" in score_data

@pytest.mark.asyncio
async def test_source_failure_handling(collector):
    """Teste la gestion des erreurs de source."""
    with patch("aiohttp.ClientSession.get") as mock_get:
        # Simulation d'erreur pour une source
        mock_get.return_value.__aenter__.return_value.status = 500
        mock_get.return_value.__aenter__.return_value.text = AsyncMock(
            return_value="Server error"
        )
        
        # La collecte devrait continuer malgré l'erreur
        data = await collector.collect()
        assert data is not None

@pytest.mark.asyncio
async def test_sentiment_analysis_integration(
    collector,
    mock_twitter_data,
    mock_reddit_data,
    mock_news_data
):
    """Teste l'intégration avec l'analyseur de sentiment."""
    analyzer = SentimentAnalyzer()
    
    with patch("aiohttp.ClientSession.get") as mock_get, \
         patch("aiohttp.ClientSession.post") as mock_post:
        
        # Configuration des mocks
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_post.return_value.__aenter__.return_value.status = 200
        
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(side_effect=lambda: mock_twitter_data)
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value={"access_token": "test_token"})
        
        # Collecte et analyse
        data = await collector.collect()
        
        for symbol in collector.symbols:
            scores = []
            for source in collector.sources:
                if source.value in data[symbol]["scores"]:
                    score_data = data[symbol]["scores"][source.value]
                    scores.append(SentimentScore(
                        symbol=symbol,
                        source=source,
                        score=Decimal(score_data["score"]),
                        timestamp=datetime.fromisoformat(score_data["timestamp"]),
                        volume=score_data["volume"],
                        metadata=score_data["metadata"]
                    ))
            
            # Analyse des scores collectés
            if scores:
                analysis = analyzer.analyze_symbol(symbol, scores)
                assert "symbol" in analysis
                assert "sources" in analysis
                assert "aggregated" in analysis
                
                # Vérification des tendances
                for source_data in analysis["sources"].values():
                    assert "trend" in source_data
                    assert "volume" in source_data
                    assert "anomalies" in source_data 