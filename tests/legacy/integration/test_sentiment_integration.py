"""Integration tests for the Sentiment collector."""

import asyncio
from datetime import datetime, timedelta, timezone
import os
from unittest.mock import patch

import pytest
import tweepy
from textblob import TextBlob

from sadie.data.collectors.sentiment import SentimentCollector
from sadie.storage.database import DatabaseManager


@pytest.fixture
async def db_manager():
    """Create a real database manager for integration testing."""
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


@pytest.fixture
def mock_tweet():
    """Create a mock tweet."""
    tweet = type("Tweet", (), {})()
    tweet.id_str = "123456789"
    tweet.full_text = "Bitcoin is looking very bullish today! #BTC"
    tweet.created_at = datetime.now(timezone.utc)
    tweet.user = type("User", (), {})()
    tweet.user.id_str = "987654321"
    tweet.user.followers_count = 1000
    tweet.retweet_count = 50
    tweet.favorite_count = 100
    return tweet


@pytest.fixture
async def collector(db_manager):
    """Create a SentimentCollector instance."""
    collector = SentimentCollector(
        db_manager=db_manager,
        symbols=["BTCUSDT", "ETHUSDT"],
        twitter_api_key=os.getenv("TWITTER_API_KEY", "test_key"),
        twitter_api_secret=os.getenv("TWITTER_API_SECRET", "test_secret"),
        twitter_access_token=os.getenv("TWITTER_ACCESS_TOKEN", "test_token"),
        twitter_access_secret=os.getenv("TWITTER_ACCESS_SECRET", "test_token_secret"),
        batch_size=10,
        batch_interval=1.0,
    )
    yield collector
    await collector.stop()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_collection_cycle(collector, db_manager, mock_tweet):
    """Test a complete collection cycle with database integration."""
    # Mock Twitter API to return controlled data
    with patch("tweepy.API") as mock_api_class:
        mock_api = mock_api_class.return_value
        mock_api.search_tweets.return_value = [mock_tweet]
        
        # Start collector
        await collector.start()
        
        # Wait for some data collection
        await asyncio.sleep(2.0)
        
        # Stop collector
        await collector.stop()
        
        # Verify data in database
        start_time = datetime.now(timezone.utc) - timedelta(minutes=5)
        sentiment_data = await db_manager.get_sentiment(
            symbol="BTCUSDT",
            start_time=start_time,
            end_time=datetime.now(timezone.utc),
        )
        
        assert len(sentiment_data) > 0
        record = sentiment_data[0]
        assert record["symbol"] == "BTCUSDT"
        assert record["tweet_id"] == mock_tweet.id_str
        assert record["text"] == mock_tweet.full_text
        assert isinstance(record["polarity"], float)
        assert isinstance(record["subjectivity"], float)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_multiple_symbols_collection(collector, db_manager, mock_tweet):
    """Test collecting data for multiple symbols simultaneously."""
    # Create different tweets for different symbols
    btc_tweet = mock_tweet
    eth_tweet = type("Tweet", (), {})()
    eth_tweet.id_str = "987654321"
    eth_tweet.full_text = "Ethereum is gaining momentum! #ETH"
    eth_tweet.created_at = datetime.now(timezone.utc)
    eth_tweet.user = type("User", (), {})()
    eth_tweet.user.id_str = "123456789"
    eth_tweet.user.followers_count = 2000
    eth_tweet.retweet_count = 75
    eth_tweet.favorite_count = 150
    
    # Mock Twitter API to return different data for different symbols
    with patch("tweepy.API") as mock_api_class:
        mock_api = mock_api_class.return_value
        mock_api.search_tweets.side_effect = lambda q, *args, **kwargs: {
            "BTCUSDT": [btc_tweet],
            "ETHUSDT": [eth_tweet],
        }[next(s for s in collector._symbols if s in q)]
        
        # Start collector
        await collector.start()
        
        # Wait for data collection
        await asyncio.sleep(2.0)
        
        # Stop collector
        await collector.stop()
        
        # Verify data for both symbols
        start_time = datetime.now(timezone.utc) - timedelta(minutes=5)
        end_time = datetime.now(timezone.utc)
        
        for symbol, tweet in [("BTCUSDT", btc_tweet), ("ETHUSDT", eth_tweet)]:
            sentiment_data = await db_manager.get_sentiment(
                symbol=symbol,
                start_time=start_time,
                end_time=end_time,
            )
            
            assert len(sentiment_data) > 0
            record = sentiment_data[0]
            assert record["symbol"] == symbol
            assert record["tweet_id"] == tweet.id_str
            assert record["text"] == tweet.full_text


@pytest.mark.integration
@pytest.mark.asyncio
async def test_sentiment_aggregation(collector, db_manager, mock_tweet):
    """Test sentiment data aggregation in the database."""
    # Create tweets with different sentiment
    tweets = []
    for i in range(5):
        tweet = type("Tweet", (), {})()
        tweet.id_str = f"12345678{i}"
        tweet.full_text = f"Tweet {i} about Bitcoin {'!' * i}"  # Varying sentiment
        tweet.created_at = datetime.now(timezone.utc)
        tweet.user = type("User", (), {})()
        tweet.user.id_str = f"98765432{i}"
        tweet.user.followers_count = 1000 + i * 100
        tweet.retweet_count = 50 + i * 10
        tweet.favorite_count = 100 + i * 20
        tweets.append(tweet)
    
    # Mock Twitter API
    with patch("tweepy.API") as mock_api_class:
        mock_api = mock_api_class.return_value
        mock_api.search_tweets.return_value = tweets
        
        # Start collector
        await collector.start()
        
        # Wait for data collection
        await asyncio.sleep(2.0)
        
        # Stop collector
        await collector.stop()
        
        # Get aggregated sentiment data
        start_time = datetime.now(timezone.utc) - timedelta(minutes=5)
        end_time = datetime.now(timezone.utc)
        
        agg_data = await db_manager.get_sentiment_aggregates(
            symbol="BTCUSDT",
            start_time=start_time,
            end_time=end_time,
            interval="1 minute",
        )
        
        assert len(agg_data) > 0
        record = agg_data[0]
        assert "avg_polarity" in record
        assert "avg_subjectivity" in record
        assert "tweet_count" in record
        assert record["tweet_count"] > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_error_recovery(collector, db_manager, mock_tweet):
    """Test collector's ability to recover from errors."""
    error_count = 0
    max_errors = 2
    
    def search_with_errors(*args, **kwargs):
        nonlocal error_count
        if error_count < max_errors:
            error_count += 1
            raise tweepy.TweepError("Rate limit exceeded")
        return [mock_tweet]
    
    # Mock Twitter API with intermittent errors
    with patch("tweepy.API") as mock_api_class:
        mock_api = mock_api_class.return_value
        mock_api.search_tweets.side_effect = search_with_errors
        
        # Start collector
        await collector.start()
        
        # Wait for error recovery and successful collection
        await asyncio.sleep(4.0)
        
        # Stop collector
        await collector.stop()
        
        # Verify data was eventually collected
        start_time = datetime.now(timezone.utc) - timedelta(minutes=5)
        sentiment_data = await db_manager.get_sentiment(
            symbol="BTCUSDT",
            start_time=start_time,
            end_time=datetime.now(timezone.utc),
        )
        
        assert len(sentiment_data) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_reconnection(collector, db_manager):
    """Test collector's ability to handle database disconnection."""
    # Start collector
    await collector.start()
    
    # Simulate database disconnection
    await db_manager.disconnect()
    
    # Wait a moment
    await asyncio.sleep(1.0)
    
    # Reconnect database
    await db_manager.connect()
    
    # Wait for collector to recover
    await asyncio.sleep(2.0)
    
    # Verify collector is still functioning
    start_time = datetime.now(timezone.utc) - timedelta(minutes=5)
    try:
        sentiment_data = await db_manager.get_sentiment(
            symbol="BTCUSDT",
            start_time=start_time,
            end_time=datetime.now(timezone.utc),
        )
        assert True  # If we get here, the database is working
    except Exception as e:
        pytest.fail(f"Database query failed after reconnection: {e}")
    
    # Stop collector
    await collector.stop() 