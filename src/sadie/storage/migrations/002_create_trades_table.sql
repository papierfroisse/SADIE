-- Create trades table with TimescaleDB hypertable
CREATE TABLE IF NOT EXISTS trades (
    id BIGSERIAL PRIMARY KEY,
    trade_id BIGINT NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(50) NOT NULL,
    price DECIMAL(24, 8) NOT NULL,
    quantity DECIMAL(24, 8) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    buyer_order_id BIGINT NOT NULL,
    seller_order_id BIGINT NOT NULL,
    buyer_is_maker BOOLEAN NOT NULL,
    is_best_match BOOLEAN NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (exchange, trade_id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades (symbol);
CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_trades_exchange ON trades (exchange);
CREATE INDEX IF NOT EXISTS idx_trades_price ON trades (price);

-- Convert to TimescaleDB hypertable
SELECT create_hypertable('trades', 'timestamp', 
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- Add retention policy (90 days)
SELECT add_retention_policy('trades', 
    INTERVAL '90 days',
    if_not_exists => TRUE
);

-- Add compression policy (after 7 days)
SELECT add_compression_policy('trades', 
    INTERVAL '7 days',
    if_not_exists => TRUE
);

-- Create aggregated trades view
CREATE MATERIALIZED VIEW IF NOT EXISTS trades_1m AS
SELECT
    time_bucket('1 minute', timestamp) AS bucket,
    symbol,
    exchange,
    first(price, timestamp) AS open_price,
    max(price) AS high_price,
    min(price) AS low_price,
    last(price, timestamp) AS close_price,
    sum(quantity) AS volume,
    count(*) AS trade_count
FROM trades
GROUP BY bucket, symbol, exchange
WITH NO DATA;

-- Create indexes on the materialized view
CREATE INDEX IF NOT EXISTS idx_trades_1m_bucket ON trades_1m (bucket DESC);
CREATE INDEX IF NOT EXISTS idx_trades_1m_symbol ON trades_1m (symbol);
CREATE INDEX IF NOT EXISTS idx_trades_1m_exchange ON trades_1m (exchange);

-- Create continuous aggregate policy
SELECT add_continuous_aggregate_policy('trades_1m',
    start_offset => INTERVAL '1 day',
    end_offset => INTERVAL '1 minute',
    schedule_interval => INTERVAL '1 minute'
); 