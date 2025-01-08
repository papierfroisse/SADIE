"""
Tests d'intégration pour les collecteurs de données.
"""

import os
import pytest
import pandas as pd
from datetime import datetime, timedelta

from sadie.data.collectors.orderbook import OrderBookCollector
from sadie.data.collectors.binance import BinanceDataCollector
from sadie.data.collectors.factory import DataCollectorFactory

class TestCollectorIntegration:
    """Tests d'intégration pour les collecteurs de données."""
    
    @pytest.fixture
    def api_key(self):
        """Récupère la clé API depuis les variables d'environnement."""
        return os.getenv("BINANCE_API_KEY", "dummy_key")
    
    @pytest.fixture
    def api_secret(self):
        """Récupère le secret API depuis les variables d'environnement."""
        return os.getenv("BINANCE_API_SECRET", "dummy_secret")
    
    @pytest.fixture
    def orderbook_collector(self, api_key, api_secret):
        """Crée une instance du collecteur OrderBook."""
        return OrderBookCollector(api_key, api_secret)
    
    @pytest.fixture
    def binance_collector(self, api_key, api_secret):
        """Crée une instance du collecteur Binance."""
        return BinanceDataCollector(api_key, api_secret)
    
    def test_orderbook_data_consistency(self, orderbook_collector):
        """Vérifie la cohérence des données du carnet d'ordres."""
        # Récupérer le carnet d'ordres L2
        book_l2 = orderbook_collector.get_order_book("BTC/USDT", level="L2")
        
        # Vérifications de base
        assert isinstance(book_l2, dict)
        assert "timestamp" in book_l2
        assert "bids" in book_l2
        assert "asks" in book_l2
        assert book_l2["level"] == "L2"
        
        # Vérifier l'ordre des prix
        bids = pd.DataFrame(book_l2["bids"], columns=["price", "quantity"])
        asks = pd.DataFrame(book_l2["asks"], columns=["price", "quantity"])
        
        assert bids["price"].is_monotonic_decreasing  # Prix des achats décroissants
        assert asks["price"].is_monotonic_increasing  # Prix des ventes croissants
        assert float(bids["price"].iloc[0]) < float(asks["price"].iloc[0])  # Spread valide
    
    def test_historical_data_integration(self, binance_collector):
        """Vérifie l'intégration avec les données historiques."""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=1)
        
        data = binance_collector.get_historical_data(
            symbol="BTC/USDT",
            interval="1h",
            start_time=start_time,
            end_time=end_time
        )
        
        # Conversion en DataFrame pour analyse
        df = pd.DataFrame(data)
        
        # Vérifications
        assert not df.empty
        assert "timestamp" in df.columns
        assert "open" in df.columns
        assert "high" in df.columns
        assert "low" in df.columns
        assert "close" in df.columns
        assert "volume" in df.columns
        
        # Vérifier la cohérence des données OHLCV
        assert (df["high"] >= df["low"]).all()
        assert (df["high"] >= df["open"]).all()
        assert (df["high"] >= df["close"]).all()
        assert (df["low"] <= df["open"]).all()
        assert (df["low"] <= df["close"]).all()
        assert (df["volume"] >= 0).all()
    
    def test_collector_factory_integration(self, api_key, api_secret):
        """Vérifie l'intégration avec la factory de collecteurs."""
        # Créer différents types de collecteurs
        collectors = {
            "binance": DataCollectorFactory.create("binance", api_key, api_secret),
            "orderbook": DataCollectorFactory.create("orderbook", api_key, api_secret)
        }
        
        # Vérifier que chaque collecteur peut récupérer des données
        for name, collector in collectors.items():
            if hasattr(collector, "get_current_price"):
                price = collector.get_current_price("BTC/USDT")
                assert isinstance(price, float)
                assert price > 0
    
    def test_realtime_updates_integration(self, orderbook_collector):
        """Vérifie l'intégration des mises à jour en temps réel."""
        updates = []
        
        def callback(update):
            updates.append(update)
        
        # Démarrer le flux de mises à jour
        orderbook_collector.start_order_book_stream("BTC/USDT", callback)
        
        # Attendre quelques mises à jour
        import time
        time.sleep(5)
        
        # Arrêter le flux
        orderbook_collector.stop_order_book_stream("BTC/USDT")
        
        # Vérifier les mises à jour
        assert len(updates) > 0
        for update in updates:
            assert "lastUpdateId" in update
            assert "bids" in update or "asks" in update 