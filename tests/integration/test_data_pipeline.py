"""
Tests d'intégration pour le pipeline de données.
"""

import pytest
import asyncio
from datetime import datetime, timedelta

from sadie.data.collectors import WebSocketCollector
from sadie.storage import MemoryStorage
from sadie.analysis import TimeSeriesAnalyzer
from sadie.data.exceptions import DataCollectionError

class TestDataPipeline:
    """Tests d'intégration pour le pipeline complet."""
    
    @pytest.fixture
    async def setup_pipeline(self):
        """Configure le pipeline de test."""
        # Initialisation des composants
        self.collector = WebSocketCollector(
            symbols=["BTCUSDT"],
            ws_url="wss://stream.binance.com:9443/ws"
        )
        self.storage = MemoryStorage()
        self.analyzer = TimeSeriesAnalyzer(window_size=20)
        
        # Démarrage des composants
        await self.storage.connect()
        
        yield
        
        # Nettoyage
        await self.collector.stop()
        await self.storage.disconnect()
    
    @pytest.mark.asyncio
    async def test_data_collection_to_storage(self, setup_pipeline):
        """Teste la collecte et le stockage des données."""
        # Simulation de données
        test_data = {
            "symbol": "BTCUSDT",
            "price": 50000.0,
            "volume": 1.5,
            "timestamp": datetime.utcnow()
        }
        
        # Stockage des données
        await self.storage.store(test_data)
        
        # Vérification du stockage
        stored_data = await self.storage.retrieve(
            start_time=datetime.utcnow() - timedelta(minutes=1)
        )
        assert len(stored_data) == 1
        assert stored_data[0]["symbol"] == test_data["symbol"]
        assert stored_data[0]["price"] == test_data["price"]
    
    @pytest.mark.asyncio
    async def test_storage_to_analysis(self, setup_pipeline):
        """Teste l'analyse des données stockées."""
        # Préparation des données
        now = datetime.utcnow()
        test_data = []
        
        for i in range(30):
            data = {
                "symbol": "BTCUSDT",
                "price": 50000.0 + i * 100,
                "volume": 1.5 + i * 0.1
            }
            await self.storage.store(data, now + timedelta(minutes=i))
            test_data.append(data)
        
        # Récupération et analyse des données
        stored_data = await self.storage.retrieve()
        analysis_results = await self.analyzer.process(stored_data)
        
        # Vérification des résultats
        assert "mean" in analysis_results
        assert "trend" in analysis_results
        assert analysis_results["trend"]["price"] == "up"
    
    @pytest.mark.asyncio
    async def test_complete_pipeline(self, setup_pipeline):
        """Teste le pipeline complet de bout en bout."""
        # Démarrage de la collecte
        collection_task = asyncio.create_task(self.collector.start())
        
        try:
            # Attente de quelques données
            await asyncio.sleep(5)
            
            # Vérification du stockage
            stored_data = await self.storage.retrieve()
            assert len(stored_data) > 0
            
            # Analyse des données
            analysis_results = await self.analyzer.process(stored_data)
            assert "mean" in analysis_results
            assert "std" in analysis_results
        
        finally:
            # Arrêt propre
            collection_task.cancel()
            try:
                await collection_task
            except asyncio.CancelledError:
                pass
    
    @pytest.mark.asyncio
    async def test_error_handling(self, setup_pipeline):
        """Teste la gestion des erreurs dans le pipeline."""
        # Test d'erreur de connexion
        with pytest.raises(DataCollectionError):
            self.collector.ws_url = "wss://invalid.url"
            await self.collector.start()
        
        # Test d'erreur de stockage
        with pytest.raises(Exception):
            await self.storage.store(None)
        
        # Test d'erreur d'analyse
        with pytest.raises(Exception):
            await self.analyzer.process([]) 