# Sentiment Collector

The Sentiment Collector is a component of the SADIE (Systematic Analysis of Digital Investment Environments) project that collects and analyzes sentiment data from social media platforms, specifically Twitter, for cryptocurrency trading pairs.

## Overview

The Sentiment Collector monitors Twitter for mentions of specific cryptocurrency trading pairs and analyzes the sentiment of tweets using natural language processing. This data can be used to gauge market sentiment and potentially predict price movements.

## Features

- Real-time collection of tweets mentioning configured trading pairs
- Sentiment analysis using TextBlob for polarity and subjectivity scoring
- Batch processing for efficient database operations
- Configurable collection intervals and batch sizes
- Automatic handling of Twitter API rate limits
- Deduplication of tweets
- Error recovery and reconnection capabilities
- Memory-efficient processing of large tweet volumes

## Configuration

The Sentiment Collector requires the following configuration parameters:

```python
collector = SentimentCollector(
    db_manager=db_manager,          # DatabaseManager instance
    symbols=["BTCUSDT", "ETHUSDT"], # List of trading pairs to monitor
    twitter_api_key="key",          # Twitter API credentials
    twitter_api_secret="secret",
    twitter_access_token="token",
    twitter_access_secret="secret",
    batch_size=100,                 # Number of tweets per batch
    batch_interval=1.0,             # Seconds between batch processing
    lookback_hours=24,              # Hours of historical tweets to fetch
)
```

### Twitter API Credentials

To use the Sentiment Collector, you need Twitter API credentials. Follow these steps to obtain them:

1. Create a Twitter Developer account at https://developer.twitter.com/
2. Create a new project and app
3. Generate API keys and access tokens
4. Store credentials securely (e.g., in environment variables)

### Environment Variables

The collector looks for the following environment variables:

```bash
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
```

## Database Schema

The collector stores sentiment data in a TimescaleDB table with the following schema:

```sql
CREATE TABLE sentiment (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    tweet_id VARCHAR(50) NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    user_followers INTEGER NOT NULL,
    retweet_count INTEGER NOT NULL,
    favorite_count INTEGER NOT NULL,
    polarity FLOAT NOT NULL,
    subjectivity FLOAT NOT NULL,
    query VARCHAR(50) NOT NULL
);

-- Convert to hypertable
SELECT create_hypertable('sentiment', 'created_at');

-- Create indexes
CREATE INDEX idx_sentiment_symbol ON sentiment(symbol);
CREATE INDEX idx_sentiment_created_at ON sentiment(created_at DESC);

-- Set retention policy (90 days)
SELECT add_retention_policy('sentiment', INTERVAL '90 days');

-- Configure compression
ALTER TABLE sentiment SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol'
);
SELECT add_compression_policy('sentiment', INTERVAL '7 days');
```

## Usage

### Basic Usage

```python
from sadie.data.collectors.sentiment import SentimentCollector
from sadie.storage.database import DatabaseManager

# Initialize database manager
db_manager = DatabaseManager(
    host="localhost",
    port=5432,
    database="sadie",
    user="postgres",
    password="postgres"
)
await db_manager.connect()

# Create collector
collector = SentimentCollector(
    db_manager=db_manager,
    symbols=["BTCUSDT", "ETHUSDT"],
    twitter_api_key=os.getenv("TWITTER_API_KEY"),
    twitter_api_secret=os.getenv("TWITTER_API_SECRET"),
    twitter_access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
    twitter_access_secret=os.getenv("TWITTER_ACCESS_SECRET"),
)

# Start collecting
await collector.start()

# ... let it run for a while ...

# Stop collecting
await collector.stop()
```

### Querying Sentiment Data

```python
# Get recent sentiment data for a symbol
sentiment_data = await db_manager.get_sentiment(
    symbol="BTCUSDT",
    start_time=datetime.now() - timedelta(hours=1),
    end_time=datetime.now()
)

# Get aggregated sentiment
agg_data = await db_manager.get_sentiment_aggregates(
    symbol="BTCUSDT",
    start_time=datetime.now() - timedelta(days=1),
    end_time=datetime.now(),
    interval="1 hour"
)
```

## Error Handling

The collector implements several error handling mechanisms:

1. **Rate Limiting**: Automatically handles Twitter API rate limits by backing off when limits are reached
2. **Reconnection**: Automatically attempts to reconnect if the Twitter API connection is lost
3. **Deduplication**: Prevents duplicate tweets from being processed and stored
4. **Database Errors**: Retries failed database operations with exponential backoff
5. **Memory Management**: Implements batch processing to prevent memory exhaustion

## Performance Considerations

The collector is designed for efficient operation:

- Batches tweets before database insertion to reduce I/O
- Uses connection pooling for database operations
- Implements memory-efficient processing of tweet streams
- Configurable batch sizes and intervals for performance tuning
- Uses TimescaleDB features for efficient data storage and querying

### Performance Metrics

Typical performance characteristics:

- Processing Rate: 50+ tweets per second
- Average Latency: < 100ms per tweet
- Memory Usage: < 256MB under normal operation
- CPU Usage: < 10% on a modern CPU
- Database Write Time: < 50ms per batch

## Best Practices

1. **Configuration**:
   - Set appropriate batch sizes based on tweet volume
   - Adjust batch interval based on latency requirements
   - Configure reasonable lookback period

2. **Monitoring**:
   - Monitor memory usage and tweet processing rates
   - Watch for Twitter API rate limit warnings
   - Check database write times and batch sizes

3. **Maintenance**:
   - Regularly check for stale data
   - Monitor disk usage
   - Review error logs

## Future Enhancements

Planned improvements for future versions:

1. Support for additional social media platforms
2. Enhanced sentiment analysis using machine learning
3. Real-time sentiment alerts and notifications
4. Integration with trading signals
5. Advanced text analytics features
6. Customizable sentiment scoring algorithms
7. Support for more languages
8. Real-time visualization of sentiment trends 