"""
Tests unitaires pour les collecteurs de données.
"""

import datetime
import pytest
from unittest.mock import Mock, patch

from sadie.data.collectors import DataCollector
from sadie.data.collectors.binance import BinanceDataCollector
from sadie.data.collectors.alpha_vantage import AlphaVantageDataCollector
from sadie.data.collectors.factory import DataCollectorFactory

class TestDataCollector:
    """Tests pour la classe de base DataCollector."""
    
    def test_abstract_methods(self):
        """Vérifie que les méthodes abstraites sont bien définies."""
        with pytest.raises(TypeError):
            DataCollector("dummy_key")

class TestBinanceDataCollector:
    """Tests pour le collecteur de données Binance."""
    
    @pytest.fixture
    def collector(self):
        """Fixture pour créer un collecteur Binance avec un client mocké."""
        with patch("binance.client.Client") as mock_client:
            collector = BinanceDataCollector("dummy_key", "dummy_secret")
            collector.client = mock_client
            return collector
    
    def test_initialization(self, collector):
        """Vérifie l'initialisation du collecteur."""
        assert collector.api_key == "dummy_key"
        assert collector.api_secret == "dummy_secret"
    
    def test_get_historical_data(self, collector):
        """Vérifie la récupération des données historiques."""
        # Configuration du mock
        mock_klines = [
            [
                1499040000000,      # Open time
                "0.01634790",       # Open
                "0.80000000",       # High
                "0.01575800",       # Low
                "0.01577100",       # Close
                "148976.11427815",  # Volume
                1499644799999,      # Close time
                "2434.19055334",    # Quote asset volume
                308,                # Number of trades
                "1756.87402397",    # Taker buy base asset volume
                "28.46694368"       # Taker buy quote asset volume
            ]
        ]
        collector.client.get_historical_klines.return_value = mock_klines
        
        # Test
        start_time = datetime.datetime(2023, 1, 1)
        data = collector.get_historical_data(
            symbol="BTC/USDT",
            interval="1h",
            start_time=start_time
        )
        
        # Vérifications
        assert len(data) == 1
        assert data[0]["timestamp"] == 1499040000000 / 1000
        assert data[0]["open"] == 0.01634790
        assert data[0]["volume"] == 148976.11427815
    
    def test_get_current_price(self, collector):
        """Vérifie la récupération du prix actuel."""
        # Configuration du mock
        collector.client.get_symbol_ticker.return_value = {"price": "50000.00"}
        
        # Test
        price = collector.get_current_price("BTC/USDT")
        
        # Vérifications
        assert price == 50000.00
        collector.client.get_symbol_ticker.assert_called_once_with(symbol="BTCUSDT")
    
    def test_get_order_book(self, collector):
        """Vérifie la récupération du carnet d'ordres."""
        # Configuration du mock
        mock_depth = {
            "lastUpdateId": 1027024,
            "bids": [["4.00000000", "431.00000000"]],
            "asks": [["4.00000200", "12.00000000"]]
        }
        collector.client.get_order_book.return_value = mock_depth
        
        # Test
        book = collector.get_order_book("BTC/USDT", limit=5)
        
        # Vérifications
        assert book["timestamp"] == 1027024
        assert len(book["bids"]) == 1
        assert len(book["asks"]) == 1
        assert book["bids"][0] == [4.0, 431.0]
        assert book["asks"][0] == [4.000002, 12.0]

class TestAlphaVantageDataCollector:
    """Tests pour le collecteur de données Alpha Vantage."""
    
    @pytest.fixture
    def collector(self):
        """Fixture pour créer un collecteur Alpha Vantage avec des clients mockés."""
        with patch("alpha_vantage.cryptocurrencies.CryptoCurrencies") as mock_crypto, \
             patch("alpha_vantage.timeseries.TimeSeries") as mock_ts:
            collector = AlphaVantageDataCollector("dummy_key")
            collector.crypto_client = mock_crypto
            collector.ts_client = mock_ts
            return collector
    
    def test_initialization(self, collector):
        """Vérifie l'initialisation du collecteur."""
        assert collector.api_key == "dummy_key"
        assert collector.api_secret is None
    
    def test_get_historical_data(self, collector):
        """Vérifie la récupération des données historiques."""
        # Configuration du mock
        mock_data = {
            "2023-01-01 00:00:00": {
                "1. open": "50000.00",
                "2. high": "51000.00",
                "3. low": "49000.00",
                "4. close": "50500.00",
                "5. volume": "1000.00"
            }
        }
        collector.crypto_client.get_crypto_intraday.return_value = (mock_data, None)
        
        # Test
        start_time = datetime.datetime(2023, 1, 1)
        data = collector.get_historical_data(
            symbol="BTC/USD",
            interval="1h",
            start_time=start_time
        )
        
        # Vérifications
        assert len(data) == 1
        assert data[0]["open"] == 50000.00
        assert data[0]["high"] == 51000.00
        assert data[0]["volume"] == 1000.00
    
    def test_get_current_price(self, collector):
        """Vérifie la récupération du prix actuel."""
        # Configuration du mock
        mock_data = {"5. Exchange Rate": "50000.00"}
        collector.crypto_client.get_currency_exchange_rate.return_value = (mock_data, None)
        
        # Test
        price = collector.get_current_price("BTC/USD")
        
        # Vérifications
        assert price == 50000.00
    
    def test_get_order_book_not_supported(self, collector):
        """Vérifie que le carnet d'ordres n'est pas supporté."""
        with pytest.raises(NotImplementedError):
            collector.get_order_book("BTC/USD")

class TestDataCollectorFactory:
    """Tests pour la factory de collecteurs de données."""
    
    def test_create_binance(self):
        """Vérifie la création d'un collecteur Binance."""
        collector = DataCollectorFactory.create(
            source="binance",
            api_key="dummy_key",
            api_secret="dummy_secret"
        )
        assert isinstance(collector, BinanceDataCollector)
    
    def test_create_alpha_vantage(self):
        """Vérifie la création d'un collecteur Alpha Vantage."""
        collector = DataCollectorFactory.create(
            source="alpha_vantage",
            api_key="dummy_key"
        )
        assert isinstance(collector, AlphaVantageDataCollector)
    
    def test_create_invalid_source(self):
        """Vérifie que la création échoue avec une source invalide."""
        with pytest.raises(ValueError):
            DataCollectorFactory.create(
                source="invalid_source",
                api_key="dummy_key"
            )
    
    def test_register_collector(self):
        """Vérifie l'enregistrement d'un nouveau collecteur."""
        # Création d'une classe de test
        class TestCollector(DataCollector):
            def _initialize_client(self): pass
            def get_historical_data(self, *args, **kwargs): pass
            def get_current_price(self, symbol): pass
            def get_order_book(self, symbol, limit=None): pass
        
        # Enregistrement
        DataCollectorFactory.register_collector("test", TestCollector)
        
        # Vérification
        collector = DataCollectorFactory.create(
            source="test",
            api_key="dummy_key"
        )
        assert isinstance(collector, TestCollector)
    
    def test_register_invalid_collector(self):
        """Vérifie que l'enregistrement échoue avec une classe invalide."""
        class InvalidCollector:
            pass
        
        with pytest.raises(TypeError):
            DataCollectorFactory.register_collector("invalid", InvalidCollector) 