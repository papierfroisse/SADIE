"""Unit tests for the enhanced order book collector."""
import asyncio
import json
from decimal import Decimal
from typing import Dict, List, Tuple
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from sadie.data.collectors.orderbook import OrderBook, OrderBookMetrics, OrderBookCollector
from sadie.data.collectors.exceptions import CollectorError

@pytest.fixture
def sample_order_book_data():
    """Sample order book data for testing."""
    return {
        "lastUpdateId": 1234567890,
        "bids": [
            ["100.00", "1.000"],
            ["99.50", "2.000"],
            ["99.00", "3.000"]
        ],
        "asks": [
            ["101.00", "1.500"],
            ["101.50", "2.500"],
            ["102.00", "3.500"]
        ]
    }

@pytest.fixture
def sample_ws_message():
    """Sample WebSocket message for testing."""
    return json.dumps({
        "e": "depthUpdate",
        "E": 123456789,
        "s": "BTCUSDT",
        "U": 157,
        "u": 160,
        "b": [["100.50", "1.200"]],
        "a": [["101.20", "0.800"]]
    })

class TestOrderBookMetrics:
    """Test cases for OrderBookMetrics."""
    
    def test_compute_spread(self):
        """Test spread computation."""
        bids = [(Decimal("100.00"), Decimal("1.000"))]
        asks = [(Decimal("101.00"), Decimal("1.500"))]
        spread = OrderBookMetrics.compute_spread(bids, asks)
        assert spread == Decimal("1.00")
        
    def test_compute_spread_empty_book(self):
        """Test spread computation with empty order book."""
        spread = OrderBookMetrics.compute_spread([], [])
        assert spread == Decimal("0")
        
    def test_compute_depth(self):
        """Test depth computation."""
        bids = [
            (Decimal("100.00"), Decimal("1.000")),
            (Decimal("99.50"), Decimal("2.000"))
        ]
        asks = [
            (Decimal("101.00"), Decimal("1.500")),
            (Decimal("101.50"), Decimal("2.500"))
        ]
        bid_depth, ask_depth = OrderBookMetrics.compute_depth(
            bids, asks, Decimal("1.00")
        )
        assert bid_depth == Decimal("3.000")  # 1.000 + 2.000
        assert ask_depth == Decimal("4.000")  # 1.500 + 2.500
        
    def test_compute_imbalance(self):
        """Test imbalance computation."""
        bids = [
            (Decimal("100.00"), Decimal("4.000")),
            (Decimal("99.50"), Decimal("2.000"))
        ]
        asks = [
            (Decimal("101.00"), Decimal("3.000")),
            (Decimal("101.50"), Decimal("1.000"))
        ]
        imbalance = OrderBookMetrics.compute_imbalance(bids, asks, levels=2)
        # (6 - 4) / 10 = 0.2
        assert imbalance == Decimal("0.2")

class TestOrderBook:
    """Test cases for OrderBook."""
    
    def test_initialization(self):
        """Test order book initialization."""
        book = OrderBook(depth=100)
        assert len(book.bids) == 0
        assert len(book.asks) == 0
        assert book.depth == 100
        
    def test_update(self):
        """Test order book update."""
        book = OrderBook(depth=100)
        bids = [("100.00", "1.000"), ("99.50", "2.000")]
        asks = [("101.00", "1.500"), ("101.50", "2.500")]
        book.update(bids, asks, 1)
        
        assert len(book.bids) == 2
        assert len(book.asks) == 2
        assert book.bids[Decimal("100.00")] == Decimal("1.000")
        assert book.asks[Decimal("101.00")] == Decimal("1.500")
        
    def test_update_remove_price_level(self):
        """Test removing price level with zero quantity."""
        book = OrderBook(depth=100)
        # Add initial levels
        book.update([("100.00", "1.000")], [], 1)
        assert len(book.bids) == 1
        
        # Remove level with zero quantity
        book.update([("100.00", "0.000")], [], 2)
        assert len(book.bids) == 0
        
    def test_depth_maintenance(self):
        """Test order book depth maintenance."""
        book = OrderBook(depth=2)
        bids = [
            ("100.00", "1.000"),
            ("99.50", "2.000"),
            ("99.00", "3.000")
        ]
        book.update(bids, [], 1)
        assert len(book.bids) == 2  # Only keeps top 2 levels
        
    def test_get_snapshot(self):
        """Test getting order book snapshot."""
        book = OrderBook(depth=100)
        bids = [("100.00", "1.000"), ("99.50", "2.000")]
        asks = [("101.00", "1.500"), ("101.50", "2.500")]
        book.update(bids, asks, 1)
        
        snapshot_bids, snapshot_asks = book.get_snapshot(depth=1)
        assert len(snapshot_bids) == 1
        assert len(snapshot_asks) == 1
        assert snapshot_bids[0] == (Decimal("100.00"), Decimal("1.000"))
        assert snapshot_asks[0] == (Decimal("101.00"), Decimal("1.500"))
        
    def test_get_metrics(self):
        """Test getting order book metrics."""
        book = OrderBook(depth=100)
        bids = [("100.00", "1.000"), ("99.50", "2.000")]
        asks = [("101.00", "1.500"), ("101.50", "2.500")]
        book.update(bids, asks, 1)
        
        metrics = book.get_metrics(price_range=Decimal("1.00"), levels=2)
        assert "spread" in metrics
        assert "bid_depth" in metrics
        assert "ask_depth" in metrics
        assert "imbalance" in metrics

@pytest.mark.asyncio
class TestOrderBookCollector:
    """Test cases for OrderBookCollector."""
    
    @pytest.fixture
    def collector(self):
        """Create a collector instance for testing."""
        return OrderBookCollector(
            symbols=["BTCUSDT"],
            depth=100,
            update_interval=0.1,
            rate_limit=10
        )
        
    @pytest.fixture
    async def initialized_collector(self, collector, sample_order_book_data):
        """Create and initialize a collector for testing."""
        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = sample_order_book_data
            mock_get.return_value.__aenter__.return_value = mock_response
            
            await collector.start()
            yield collector
            await collector.stop()
            
    async def test_initialization(self, collector):
        """Test collector initialization."""
        assert collector.symbols == ["BTCUSDT"]
        assert collector.depth == 100
        assert collector.update_interval == 0.1
        
    async def test_start_stop(self, initialized_collector):
        """Test starting and stopping the collector."""
        assert len(initialized_collector._order_books) == 1
        assert "BTCUSDT" in initialized_collector._order_books
        assert len(initialized_collector._ws_connections) == 1
        
        await initialized_collector.stop()
        assert len(initialized_collector._ws_connections) == 0
        
    async def test_get_order_book(self, initialized_collector):
        """Test getting order book snapshot."""
        bids, asks = await initialized_collector.get_order_book("BTCUSDT")
        assert len(bids) > 0
        assert len(asks) > 0
        assert all(isinstance(price, Decimal) for price, _ in bids)
        assert all(isinstance(qty, Decimal) for _, qty in bids)
        
    async def test_get_metrics(self, initialized_collector):
        """Test getting order book metrics."""
        metrics = await initialized_collector.get_metrics(
            "BTCUSDT",
            price_range=Decimal("100"),
            levels=10
        )
        assert isinstance(metrics["spread"], Decimal)
        assert isinstance(metrics["bid_depth"], Decimal)
        assert isinstance(metrics["ask_depth"], Decimal)
        assert isinstance(metrics["imbalance"], Decimal)
        
    async def test_handle_ws_message(self, initialized_collector, sample_ws_message):
        """Test handling WebSocket messages."""
        await initialized_collector._handle_ws_message("BTCUSDT", sample_ws_message)
        book = initialized_collector._order_books["BTCUSDT"]
        assert Decimal("100.50") in book.bids
        assert Decimal("101.20") in book.asks
        
    async def test_invalid_symbol(self, initialized_collector):
        """Test accessing invalid symbol."""
        with pytest.raises(CollectorError):
            await initialized_collector.get_order_book("INVALID")
            
    async def test_metrics_callback(self):
        """Test metrics callback functionality."""
        callback_data = []
        def metrics_callback(symbol: str, metrics: Dict[str, Decimal]):
            callback_data.append((symbol, metrics))
            
        collector = OrderBookCollector(
            symbols=["BTCUSDT"],
            metrics_callback=metrics_callback
        )
        
        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {
                "lastUpdateId": 1,
                "bids": [["100.00", "1.000"]],
                "asks": [["101.00", "1.500"]]
            }
            mock_get.return_value.__aenter__.return_value = mock_response
            
            await collector.start()
            await asyncio.sleep(0.2)  # Wait for metrics callback
            await collector.stop()
            
        assert len(callback_data) > 0
        symbol, metrics = callback_data[0]
        assert symbol == "BTCUSDT"
        assert "spread" in metrics 