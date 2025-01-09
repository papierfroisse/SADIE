-- Create sentiment table with TimescaleDB hypertable
CREATE TABLE IF NOT EXISTS sentiment (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    tweet_id VARCHAR(50) NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    user_followers INTEGER NOT NULL,
    retweet_count INTEGER NOT NULL,
    favorite_count INTEGER NOT NULL,
    polarity DECIMAL(5, 4) NOT NULL,
    subjectivity DECIMAL(5, 4) NOT NULL,
    query VARCHAR(100) NOT NULL,
    source VARCHAR(50) DEFAULT 'twitter',
    collected_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (source, tweet_id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_sentiment_symbol ON sentiment (symbol);
CREATE INDEX IF NOT EXISTS idx_sentiment_created_at ON sentiment (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sentiment_polarity ON sentiment (polarity);
CREATE INDEX IF NOT EXISTS idx_sentiment_source ON sentiment (source);

-- Convert to TimescaleDB hypertable
SELECT create_hypertable('sentiment', 'created_at', 
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- Add retention policy (90 days)
SELECT add_retention_policy('sentiment', 
    INTERVAL '90 days',
    if_not_exists => TRUE
);

-- Add compression policy (after 7 days)
SELECT add_compression_policy('sentiment', 
    INTERVAL '7 days',
    if_not_exists => TRUE
);

-- Create aggregated sentiment view
CREATE MATERIALIZED VIEW IF NOT EXISTS sentiment_1h AS
SELECT
    time_bucket('1 hour', created_at) AS bucket,
    symbol,
    source,
    COUNT(*) AS message_count,
    AVG(polarity) AS avg_polarity,
    AVG(subjectivity) AS avg_subjectivity,
    SUM(user_followers) AS total_reach,
    SUM(retweet_count) AS total_retweets,
    SUM(favorite_count) AS total_favorites
FROM sentiment
GROUP BY bucket, symbol, source
WITH NO DATA;

-- Create indexes on the materialized view
CREATE INDEX IF NOT EXISTS idx_sentiment_1h_bucket ON sentiment_1h (bucket DESC);
CREATE INDEX IF NOT EXISTS idx_sentiment_1h_symbol ON sentiment_1h (symbol);
CREATE INDEX IF NOT EXISTS idx_sentiment_1h_source ON sentiment_1h (source);

-- Create continuous aggregate policy
SELECT add_continuous_aggregate_policy('sentiment_1h',
    start_offset => INTERVAL '1 day',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour'
); 