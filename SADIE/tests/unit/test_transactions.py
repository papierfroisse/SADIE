"""Unit tests for the transaction flow collector."""
import asyncio
import json
from decimal import Decimal
from datetime import datetime, timezone
from typing import Dict, List, Any
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from sadie.data.collectors.transactions import (
    Transaction,
    TransactionMetrics,
    TransactionCollector,
)
from sadie.data.collectors.exceptions import CollectorError

@pytest.fixture
def sample_transaction():
    """Create a sample transaction for testing."""
    return Transaction(
        price=Decimal("50000.00"),
        quantity=Decimal("1.5"),
        timestamp=datetime.now(timezone.utc),
        is_buyer_maker=False,
        trade_id=12345
    )

@pytest.fixture
def sample_transactions():
    """Create a list of sample transactions for testing."""
    return [
        Transaction(
            price=Decimal("50000.00"),
            quantity=Decimal("1.0"),
            timestamp=datetime.now(timezone.utc),
            is_buyer_maker=False,
            trade_id=1
        ),
        Transaction(
            price=Decimal("50100.00"),
            quantity=Decimal("2.0"),
            timestamp=datetime.now(timezone.utc),
            is_buyer_maker=True,
            trade_id=2
        ),
        Transaction(
            price=Decimal("49900.00"),
            quantity=Decimal("1.5"),
            timestamp=datetime.now(timezone.utc),
            is_buyer_maker=False,
            trade_id=3
        )
    ]

@pytest.fixture
def sample_ws_message():
    """Sample WebSocket message for testing."""
    return json.dumps({
        "e": "trade",
        "E": 123456789,
        "s": "BTCUSDT",
        "t": 12345,
        "p": "50000.00",
        "q": "1.5",
        "b": 88,
        "a": 50,
        "T": 123456789000,
        "m": False,
        "M": True
    })

class TestTransaction:
    """Test cases for Transaction class."""
    
    def test_initialization(self, sample_transaction):
        """Test transaction initialization."""
        assert sample_transaction.price == Decimal("50000.00")
        assert sample_transaction.quantity == Decimal("1.5")
        assert isinstance(sample_transaction.timestamp, datetime)
        assert sample_transaction.is_buyer_maker is False
        assert sample_transaction.trade_id == 12345
        
    def test_side_property(self, sample_transaction):
        """Test transaction side property."""
        assert sample_transaction.side == "buy"
        
        sample_transaction.is_buyer_maker = True
        assert sample_transaction.side == "sell"
        
    def test_volume_property(self, sample_transaction):
        """Test transaction volume property."""
        expected_volume = Decimal("50000.00") * Decimal("1.5")
        assert sample_transaction.volume == expected_volume

class TestTransactionMetrics:
    """Test cases for TransactionMetrics."""
    
    def test_compute_vwap(self, sample_transactions):
        """Test VWAP computation."""
        vwap = TransactionMetrics.compute_vwap(sample_transactions)
        
        # Manual calculation
        total_volume = sum(tx.volume for tx in sample_transactions)
        weighted_sum = sum(tx.price * tx.volume for tx in sample_transactions)
        expected_vwap = weighted_sum / total_volume
        
        assert vwap == expected_vwap
        
    def test_compute_vwap_empty(self):
        """Test VWAP computation with empty transaction list."""
        vwap = TransactionMetrics.compute_vwap([])
        assert vwap == Decimal('0')
        
    def test_compute_buy_sell_ratio(self, sample_transactions):
        """Test buy/sell ratio computation."""
        ratio = TransactionMetrics.compute_buy_sell_ratio(sample_transactions)
        
        # Manual calculation
        buy_volume = sum(tx.volume for tx in sample_transactions if not tx.is_buyer_maker)
        sell_volume = sum(tx.volume for tx in sample_transactions if tx.is_buyer_maker)
        expected_ratio = buy_volume / sell_volume
        
        assert ratio == expected_ratio
        
    def test_compute_buy_sell_ratio_empty(self):
        """Test buy/sell ratio computation with empty transaction list."""
        ratio = TransactionMetrics.compute_buy_sell_ratio([])
        assert ratio == Decimal('1')
        
    def test_compute_trade_stats(self, sample_transactions):
        """Test trade statistics computation."""
        avg_size, volume, count = TransactionMetrics.compute_trade_stats(sample_transactions)
        
        # Manual calculation
        total_volume = sum(tx.volume for tx in sample_transactions)
        expected_avg_size = total_volume / len(sample_transactions)
        
        assert avg_size == expected_avg_size
        assert volume == total_volume
        assert count == len(sample_transactions)
        
    def test_compute_trade_stats_empty(self):
        """Test trade statistics computation with empty transaction list."""
        avg_size, volume, count = TransactionMetrics.compute_trade_stats([])
        assert avg_size == Decimal('0')
        assert volume == Decimal('0')
        assert count == 0

@pytest.mark.asyncio
class TestTransactionCollector:
    """Test cases for TransactionCollector."""
    
    @pytest.fixture
    def collector(self):
        """Create a collector instance for testing."""
        return TransactionCollector(
            symbols=["BTCUSDT"],
            window_size=1000,
            update_interval=0.1,
            rate_limit=10
        )
        
    async def test_initialization(self, collector):
        """Test collector initialization."""
        assert collector.symbols == ["BTCUSDT"]
        assert collector.window_size == 1000
        assert collector.update_interval == 0.1
        
    async def test_start_stop(self, collector):
        """Test starting and stopping the collector."""
        await collector.start()
        
        assert len(collector._transactions) == 1
        assert "BTCUSDT" in collector._transactions
        assert len(collector._ws_connections) == 1
        
        await collector.stop()
        assert len(collector._ws_connections) == 0
        
    async def test_handle_ws_message(self, collector, sample_ws_message):
        """Test handling WebSocket messages."""
        await collector.start()
        await collector._handle_ws_message("BTCUSDT", sample_ws_message)
        
        transactions = await collector.get_transactions("BTCUSDT")
        assert len(transactions) == 1
        
        tx = transactions[0]
        assert tx.price == Decimal("50000.00")
        assert tx.quantity == Decimal("1.5")
        assert tx.is_buyer_maker is False
        assert tx.trade_id == 12345
        
        await collector.stop()
        
    async def test_get_transactions(self, collector, sample_ws_message):
        """Test getting transactions with limit."""
        await collector.start()
        
        # Add multiple transactions
        for i in range(5):
            data = json.loads(sample_ws_message)
            data['t'] = i  # Unique trade ID
            await collector._handle_ws_message("BTCUSDT", json.dumps(data))
            
        # Test without limit
        transactions = await collector.get_transactions("BTCUSDT")
        assert len(transactions) == 5
        
        # Test with limit
        transactions = await collector.get_transactions("BTCUSDT", limit=3)
        assert len(transactions) == 3
        
        await collector.stop()
        
    async def test_get_metrics(self, collector, sample_ws_message):
        """Test getting transaction metrics."""
        await collector.start()
        
        # Add some transactions
        for i in range(3):
            data = json.loads(sample_ws_message)
            data['t'] = i  # Unique trade ID
            await collector._handle_ws_message("BTCUSDT", json.dumps(data))
            
        metrics = await collector.get_metrics("BTCUSDT")
        
        assert 'vwap' in metrics
        assert 'buy_sell_ratio' in metrics
        assert 'avg_trade_size' in metrics
        assert 'total_volume' in metrics
        assert 'trade_count' in metrics
        assert 'timestamp' in metrics
        
        assert isinstance(metrics['vwap'], Decimal)
        assert isinstance(metrics['buy_sell_ratio'], Decimal)
        assert isinstance(metrics['avg_trade_size'], Decimal)
        assert isinstance(metrics['total_volume'], Decimal)
        assert isinstance(metrics['trade_count'], int)
        assert isinstance(metrics['timestamp'], datetime)
        
        await collector.stop()
        
    async def test_invalid_symbol(self, collector):
        """Test accessing invalid symbol."""
        await collector.start()
        
        with pytest.raises(CollectorError):
            await collector.get_transactions("INVALID")
            
        with pytest.raises(CollectorError):
            await collector.get_metrics("INVALID")
            
        await collector.stop()
        
    async def test_metrics_callback(self):
        """Test metrics callback functionality."""
        callback_data = []
        def metrics_callback(symbol: str, metrics: Dict[str, Any]):
            callback_data.append((symbol, metrics))
            
        collector = TransactionCollector(
            symbols=["BTCUSDT"],
            metrics_callback=metrics_callback
        )
        
        await collector.start()
        
        # Add a transaction
        data = json.loads(sample_ws_message)
        await collector._handle_ws_message("BTCUSDT", json.dumps(data))
        
        # Wait for callback
        await asyncio.sleep(0.2)
        
        await collector.stop()
        
        assert len(callback_data) > 0
        symbol, metrics = callback_data[0]
        assert symbol == "BTCUSDT"
        assert 'vwap' in metrics 