"""Unit tests for data collectors."""

import asyncio
import json
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest
import websockets

from sadie.data.collectors import AsyncRESTCollector, AsyncWebSocketCollector

# Tests pour AsyncRESTCollector
@pytest.fixture
def rest_collector():
    """Create a REST collector for testing."""
    return AsyncRESTCollector(
        base_url="https://api.example.com",
        timeout=5,
        headers={"Authorization": "Bearer test"}
    )

@pytest.mark.asyncio
async def test_rest_collector_init(rest_collector):
    """Test REST collector initialization."""
    assert rest_collector.base_url == "https://api.example.com"
    assert rest_collector.timeout == 5
    assert rest_collector.headers == {"Authorization": "Bearer test"}
    assert not rest_collector.is_running

@pytest.mark.asyncio
async def test_rest_collector_start_stop(rest_collector):
    """Test REST collector start and stop."""
    await rest_collector.start()
    assert rest_collector.is_running
    assert rest_collector._session is not None

    await rest_collector.stop()
    assert not rest_collector.is_running
    assert rest_collector._session is None

@pytest.mark.asyncio
async def test_rest_collector_fetch(rest_collector):
    """Test REST collector fetch method."""
    test_data = {"key": "value"}
    
    async def mock_request(*args, **kwargs):
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_response.json = AsyncMock(return_value=test_data)
        return mock_response

    await rest_collector.start()
    with patch.object(rest_collector._session, "request", mock_request):
        data = await rest_collector.fetch("test/endpoint")
        assert data == test_data

    await rest_collector.stop()

@pytest.mark.asyncio
async def test_rest_collector_fetch_error(rest_collector):
    """Test REST collector fetch error handling."""
    async def mock_request(*args, **kwargs):
        raise aiohttp.ClientError("Test error")

    await rest_collector.start()
    with patch.object(rest_collector._session, "request", mock_request):
        with pytest.raises(aiohttp.ClientError):
            await rest_collector.fetch("test/endpoint")

    await rest_collector.stop()

@pytest.mark.asyncio
async def test_rest_collector_fetch_batch(rest_collector):
    """Test REST collector batch fetch."""
    test_data = {"key": "value"}
    
    async def mock_request(*args, **kwargs):
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_response.json = AsyncMock(return_value=test_data)
        return mock_response

    await rest_collector.start()
    with patch.object(rest_collector._session, "request", mock_request):
        data = await rest_collector.fetch_batch(["endpoint1", "endpoint2"])
        assert len(data) == 2
        assert all(d == test_data for d in data)

    await rest_collector.stop()

# Tests pour AsyncWebSocketCollector
@pytest.fixture
def ws_collector():
    """Create a WebSocket collector for testing."""
    return AsyncWebSocketCollector(
        url="wss://ws.example.com",
        headers={"Authorization": "Bearer test"}
    )

@pytest.mark.asyncio
async def test_ws_collector_init(ws_collector):
    """Test WebSocket collector initialization."""
    assert ws_collector.url == "wss://ws.example.com"
    assert ws_collector.headers == {"Authorization": "Bearer test"}
    assert not ws_collector.is_running

@pytest.mark.asyncio
async def test_ws_collector_connect_disconnect():
    """Test WebSocket collector connect and disconnect."""
    collector = AsyncWebSocketCollector("wss://ws.example.com")
    
    mock_ws = AsyncMock()
    mock_ws.close = AsyncMock()
    
    with patch("websockets.connect", AsyncMock(return_value=mock_ws)):
        await collector.connect()
        assert collector._ws is not None
        
        await collector.disconnect()
        assert collector._ws is None
        mock_ws.close.assert_called_once()

@pytest.mark.asyncio
async def test_ws_collector_subscribe_unsubscribe():
    """Test WebSocket collector subscribe and unsubscribe."""
    collector = AsyncWebSocketCollector("wss://ws.example.com")
    mock_ws = AsyncMock()
    mock_ws.send = AsyncMock()
    collector._ws = mock_ws

    await collector.subscribe("test_channel")
    assert "test_channel" in collector._subscribed_channels
    mock_ws.send.assert_called_with('{"type": "subscribe", "channel": "test_channel"}')

    await collector.unsubscribe("test_channel")
    assert "test_channel" not in collector._subscribed_channels
    mock_ws.send.assert_called_with('{"type": "unsubscribe", "channel": "test_channel"}')

@pytest.mark.asyncio
async def test_ws_collector_message_handling():
    """Test WebSocket collector message handling."""
    collector = AsyncWebSocketCollector("wss://ws.example.com")
    mock_ws = AsyncMock()
    
    # Simuler des messages WebSocket
    messages = [
        json.dumps({"channel": "test", "data": "message1"}),
        json.dumps({"channel": "test", "data": "message2"}),
    ]
    mock_ws.__aiter__.return_value = messages
    collector._ws = mock_ws

    # Ajouter un handler de message
    message_handler = AsyncMock()
    collector.add_message_handler("test", message_handler)

    # Tester le traitement des messages
    await collector._handle_messages()
    assert message_handler.call_count == 2

@pytest.mark.asyncio
async def test_ws_collector_reconnection():
    """Test WebSocket collector reconnection logic."""
    collector = AsyncWebSocketCollector("wss://ws.example.com")
    
    # Simuler une erreur de connexion puis une reconnexion réussie
    mock_ws = AsyncMock()
    mock_ws.close = AsyncMock()
    
    with patch("websockets.connect") as mock_connect:
        mock_connect.side_effect = [
            websockets.WebSocketException("Connection failed"),
            mock_ws,
        ]
        
        await collector.start()
        await asyncio.sleep(0.1)  # Laisser le temps à la reconnexion
        
        assert collector._reconnect_delay > 1.0  # Le délai devrait avoir augmenté
        assert mock_connect.call_count == 2  # Devrait avoir tenté de se reconnecter
        
        await collector.stop() 