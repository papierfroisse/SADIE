"""Configuration for performance tests."""

# Test durations in seconds
LOAD_TEST_DURATION = 60
STRESS_TEST_DURATION = 300
ENDURANCE_TEST_DURATION = 3600

# Request rates (transactions per second)
NORMAL_LOAD_TPS = 100
HIGH_LOAD_TPS = 1000
STRESS_TEST_TPS = 5000

# Memory thresholds in MB
MAX_MEMORY_INCREASE = {
    "orderbook": 200,
    "transactions": 100,
    "tick": 150
}

# CPU usage thresholds in percentage
MAX_CPU_USAGE = {
    "orderbook": 30,
    "transactions": 40,
    "tick": 50
}

# Latency thresholds in milliseconds
LATENCY_THRESHOLDS = {
    "orderbook": {
        "avg": 100,
        "p95": 200,
        "p99": 500,
        "max": 1000
    },
    "transactions": {
        "avg": 50,
        "p95": 100,
        "p99": 200,
        "max": 500
    },
    "tick": {
        "avg": 1,
        "p95": 2,
        "p99": 5,
        "max": 10
    }
}

# Success rate thresholds
MIN_SUCCESS_RATE = 0.99  # 99%
MAX_ERROR_RATE = 0.01    # 1%

# WebSocket configuration
WEBSOCKET_CONFIG = {
    "reconnect_timeout": 5,
    "max_reconnect_attempts": 3,
    "heartbeat_interval": 30
}

# Batch processing configuration
BATCH_CONFIG = {
    "size": 100,
    "timeout": 1.0,
    "max_queue_size": 10000
}

# Test symbols
TEST_SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "ADAUSDT",
    "DOGEUSDT"
]

# Resource monitoring intervals
MONITORING_CONFIG = {
    "memory_interval": 1.0,  # seconds
    "cpu_interval": 1.0,     # seconds
    "metrics_interval": 0.1   # seconds
}

# Performance test scenarios
TEST_SCENARIOS = {
    "normal_load": {
        "duration": LOAD_TEST_DURATION,
        "tps": NORMAL_LOAD_TPS,
        "symbols": TEST_SYMBOLS[:1]
    },
    "high_load": {
        "duration": LOAD_TEST_DURATION,
        "tps": HIGH_LOAD_TPS,
        "symbols": TEST_SYMBOLS[:3]
    },
    "stress_test": {
        "duration": STRESS_TEST_DURATION,
        "tps": STRESS_TEST_TPS,
        "symbols": TEST_SYMBOLS
    },
    "endurance_test": {
        "duration": ENDURANCE_TEST_DURATION,
        "tps": NORMAL_LOAD_TPS,
        "symbols": TEST_SYMBOLS[:2]
    }
}

# Reporting configuration
REPORTING_CONFIG = {
    "output_dir": "test_results",
    "save_metrics": True,
    "plot_graphs": True,
    "formats": ["json", "csv", "html"]
}

# Cleanup configuration
CLEANUP_CONFIG = {
    "gc_interval": 60,  # seconds
    "log_cleanup": True,
    "max_log_size": 100  # MB
} 