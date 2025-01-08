"""Unit tests for enhanced order book collector."""
import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime

from sadie.data.collectors.enhanced_orderbook import (
    EnhancedOrderBookCollector,
    OrderBookUpdate
)
from sadie.analysis.orderbook_metrics import OrderBookMetrics

@pytest.fixture
def sample_orderbook():
    """Create sample order book data."""
    bids = [
        (100.0, 1.0),  # price, quantity
        (99.5, 2.0),
        (99.0, 3.0),
        (98.5, 4.0),
        (98.0, 5.0),
    ]
    asks = [
        (101.0, 1.0),
        (101.5, 2.0),
        (102.0, 3.0),
        (102.5, 4.0),
        (103.0, 5.0),
    ]
    return bids, asks

@pytest.fixture
async def collector():
    """Create a collector instance for testing."""
    collector = EnhancedOrderBookCollector(
        symbols=["BTCUSDT"],
        depth=10,
        update_interval=0.1,
        metrics_window=5,
        metrics_levels=5,
        callback_interval=0.1
    )
    await collector.start()
    yield collector
    await collector.stop()

async def test_initialization():
    """Test collector initialization."""
    collector = EnhancedOrderBookCollector(
        symbols=["BTCUSDT", "ETHUSDT"],
        depth=100,
        metrics_window=10
    )
    
    assert collector.symbols == ["BTCUSDT", "ETHUSDT"]
    assert collector.depth == 100
    assert len(collector.analyzers) == 2
    assert not collector._running
    assert isinstance(collector.callbacks["BTCUSDT"], list)

async def test_start_stop(collector):
    """Test starting and stopping the collector."""
    assert collector._running
    assert collector._callback_tasks
    
    await collector.stop()
    assert not collector._running
    assert all(task.cancelled() for task in collector._callback_tasks.values())

async def test_get_orderbook_with_metrics(collector, sample_orderbook):
    """Test getting order book with metrics."""
    bids, asks = sample_orderbook
    
    # Mock the base collector's get_order_book method
    with patch.object(collector.collector, 'get_order_book', return_value=(bids, asks)):
        update = await collector.get_orderbook_with_metrics("BTCUSDT")
        
        assert isinstance(update, OrderBookUpdate)
        assert update.symbol == "BTCUSDT"
        assert update.bids == bids
        assert update.asks == asks
        assert isinstance(update.metrics, OrderBookMetrics)
        assert update.metrics.spread == 1.0  # 101.0 - 100.0
        assert update.metrics.mid_price == 100.5  # (101.0 + 100.0) / 2

async def test_callbacks(collector, sample_orderbook):
    """Test callback registration and execution."""
    bids, asks = sample_orderbook
    callback_mock = Mock()
    
    # Register callback
    collector.register_callback(callback_mock, "BTCUSDT")
    assert callback_mock in collector.callbacks["BTCUSDT"]
    
    # Mock order book data
    with patch.object(collector.collector, 'get_order_book', return_value=(bids, asks)):
        # Wait for callback execution
        await asyncio.sleep(0.2)
        
        # Verify callback was called
        assert callback_mock.called
        call_args = callback_mock.call_args[0][0]
        assert isinstance(call_args, OrderBookUpdate)
        assert call_args.symbol == "BTCUSDT"
        
    # Unregister callback
    collector.unregister_callback(callback_mock, "BTCUSDT")
    assert callback_mock not in collector.callbacks["BTCUSDT"]

async def test_metrics_history(collector, sample_orderbook):
    """Test retrieving metrics history."""
    bids, asks = sample_orderbook
    
    # Generate some history
    with patch.object(collector.collector, 'get_order_book', return_value=(bids, asks)):
        for _ in range(3):
            await collector.get_orderbook_with_metrics("BTCUSDT")
            
    # Get history
    history = await collector.get_metrics_history("BTCUSDT", "volatility")
    assert isinstance(history, list)
    assert len(history) > 0
    
    # Test invalid metric
    with pytest.raises(ValueError):
        await collector.get_metrics_history("BTCUSDT", "invalid_metric")
        
    # Test invalid symbol
    with pytest.raises(ValueError):
        await collector.get_metrics_history("INVALID", "volatility")

async def test_get_all_metrics(collector):
    """Test getting all metrics."""
    metrics = collector.get_all_metrics("BTCUSDT")
    
    assert isinstance(metrics, dict)
    assert "price_history" in metrics
    assert "window_size" in metrics
    assert "depth_levels" in metrics
    
    with pytest.raises(ValueError):
        collector.get_all_metrics("INVALID")

async def test_error_handling(collector):
    """Test error handling in callbacks."""
    def failing_callback(_):
        raise Exception("Test error")
        
    collector.register_callback(failing_callback, "BTCUSDT")
    
    # Should not raise exception
    await collector._run_callbacks("BTCUSDT")

async def test_multiple_symbols():
    """Test collector with multiple symbols."""
    collector = EnhancedOrderBookCollector(
        symbols=["BTCUSDT", "ETHUSDT"],
        depth=10,
        metrics_window=5
    )
    await collector.start()
    
    try:
        assert len(collector._callback_tasks) == 2
        assert "BTCUSDT" in collector.analyzers
        assert "ETHUSDT" in collector.analyzers
        
        # Register callback for all symbols
        callback_mock = Mock()
        collector.register_callback(callback_mock)
        assert callback_mock in collector.callbacks["BTCUSDT"]
        assert callback_mock in collector.callbacks["ETHUSDT"]
        
    finally:
        await collector.stop()

async def test_concurrent_updates(collector, sample_orderbook):
    """Test concurrent updates handling."""
    bids, asks = sample_orderbook
    results = []
    
    async def update_task():
        with patch.object(collector.collector, 'get_order_book', return_value=(bids, asks)):
            update = await collector.get_orderbook_with_metrics("BTCUSDT")
            results.append(update)
            
    # Run multiple concurrent updates
    tasks = [update_task() for _ in range(5)]
    await asyncio.gather(*tasks)
    
    assert len(results) == 5
    assert all(isinstance(r, OrderBookUpdate) for r in results)
    assert all(r.symbol == "BTCUSDT" for r in results) 