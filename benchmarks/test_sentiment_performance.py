"""Performance benchmarks for the Sentiment collector."""

import asyncio
from datetime import datetime, timedelta, timezone
import os
import time
from typing import Dict, List
import psutil
import pytest
from unittest.mock import patch

from sadie.data.collectors.sentiment import SentimentCollector
from sadie.storage.database import DatabaseManager


class PerformanceMetrics:
    """Class to track performance metrics during benchmarks."""
    
    def __init__(self):
        """Initialize performance metrics."""
        self.start_time = time.time()
        self.end_time = None
        self.total_tweets = 0
        self.total_batches = 0
        self.processing_times: List[float] = []
        self.batch_sizes: List[int] = []
        self.memory_samples: List[float] = []
        self.cpu_samples: List[float] = []
        self.db_write_times: List[float] = []
        self.errors: List[str] = []
    
    def record_processing_time(self, duration: float):
        """Record the time taken to process a batch of tweets."""
        self.processing_times.append(duration)
    
    def record_batch(self, size: int):
        """Record information about a processed batch."""
        self.total_batches += 1
        self.total_tweets += size
        self.batch_sizes.append(size)
    
    def record_db_write(self, duration: float):
        """Record the time taken to write to the database."""
        self.db_write_times.append(duration)
    
    def record_memory_usage(self):
        """Record current memory usage."""
        process = psutil.Process(os.getpid())
        self.memory_samples.append(process.memory_info().rss / 1024 / 1024)  # MB
    
    def record_cpu_usage(self):
        """Record current CPU usage."""
        process = psutil.Process(os.getpid())
        self.cpu_samples.append(process.cpu_percent())
    
    def record_error(self, error: str):
        """Record an error that occurred during benchmarking."""
        self.errors.append(error)
    
    def complete(self):
        """Mark the end of benchmark collection."""
        self.end_time = time.time()
    
    def get_summary(self) -> Dict:
        """Get a summary of the performance metrics."""
        if not self.end_time:
            self.complete()
        
        total_duration = self.end_time - self.start_time
        avg_processing_time = sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0
        avg_batch_size = sum(self.batch_sizes) / len(self.batch_sizes) if self.batch_sizes else 0
        avg_db_write_time = sum(self.db_write_times) / len(self.db_write_times) if self.db_write_times else 0
        tweets_per_second = self.total_tweets / total_duration if total_duration > 0 else 0
        
        return {
            "total_duration": total_duration,
            "total_tweets": self.total_tweets,
            "total_batches": self.total_batches,
            "tweets_per_second": tweets_per_second,
            "avg_processing_time": avg_processing_time,
            "avg_batch_size": avg_batch_size,
            "avg_db_write_time": avg_db_write_time,
            "peak_memory_mb": max(self.memory_samples) if self.memory_samples else 0,
            "avg_memory_mb": sum(self.memory_samples) / len(self.memory_samples) if self.memory_samples else 0,
            "peak_cpu_percent": max(self.cpu_samples) if self.cpu_samples else 0,
            "avg_cpu_percent": sum(self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0,
            "error_count": len(self.errors),
        }


class InstrumentedSentimentCollector(SentimentCollector):
    """SentimentCollector with performance instrumentation."""
    
    def __init__(self, *args, **kwargs):
        """Initialize the instrumented collector."""
        super().__init__(*args, **kwargs)
        self.metrics = PerformanceMetrics()
    
    async def _process_batches(self, force: bool = False):
        """Override batch processing to collect metrics."""
        start_time = time.time()
        try:
            await super()._process_batches(force)
            duration = time.time() - start_time
            self.metrics.record_processing_time(duration)
            
            # Record batch sizes
            for symbol, batch in self._tweet_batches.items():
                if batch:
                    self.metrics.record_batch(len(batch))
            
            # Record system metrics
            self.metrics.record_memory_usage()
            self.metrics.record_cpu_usage()
            
        except Exception as e:
            self.metrics.record_error(str(e))
            raise
    
    async def _store_batch(self, symbol: str, batch: List[Dict]):
        """Override batch storage to collect metrics."""
        start_time = time.time()
        try:
            await super()._store_batch(symbol, batch)
            duration = time.time() - start_time
            self.metrics.record_db_write(duration)
        except Exception as e:
            self.metrics.record_error(str(e))
            raise


async def run_benchmark(collector: InstrumentedSentimentCollector, duration: float = 60.0):
    """Run a benchmark for the specified duration."""
    await collector.start()
    await asyncio.sleep(duration)
    await collector.stop()
    collector.metrics.complete()
    return collector.metrics.get_summary()


@pytest.fixture
async def db_manager():
    """Create a database manager for benchmarking."""
    manager = DatabaseManager(
        host=os.getenv("TEST_DB_HOST", "localhost"),
        port=int(os.getenv("TEST_DB_PORT", "5432")),
        database=os.getenv("TEST_DB_NAME", "sadie_test"),
        user=os.getenv("TEST_DB_USER", "postgres"),
        password=os.getenv("TEST_DB_PASSWORD", "postgres"),
    )
    await manager.connect()
    yield manager
    await manager.disconnect()


def generate_mock_tweets(count: int) -> List:
    """Generate a list of mock tweets for testing."""
    tweets = []
    for i in range(count):
        tweet = type("Tweet", (), {})()
        tweet.id_str = f"tweet_{i}"
        tweet.full_text = f"Tweet {i} about Bitcoin {'!' * (i % 5)}"
        tweet.created_at = datetime.now(timezone.utc)
        tweet.user = type("User", (), {})()
        tweet.user.id_str = f"user_{i}"
        tweet.user.followers_count = 1000 + i
        tweet.retweet_count = 50 + i
        tweet.favorite_count = 100 + i
        tweets.append(tweet)
    return tweets


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_single_symbol_performance(db_manager):
    """Benchmark performance for a single symbol."""
    collector = InstrumentedSentimentCollector(
        db_manager=db_manager,
        symbols=["BTCUSDT"],
        twitter_api_key="test_key",
        twitter_api_secret="test_secret",
        twitter_access_token="test_token",
        twitter_access_secret="test_token_secret",
        batch_size=100,
        batch_interval=1.0,
    )
    
    # Mock Twitter API to return controlled data
    mock_tweets = generate_mock_tweets(500)
    with patch("tweepy.API") as mock_api_class:
        mock_api = mock_api_class.return_value
        mock_api.search_tweets.return_value = mock_tweets
        
        # Run benchmark
        results = await run_benchmark(collector, duration=30.0)
        
        # Print results
        print("\nSingle Symbol Performance Results:")
        for key, value in results.items():
            print(f"{key}: {value}")
        
        # Verify performance meets requirements
        assert results["tweets_per_second"] >= 10.0  # Minimum tweets per second
        assert results["avg_processing_time"] <= 0.1  # Maximum average processing time
        assert results["error_count"] == 0  # No errors allowed


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_multiple_symbols_performance(db_manager):
    """Benchmark performance for multiple symbols."""
    collector = InstrumentedSentimentCollector(
        db_manager=db_manager,
        symbols=["BTCUSDT", "ETHUSDT", "BNBUSDT"],
        twitter_api_key="test_key",
        twitter_api_secret="test_secret",
        twitter_access_token="test_token",
        twitter_access_secret="test_token_secret",
        batch_size=100,
        batch_interval=1.0,
    )
    
    # Mock Twitter API to return different data for different symbols
    mock_tweets = {
        "BTCUSDT": generate_mock_tweets(200),
        "ETHUSDT": generate_mock_tweets(200),
        "BNBUSDT": generate_mock_tweets(200),
    }
    
    with patch("tweepy.API") as mock_api_class:
        mock_api = mock_api_class.return_value
        mock_api.search_tweets.side_effect = lambda q, *args, **kwargs: mock_tweets[
            next(s for s in collector._symbols if s in q)
        ]
        
        # Run benchmark
        results = await run_benchmark(collector, duration=30.0)
        
        # Print results
        print("\nMultiple Symbols Performance Results:")
        for key, value in results.items():
            print(f"{key}: {value}")
        
        # Verify performance meets requirements
        assert results["tweets_per_second"] >= 30.0  # Minimum tweets per second (10 per symbol)
        assert results["avg_processing_time"] <= 0.2  # Maximum average processing time
        assert results["error_count"] == 0  # No errors allowed


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_high_frequency_performance(db_manager):
    """Benchmark performance under high-frequency data collection."""
    collector = InstrumentedSentimentCollector(
        db_manager=db_manager,
        symbols=["BTCUSDT"],
        twitter_api_key="test_key",
        twitter_api_secret="test_secret",
        twitter_access_token="test_token",
        twitter_access_secret="test_token_secret",
        batch_size=1000,
        batch_interval=0.1,  # Very short interval
    )
    
    # Generate a large number of mock tweets
    mock_tweets = generate_mock_tweets(2000)
    
    with patch("tweepy.API") as mock_api_class:
        mock_api = mock_api_class.return_value
        mock_api.search_tweets.return_value = mock_tweets
        
        # Run benchmark
        results = await run_benchmark(collector, duration=30.0)
        
        # Print results
        print("\nHigh Frequency Performance Results:")
        for key, value in results.items():
            print(f"{key}: {value}")
        
        # Verify performance meets requirements
        assert results["tweets_per_second"] >= 50.0  # High throughput requirement
        assert results["avg_processing_time"] <= 0.05  # Very low latency requirement
        assert results["error_count"] == 0  # No errors allowed
        assert results["peak_memory_mb"] <= 512  # Maximum memory usage


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_memory_usage(db_manager):
    """Benchmark memory usage over time."""
    collector = InstrumentedSentimentCollector(
        db_manager=db_manager,
        symbols=["BTCUSDT"],
        twitter_api_key="test_key",
        twitter_api_secret="test_secret",
        twitter_access_token="test_token",
        twitter_access_secret="test_token_secret",
        batch_size=100,
        batch_interval=1.0,
    )
    
    # Generate tweets with increasing memory footprint
    mock_tweets = []
    for i in range(1000):
        tweet = type("Tweet", (), {})()
        tweet.id_str = f"tweet_{i}"
        tweet.full_text = f"Tweet {i} about Bitcoin " + "!" * (i % 100)  # Varying text size
        tweet.created_at = datetime.now(timezone.utc)
        tweet.user = type("User", (), {})()
        tweet.user.id_str = f"user_{i}"
        tweet.user.followers_count = 1000 + i
        tweet.retweet_count = 50 + i
        tweet.favorite_count = 100 + i
        mock_tweets.append(tweet)
    
    with patch("tweepy.API") as mock_api_class:
        mock_api = mock_api_class.return_value
        mock_api.search_tweets.return_value = mock_tweets
        
        # Run benchmark
        results = await run_benchmark(collector, duration=60.0)
        
        # Print results
        print("\nMemory Usage Results:")
        for key, value in results.items():
            print(f"{key}: {value}")
        
        # Verify memory usage meets requirements
        assert results["peak_memory_mb"] <= 256  # Maximum memory usage
        assert results["avg_memory_mb"] <= 128  # Average memory usage
        assert results["error_count"] == 0  # No errors allowed 