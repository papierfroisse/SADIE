"""Tests unitaires pour les collecteurs de données."""

import asyncio
import json
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest
import websockets

from sadie.data.collectors.base import BaseCollector
from sadie.data.collectors.rest import RESTCollector
from sadie.data.collectors.websocket import WebSocketCollector

# Tests pour RESTCollector
@pytest.fixture
def rest_collector():
    """Crée un collecteur REST pour les tests."""
    return RESTCollector(
        name="test_rest",
        base_url="https://api.example.com",
        timeout=5,
        headers={"Authorization": "Bearer test"}
    )

@pytest.mark.asyncio
async def test_rest_collector_init(rest_collector):
    """Teste l'initialisation du collecteur REST."""
    assert rest_collector.base_url == "https://api.example.com"
    assert rest_collector.timeout == 5
    assert rest_collector.headers == {"Authorization": "Bearer test"}
    assert not rest_collector._running

@pytest.mark.asyncio
async def test_rest_collector_start_stop(rest_collector):
    """Teste le démarrage et l'arrêt du collecteur REST."""
    await rest_collector.start()
    assert rest_collector._running
    assert rest_collector._session is not None

    await rest_collector.stop()
    assert not rest_collector._running
    assert rest_collector._session is None

@pytest.mark.asyncio
async def test_rest_collector_fetch(rest_collector):
    """Teste la méthode fetch du collecteur REST."""
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
    """Teste la gestion des erreurs du collecteur REST."""
    async def mock_request(*args, **kwargs):
        raise aiohttp.ClientError("Test error")

    await rest_collector.start()
    with patch.object(rest_collector._session, "request", mock_request):
        with pytest.raises(aiohttp.ClientError):
            await rest_collector.fetch("test/endpoint")

    await rest_collector.stop()

# Tests pour WebSocketCollector
@pytest.fixture
def ws_collector():
    """Crée un collecteur WebSocket pour les tests."""
    return WebSocketCollector(
        name="test_ws",
        url="wss://ws.example.com",
        headers={"Authorization": "Bearer test"}
    )

@pytest.mark.asyncio
async def test_ws_collector_init(ws_collector):
    """Teste l'initialisation du collecteur WebSocket."""
    assert ws_collector.url == "wss://ws.example.com"
    assert ws_collector.headers == {"Authorization": "Bearer test"}
    assert not ws_collector._running

@pytest.mark.asyncio
async def test_ws_collector_connect_disconnect():
    """Teste la connexion et déconnexion du collecteur WebSocket."""
    collector = WebSocketCollector(
        name="test_ws",
        url="wss://ws.example.com"
    )
    
    mock_ws = AsyncMock()
    mock_ws.close = AsyncMock()
    
    with patch("websockets.connect", AsyncMock(return_value=mock_ws)):
        await collector.connect()
        assert collector._ws is not None
        
        await collector.disconnect()
        assert collector._ws is None
        mock_ws.close.assert_called_once()

@pytest.mark.asyncio
async def test_ws_collector_message_handling():
    """Teste le traitement des messages du collecteur WebSocket."""
    collector = WebSocketCollector(
        name="test_ws",
        url="wss://ws.example.com"
    )
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
    """Teste la logique de reconnexion du collecteur WebSocket."""
    collector = WebSocketCollector(
        name="test_ws",
        url="wss://ws.example.com"
    )
    
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