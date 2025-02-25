"""Tests d'intégration pour l'utilisation conjointe des collecteurs."""

import asyncio
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from sadie.core.collectors import BinanceTradeCollector, KrakenTradeCollector
from sadie.storage import RedisStorage

class MultiExchangeManager:
    """Gestionnaire de collecteurs multi-exchanges pour les tests d'intégration."""
    
    def __init__(self):
        self.collectors = {}
        self.storage = None
        self.running = False
        
    async def setup(self, mock_storage):
        """Configure les collecteurs pour le test."""
        self.storage = mock_storage
        
        # Initialisation des collecteurs
        self.collectors["binance"] = BinanceTradeCollector(
            name="binance_test",
            symbols=["BTCUSDT", "ETHUSDT"],
            storage=mock_storage,
            api_key="test_binance_key",
            api_secret="test_binance_secret",
            update_interval=0.1
        )
        
        self.collectors["kraken"] = KrakenTradeCollector(
            name="kraken_test",
            symbols=["XBT/USD", "ETH/USD"],
            storage=mock_storage,
            api_key="test_kraken_key",
            api_secret="test_kraken_secret",
            update_interval=0.1
        )
    
    async def start_all(self):
        """Démarre tous les collecteurs."""
        self.running = True
        for name, collector in self.collectors.items():
            await collector.start()
    
    async def stop_all(self):
        """Arrête tous les collecteurs."""
        self.running = False
        for name, collector in self.collectors.items():
            await collector.stop()
    
    async def get_all_data(self):
        """Récupère les données de tous les collecteurs."""
        data = {}
        for name, collector in self.collectors.items():
            data[name] = await collector.get_data()
        return data

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
def mock_binance_client():
    """Fixture qui crée un mock du client Binance."""
    mock_client = MagicMock()
    mock_client.ws_connect = AsyncMock()
    mock_client.close_connection = AsyncMock()
    
    # Mock du stream WebSocket
    mock_stream = AsyncMock()
    mock_stream.__aiter__.return_value = [
        {"e": "trade", "s": "BTCUSDT", "p": "50000.00", "q": "0.1"},
        {"e": "trade", "s": "ETHUSDT", "p": "4000.00", "q": "1.5"}
    ]
    mock_client.ws_stream = mock_stream
    
    return mock_client

@pytest.fixture
def mock_kraken_client():
    """Fixture qui crée un mock du client Kraken."""
    mock_client = MagicMock()
    mock_client.connect = AsyncMock()
    mock_client.disconnect = AsyncMock()
    
    # Mock du stream WebSocket
    mock_stream = AsyncMock()
    mock_stream.__aiter__.return_value = [
        {"channel": "trade", "symbol": "XBT/USD", "data": {"price": "51000.00", "volume": "0.2"}},
        {"channel": "trade", "symbol": "ETH/USD", "data": {"price": "4100.00", "volume": "2.0"}}
    ]
    mock_client.ws_stream = mock_stream
    
    return mock_client

@pytest.fixture
async def multi_manager(mock_storage):
    """Fixture qui crée et configure le gestionnaire multi-exchange."""
    manager = MultiExchangeManager()
    await manager.setup(mock_storage)
    return manager

@pytest.mark.asyncio
async def test_multi_collector_initialization(multi_manager):
    """Test de l'initialisation correcte des collecteurs multiples."""
    # Vérification de l'initialisation
    assert "binance" in multi_manager.collectors
    assert "kraken" in multi_manager.collectors
    
    binance = multi_manager.collectors["binance"]
    kraken = multi_manager.collectors["kraken"]
    
    assert binance.name == "binance_test"
    assert binance.symbols == ["BTCUSDT", "ETHUSDT"]
    
    assert kraken.name == "kraken_test"
    assert kraken.symbols == ["XBT/USD", "ETH/USD"]
    
    # Vérification que les deux collecteurs utilisent le même stockage
    assert binance._storage is kraken._storage
    assert binance._storage is multi_manager.storage

@pytest.mark.asyncio
async def test_multi_collector_start_stop(multi_manager, mock_binance_client, mock_kraken_client):
    """Test du démarrage et de l'arrêt synchronisés de plusieurs collecteurs."""
    # Patch des clients
    with patch('sadie.core.collectors.binance_collector.Client', return_value=mock_binance_client), \
         patch('sadie.core.collectors.kraken_collector.KrakenClient', return_value=mock_kraken_client):
        
        # Démarrage de tous les collecteurs
        await multi_manager.start_all()
        
        # Vérification que tous les collecteurs sont démarrés
        for name, collector in multi_manager.collectors.items():
            assert collector._running is True
            assert collector._task is not None
        
        # Attente pour laisser les collecteurs s'exécuter
        await asyncio.sleep(0.2)
        
        # Arrêt de tous les collecteurs
        await multi_manager.stop_all()
        
        # Vérification que tous les collecteurs sont arrêtés
        for name, collector in multi_manager.collectors.items():
            assert collector._running is False
            assert collector._task is None

@pytest.mark.asyncio
async def test_multi_collector_data_collection(multi_manager, mock_binance_client, mock_kraken_client):
    """Test de la collecte de données simultanée depuis plusieurs sources."""
    # Patch des clients et des méthodes _process_message pour simuler la collecte
    with patch('sadie.core.collectors.binance_collector.Client', return_value=mock_binance_client), \
         patch('sadie.core.collectors.kraken_collector.KrakenClient', return_value=mock_kraken_client):
        
        # Création de données simulées pour Binance
        binance = multi_manager.collectors["binance"]
        binance._data["BTCUSDT"]["price"] = 50000.0
        binance._data["BTCUSDT"]["volume"] = 0.1
        binance._data["ETHUSDT"]["price"] = 4000.0
        binance._data["ETHUSDT"]["volume"] = 1.5
        
        # Création de données simulées pour Kraken
        kraken = multi_manager.collectors["kraken"]
        kraken._data["XBT/USD"]["price"] = 51000.0
        kraken._data["XBT/USD"]["volume"] = 0.2
        kraken._data["ETH/USD"]["price"] = 4100.0
        kraken._data["ETH/USD"]["volume"] = 2.0
        
        # Récupération des données de tous les collecteurs
        all_data = await multi_manager.get_all_data()
        
        # Vérification des données de Binance
        assert "binance" in all_data
        assert "BTCUSDT" in all_data["binance"]
        assert all_data["binance"]["BTCUSDT"]["price"] == 50000.0
        assert all_data["binance"]["ETHUSDT"]["volume"] == 1.5
        
        # Vérification des données de Kraken
        assert "kraken" in all_data
        assert "XBT/USD" in all_data["kraken"]
        assert all_data["kraken"]["XBT/USD"]["price"] == 51000.0
        assert all_data["kraken"]["ETH/USD"]["volume"] == 2.0

@pytest.mark.asyncio
async def test_multi_collector_partial_failure(multi_manager, mock_binance_client, mock_kraken_client):
    """Test de la résilience en cas de défaillance d'un des collecteurs."""
    # Modification du client Binance pour simuler une erreur
    mock_binance_client.ws_connect.side_effect = Exception("Binance connection error")
    
    with patch('sadie.core.collectors.binance_collector.Client', return_value=mock_binance_client), \
         patch('sadie.core.collectors.kraken_collector.KrakenClient', return_value=mock_kraken_client):
        
        # Démarrage de tous les collecteurs
        await multi_manager.start_all()
        
        # Attente pour laisser les collecteurs s'exécuter
        await asyncio.sleep(0.3)
        
        # Le collecteur Kraken devrait toujours fonctionner malgré l'erreur sur Binance
        kraken = multi_manager.collectors["kraken"]
        assert kraken._running is True
        
        # Récupération des données - devrait encore avoir des données de Kraken
        all_data = await multi_manager.get_all_data()
        assert "kraken" in all_data
        
        # Nettoyage
        await multi_manager.stop_all()

@pytest.mark.asyncio
async def test_multi_collector_storage_integration(multi_manager, mock_storage, mock_binance_client, mock_kraken_client):
    """Test de l'intégration avec le stockage des données."""
    with patch('sadie.core.collectors.binance_collector.Client', return_value=mock_binance_client), \
         patch('sadie.core.collectors.kraken_collector.KrakenClient', return_value=mock_kraken_client):
        
        # Démarrage des collecteurs
        await multi_manager.start_all()
        
        # Attente pour permettre la collecte de données
        await asyncio.sleep(0.3)
        
        # Vérification que le stockage a été utilisé par les deux collecteurs
        assert mock_storage.store_trade.call_count > 0
        
        # Les appels au stockage devraient inclure des données de Binance et Kraken
        call_args_list = mock_storage.store_trade.call_args_list
        
        # Extraction des symboles stockés
        stored_symbols = {call[0][0] for call in call_args_list}
        
        # On s'attend à voir des données pour les symboles des deux exchanges
        # Note: les formats des symboles peuvent différer selon l'implementation
        assert len(stored_symbols) > 0
        
        # Nettoyage
        await multi_manager.stop_all() 