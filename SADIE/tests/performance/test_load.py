"""Performance and load tests for data collectors."""
import asyncio
import time
import psutil
import pytest
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
from datetime import datetime, timedelta

from sadie.data.collectors.orderbook import OrderBookCollector
from sadie.data.collectors.transactions import TransactionCollector
from sadie.data.collectors.tick import TickCollector

class PerformanceMetrics:
    """Class for measuring performance metrics."""
    
    @staticmethod
    def measure_memory_usage() -> float:
        """Measure current memory usage in MB."""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
        
    @staticmethod
    def measure_cpu_usage() -> float:
        """Measure current CPU usage percentage."""
        return psutil.cpu_percent(interval=1)
        
    @staticmethod
    async def measure_latency(func, *args, **kwargs) -> float:
        """Measure function execution latency in milliseconds."""
        start = time.perf_counter()
        await func(*args, **kwargs)
        end = time.perf_counter()
        return (end - start) * 1000
        
    @staticmethod
    def calculate_percentile(values: List[float], percentile: float) -> float:
        """Calculate percentile from a list of values."""
        return float(np.percentile(values, percentile))
        
class LoadGenerator:
    """Class for generating test load."""
    
    def __init__(self, tps: int, duration: int):
        """Initialize load generator.
        
        Args:
            tps: Target transactions per second
            duration: Test duration in seconds
        """
        self.tps = tps
        self.duration = duration
        self.interval = 1.0 / tps
        
    async def generate_load(self, func, *args, **kwargs) -> List[float]:
        """Generate load by calling function at specified rate.
        
        Returns:
            List of latencies in milliseconds
        """
        start_time = time.perf_counter()
        latencies = []
        
        while time.perf_counter() - start_time < self.duration:
            iteration_start = time.perf_counter()
            
            # Measure latency
            latency = await PerformanceMetrics.measure_latency(func, *args, **kwargs)
            latencies.append(latency)
            
            # Sleep remaining time to maintain TPS
            elapsed = time.perf_counter() - iteration_start
            if elapsed < self.interval:
                await asyncio.sleep(self.interval - elapsed)
                
        return latencies

@pytest.mark.performance
class TestOrderBookCollector:
    """Performance tests for OrderBookCollector."""
    
    @pytest.fixture
    async def collector(self):
        """Create collector instance for testing."""
        collector = OrderBookCollector(
            symbols=["BTCUSDT"],
            depth_level="L2",
            update_interval=0.1
        )
        await collector.start()
        yield collector
        await collector.stop()
        
    async def test_memory_usage(self, collector):
        """Test memory usage under load."""
        initial_memory = PerformanceMetrics.measure_memory_usage()
        
        # Generate load
        load_gen = LoadGenerator(tps=100, duration=60)
        await load_gen.generate_load(collector.get_order_book, "BTCUSDT")
        
        final_memory = PerformanceMetrics.measure_memory_usage()
        memory_increase = final_memory - initial_memory
        
        assert memory_increase < 200  # Max 200MB increase
        
    async def test_cpu_usage(self, collector):
        """Test CPU usage under load."""
        cpu_samples = []
        
        # Generate load and measure CPU
        load_gen = LoadGenerator(tps=100, duration=60)
        async def measure_cpu():
            while True:
                cpu_samples.append(PerformanceMetrics.measure_cpu_usage())
                await asyncio.sleep(1)
                
        cpu_task = asyncio.create_task(measure_cpu())
        await load_gen.generate_load(collector.get_order_book, "BTCUSDT")
        cpu_task.cancel()
        
        avg_cpu = sum(cpu_samples) / len(cpu_samples)
        assert avg_cpu < 30  # Max 30% CPU usage
        
    async def test_latency(self, collector):
        """Test response latency under load."""
        load_gen = LoadGenerator(tps=100, duration=60)
        latencies = await load_gen.generate_load(collector.get_order_book, "BTCUSDT")
        
        avg_latency = sum(latencies) / len(latencies)
        p95_latency = PerformanceMetrics.calculate_percentile(latencies, 95)
        p99_latency = PerformanceMetrics.calculate_percentile(latencies, 99)
        
        assert avg_latency < 100  # Average < 100ms
        assert p95_latency < 200  # 95th percentile < 200ms
        assert p99_latency < 500  # 99th percentile < 500ms
        
    async def test_concurrent_requests(self, collector):
        """Test performance with concurrent requests."""
        async def make_requests(n: int) -> List[float]:
            latencies = []
            for _ in range(n):
                latency = await PerformanceMetrics.measure_latency(
                    collector.get_order_book, "BTCUSDT"
                )
                latencies.append(latency)
            return latencies
            
        # Run 10 concurrent request batches
        tasks = [make_requests(10) for _ in range(10)]
        all_latencies = await asyncio.gather(*tasks)
        
        # Flatten latencies list
        latencies = [lat for batch in all_latencies for lat in batch]
        
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        
        assert avg_latency < 200  # Average < 200ms under load
        assert max_latency < 1000  # Max < 1s
        
@pytest.mark.performance
class TestTransactionCollector:
    """Performance tests for TransactionCollector."""
    
    @pytest.fixture
    async def collector(self):
        """Create collector instance for testing."""
        collector = TransactionCollector(
            symbols=["BTCUSDT"],
            window_size=1000,
            update_interval=0.1
        )
        await collector.start()
        yield collector
        await collector.stop()
        
    async def test_memory_usage(self, collector):
        """Test memory usage under load."""
        initial_memory = PerformanceMetrics.measure_memory_usage()
        
        # Generate load
        load_gen = LoadGenerator(tps=1000, duration=60)
        await load_gen.generate_load(collector.get_recent_transactions, "BTCUSDT")
        
        final_memory = PerformanceMetrics.measure_memory_usage()
        memory_increase = final_memory - initial_memory
        
        assert memory_increase < 100  # Max 100MB increase
        
    async def test_high_throughput(self, collector):
        """Test collector under high transaction throughput."""
        load_gen = LoadGenerator(tps=1000, duration=60)
        latencies = await load_gen.generate_load(
            collector.get_recent_transactions, "BTCUSDT"
        )
        
        success_rate = len(latencies) / (load_gen.tps * load_gen.duration)
        avg_latency = sum(latencies) / len(latencies)
        
        assert success_rate > 0.99  # 99% success rate
        assert avg_latency < 50  # Average < 50ms
        
    async def test_callback_performance(self, collector):
        """Test callback execution performance."""
        callback_latencies = []
        
        async def test_callback(transactions, metrics):
            start = time.perf_counter()
            # Simulate callback processing
            await asyncio.sleep(0.001)
            end = time.perf_counter()
            callback_latencies.append((end - start) * 1000)
            
        collector.register_callback(test_callback, "BTCUSDT")
        
        # Wait for callbacks to accumulate
        await asyncio.sleep(10)
        
        avg_latency = sum(callback_latencies) / len(callback_latencies)
        max_latency = max(callback_latencies)
        
        assert avg_latency < 10  # Average < 10ms
        assert max_latency < 50  # Max < 50ms
        
@pytest.mark.performance
class TestTickCollector:
    """Performance tests for TickCollector."""
    
    @pytest.fixture
    async def collector(self):
        """Create collector instance for testing."""
        collector = TickCollector(
            symbols=["BTCUSDT"],
            batch_size=100,
            update_interval=0.1
        )
        await collector.start()
        yield collector
        await collector.stop()
        
    async def test_memory_usage(self, collector):
        """Test memory usage under load."""
        initial_memory = PerformanceMetrics.measure_memory_usage()
        
        # Generate load
        load_gen = LoadGenerator(tps=1000, duration=60)
        await load_gen.generate_load(collector.get_latest_ticks, "BTCUSDT")
        
        final_memory = PerformanceMetrics.measure_memory_usage()
        memory_increase = final_memory - initial_memory
        
        assert memory_increase < 150  # Max 150MB increase
        
    async def test_batch_processing(self, collector):
        """Test tick batch processing performance."""
        processing_times = []
        
        for _ in range(100):
            start = time.perf_counter()
            await collector._process_tick_batches()
            end = time.perf_counter()
            processing_times.append((end - start) * 1000)
            
        avg_time = sum(processing_times) / len(processing_times)
        max_time = max(processing_times)
        
        assert avg_time < 20  # Average < 20ms
        assert max_time < 100  # Max < 100ms
        
    async def test_high_frequency_updates(self, collector):
        """Test performance with high-frequency tick updates."""
        update_latencies = []
        
        async def measure_update_latency(symbol: str, tick_data: Dict[str, Any]):
            start = time.perf_counter()
            await collector._handle_tick(tick_data)
            end = time.perf_counter()
            update_latencies.append((end - start) * 1000)
            
        collector.register_callback(measure_update_latency, "BTCUSDT")
        
        # Generate high-frequency updates
        load_gen = LoadGenerator(tps=5000, duration=10)
        await load_gen.generate_load(
            collector._handle_tick,
            {"symbol": "BTCUSDT", "price": 50000, "quantity": 1.0}
        )
        
        avg_latency = sum(update_latencies) / len(update_latencies)
        p99_latency = PerformanceMetrics.calculate_percentile(update_latencies, 99)
        
        assert avg_latency < 1  # Average < 1ms
        assert p99_latency < 5  # 99th percentile < 5ms 