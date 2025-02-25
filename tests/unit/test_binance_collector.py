"""Tests unitaires pour le collecteur Binance standardisé."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from sadie.core.collectors import BinanceTradeCollector
from sadie.storage import RedisStorage

@pytest.fixture
def mock_binance_client():
    """Fixture qui crée un mock du client Binance."""
    mock_client = MagicMock()
    
    # Mock des méthodes asynchrones
    mock_client.get_historical_trades = AsyncMock(return_value=[
        {
            "id": 28457,
            "price": "4.00000100",
            "qty": "12.00000000",
            "time": 1499865549590,
            "isBuyerMaker": True,
        }
    ])
    
    mock_client.get_recent_trades = AsyncMock(return_value=[
        {
            "id": 28457,
            "price": "4.00000100",
            "qty": "12.00000000",
            "time": 1499865549590,
            "isBuyerMaker": True,
        }
    ])
    
    # Mock pour la connexion WebSocket
    mock_client.ws_connect = AsyncMock()
    mock_client.close_connection = AsyncMock()
    
    return mock_client

@pytest.fixture
def mock_storage():
    """Fixture qui crée un mock du stockage Redis."""
    mock_redis = MagicMock(spec=RedisStorage)
    mock_redis.connect = AsyncMock()
    mock_redis.disconnect = AsyncMock()
    mock_redis.store_trade = AsyncMock()
    mock_redis.get_trades = AsyncMock(return_value=[])
    return mock_redis

@pytest.fixture
def binance_collector(mock_storage):
    """Fixture qui crée un collecteur Binance avec un stockage mocké."""
    return BinanceTradeCollector(
        name="test_binance",
        symbols=["BTCUSDT", "ETHUSDT"],
        storage=mock_storage,
        api_key="test_key",
        api_secret="test_secret",
        update_interval=0.1
    )

@pytest.mark.asyncio
async def test_initialization(binance_collector):
    """Test de l'initialisation du collecteur Binance."""
    assert binance_collector.name == "test_binance"
    assert binance_collector.symbols == ["BTCUSDT", "ETHUSDT"]
    assert binance_collector.api_key == "test_key"
    assert binance_collector.api_secret == "test_secret"
    assert binance_collector.update_interval == 0.1
    assert binance_collector._running is False

@pytest.mark.asyncio
async def test_connect_disconnect(binance_collector, mock_binance_client):
    """Test des méthodes de connexion et déconnexion."""
    with patch('sadie.core.collectors.binance_collector.Client', return_value=mock_binance_client):
        # Test de connexion
        await binance_collector._connect()
        assert binance_collector._client is not None
        mock_binance_client.ws_connect.assert_called_once()
        
        # Test de déconnexion
        await binance_collector._disconnect()
        mock_binance_client.close_connection.assert_called_once()

@pytest.mark.asyncio
async def test_process_trade_message(binance_collector):
    """Test du traitement d'un message de trade."""
    # Message de trade simulé
    trade_msg = {
        "e": "trade",
        "E": 1598464986269,
        "s": "BTCUSDT",
        "t": 194559321,
        "p": "11467.86000000",
        "q": "0.00194000",
        "b": 678376805,
        "a": 678376819,
        "T": 1598464986267,
        "m": True,
        "M": True
    }
    
    # Mock du stockage
    mock_storage = MagicMock()
    mock_storage.store_trade = AsyncMock()
    binance_collector._storage = mock_storage
    
    # Traitement du message
    await binance_collector._process_message(trade_msg)
    
    # Vérification que les données ont été mises à jour
    assert binance_collector._data["BTCUSDT"]["price"] == float(trade_msg["p"])
    assert binance_collector._data["BTCUSDT"]["volume"] == float(trade_msg["q"])
    
    # Vérification que le trade a été stocké
    mock_storage.store_trade.assert_called_once()
    call_args = mock_storage.store_trade.call_args[0]
    assert call_args[0] == "BTCUSDT"  # Symbole
    assert call_args[1]["price"] == float(trade_msg["p"])  # Prix
    assert call_args[1]["amount"] == float(trade_msg["q"])  # Volume

@pytest.mark.asyncio
async def test_run_method(binance_collector, mock_binance_client):
    """Test de la méthode principale d'exécution."""
    # Simulation de messages pour le stream WebSocket
    mock_stream = AsyncMock()
    mock_stream.__aiter__.return_value = [
        {"e": "trade", "s": "BTCUSDT", "p": "11467.86", "q": "0.001"},
        {"e": "trade", "s": "ETHUSDT", "p": "380.25", "q": "0.05"}
    ]
    mock_binance_client.ws_stream = mock_stream
    
    # Patch de la connexion client
    with patch('sadie.core.collectors.binance_collector.Client', return_value=mock_binance_client):
        # Patch de la méthode _process_message
        process_mock = AsyncMock()
        with patch.object(binance_collector, '_process_message', process_mock):
            # Exécution d'un cycle de la méthode _run
            # On limite à un seul cycle pour le test
            binance_collector._running = True
            binance_collector._client = mock_binance_client
            await binance_collector._run()
            
            # Vérification que _process_message a été appelé pour chaque message
            assert process_mock.call_count == 2
            
            # Vérification des paramètres d'appel
            call_args_list = process_mock.call_args_list
            assert call_args_list[0][0][0]["s"] == "BTCUSDT"
            assert call_args_list[1][0][0]["s"] == "ETHUSDT"

@pytest.mark.asyncio
async def test_start_stop_integration(binance_collector, mock_binance_client):
    """Test d'intégration du démarrage et de l'arrêt du collecteur."""
    with patch('sadie.core.collectors.binance_collector.Client', return_value=mock_binance_client):
        # Démarrage
        await binance_collector.start()
        assert binance_collector._running is True
        assert binance_collector._task is not None
        
        # Attente d'un court instant pour permettre l'exécution
        await asyncio.sleep(0.2)
        
        # Arrêt
        await binance_collector.stop()
        assert binance_collector._running is False
        assert binance_collector._task is None
        
        # Vérification que la déconnexion a été appelée
        mock_binance_client.close_connection.assert_called()

@pytest.mark.asyncio
async def test_error_handling(binance_collector, mock_binance_client):
    """Test de la gestion des erreurs pendant la collecte."""
    # Configuration du mock client pour lever une exception
    mock_binance_client.ws_connect.side_effect = Exception("Connection error")
    
    with patch('sadie.core.collectors.binance_collector.Client', return_value=mock_binance_client):
        # Tentative de démarrage qui devrait gérer l'erreur
        await binance_collector.start()
        
        # Vérification que le collecteur essaie de se reconnecter
        await asyncio.sleep(0.3)
        
        # Le collecteur devrait toujours être en cours d'exécution malgré l'erreur
        assert binance_collector._running is True
        
        # Nettoyage
        await binance_collector.stop() 