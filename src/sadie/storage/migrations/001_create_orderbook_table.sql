-- Create order book table with TimescaleDB hypertable
CREATE TABLE IF NOT EXISTS order_books (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    exchange VARCHAR(50) NOT NULL,
    depth_level VARCHAR(2) NOT NULL,
    bids JSONB NOT NULL,
    asks JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_order_books_symbol ON order_books (symbol);
CREATE INDEX IF NOT EXISTS idx_order_books_timestamp ON order_books (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_order_books_exchange ON order_books (exchange);

-- Convert to TimescaleDB hypertable
SELECT create_hypertable('order_books', 'timestamp', 
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- Add retention policy (90 days)
SELECT add_retention_policy('order_books', 
    INTERVAL '90 days',
    if_not_exists => TRUE
);

-- Add compression policy (after 7 days)
SELECT add_compression_policy('order_books', 
    INTERVAL '7 days',
    if_not_exists => TRUE
); 