"""Load tests for data collectors."""

import asyncio
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List

import psutil
import pytest

from sadie.data.collectors import OrderBookCollector, TradesCollector
from sadie.storage.database import DatabaseManager


class LoadTestMetrics:
    """Class to track load test metrics."""

    def __init__(self):
        """Initialize metrics."""
        self.start_time = time.time()
        self.end_time = None
        self.initial_memory = None
        self.peak_memory = 0
        self.cpu_usage = []
        self.message_rates = []
        self.error_count = 0
        self.db_write_latencies = []
        self.websocket_latencies = []
        self.connection_drops = 0
        self.reconnections = 0

    def update(self, cpu_percent: float, memory_usage: float):
        """Update system metrics.
        
        Args:
            cpu_percent: Current CPU usage percentage.
            memory_usage: Current memory usage in bytes.
        """
        self.cpu_usage.append(cpu_percent)
        self.peak_memory = max(self.peak_memory, memory_usage)

    def add_message_rate(self, messages_per_second: float):
        """Record message processing rate.
        
        Args:
            messages_per_second: Number of messages processed per second.
        """
        self.message_rates.append(messages_per_second)

    def add_db_write_latency(self, latency: float):
        """Record database write latency.
        
        Args:
            latency: Write operation latency in seconds.
        """
        self.db_write_latencies.append(latency)

    def add_websocket_latency(self, latency: float):
        """Record WebSocket message latency.
        
        Args:
            latency: WebSocket operation latency in seconds.
        """
        self.websocket_latencies.append(latency)

    def add_error(self):
        """Record an error."""
        self.error_count += 1

    def add_connection_drop(self):
        """Record a connection drop."""
        self.connection_drops += 1

    def add_reconnection(self):
        """Record a successful reconnection."""
        self.reconnections += 1

    def get_summary(self) -> Dict:
        """Get load test metrics summary.
        
        Returns:
            Dictionary containing load test metrics.
        """
        duration = self.end_time - self.start_time if self.end_time else time.time() - self.start_time
        memory_increase = self.peak_memory - (self.initial_memory or 0)
        
        return {
            "duration_seconds": duration,
            "average_message_rate": sum(self.message_rates) / len(self.message_rates) if self.message_rates else 0,
            "peak_message_rate": max(self.message_rates) if self.message_rates else 0,
            "average_cpu_percent": sum(self.cpu_usage) / len(self.cpu_usage) if self.cpu_usage else 0,
            "peak_cpu_percent": max(self.cpu_usage) if self.cpu_usage else 0,
            "memory_increase_mb": memory_increase / (1024 * 1024),
            "peak_memory_mb": self.peak_memory / (1024 * 1024),
            "error_rate": self.error_count / (len(self.message_rates) or 1),
            "average_db_write_ms": sum(self.db_write_latencies) / len(self.db_write_latencies) * 1000 if self.db_write_latencies else 0,
            "p95_db_write_ms": sorted(self.db_write_latencies)[int(len(self.db_write_latencies) * 0.95)] * 1000 if self.db_write_latencies else 0,
            "average_websocket_ms": sum(self.websocket_latencies) / len(self.websocket_latencies) * 1000 if self.websocket_latencies else 0,
            "p95_websocket_ms": sorted(self.websocket_latencies)[int(len(self.websocket_latencies) * 0.95)] * 1000 if self.websocket_latencies else 0,
            "connection_drops": self.connection_drops,
            "successful_reconnections": self.reconnections,
            "reconnection_rate": self.reconnections / self.connection_drops if self.connection_drops > 0 else 1.0,
        }


class InstrumentedOrderBookCollector(OrderBookCollector):
    """OrderBookCollector with load test instrumentation."""

    def __init__(self, *args, metrics: LoadTestMetrics, **kwargs):
        """Initialize the collector with metrics tracking."""
        super().__init__(*args, **kwargs)
        self._metrics = metrics
        self._message_count = 0
        self._last_message_time = time.time()

    async def _handle_depth_socket(self, ws: any, symbol: str) -> None:
        """Handle depth socket messages with metrics tracking."""
        async with ws as stream:
            while True:
                try:
                    start_time = time.time()
                    msg = await stream.recv()
                    
                    # Track WebSocket latency
                    self._metrics.add_websocket_latency(time.time() - start_time)
                    
                    # Update message rate
                    self._message_count += 1
                    current_time = time.time()
                    elapsed = current_time - self._last_message_time
                    if elapsed >= 1.0:
                        self._metrics.add_message_rate(self._message_count / elapsed)
                        self._message_count = 0
                        self._last_message_time = current_time
                    
                    # Process message
                    self._order_books[symbol] = {
                        "bids": msg["b"],
                        "asks": msg["a"],
                        "last_update": msg["E"],
                    }
                    
                except Exception as e:
                    self._metrics.add_error()
                    raise


class InstrumentedTradesCollector(TradesCollector):
    """TradesCollector with load test instrumentation."""

    def __init__(self, *args, metrics: LoadTestMetrics, **kwargs):
        """Initialize the collector with metrics tracking."""
        super().__init__(*args, **kwargs)
        self._metrics = metrics
        self._message_count = 0
        self._last_message_time = time.time()

    async def _handle_trade_socket(self, ws: any, symbol: str) -> None:
        """Handle trade socket messages with metrics tracking."""
        async with ws as stream:
            while True:
                try:
                    start_time = time.time()
                    msg = await stream.recv()
                    
                    # Track WebSocket latency
                    self._metrics.add_websocket_latency(time.time() - start_time)
                    
                    # Update message rate
                    self._message_count += 1
                    current_time = time.time()
                    elapsed = current_time - self._last_message_time
                    if elapsed >= 1.0:
                        self._metrics.add_message_rate(self._message_count / elapsed)
                        self._message_count = 0
                        self._last_message_time = current_time
                    
                    # Process message
                    trade = {
                        "symbol": symbol,
                        "trade_id": msg["t"],
                        "price": msg["p"],
                        "quantity": msg["q"],
                        "buyer_order_id": msg["b"],
                        "seller_order_id": msg["a"],
                        "timestamp": msg["T"],
                        "buyer_is_maker": msg["m"],
                        "is_best_match": msg["M"],
                    }
                    
                    self._trade_batches[symbol].append(trade)
                    
                    if len(self._trade_batches[symbol]) >= self._batch_size:
                        db_start = time.time()
                        await self._store_batch(symbol)
                        self._metrics.add_db_write_latency(time.time() - db_start)
                    
                except Exception as e:
                    self._metrics.add_error()
                    raise


@pytest.fixture
async def db_manager():
    """Create a database manager instance."""
    manager = DatabaseManager(
        host=os.getenv("TEST_DB_HOST", "localhost"),
        port=int(os.getenv("TEST_DB_PORT", "5432")),
        database=os.getenv("TEST_DB_NAME", "sadie_test"),
        user=os.getenv("TEST_DB_USER", "postgres"),
        password=os.getenv("TEST_DB_PASSWORD", "postgres"),
        min_connections=50,
        max_connections=200,
    )
    await manager.connect()
    yield manager
    await manager.disconnect()


async def run_load_test(
    collector_class: type,
    symbols: List[str],
    duration: int,
    db_manager: DatabaseManager,
    **collector_kwargs,
) -> Dict:
    """Run a load test with specified parameters.
    
    Args:
        collector_class: Collector class to test.
        symbols: List of symbols to collect.
        duration: Duration in seconds.
        db_manager: Database manager instance.
        **collector_kwargs: Additional collector parameters.
        
    Returns:
        Dictionary containing load test results.
    """
    metrics = LoadTestMetrics()
    
    # Record initial system state
    process = psutil.Process()
    metrics.initial_memory = process.memory_info().rss
    
    # Create instrumented collector
    collector = collector_class(
        db_manager=db_manager,
        symbols=symbols,
        metrics=metrics,
        **collector_kwargs,
    )
    
    try:
        await collector.start()
        
        # Monitor system metrics during test
        start_time = time.time()
        while time.time() - start_time < duration:
            metrics.update(
                cpu_percent=process.cpu_percent(),
                memory_usage=process.memory_info().rss,
            )
            await asyncio.sleep(1)
            
    finally:
        await collector.stop()
        metrics.end_time = time.time()
    
    return metrics.get_summary()


@pytest.mark.load_test
@pytest.mark.asyncio
async def test_orderbook_collector_load(db_manager):
    """Load test for OrderBookCollector."""
    results = await run_load_test(
        collector_class=InstrumentedOrderBookCollector,
        symbols=["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "DOTUSDT"],
        duration=300,  # 5 minutes
        db_manager=db_manager,
        depth_level="L2",
        update_interval=1.0,
    )
    
    # Performance assertions
    assert results["average_message_rate"] >= 5.0  # At least 5 messages/sec
    assert results["average_cpu_percent"] <= 50  # CPU usage under 50%
    assert results["memory_increase_mb"] <= 200  # Memory increase under 200MB
    assert results["error_rate"] <= 0.01  # Less than 1% errors
    assert results["average_db_write_ms"] <= 100  # DB writes under 100ms
    assert results["average_websocket_ms"] <= 50  # WebSocket latency under 50ms
    assert results["reconnection_rate"] >= 0.95  # 95% successful reconnections
    
    print("\nOrderBook Collector Load Test Results:")
    for metric, value in results.items():
        print(f"{metric}: {value}")


@pytest.mark.load_test
@pytest.mark.asyncio
async def test_trades_collector_load(db_manager):
    """Load test for TradesCollector."""
    results = await run_load_test(
        collector_class=InstrumentedTradesCollector,
        symbols=["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "DOTUSDT"],
        duration=300,  # 5 minutes
        db_manager=db_manager,
        batch_size=100,
        batch_interval=1.0,
    )
    
    # Performance assertions
    assert results["average_message_rate"] >= 10.0  # At least 10 messages/sec
    assert results["average_cpu_percent"] <= 50  # CPU usage under 50%
    assert results["memory_increase_mb"] <= 200  # Memory increase under 200MB
    assert results["error_rate"] <= 0.01  # Less than 1% errors
    assert results["average_db_write_ms"] <= 100  # DB writes under 100ms
    assert results["average_websocket_ms"] <= 50  # WebSocket latency under 50ms
    assert results["reconnection_rate"] >= 0.95  # 95% successful reconnections
    
    print("\nTrades Collector Load Test Results:")
    for metric, value in results.items():
        print(f"{metric}: {value}")


@pytest.mark.load_test
@pytest.mark.asyncio
async def test_concurrent_collectors_load(db_manager):
    """Load test for running multiple collectors concurrently."""
    # Create metrics trackers
    orderbook_metrics = LoadTestMetrics()
    trades_metrics = LoadTestMetrics()
    
    # Create collectors
    orderbook_collector = InstrumentedOrderBookCollector(
        db_manager=db_manager,
        symbols=["BTCUSDT", "ETHUSDT", "BNBUSDT"],
        metrics=orderbook_metrics,
        depth_level="L2",
        update_interval=1.0,
    )
    
    trades_collector = InstrumentedTradesCollector(
        db_manager=db_manager,
        symbols=["BTCUSDT", "ETHUSDT", "BNBUSDT"],
        metrics=trades_metrics,
        batch_size=100,
        batch_interval=1.0,
    )
    
    try:
        # Start collectors
        await asyncio.gather(
            orderbook_collector.start(),
            trades_collector.start(),
        )
        
        # Monitor system metrics
        process = psutil.Process()
        start_time = time.time()
        while time.time() - start_time < 300:  # 5 minutes
            cpu_percent = process.cpu_percent()
            memory_usage = process.memory_info().rss
            orderbook_metrics.update(cpu_percent / 2, memory_usage / 2)
            trades_metrics.update(cpu_percent / 2, memory_usage / 2)
            await asyncio.sleep(1)
            
    finally:
        # Stop collectors
        await asyncio.gather(
            orderbook_collector.stop(),
            trades_collector.stop(),
        )
        orderbook_metrics.end_time = time.time()
        trades_metrics.end_time = time.time()
    
    # Get results
    orderbook_results = orderbook_metrics.get_summary()
    trades_results = trades_metrics.get_summary()
    
    # Combined performance assertions
    assert orderbook_results["average_message_rate"] >= 3.0  # At least 3 messages/sec
    assert trades_results["average_message_rate"] >= 5.0  # At least 5 messages/sec
    assert orderbook_results["average_cpu_percent"] + trades_results["average_cpu_percent"] <= 70  # Combined CPU under 70%
    assert orderbook_results["memory_increase_mb"] + trades_results["memory_increase_mb"] <= 400  # Combined memory under 400MB
    
    print("\nConcurrent Collectors Load Test Results:")
    print("\nOrderBook Collector:")
    for metric, value in orderbook_results.items():
        print(f"{metric}: {value}")
    
    print("\nTrades Collector:")
    for metric, value in trades_results.items():
        print(f"{metric}: {value}")


if __name__ == "__main__":
    asyncio.run(test_concurrent_collectors_load(DatabaseManager())) 