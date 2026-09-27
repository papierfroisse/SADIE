"""Tests for the Sentiment collector."""

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import tweepy
from textblob import TextBlob

from sadie.data.collectors.sentiment import SentimentCollector
from sadie.storage.database import DatabaseManager


@pytest.fixture
def db_manager():
    """Create a mock database manager."""
    manager = AsyncMock(spec=DatabaseManager)
    manager.insert_sentiment = AsyncMock()
    return manager


@pytest.fixture
def mock_twitter_api():
    """Create a mock Twitter API."""
    api = MagicMock(spec=tweepy.API)
    return api


@pytest.fixture
def mock_tweet():
    """Create a mock tweet."""
    tweet = MagicMock()
    tweet.id_str = "123456789"
    tweet.full_text = "Bitcoin is looking very bullish today! #BTC"
    tweet.created_at = datetime.now(timezone.utc)
    tweet.user = MagicMock()
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
        twitter_api_key="test_key",
        twitter_api_secret="test_secret",
        twitter_access_token="test_token",
        twitter_access_secret="test_token_secret",
        batch_size=10,
        batch_interval=1.0,
    )
    yield collector
    await collector.stop()


@pytest.mark.asyncio
async def test_initialization(collector):
    """Test collector initialization."""
    assert collector._symbols == ["BTCUSDT", "ETHUSDT"]
    assert collector._batch_size == 10
    assert collector._batch_interval == 1.0
    assert collector._tweet_batches == {}
    assert collector._last_batch_time == {}
    assert collector._processed_tweets == set()


@pytest.mark.asyncio
async def test_build_search_queries(collector):
    """Test search query building."""
    queries = collector._build_search_queries()
    
    assert "BTCUSDT" in queries
    assert "ETHUSDT" in queries
    
    btc_queries = queries["BTCUSDT"]
    assert "#BTC" in btc_queries
    assert "#BTCUSD" in btc_queries
    assert "#BTCUSDT" in btc_queries
    assert "#BTCTrading" in btc_queries
    assert "#BTCPrice" in btc_queries
    assert "BTC" in btc_queries


@pytest.mark.asyncio
async def test_collect_and_store(
    collector,
    mock_twitter_api,
    mock_tweet,
    db_manager,
):
    """Test collecting and storing sentiment data."""
    # Mock Twitter API
    with patch("tweepy.API") as mock_api_class:
        mock_api_class.return_value = mock_twitter_api
        mock_twitter_api.search_tweets.return_value = [mock_tweet]
        
        # Initialize collector
        await collector._initialize()
        
        # Collect data for one symbol
        await collector._collect_symbol_sentiment("BTCUSDT")
        
        # Force batch processing
        await collector._process_batches(force=True)
        
        # Verify data was stored
        db_manager.insert_sentiment.assert_called()
        call_args = db_manager.insert_sentiment.call_args_list[0][1]
        assert len(call_args["sentiment_data"]) == 1
        
        record = call_args["sentiment_data"][0]
        assert record["symbol"] == "BTCUSDT"
        assert record["tweet_id"] == mock_tweet.id_str
        assert record["text"] == mock_tweet.full_text
        assert record["created_at"] == mock_tweet.created_at
        assert record["user_id"] == mock_tweet.user.id_str
        assert record["user_followers"] == mock_tweet.user.followers_count
        assert record["retweet_count"] == mock_tweet.retweet_count
        assert record["favorite_count"] == mock_tweet.favorite_count
        assert isinstance(record["polarity"], float)
        assert isinstance(record["subjectivity"], float)


@pytest.mark.asyncio
async def test_batch_processing(collector, db_manager, mock_tweet):
    """Test batch processing logic."""
    symbol = "BTCUSDT"
    collector._tweet_batches[symbol] = []
    collector._last_batch_time[symbol] = datetime.utcnow()
    
    # Add tweets to fill a batch
    for i in range(collector._batch_size + 5):  # Add more than batch size
        sentiment = TextBlob(mock_tweet.full_text)
        record = {
            "symbol": symbol,
            "tweet_id": f"{mock_tweet.id_str}_{i}",
            "text": mock_tweet.full_text,
            "created_at": mock_tweet.created_at,
            "user_id": mock_tweet.user.id_str,
            "user_followers": mock_tweet.user.followers_count,
            "retweet_count": mock_tweet.retweet_count,
            "favorite_count": mock_tweet.favorite_count,
            "polarity": sentiment.sentiment.polarity,
            "subjectivity": sentiment.sentiment.subjectivity,
            "query": "#BTC",
        }
        collector._tweet_batches[symbol].append(record)
    
    # Process batches
    await collector._process_batches()
    
    # Verify a full batch was stored
    db_manager.insert_sentiment.assert_called()
    call_args = db_manager.insert_sentiment.call_args_list[0][1]
    assert len(call_args["sentiment_data"]) == collector._batch_size
    
    # Verify remaining tweets are still in the batch
    assert len(collector._tweet_batches[symbol]) == 5


@pytest.mark.asyncio
async def test_duplicate_tweet_handling(
    collector,
    mock_twitter_api,
    mock_tweet,
    db_manager,
):
    """Test handling of duplicate tweets."""
    # Mock Twitter API
    with patch("tweepy.API") as mock_api_class:
        mock_api_class.return_value = mock_twitter_api
        mock_twitter_api.search_tweets.return_value = [mock_tweet, mock_tweet]  # Same tweet twice
        
        # Initialize collector
        await collector._initialize()
        
        # Collect data
        await collector._collect_symbol_sentiment("BTCUSDT")
        await collector._process_batches(force=True)
        
        # Verify only one tweet was stored
        db_manager.insert_sentiment.assert_called()
        call_args = db_manager.insert_sentiment.call_args_list[0][1]
        assert len(call_args["sentiment_data"]) == 1
        assert mock_tweet.id_str in collector._processed_tweets


@pytest.mark.asyncio
async def test_error_handling(collector, mock_twitter_api, db_manager):
    """Test error handling during collection."""
    # Mock Twitter API error
    with patch("tweepy.API") as mock_api_class:
        mock_api_class.return_value = mock_twitter_api
        mock_twitter_api.search_tweets.side_effect = tweepy.TweepError("Rate limit exceeded")
        
        # Initialize collector
        await collector._initialize()
        
        # Collect data (should handle error gracefully)
        await collector._collect_symbol_sentiment("BTCUSDT")
        
        # Verify no data was stored
        db_manager.insert_sentiment.assert_not_called()


@pytest.mark.asyncio
async def test_cleanup(collector, db_manager, mock_tweet):
    """Test cleanup process."""
    symbol = "BTCUSDT"
    
    # Add some tweets to the batch
    sentiment = TextBlob(mock_tweet.full_text)
    record = {
        "symbol": symbol,
        "tweet_id": mock_tweet.id_str,
        "text": mock_tweet.full_text,
        "created_at": mock_tweet.created_at,
        "user_id": mock_tweet.user.id_str,
        "user_followers": mock_tweet.user.followers_count,
        "retweet_count": mock_tweet.retweet_count,
        "favorite_count": mock_tweet.favorite_count,
        "polarity": sentiment.sentiment.polarity,
        "subjectivity": sentiment.sentiment.subjectivity,
        "query": "#BTC",
    }
    collector._tweet_batches[symbol] = [record]
    
    # Perform cleanup
    await collector._cleanup()
    
    # Verify remaining data was stored
    db_manager.insert_sentiment.assert_called()
    assert collector._tweet_batches[symbol] == [] 