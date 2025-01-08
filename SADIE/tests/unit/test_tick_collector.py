"""
Tests unitaires pour le collecteur de données tick par tick.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from decimal import Decimal

from sadie.data.collectors.tick import TickCollector

class TestTickCollector:
    """Tests pour le collecteur de données tick par tick."""
    
    @pytest.fixture
    def collector(self):
        """Fixture pour créer un collecteur tick avec un client mocké."""
        symbols = ["BTC/USDT", "ETH/USDT"]
        with patch("binance.client.Client"):
            collector = TickCollector(
                api_key="dummy_key",
                api_secret="dummy_secret",
                symbols=symbols
            )
            return collector
    
    def test_initialization(self, collector):
        """Vérifie l'initialisation du collecteur."""
        assert collector.api_key == "dummy_key"
        assert collector.api_secret == "dummy_secret"
        assert len(collector.symbols) == 2
        assert collector.batch_size == 1000
        assert not collector._running
        
    @pytest.mark.asyncio
    async def test_start_stop(self, collector):
        """Vérifie le démarrage et l'arrêt du collecteur."""
        # Démarrage
        await collector.start()
        assert collector._running
        assert len(collector._streams) == 2
        assert len(collector._batch_processors) == 2
        
        # Arrêt
        await collector.stop()
        assert not collector._running
        assert not collector._streams
        assert not collector._batch_processors
        
    def test_parse_tick_message(self, collector):
        """Vérifie le parsing des messages tick."""
        message = {
            "e": "trade",
            "E": 1672515782136,
            "s": "BTCUSDT",
            "t": 123456,
            "p": "16500.50",
            "q": "1.234",
            "T": 1672515782136,
            "m": True
        }
        
        tick = collector._parse_tick_message(str(message))
        
        assert isinstance(tick["timestamp"], float)
        assert isinstance(tick["price"], Decimal)
        assert isinstance(tick["quantity"], Decimal)
        assert isinstance(tick["buyer_maker"], bool)
        assert tick["trade_id"] == "123456"
        assert tick["price"] == Decimal("16500.50")
        assert tick["quantity"] == Decimal("1.234")
        assert tick["buyer_maker"] is True
        
    def test_compute_batch_stats(self, collector):
        """Vérifie le calcul des statistiques sur les lots."""
        batch = [
            {
                "timestamp": 1672515782.136,
                "price": Decimal("16500.50"),
                "quantity": Decimal("1.234"),
                "buyer_maker": True,
                "trade_id": "1"
            },
            {
                "timestamp": 1672515783.136,
                "price": Decimal("16501.00"),
                "quantity": Decimal("0.5"),
                "buyer_maker": False,
                "trade_id": "2"
            }
        ]
        
        stats = collector._compute_batch_stats(batch)
        
        assert stats["timestamp"] == 1672515783.136
        assert stats["price_min"] == Decimal("16500.50")
        assert stats["price_max"] == Decimal("16501.00")
        assert stats["price_mean"] == Decimal("16500.75")
        assert stats["volume"] == Decimal("1.734")
        assert stats["trades"] == 2
        assert stats["buyer_maker_ratio"] == 0.5
        
    @pytest.mark.asyncio
    async def test_callbacks(self, collector):
        """Vérifie la gestion des callbacks."""
        received_ticks = []
        
        def callback(tick):
            received_ticks.append(tick)
        
        # Enregistrement du callback
        collector.register_callback("BTC/USDT", callback)
        
        # Simulation d'un tick
        tick = {
            "timestamp": 1672515782.136,
            "price": Decimal("16500.50"),
            "quantity": Decimal("1.234"),
            "buyer_maker": True,
            "trade_id": "1"
        }
        await collector._handle_tick("BTC/USDT", tick)
        
        assert len(received_ticks) == 1
        assert received_ticks[0] == tick
        
        # Désenregistrement du callback
        collector.unregister_callback("BTC/USDT", callback)
        await collector._handle_tick("BTC/USDT", tick)
        
        assert len(received_ticks) == 1  # Pas de nouveau tick reçu
        
    @pytest.mark.asyncio
    async def test_get_latest_ticks(self, collector):
        """Vérifie la récupération des derniers ticks."""
        # Ajout de quelques ticks
        ticks = [
            {
                "timestamp": 1672515782.136,
                "price": Decimal("16500.50"),
                "quantity": Decimal("1.234"),
                "buyer_maker": True,
                "trade_id": str(i)
            }
            for i in range(5)
        ]
        
        for tick in ticks:
            await collector._handle_tick("BTC/USDT", tick)
        
        # Récupération des 3 derniers ticks
        latest = await collector.get_latest_ticks("BTC/USDT", limit=3)
        
        assert len(latest) == 3
        assert latest[-1]["trade_id"] == "4"
        assert latest[0]["trade_id"] == "2" 