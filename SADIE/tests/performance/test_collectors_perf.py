"""
Tests de performance pour les collecteurs de données.
"""

import time
import pytest
import psutil
import threading
from unittest.mock import patch

from sadie.data.collectors.orderbook import OrderBookCollector
from sadie.data.collectors.binance import BinanceDataCollector

def measure_execution_time(func):
    """Décorateur pour mesurer le temps d'exécution."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        return result, execution_time
    return wrapper

def measure_memory_usage(func):
    """Décorateur pour mesurer l'utilisation de la mémoire."""
    def wrapper(*args, **kwargs):
        process = psutil.Process()
        memory_before = process.memory_info().rss
        result = func(*args, **kwargs)
        memory_after = process.memory_info().rss
        memory_used = memory_after - memory_before
        return result, memory_used
    return wrapper

class TestCollectorPerformance:
    """Tests de performance pour les collecteurs."""
    
    @pytest.fixture
    def orderbook_collector(self):
        """Fixture pour le collecteur OrderBook."""
        with patch("binance.client.Client"):
            return OrderBookCollector("dummy_key", "dummy_secret")
    
    @pytest.fixture
    def binance_collector(self):
        """Fixture pour le collecteur Binance."""
        with patch("binance.client.Client"):
            return BinanceDataCollector("dummy_key", "dummy_secret")
    
    def test_orderbook_response_time(self, orderbook_collector):
        """Test du temps de réponse pour la récupération du carnet d'ordres."""
        @measure_execution_time
        def get_orderbook():
            return orderbook_collector.get_order_book("BTC/USDT", level="L2")
        
        _, execution_time = get_orderbook()
        assert execution_time < 1.0  # La réponse doit être < 1 seconde
    
    def test_orderbook_memory_usage(self, orderbook_collector):
        """Test de l'utilisation mémoire pour la récupération du carnet d'ordres."""
        @measure_memory_usage
        def get_orderbook():
            return orderbook_collector.get_order_book("BTC/USDT", level="L2")
        
        _, memory_used = get_orderbook()
        assert memory_used < 10 * 1024 * 1024  # Utilisation < 10MB
    
    def test_historical_data_performance(self, binance_collector):
        """Test des performances pour la récupération des données historiques."""
        @measure_execution_time
        def get_historical():
            return binance_collector.get_historical_data(
                symbol="BTC/USDT",
                interval="1h",
                limit=1000
            )
        
        _, execution_time = get_historical()
        assert execution_time < 5.0  # La réponse doit être < 5 secondes
    
    def test_concurrent_requests(self, orderbook_collector):
        """Test des performances avec des requêtes concurrentes."""
        results = []
        
        def worker():
            start_time = time.time()
            orderbook_collector.get_order_book("BTC/USDT", level="L2")
            execution_time = time.time() - start_time
            results.append(execution_time)
        
        threads = []
        for _ in range(5):  # Test avec 5 requêtes simultanées
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Vérifier que toutes les requêtes sont traitées dans un délai raisonnable
        assert max(results) < 2.0  # Chaque requête doit être < 2 secondes
        assert sum(results) / len(results) < 1.0  # Moyenne < 1 seconde 