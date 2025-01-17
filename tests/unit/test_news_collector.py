"""Tests unitaires pour le collecteur d'actualités."""

import json
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientSession

from sadie.data.sentiment.news import NewsCollector
from sadie.data.sentiment.models import SentimentSource

@pytest.fixture
def mock_response():
    """Crée une réponse mock pour l'API."""
    return {
        "status": "ok",
        "totalResults": 2,
        "articles": [
            {
                "source": {"id": "bloomberg", "name": "Bloomberg"},
                "title": "Bitcoin Surges to New High",
                "description": "Bitcoin reaches $50,000 in major rally",
                "content": "Bitcoin price increases significantly...",
                "url": "https://bloomberg.com/article1",
                "publishedAt": datetime.now(timezone.utc).isoformat()
            },
            {
                "source": {"id": "reuters", "name": "Reuters"},
                "title": "Crypto Market Analysis",
                "description": "Market trends show positive momentum",
                "content": "Cryptocurrency markets continue to grow...",
                "url": "https://reuters.com/article2",
                "publishedAt": datetime.now(timezone.utc).isoformat()
            }
        ]
    }

@pytest.fixture
async def collector():
    """Crée une instance du collecteur."""
    collector = NewsCollector(
        api_key="test_key",
        batch_size=10,
        lang="en",
        lookback_hours=24
    )
    return collector

@pytest.mark.asyncio
async def test_initialization(collector):
    """Teste l'initialisation du collecteur."""
    assert collector.api_key == "test_key"
    assert collector.batch_size == 10
    assert collector.lang == "en"
    assert collector.lookback_hours == 24
    assert collector._session is None

@pytest.mark.asyncio
async def test_context_manager(collector):
    """Teste le gestionnaire de contexte."""
    async with collector as c:
        assert isinstance(c._session, ClientSession)
        assert "X-Api-Key" in c._session.headers
        assert c._session.headers["X-Api-Key"] == "test_key"
    assert collector._session is None

@pytest.mark.asyncio
async def test_build_query(collector):
    """Teste la construction des requêtes."""
    # Test pour crypto
    query = collector._build_query("BTC")
    assert "BTC" in query
    assert "crypto" in query
    assert "blockchain" in query
    
    # Test pour forex
    query = collector._build_query("EUR")
    assert "EUR" in query
    assert "forex" in query
    assert "exchange rate" in query

@pytest.mark.asyncio
async def test_analyze_sentiment(collector):
    """Teste l'analyse de sentiment."""
    # Test sentiment positif
    score = collector._analyze_sentiment("Great news for investors!")
    assert isinstance(score, Decimal)
    assert score > 0
    
    # Test sentiment négatif
    score = collector._analyze_sentiment("Market crash continues.")
    assert isinstance(score, Decimal)
    assert score < 0
    
    # Test sentiment neutre
    score = collector._analyze_sentiment("Market remains stable.")
    assert isinstance(score, Decimal)
    assert -0.1 <= float(score) <= 0.1

@pytest.mark.asyncio
async def test_analyze_article(collector):
    """Teste l'analyse d'articles."""
    article = {
        "title": "Bitcoin Surges to New High",
        "description": "Positive market momentum",
        "content": "Great news for investors",
        "url": "https://bloomberg.com/article",
        "publishedAt": datetime.now(timezone.utc).isoformat()
    }
    
    score, pertinence = collector._analyze_article(article)
    assert isinstance(score, Decimal)
    assert isinstance(pertinence, int)
    assert pertinence > 0
    
    # Test pondération par source
    article["url"] = "https://reuters.com/article"
    _, pertinence_reuters = collector._analyze_article(article)
    assert pertinence_reuters > 0
    
    article["url"] = "https://unknown.com/article"
    _, pertinence_unknown = collector._analyze_article(article)
    assert pertinence_unknown < pertinence_reuters

@pytest.mark.asyncio
async def test_search_articles(collector, mock_response):
    """Teste la recherche d'articles."""
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_response
        )
        
        async with collector:
            articles = await collector.search_articles("BTC")
            assert len(articles) == 2
            assert articles[0]["source"]["name"] == "Bloomberg"
            assert articles[1]["source"]["name"] == "Reuters"
            
            # Vérifie les paramètres de la requête
            call_args = mock_get.call_args
            assert "BTC" in call_args[1]["params"]["q"]
            assert call_args[1]["params"]["language"] == "en"
            assert call_args[1]["params"]["pageSize"] == 10

@pytest.mark.asyncio
async def test_collect(collector, mock_response):
    """Teste la collecte complète."""
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_response
        )
        
        async with collector:
            score = await collector.collect("BTC")
            assert score is not None
            assert score.symbol == "BTC"
            assert score.source == SentimentSource.NEWS
            assert isinstance(score.score, Decimal)
            assert score.volume > 0
            assert "article_count" in score.metadata
            assert "sources" in score.metadata
            assert len(score.metadata["sources"]) == 2

@pytest.mark.asyncio
async def test_error_handling(collector):
    """Teste la gestion des erreurs."""
    with patch("aiohttp.ClientSession.get") as mock_get:
        # Test erreur HTTP
        mock_get.return_value.__aenter__.return_value.status = 401
        mock_get.return_value.__aenter__.return_value.text = AsyncMock(
            return_value="Unauthorized"
        )
        
        async with collector:
            articles = await collector.search_articles("BTC")
            assert articles == []
            
        # Test erreur réseau
        mock_get.side_effect = Exception("Network error")
        async with collector:
            articles = await collector.search_articles("BTC")
            assert articles == [] 