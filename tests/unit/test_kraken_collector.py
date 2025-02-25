"""Tests unitaires pour le collecteur Kraken."""

import asyncio
import json
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch, call

import pytest
from websockets.exceptions import ConnectionClosed

from sadie.core.collectors.kraken_collector import KrakenTradeCollector
from sadie.core.models.events import Exchange, Symbol, Trade

@pytest.fixture
def kraken_collector():
    """Fixture pour le collecteur de trades Kraken."""
    return KrakenTradeCollector(
        name="kraken_test",
        symbols=["XBT/USD", "ETH/USD"],
        update_interval=0.1,
        max_retries=3,
        retry_delay=0.1,
        connection_timeout=2.0,
        api_key="test_key",
        api_secret="test_secret"
    )

@pytest.mark.asyncio
async def test_initialization(kraken_collector):
    """Test de l'initialisation du collecteur."""
    assert kraken_collector.name == "kraken_test"
    assert kraken_collector.symbols == ["XBT/USD", "ETH/USD"]
    assert kraken_collector.update_interval == 0.1
    assert kraken_collector.max_retries == 3
    assert kraken_collector.retry_delay == 0.1
    assert kraken_collector.connection_timeout == 2.0
    assert kraken_collector.api_key == "test_key"
    assert kraken_collector.api_secret == "test_secret"
    assert not kraken_collector._running

@pytest.mark.asyncio
async def test_start_stop(kraken_collector):
    """Test du démarrage et de l'arrêt du collecteur."""
    # Mock de la connexion websocket
    mock_ws = AsyncMock()
    mock_ws.connect = AsyncMock()
    mock_ws.close = AsyncMock()

    with patch('sadie.core.collectors.kraken_collector.websockets.connect', 
               return_value=mock_ws):
        # Démarrage du collecteur
        await kraken_collector.start()
        assert kraken_collector._running is True
        assert kraken_collector._task is not None
        
        # Arrêt du collecteur
        await kraken_collector.stop()
        assert kraken_collector._running is False
        assert kraken_collector._task is None

@pytest.mark.asyncio
async def test_connect_to_websocket(kraken_collector):
    """Test de la connexion au websocket Kraken."""
    mock_ws = AsyncMock()
    mock_ws.__aenter__ = AsyncMock(return_value=mock_ws)
    mock_ws.__aexit__ = AsyncMock()
    mock_ws.send = AsyncMock()
    mock_ws.recv = AsyncMock(side_effect=[
        json.dumps({"connectionID": 12345}),  # Message de confirmation de connexion
        asyncio.CancelledError()  # Pour sortir de la boucle
    ])

    with patch('sadie.core.collectors.kraken_collector.websockets.connect', 
               return_value=mock_ws):
        # Démarrage du collecteur
        await kraken_collector.start()
        
        # Attendre que la connexion soit établie
        await asyncio.sleep(0.2)
        
        # Vérifier que le message de souscription a été envoyé
        mock_ws.send.assert_called_with(json.dumps({
            "name": "subscribe",
            "reqid": kraken_collector._req_id - 1,
            "pair": ["XBT/USD", "ETH/USD"],
            "subscription": {"name": "trade"}
        }))
        
        # Arrêt du collecteur
        await kraken_collector.stop()

@pytest.mark.asyncio
async def test_process_message(kraken_collector):
    """Test du traitement des messages de trades."""
    # Création d'un message de trade Kraken
    mock_trade_message = json.dumps([
        278,
        [
            ["5541.20000", "0.15850208", "1534614057.321597", "s", "l", ""],
            ["6060.00000", "0.02455000", "1534614057.324998", "b", "l", ""]
        ],
        "trade",
        "XBT/USD"
    ])
    
    # Mock de la connexion websocket
    mock_ws = AsyncMock()
    mock_ws.__aenter__ = AsyncMock(return_value=mock_ws)
    mock_ws.__aexit__ = AsyncMock()
    mock_ws.send = AsyncMock()
    mock_ws.recv = AsyncMock(side_effect=[
        json.dumps({"connectionID": 12345}),  # Message de confirmation de connexion
        mock_trade_message,  # Message de trade
        asyncio.CancelledError()  # Pour sortir de la boucle
    ])

    with patch('sadie.core.collectors.kraken_collector.websockets.connect', 
               return_value=mock_ws):
        # Démarrage du collecteur
        await kraken_collector.start()
        
        # Attendre que les messages soient traités
        await asyncio.sleep(0.3)
        
        # Vérifier que les trades ont été collectés
        trades = await kraken_collector.get_trades("XBT/USD")
        assert len(trades) == 2
        
        # Vérifier les détails du premier trade
        assert trades[0]["price"] == Decimal("5541.20000")
        assert trades[0]["amount"] == Decimal("0.15850208")
        assert trades[0]["side"] == "sell"
        
        # Arrêt du collecteur
        await kraken_collector.stop()

@pytest.mark.asyncio
async def test_error_handling(kraken_collector):
    """Test de la gestion des erreurs."""
    # Mock de la connexion websocket avec erreurs
    mock_ws_factory = MagicMock()
    
    # Premier appel : lève une erreur
    mock_ws1 = AsyncMock()
    mock_ws1.__aenter__ = AsyncMock(side_effect=ConnectionClosed(1006, "Connection closed abnormally"))
    
    # Deuxième appel : réussit mais reçoit une erreur de l'API
    mock_ws2 = AsyncMock()
    mock_ws2.__aenter__ = AsyncMock(return_value=mock_ws2)
    mock_ws2.__aexit__ = AsyncMock()
    mock_ws2.send = AsyncMock()
    mock_ws2.recv = AsyncMock(side_effect=[
        json.dumps({"connectionID": 12345}),
        json.dumps({"error": "API rate limit exceeded"}),
        asyncio.CancelledError()
    ])
    
    # Définir l'ordre des mocks retournés
    mock_ws_factory.side_effect = [mock_ws1, mock_ws2]
    
    with patch('sadie.core.collectors.kraken_collector.websockets.connect', 
               mock_ws_factory):
        # Démarrage du collecteur
        await kraken_collector.start()
        
        # Attendre que les tentatives de reconnexion se produisent
        await asyncio.sleep(0.5)
        
        # Vérifier que le collecteur est toujours en cours d'exécution malgré les erreurs
        assert kraken_collector._running is True
        
        # Arrêt du collecteur
        await kraken_collector.stop()

@pytest.mark.asyncio
async def test_ping_mechanism(kraken_collector):
    """Test du mécanisme de ping pour maintenir la connexion active."""
    # Mock de la connexion websocket
    mock_ws = AsyncMock()
    mock_ws.__aenter__ = AsyncMock(return_value=mock_ws)
    mock_ws.__aexit__ = AsyncMock()
    mock_ws.send = AsyncMock()
    mock_ws.recv = AsyncMock(side_effect=[
        json.dumps({"connectionID": 12345}),  # Message de confirmation de connexion
        asyncio.TimeoutError(),  # Simule un timeout pour déclencher un ping
        json.dumps({"pong": "test"}),  # Réponse au ping
        asyncio.CancelledError()  # Pour sortir de la boucle
    ])

    # Réduire l'intervalle de ping pour le test
    kraken_collector._ping_interval = 0.1
    
    with patch('sadie.core.collectors.kraken_collector.websockets.connect', 
               return_value=mock_ws):
        # Démarrage du collecteur
        await kraken_collector.start()
        
        # Attendre que le ping soit envoyé
        await asyncio.sleep(0.3)
        
        # Vérifier que le ping a été envoyé
        assert any(call(json.dumps({"ping": mock_ws.mock_calls})) in mock_ws.send.call_args_list for c in mock_ws.mock_calls)
        
        # Arrêt du collecteur
        await kraken_collector.stop() 