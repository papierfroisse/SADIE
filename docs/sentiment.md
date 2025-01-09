# Sentiment Analysis Components

## Overview

The sentiment analysis components of the SADIE (Systematic Analysis of Digital Investment Environments) project provide tools for collecting, analyzing, and visualizing sentiment data from social media platforms, specifically Twitter, for cryptocurrency trading pairs.

## Features

- Real-time sentiment data collection from Twitter
- Natural language processing for sentiment analysis
- Batch processing for efficient data handling
- Time series analysis and visualization
- User influence weighting
- Configurable data retention and aggregation
- Real-time visualization dashboard
- Performance monitoring and metrics collection

## Installation

### Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher with TimescaleDB extension
- Twitter API credentials

### Dependencies

Install the required dependencies:

```bash
pip install -r requirements/sentiment.txt
```

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Twitter API credentials
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret

# Database configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sadie
DB_USER=postgres
DB_PASSWORD=postgres
```

## Usage

### Data Collection

Start collecting sentiment data:

```python
from sadie.data.collectors.sentiment import SentimentCollector
from sadie.storage.database import DatabaseManager

# Initialize database manager
db_manager = DatabaseManager(
    host="localhost",
    port=5432,
    database="sadie",
    user="postgres",
    password="postgres",
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
```

### Data Analysis

Analyze collected sentiment data:

```python
from sadie.data.collectors.sentiment import (
    analyze_sentiment_distribution,
    analyze_temporal_patterns,
    analyze_user_influence,
)

# Fetch data
data = await db_manager.get_sentiment(
    symbol="BTCUSDT",
    start_time=datetime.now() - timedelta(days=7),
    end_time=datetime.now(),
)

# Analyze distribution
dist = analyze_sentiment_distribution(data)
print("Sentiment Distribution:")
print(f"Mean polarity: {dist['polarity']['mean']:.3f}")
print(f"Mean subjectivity: {dist['subjectivity']['mean']:.3f}")

# Analyze temporal patterns
temporal_df = analyze_temporal_patterns(data)
print("\nTemporal Analysis:")
print(f"Average daily tweet volume: {temporal_df['volume'].mean():.1f}")

# Analyze user influence
user_df = analyze_user_influence(data)
print("\nTop Influencers:")
print(user_df.head())
```

### Visualization

Run the visualization dashboard:

```python
from sadie.data.collectors.sentiment import SentimentDashboard

# Create and run dashboard
dashboard = SentimentDashboard(
    db_manager=db_manager,
    symbols=["BTCUSDT", "ETHUSDT", "BNBUSDT"],
    update_interval=5.0,
    lookback_hours=24,
)

dashboard.run()
```

## Configuration

### Collector Configuration

The `SentimentCollector` can be configured with the following parameters:

- `symbols`: List of trading pairs to monitor
- `batch_size`: Number of tweets per batch (default: 100)
- `batch_interval`: Seconds between batch processing (default: 1.0)
- `lookback_hours`: Hours of historical tweets to fetch (default: 24)

### Database Configuration

The sentiment data is stored in a TimescaleDB table with the following schema:

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
```

### Performance Configuration

Performance settings can be adjusted in `sentiment_config.py`:

```python
# Memory management
MEMORY_LIMIT_MB = 256
MEMORY_CHECK_INTERVAL = 60  # seconds
CLEANUP_THRESHOLD = 0.9  # 90% of memory limit

# Batch processing
DB_BATCH_SIZE = 1000
DB_MAX_RETRIES = 3
DB_RETRY_DELAY = 1.0  # seconds
DB_TIMEOUT = 10.0  # seconds
```

## Monitoring

### Metrics Collection

The collector includes built-in metrics collection:

```python
# Get metrics summary
metrics = collector.metrics_collector.get_metrics_summary()

print("Performance Metrics:")
print(f"Tweets per second: {metrics['performance']['tweets_per_second']}")
print(f"Memory usage: {metrics['performance']['memory_usage']} MB")
print(f"Error count: {metrics['errors']['error_count']}")
```

### Logging

Logs are written to `logs/sentiment_collector.log` with configurable levels:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
```

## Development

### Running Tests

Run the test suite:

```bash
pytest tests/test_sentiment_collector.py
pytest tests/integration/test_sentiment_integration.py
pytest benchmarks/test_sentiment_performance.py
```

### Code Style

Format code using Black:

```bash
black src/sadie/data/collectors/
```

Run linters:

```bash
flake8 src/sadie/data/collectors/
mypy src/sadie/data/collectors/
```

## Documentation

Generate documentation:

```bash
cd docs
make html
```

View the documentation at `docs/_build/html/index.html`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linters
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- TextBlob for sentiment analysis
- Tweepy for Twitter API integration
- Dash and Plotly for visualization
- TimescaleDB for time series data storage 