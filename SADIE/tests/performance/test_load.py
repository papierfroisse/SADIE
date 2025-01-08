"""Load and resilience tests for data collectors."""
import asyncio
import time
from typing import List, Dict, Any
import pytest
import psutil
import logging
from concurrent.futures import ThreadPoolExecutor

from sadie.data.collectors.orderbook import OrderBookCollector
from sadie.data.collectors.transactions import TransactionCollector
from sadie.data.collectors.tick import TickCollector

logger = logging.getLogger(__name__)

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
        start_time = time.perf_counter()
        await func(*args, **kwargs)
        end_time = time.perf_counter()
        return (end_time - start_time) * 1000

@pytest.mark.performance
class TestCollectorLoad:
    """Load tests for data collectors."""
    
    @pytest.fixture
    async def collectors(self):
        """Create collectors for testing."""
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "DOGEUSDT"]
        
        orderbook = OrderBookCollector(symbols=symbols, depth=1000)
        transactions = TransactionCollector(symbols=symbols, window_size=5000)
        tick = TickCollector(symbols=symbols, batch_size=1000)
        
        await asyncio.gather(
            orderbook.start(),
            transactions.start(),
            tick.start()
        )
        
        yield orderbook, transactions, tick
        
        await asyncio.gather(
            orderbook.stop(),
            transactions.stop(),
            tick.stop()
        )
        
    async def test_memory_usage(self, collectors):
        """Test memory usage under load."""
        orderbook, transactions, tick = collectors
        initial_memory = PerformanceMetrics.measure_memory_usage()
        
        # Generate load
        for _ in range(1000):
            await asyncio.gather(
                orderbook.get_order_book("BTCUSDT"),
                transactions.get_transactions("BTCUSDT"),
                tick.get_ticks("BTCUSDT")
            )
            
        final_memory = PerformanceMetrics.measure_memory_usage()
        memory_increase = final_memory - initial_memory
        
        logger.info(f"Memory usage increase: {memory_increase:.2f} MB")
        assert memory_increase < 500  # Max 500MB increase
        
    async def test_cpu_usage(self, collectors):
        """Test CPU usage under load."""
        orderbook, transactions, tick = collectors
        cpu_usage_samples = []
        
        # Generate load and measure CPU
        for _ in range(10):
            await asyncio.gather(
                orderbook.get_metrics("BTCUSDT"),
                transactions.get_metrics("BTCUSDT"),
                tick.get_metrics("BTCUSDT")
            )
            cpu_usage_samples.append(PerformanceMetrics.measure_cpu_usage())
            
        avg_cpu_usage = sum(cpu_usage_samples) / len(cpu_usage_samples)
        logger.info(f"Average CPU usage: {avg_cpu_usage:.2f}%")
        assert avg_cpu_usage < 80  # Max 80% CPU usage
        
    async def test_latency(self, collectors):
        """Test response latency under load."""
        orderbook, transactions, tick = collectors
        latencies = []
        
        # Measure latency for different operations
        for _ in range(100):
            latency = await PerformanceMetrics.measure_latency(
                orderbook.get_order_book, "BTCUSDT"
            )
            latencies.append(latency)
            
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        
        logger.info(f"Average latency: {avg_latency:.2f}ms")
        logger.info(f"Maximum latency: {max_latency:.2f}ms")
        
        assert avg_latency < 50  # Max 50ms average latency
        assert max_latency < 200  # Max 200ms peak latency
        
    async def test_concurrent_requests(self, collectors):
        """Test handling of concurrent requests."""
        orderbook, transactions, tick = collectors
        
        async def make_requests():
            """Make multiple requests to collectors."""
            for _ in range(50):
                await asyncio.gather(
                    orderbook.get_order_book("BTCUSDT"),
                    transactions.get_transactions("BTCUSDT"),
                    tick.get_ticks("BTCUSDT")
                )
                
        # Run multiple concurrent request streams
        tasks = [make_requests() for _ in range(10)]
        await asyncio.gather(*tasks)

@pytest.mark.resilience
class TestCollectorResilience:
    """Resilience tests for data collectors."""
    
    @pytest.fixture
    async def collector(self):
        """Create a collector for testing."""
        collector = OrderBookCollector(
            symbols=["BTCUSDT"],
            depth=1000,
            update_interval=0.1
        )
        await collector.start()
        yield collector
        await collector.stop()
        
    async def test_reconnection(self, collector):
        """Test WebSocket reconnection capability."""
        # Force disconnect
        for ws in collector._ws_connections.values():
            ws.cancel()
            
        # Wait for reconnection
        await asyncio.sleep(6)  # Allow time for reconnection
        
        # Verify functionality
        book = await collector.get_order_book("BTCUSDT")
        assert len(book[0]) > 0  # Verify we have bids
        assert len(book[1]) > 0  # Verify we have asks
        
    async def test_error_recovery(self, collector):
        """Test recovery from various error conditions."""
        # Simulate invalid data
        await collector._handle_ws_message("BTCUSDT", "invalid json")
        
        # Verify collector still functions
        book = await collector.get_order_book("BTCUSDT")
        assert len(book[0]) > 0
        assert len(book[1]) > 0
        
    async def test_data_consistency(self, collector):
        """Test data consistency under stress."""
        initial_book = await collector.get_order_book("BTCUSDT")
        
        # Generate rapid updates
        for _ in range(1000):
            await collector.get_order_book("BTCUSDT")
            
        final_book = await collector.get_order_book("BTCUSDT")
        
        # Verify basic consistency
        assert len(final_book[0]) > 0  # Has bids
        assert len(final_book[1]) > 0  # Has asks
        assert final_book[0][0][0] < final_book[1][0][0]  # Bid < Ask
        
    async def test_memory_leak(self, collector):
        """Test for memory leaks during extended operation."""
        initial_memory = PerformanceMetrics.measure_memory_usage()
        
        # Run for extended period
        for _ in range(100):
            await collector.get_order_book("BTCUSDT")
            await asyncio.sleep(0.1)
            
        # Force garbage collection
        import gc
        gc.collect()
        
        final_memory = PerformanceMetrics.measure_memory_usage()
        memory_diff = final_memory - initial_memory
        
        logger.info(f"Memory change after extended operation: {memory_diff:.2f} MB")
        assert memory_diff < 50  # Max 50MB increase 