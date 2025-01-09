"""Performance benchmarks for the OrderBook collector."""

import asyncio
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List

import psutil
import pytest

from sadie.data.collectors import OrderBookCollector
from sadie.storage.database import DatabaseManager


class PerformanceMetrics:
    """Class to track performance metrics."""

    def __init__(self):
        """Initialize metrics."""
        self.start_time = time.time()
        self.end_time = None
        self.initial_memory = None
        self.peak_memory = 0
        self.cpu_usage = []
        self.message_count = 0
        self.error_count = 0
        self.latencies = []
        self.db_write_times = []

    def update(self, cpu_percent: float, memory_usage: float):
        """Update metrics.
        
        Args:
            cpu_percent: Current CPU usage percentage.
            memory_usage: Current memory usage in bytes.
        """
        self.cpu_usage.append(cpu_percent)
        self.peak_memory = max(self.peak_memory, memory_usage)

    def add_message(self, latency: float):
        """Record a message and its latency.
        
        Args:
            latency: Message processing latency in seconds.
        """
        self.message_count += 1
        self.latencies.append(latency)

    def add_db_write(self, write_time: float):
        """Record a database write operation time.
        
        Args:
            write_time: Write operation time in seconds.
        """
        self.db_write_times.append(write_time)

    def add_error(self):
        """Record an error."""
        self.error_count += 1

    def get_summary(self) -> Dict:
        """Get performance metrics summary.
        
        Returns:
            Dictionary containing performance metrics.
        """
        duration = self.end_time - self.start_time if self.end_time else time.time() - self.start_time
        memory_increase = self.peak_memory - (self.initial_memory or 0)
        
        return {
            "duration_seconds": duration,
            "messages_per_second": self.message_count / duration if duration > 0 else 0,
            "average_latency_ms": sum(self.latencies) / len(self.latencies) * 1000 if self.latencies else 0,
            "p95_latency_ms": sorted(self.latencies)[int(len(self.latencies) * 0.95)] * 1000 if self.latencies else 0,
            "average_cpu_percent": sum(self.cpu_usage) / len(self.cpu_usage) if self.cpu_usage else 0,
            "peak_cpu_percent": max(self.cpu_usage) if self.cpu_usage else 0,
            "memory_increase_mb": memory_increase / (1024 * 1024),
            "peak_memory_mb": self.peak_memory / (1024 * 1024),
            "error_rate": self.error_count / self.message_count if self.message_count > 0 else 0,
            "average_db_write_ms": sum(self.db_write_times) / len(self.db_write_times) * 1000 if self.db_write_times else 0,
            "total_messages": self.message_count,
            "total_errors": self.error_count,
        }


class InstrumentedOrderBookCollector(OrderBookCollector):
    """OrderBookCollector with performance instrumentation."""

    def __init__(self, *args, metrics: PerformanceMetrics, **kwargs):
        """Initialize the collector with metrics tracking.
        
        Args:
            metrics: Performance metrics instance.
            *args: Positional arguments for OrderBookCollector.
            **kwargs: Keyword arguments for OrderBookCollector.
        """
        super().__init__(*args, **kwargs)
        self._metrics = metrics
        self._message_timestamps: Dict[str, float] = {}

    async def _handle_depth_socket(self, ws: any, symbol: str) -> None:
        """Handle depth socket messages with performance tracking."""
        async with ws as stream:
            while True:
                try:
                    start_time = time.time()
                    msg = await stream.recv()
                    
                    # Record message receipt
                    msg_id = f"{symbol}_{msg['E']}"
                    self._message_timestamps[msg_id] = start_time
                    
                    # Process message
                    self._order_books[symbol] = {
                        "bids": msg["b"],
                        "asks": msg["a"],
                        "last_update": msg["E"],
                    }
                    
                    # Calculate and record latency
                    latency = time.time() - start_time
                    self._metrics.add_message(latency)
                    
                except Exception as e:
                    self._metrics.add_error()
                    raise

    async def _collect(self) -> None:
        """Collect data with performance tracking."""
        try:
            for symbol in self._symbols:
                if self._depth_level == "L2":
                    ws = self._bm.depth_socket(symbol)
                    task = asyncio.create_task(self._handle_depth_socket(ws, symbol))
                    self._ws_tasks.append(task)
            
            while self._running:
                start_time = time.time()
                
                # Store order books
                timestamp = datetime.utcnow()
                for symbol, book in self._order_books.items():
                    db_start = time.time()
                    await self._db_manager.insert_order_book(
                        symbol=symbol,
                        timestamp=timestamp,
                        bids=book.get("bids", []),
                        asks=book.get("asks", []),
                        exchange=self._exchange,
                        depth_level=self._depth_level,
                    )
                    self._metrics.add_db_write(time.time() - db_start)
                
                # Update system metrics
                process = psutil.Process()
                self._metrics.update(
                    cpu_percent=process.cpu_percent(),
                    memory_usage=process.memory_info().rss,
                )
                
                await asyncio.sleep(self._update_interval)
                
        except asyncio.CancelledError:
            pass
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
        min_connections=20,
        max_connections=100,
    )
    await manager.connect()
    yield manager
    await manager.disconnect()


async def run_benchmark(
    symbols: List[str],
    duration: int,
    update_interval: float,
    db_manager: DatabaseManager,
) -> Dict:
    """Run a benchmark with specified parameters.
    
    Args:
        symbols: List of symbols to collect.
        duration: Duration in seconds.
        update_interval: Update interval in seconds.
        db_manager: Database manager instance.
        
    Returns:
        Dictionary containing benchmark results.
    """
    metrics = PerformanceMetrics()
    
    # Record initial system state
    process = psutil.Process()
    metrics.initial_memory = process.memory_info().rss
    
    collector = InstrumentedOrderBookCollector(
        db_manager=db_manager,
        symbols=symbols,
        depth_level="L2",
        update_interval=update_interval,
        metrics=metrics,
    )
    
    try:
        await collector.start()
        await asyncio.sleep(duration)
    finally:
        await collector.stop()
        metrics.end_time = time.time()
    
    return metrics.get_summary()


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_single_symbol_performance(db_manager):
    """Benchmark single symbol collection."""
    results = await run_benchmark(
        symbols=["BTCUSDT"],
        duration=60,
        update_interval=1.0,
        db_manager=db_manager,
    )
    
    # Performance assertions
    assert results["messages_per_second"] >= 0.5  # At least 1 message every 2 seconds
    assert results["average_latency_ms"] <= 100  # Processing under 100ms
    assert results["error_rate"] <= 0.01  # Less than 1% errors
    assert results["average_db_write_ms"] <= 50  # DB writes under 50ms
    
    print("\nSingle Symbol Performance Results:")
    for metric, value in results.items():
        print(f"{metric}: {value}")


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_multiple_symbols_performance(db_manager):
    """Benchmark multiple symbol collection."""
    results = await run_benchmark(
        symbols=["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "DOTUSDT"],
        duration=60,
        update_interval=1.0,
        db_manager=db_manager,
    )
    
    # Performance assertions
    assert results["messages_per_second"] >= 2.0  # At least 2 messages per second
    assert results["average_latency_ms"] <= 200  # Processing under 200ms
    assert results["error_rate"] <= 0.01  # Less than 1% errors
    assert results["average_db_write_ms"] <= 100  # DB writes under 100ms
    
    print("\nMultiple Symbols Performance Results:")
    for metric, value in results.items():
        print(f"{metric}: {value}")


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_high_frequency_performance(db_manager):
    """Benchmark high-frequency collection."""
    results = await run_benchmark(
        symbols=["BTCUSDT"],
        duration=60,
        update_interval=0.1,  # 100ms updates
        db_manager=db_manager,
    )
    
    # Performance assertions
    assert results["messages_per_second"] >= 5.0  # At least 5 messages per second
    assert results["average_latency_ms"] <= 50  # Processing under 50ms
    assert results["error_rate"] <= 0.01  # Less than 1% errors
    assert results["average_db_write_ms"] <= 30  # DB writes under 30ms
    
    print("\nHigh Frequency Performance Results:")
    for metric, value in results.items():
        print(f"{metric}: {value}")


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_memory_usage(db_manager):
    """Benchmark memory usage over time."""
    results = await run_benchmark(
        symbols=["BTCUSDT", "ETHUSDT", "BNBUSDT"],
        duration=300,  # 5 minutes
        update_interval=1.0,
        db_manager=db_manager,
    )
    
    # Memory assertions
    assert results["memory_increase_mb"] <= 100  # Less than 100MB increase
    assert results["peak_memory_mb"] <= 500  # Peak under 500MB
    
    print("\nMemory Usage Results:")
    for metric, value in results.items():
        print(f"{metric}: {value}")


if __name__ == "__main__":
    asyncio.run(test_single_symbol_performance(DatabaseManager())) 