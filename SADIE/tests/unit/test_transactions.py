"""Unit tests for transaction collector."""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from sadie.data.collectors.transactions import (
    Transaction,
    TransactionMetrics,
    TransactionCollector
)

@pytest.fixture
def sample_transactions():
    """Create sample transaction data."""
    return [
        Transaction(
            symbol="BTCUSDT",
            timestamp=datetime.now().timestamp(),
            price=50000.0,
            quantity=1.0,
            is_buyer_maker=False,
            trade_id=1
        ),
        Transaction(
            symbol="BTCUSDT",
            timestamp=datetime.now().timestamp(),
            price=50100.0,
            quantity=0.5,
            is_buyer_maker=True,
            trade_id=2
        ),
        Transaction(
            symbol="BTCUSDT",
            timestamp=datetime.now().timestamp(),
            price=49900.0,
            quantity=1.5,
            is_buyer_maker=False,
            trade_id=3
        )
    ]

class MockWebSocket:
    """Mock WebSocket for testing."""
    def __init__(self, messages):
        self.messages = messages
        self.index = 0
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
        
    async def __aiter__(self):
        return self
        
    async def __anext__(self):
        if self.index >= len(self.messages):
            raise StopAsyncIteration
        message = self.messages[self.index]
        self.index += 1
        return message

class TestTransactionCollector:
    """Test cases for transaction collector."""
    
    @pytest.fixture
    async def collector(self):
        """Create a collector instance for testing."""
        collector = TransactionCollector(
            symbols=["BTCUSDT"],
            window_size=100,
            update_interval=0.1,
            callback_interval=0.1
        )
        
        # Mock WebSocket connection
        collector._connect_websocket = AsyncMock(
            return_value=MockWebSocket([
                '{"symbol": "BTCUSDT", "price": "50000", "quantity": "1.0", "is_buyer_maker": false}'
            ])
        )
        
        # Mock transaction parsing
        collector._parse_transaction = Mock(
            return_value=Transaction(
                symbol="BTCUSDT",
                timestamp=datetime.now().timestamp(),
                price=50000.0,
                quantity=1.0,
                is_buyer_maker=False,
                trade_id=1
            )
        )
        
        await collector.start()
        yield collector
        await collector.stop()
        
    async def test_initialization(self):
        """Test collector initialization."""
        collector = TransactionCollector(
            symbols=["BTCUSDT", "ETHUSDT"],
            window_size=100
        )
        
        assert collector.symbols == ["BTCUSDT", "ETHUSDT"]
        assert collector.window_size == 100
        assert not collector._running
        assert isinstance(collector.transactions["BTCUSDT"], deque)
        assert isinstance(collector.callbacks["BTCUSDT"], list)
        
    async def test_start_stop(self, collector):
        """Test starting and stopping the collector."""
        assert collector._running
        assert collector._ws_connections
        assert collector._callback_tasks
        
        await collector.stop()
        assert not collector._running
        assert all(task.cancelled() for task in collector._ws_connections.values())
        assert all(task.cancelled() for task in collector._callback_tasks.values())
        
    def test_compute_metrics(self, sample_transactions):
        """Test metrics computation."""
        collector = TransactionCollector(symbols=["BTCUSDT"])
        metrics = collector.compute_metrics(sample_transactions)
        
        assert isinstance(metrics, TransactionMetrics)
        assert metrics.trade_count == 3
        assert metrics.volume == 3.0  # 1.0 + 0.5 + 1.5
        assert abs(metrics.vwap - 49966.67) < 1  # (50000*1 + 50100*0.5 + 49900*1.5) / 3
        assert metrics.buy_volume == 2.5  # 1.0 + 1.5
        assert metrics.sell_volume == 0.5
        assert metrics.buy_sell_ratio == 5.0  # 2.5 / 0.5
        assert metrics.volatility > 0
        
    async def test_callbacks(self, collector):
        """Test callback registration and execution."""
        callback_mock = Mock()
        collector.register_callback(callback_mock, "BTCUSDT")
        
        assert callback_mock in collector.callbacks["BTCUSDT"]
        
        # Wait for callback execution
        await asyncio.sleep(0.2)
        
        # Verify callback was called
        assert callback_mock.called
        call_args = callback_mock.call_args
        transactions, metrics = call_args[0]
        
        assert isinstance(transactions, list)
        assert isinstance(metrics, TransactionMetrics)
        
        # Unregister callback
        collector.unregister_callback(callback_mock, "BTCUSDT")
        assert callback_mock not in collector.callbacks["BTCUSDT"]
        
    async def test_get_recent_transactions(self, collector):
        """Test retrieving recent transactions."""
        # Wait for some transactions to accumulate
        await asyncio.sleep(0.2)
        
        transactions = await collector.get_recent_transactions("BTCUSDT")
        assert isinstance(transactions, list)
        assert len(transactions) > 0
        assert all(isinstance(tx, Transaction) for tx in transactions)
        
        # Test with limit
        limited = await collector.get_recent_transactions("BTCUSDT", limit=1)
        assert len(limited) == 1
        
        # Test invalid symbol
        with pytest.raises(ValueError):
            await collector.get_recent_transactions("INVALID")
            
    async def test_error_handling(self, collector):
        """Test error handling in callbacks."""
        def failing_callback(_, __):
            raise Exception("Test error")
            
        collector.register_callback(failing_callback, "BTCUSDT")
        
        # Should not raise exception
        await collector._run_callbacks("BTCUSDT")
        
    async def test_multiple_symbols():
        """Test collector with multiple symbols."""
        collector = TransactionCollector(
            symbols=["BTCUSDT", "ETHUSDT"],
            window_size=10
        )
        
        # Mock WebSocket and parsing
        collector._connect_websocket = AsyncMock(
            return_value=MockWebSocket(['{"test": "data"}'])
        )
        collector._parse_transaction = Mock(return_value=None)
        
        await collector.start()
        
        try:
            assert len(collector._ws_connections) == 2
            assert "BTCUSDT" in collector.transactions
            assert "ETHUSDT" in collector.transactions
            
            # Register callbacks
            callback_mock = Mock()
            collector.register_callback(callback_mock, "BTCUSDT")
            assert callback_mock in collector.callbacks["BTCUSDT"]
            
        finally:
            await collector.stop()
            
    async def test_empty_metrics():
        """Test metrics computation with empty transaction list."""
        collector = TransactionCollector(symbols=["BTCUSDT"])
        metrics = collector.compute_metrics([])
        
        assert metrics.vwap == 0.0
        assert metrics.volume == 0.0
        assert metrics.trade_count == 0
        assert metrics.buy_sell_ratio == 1.0
        assert metrics.volatility == 0.0
        assert metrics.price_impact == 0.0 