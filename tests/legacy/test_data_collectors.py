"""
Tests unitaires pour les collecteurs de données.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from sadie.data.collectors import BaseCollector, RESTCollector, WebSocketCollector
from sadie.data.exceptions import DataCollectionError, ValidationError

@pytest.fixture
def mock_session():
    """Fixture pour simuler une session HTTP."""
    session = AsyncMock()
    session.get = AsyncMock()
    session.close = AsyncMock()
    return session

@pytest.fixture
def mock_websocket():
    """Fixture pour simuler une connexion WebSocket."""
    ws = AsyncMock()
    ws.connect = AsyncMock()
    ws.close = AsyncMock()
    ws.recv = AsyncMock()
    return ws

@pytest.mark.asyncio
async def test_rest_collector_init():
    """Teste l'initialisation du collecteur REST."""
    symbols = ["BTCUSDT", "ETHUSDT"]
    base_url = "https://api.example.com"
    collector = RESTCollector(symbols=symbols, base_url=base_url)
    
    assert collector.symbols == symbols
    assert collector.base_url == base_url
    assert not collector.running
    assert collector.session is None

@pytest.mark.asyncio
async def test_rest_collector_start_stop(mock_session):
    """Teste le démarrage et l'arrêt du collecteur REST."""
    with patch("aiohttp.ClientSession", return_value=mock_session):
        collector = RESTCollector(symbols=["BTCUSDT"], base_url="https://api.example.com")
        
        await collector.start()
        assert collector.running
        assert collector.session is not None
        
        await collector.stop()
        assert not collector.running
        assert collector.session is None
        mock_session.close.assert_called_once()

@pytest.mark.asyncio
async def test_websocket_collector_init():
    """Teste l'initialisation du collecteur WebSocket."""
    symbols = ["BTCUSDT", "ETHUSDT"]
    ws_url = "wss://stream.example.com"
    collector = WebSocketCollector(symbols=symbols, ws_url=ws_url)
    
    assert collector.symbols == symbols
    assert collector.ws_url == ws_url
    assert not collector.running
    assert collector.ws is None

@pytest.mark.asyncio
async def test_websocket_collector_connect(mock_websocket):
    """Teste la connexion WebSocket."""
    with patch("websockets.connect", return_value=mock_websocket):
        collector = WebSocketCollector(
            symbols=["BTCUSDT"],
            ws_url="wss://stream.example.com"
        )
        
        await collector._connect()
        assert collector.ws is not None

@pytest.mark.asyncio
async def test_websocket_collector_connect_error(mock_websocket):
    """Teste la gestion des erreurs de connexion WebSocket."""
    mock_websocket.connect.side_effect = Exception("Connection failed")
    
    with patch("websockets.connect", return_value=mock_websocket):
        collector = WebSocketCollector(
            symbols=["BTCUSDT"],
            ws_url="wss://stream.example.com"
        )
        
        with pytest.raises(DataCollectionError):
            await collector._connect()

@pytest.mark.asyncio
async def test_collector_validation():
    """Teste la validation des symboles."""
    with pytest.raises(ValidationError):
        RESTCollector(symbols=[""], base_url="https://api.example.com")
    
    with pytest.raises(ValidationError):
        RESTCollector(symbols=["BTC/"], base_url="https://api.example.com")
    
    with pytest.raises(ValidationError):
        RESTCollector(symbols=["BTC@USD"], base_url="https://api.example.com") 