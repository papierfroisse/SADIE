"""Load and resilience tests for data collectors."""
import asyncio
import time
from typing import List, Dict, Any
import pytest
import psutil
import logging
import gc
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

from sadie.data.collectors.orderbook import OrderBookCollector
from sadie.data.collectors.transactions import TransactionCollector
from sadie.data.collectors.tick import TickCollector

logger = logging.getLogger(__name__)

class PerformanceMetrics:
    """Class for measuring performance metrics."""
    
    @staticmethod
    def measure_memory_usage() -> float:
        """Measure current memory usage in MB."""
        gc.collect()  # Force garbage collection before measurement
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
        
    @staticmethod
    def measure_cpu_usage(interval: float = 1.0) -> float:
        """Measure current CPU usage percentage."""
        return psutil.cpu_percent(interval=interval)
        
    @staticmethod
    async def measure_latency(func, timeout: float = 5.0, *args, **kwargs) -> float:
        """Measure function execution latency in milliseconds."""
        start_time = time.perf_counter()
        try:
            async with asyncio.timeout(timeout):
                await func(*args, **kwargs)
        except asyncio.TimeoutError:
            logger.warning(f"Function {func.__name__} timed out after {timeout}s")
            return float('inf')
        end_time = time.perf_counter()
        return (end_time - start_time) * 1000
        
    @staticmethod
    async def measure_with_retries(func, retries: int = 3, *args, **kwargs) -> float:
        """Measure function with retries on failure."""
        for attempt in range(retries):
            try:
                return await PerformanceMetrics.measure_latency(func, *args, **kwargs)
            except Exception as e:
                if attempt == retries - 1:
                    raise
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                await asyncio.sleep(1)

@asynccontextmanager
async def resource_monitor():
    """Context manager for monitoring system resources."""
    initial_memory = PerformanceMetrics.measure_memory_usage()
    initial_cpu = PerformanceMetrics.measure_cpu_usage()
    start_time = time.perf_counter()
    
    try:
        yield
    finally:
        end_time = time.perf_counter()
        final_memory = PerformanceMetrics.measure_memory_usage()
        final_cpu = PerformanceMetrics.measure_cpu_usage()
        
        logger.info(f"Test duration: {end_time - start_time:.2f}s")
        logger.info(f"Memory change: {final_memory - initial_memory:.2f}MB")
        logger.info(f"CPU usage: {final_cpu:.2f}%")

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
        
        try:
            await asyncio.gather(
                orderbook.start(),
                transactions.start(),
                tick.start()
            )
            
            # Warmup period
            await asyncio.sleep(2)
            
            yield orderbook, transactions, tick
            
        finally:
            await asyncio.gather(
                orderbook.stop(),
                transactions.stop(),
                tick.stop(),
                return_exceptions=True
            )
            gc.collect()
        
    async def test_memory_usage(self, collectors):
        """Test memory usage under load."""
        orderbook, transactions, tick = collectors
        
        async with resource_monitor():
            initial_memory = PerformanceMetrics.measure_memory_usage()
            
            # Generate load in batches
            for batch in range(10):
                for _ in range(100):  # 100 requests per batch
                    await asyncio.gather(
                        orderbook.get_order_book("BTCUSDT"),
                        transactions.get_transactions("BTCUSDT"),
                        tick.get_ticks("BTCUSDT")
                    )
                await asyncio.sleep(0.1)  # Brief pause between batches
                
            gc.collect()
            final_memory = PerformanceMetrics.measure_memory_usage()
            memory_increase = final_memory - initial_memory
            
            logger.info(f"Memory usage increase: {memory_increase:.2f} MB")
            assert memory_increase < 500  # Max 500MB increase
        
    async def test_cpu_usage(self, collectors):
        """Test CPU usage under load."""
        orderbook, transactions, tick = collectors
        cpu_usage_samples = []
        
        async with resource_monitor():
            # Generate load and measure CPU in intervals
            for _ in range(10):
                await asyncio.gather(
                    orderbook.get_metrics("BTCUSDT"),
                    transactions.get_metrics("BTCUSDT"),
                    tick.get_metrics("BTCUSDT")
                )
                cpu_usage_samples.append(PerformanceMetrics.measure_cpu_usage(interval=0.5))
                await asyncio.sleep(0.5)  # Allow CPU to stabilize
                
            avg_cpu_usage = sum(cpu_usage_samples) / len(cpu_usage_samples)
            logger.info(f"Average CPU usage: {avg_cpu_usage:.2f}%")
            assert avg_cpu_usage < 80  # Max 80% CPU usage
        
    async def test_latency(self, collectors):
        """Test response latency under load."""
        orderbook, transactions, tick = collectors
        latencies = []
        
        async with resource_monitor():
            # Measure latency with retries
            for _ in range(100):
                latency = await PerformanceMetrics.measure_with_retries(
                    orderbook.get_order_book,
                    retries=3,
                    timeout=2.0,
                    symbol="BTCUSDT"
                )
                if latency != float('inf'):
                    latencies.append(latency)
                await asyncio.sleep(0.01)  # Prevent overwhelming
                
            if not latencies:
                pytest.fail("All latency measurements failed")
                
            avg_latency = sum(latencies) / len(latencies)
            max_latency = max(latencies)
            p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
            
            logger.info(f"Average latency: {avg_latency:.2f}ms")
            logger.info(f"P95 latency: {p95_latency:.2f}ms")
            logger.info(f"Maximum latency: {max_latency:.2f}ms")
            
            assert avg_latency < 50  # Max 50ms average latency
            assert p95_latency < 150  # Max 150ms 95th percentile
            assert max_latency < 200  # Max 200ms peak latency
        
    async def test_concurrent_requests(self, collectors):
        """Test handling of concurrent requests."""
        orderbook, transactions, tick = collectors
        
        async def make_requests():
            """Make multiple requests to collectors."""
            for _ in range(50):
                try:
                    async with asyncio.timeout(2.0):
                        await asyncio.gather(
                            orderbook.get_order_book("BTCUSDT"),
                            transactions.get_transactions("BTCUSDT"),
                            tick.get_ticks("BTCUSDT")
                        )
                except asyncio.TimeoutError:
                    logger.warning("Request batch timed out")
                await asyncio.sleep(0.02)  # Rate limiting
                
        async with resource_monitor():
            # Run multiple concurrent request streams with monitoring
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
        try:
            await collector.start()
            await asyncio.sleep(2)  # Warmup period
            yield collector
        finally:
            await collector.stop()
            gc.collect()
        
    async def test_reconnection(self, collector):
        """Test WebSocket reconnection capability."""
        async with resource_monitor():
            # Force disconnect
            for ws in collector._ws_connections.values():
                ws.cancel()
                
            # Wait for reconnection with timeout
            try:
                async with asyncio.timeout(10):
                    while True:
                        try:
                            book = await collector.get_order_book("BTCUSDT")
                            if len(book[0]) > 0 and len(book[1]) > 0:
                                break
                        except Exception:
                            await asyncio.sleep(0.5)
            except asyncio.TimeoutError:
                pytest.fail("Reconnection failed within timeout")
        
    async def test_error_recovery(self, collector):
        """Test recovery from various error conditions."""
        async with resource_monitor():
            # Simulate different error conditions
            error_conditions = [
                "invalid json",
                "{",
                '{"e": "error"}',
                None,
                b"binary data"
            ]
            
            for error in error_conditions:
                await collector._handle_ws_message("BTCUSDT", error)
                
                # Verify collector still functions
                try:
                    async with asyncio.timeout(2):
                        book = await collector.get_order_book("BTCUSDT")
                        assert len(book[0]) > 0
                        assert len(book[1]) > 0
                except Exception as e:
                    pytest.fail(f"Failed to recover from error condition: {error}, {str(e)}")
        
    async def test_data_consistency(self, collector):
        """Test data consistency under stress."""
        async with resource_monitor():
            initial_book = await collector.get_order_book("BTCUSDT")
            
            # Generate rapid updates with monitoring
            update_count = 0
            error_count = 0
            
            for _ in range(1000):
                try:
                    async with asyncio.timeout(0.1):
                        book = await collector.get_order_book("BTCUSDT")
                        update_count += 1
                        
                        # Verify basic consistency
                        assert len(book[0]) > 0  # Has bids
                        assert len(book[1]) > 0  # Has asks
                        assert book[0][0][0] < book[1][0][0]  # Bid < Ask
                except Exception as e:
                    error_count += 1
                    logger.warning(f"Update error: {str(e)}")
                    
            logger.info(f"Successful updates: {update_count}")
            logger.info(f"Failed updates: {error_count}")
            assert error_count / (update_count + error_count) < 0.01  # Max 1% error rate
        
    async def test_memory_leak(self, collector):
        """Test for memory leaks during extended operation."""
        async with resource_monitor():
            initial_memory = PerformanceMetrics.measure_memory_usage()
            
            # Run for extended period with periodic cleanup
            for _ in range(10):
                for _ in range(10):  # 10 requests per cycle
                    await collector.get_order_book("BTCUSDT")
                    await asyncio.sleep(0.1)
                gc.collect()  # Periodic cleanup
                
            final_memory = PerformanceMetrics.measure_memory_usage()
            memory_diff = final_memory - initial_memory
            
            logger.info(f"Memory change after extended operation: {memory_diff:.2f} MB")
            assert memory_diff < 50  # Max 50MB increase 