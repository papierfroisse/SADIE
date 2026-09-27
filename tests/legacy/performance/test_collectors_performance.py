"""
Tests de performance pour les collecteurs de données.
"""

import pytest
import asyncio
import time
from datetime import datetime

from sadie.data.collectors import WebSocketCollector, RESTCollector
from sadie.utils.metrics import metrics

@pytest.mark.performance
class TestCollectorsPerformance:
    """Tests de performance pour les collecteurs."""
    
    @pytest.fixture
    async def websocket_collector(self):
        """Fixture pour le collecteur WebSocket."""
        collector = WebSocketCollector(
            symbols=["BTCUSDT", "ETHUSDT"],
            ws_url="wss://stream.binance.com:9443/ws"
        )
        yield collector
        await collector.stop()
    
    @pytest.fixture
    async def rest_collector(self):
        """Fixture pour le collecteur REST."""
        collector = RESTCollector(
            symbols=["BTCUSDT", "ETHUSDT"],
            base_url="https://api.binance.com/api/v3"
        )
        yield collector
        await collector.stop()
    
    @pytest.mark.asyncio
    async def test_websocket_connection_time(self, websocket_collector):
        """Teste le temps de connexion WebSocket."""
        metrics.start_timer("ws_connection")
        
        await websocket_collector._connect()
        
        connection_time = metrics.stop_timer("ws_connection")
        assert connection_time < 2.0, "La connexion WebSocket prend trop de temps"
    
    @pytest.mark.asyncio
    async def test_websocket_message_processing(self, websocket_collector):
        """Teste les performances de traitement des messages WebSocket."""
        # Démarrage du collecteur
        collection_task = asyncio.create_task(websocket_collector.start())
        
        try:
            # Collecte des métriques pendant 30 secondes
            start_time = time.time()
            message_count = 0
            
            while time.time() - start_time < 30:
                await asyncio.sleep(1)
                metrics_data = metrics.get_metrics(
                    start_time=datetime.fromtimestamp(start_time)
                )
                message_count = len(metrics_data)
            
            # Vérification des performances
            messages_per_second = message_count / 30
            assert messages_per_second > 1.0, "Traitement des messages trop lent"
        
        finally:
            collection_task.cancel()
            try:
                await collection_task
            except asyncio.CancelledError:
                pass
    
    @pytest.mark.asyncio
    async def test_rest_request_time(self, rest_collector):
        """Teste le temps de requête REST."""
        metrics.start_timer("rest_request")
        
        async with rest_collector.session.get(
            f"{rest_collector.base_url}/ticker/24hr",
            params={"symbol": "BTCUSDT"}
        ) as response:
            await response.json()
        
        request_time = metrics.stop_timer("rest_request")
        assert request_time < 1.0, "Les requêtes REST sont trop lentes"
    
    @pytest.mark.asyncio
    async def test_collector_memory_usage(self, websocket_collector):
        """Teste l'utilisation mémoire du collecteur."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Démarrage du collecteur
        collection_task = asyncio.create_task(websocket_collector.start())
        
        try:
            # Collecte pendant 1 minute
            await asyncio.sleep(60)
            
            # Vérification de l'utilisation mémoire
            final_memory = process.memory_info().rss
            memory_increase = (final_memory - initial_memory) / 1024 / 1024  # MB
            
            assert memory_increase < 100, "Utilisation mémoire trop élevée"
        
        finally:
            collection_task.cancel()
            try:
                await collection_task
            except asyncio.CancelledError:
                pass
    
    @pytest.mark.asyncio
    async def test_collector_cpu_usage(self, websocket_collector):
        """Teste l'utilisation CPU du collecteur."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Démarrage du collecteur
        collection_task = asyncio.create_task(websocket_collector.start())
        
        try:
            # Mesure pendant 30 secondes
            cpu_percentages = []
            start_time = time.time()
            
            while time.time() - start_time < 30:
                cpu_percentages.append(process.cpu_percent())
                await asyncio.sleep(1)
            
            average_cpu = sum(cpu_percentages) / len(cpu_percentages)
            assert average_cpu < 50, "Utilisation CPU trop élevée"
        
        finally:
            collection_task.cancel()
            try:
                await collection_task
            except asyncio.CancelledError:
                pass 