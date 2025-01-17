"""Prometheus metrics for SADIE."""
from prometheus_client import Counter, Gauge, Histogram

# Trade metrics
TRADES_PROCESSED = Counter(
    'sadie_trades_processed_total',
    'Total number of trades processed',
    ['exchange', 'symbol']
)

TRADE_PROCESSING_TIME = Histogram(
    'sadie_trade_processing_seconds',
    'Time spent processing trades',
    ['exchange', 'symbol'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0)
)

TRADE_BUFFER_SIZE = Gauge(
    'sadie_trade_buffer_size',
    'Current size of trade buffer',
    ['exchange', 'symbol']
)

# Cache metrics
CACHE_HITS = Counter(
    'sadie_cache_hits_total',
    'Total number of cache hits',
    ['type']
)

CACHE_MISSES = Counter(
    'sadie_cache_misses_total',
    'Total number of cache misses',
    ['type']
)

CACHE_SIZE = Gauge(
    'sadie_cache_size_bytes',
    'Current size of cache in bytes',
    ['type']
)

# Error metrics
ERRORS = Counter(
    'sadie_errors_total',
    'Total number of errors',
    ['type', 'exchange']
)

# Performance metrics
MEMORY_USAGE = Gauge(
    'sadie_memory_usage_bytes',
    'Current memory usage in bytes'
)

CPU_USAGE = Gauge(
    'sadie_cpu_usage_percent',
    'Current CPU usage percentage'
)

# Network metrics
NETWORK_LATENCY = Histogram(
    'sadie_network_latency_seconds',
    'Network latency for API calls',
    ['exchange', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

NETWORK_ERRORS = Counter(
    'sadie_network_errors_total',
    'Total number of network errors',
    ['exchange', 'type']
) 