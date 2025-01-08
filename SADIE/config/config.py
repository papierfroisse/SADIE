"""Configuration management for SADIE."""
import os
from pathlib import Path
from typing import Dict, List, Optional, Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models" / "saved"
CACHE_DIR = BASE_DIR / "cache"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
for directory in [DATA_DIR, MODELS_DIR, CACHE_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# API Configuration
API_KEYS = {
    "alpha_vantage": os.getenv("ALPHA_VANTAGE_API_KEY"),
    "binance": {
        "key": os.getenv("BINANCE_API_KEY"),
        "secret": os.getenv("BINANCE_API_SECRET")
    },
    "telegram": os.getenv("TELEGRAM_BOT_TOKEN")
}

# Database Configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "name": os.getenv("DB_NAME", "sadie_db"),
    "user": os.getenv("DB_USER", "sadie_user"),
    "password": os.getenv("DB_PASSWORD"),
    "timescaledb": bool(os.getenv("USE_TIMESCALEDB", True))
}

# Model Configuration
MODEL_CONFIG = {
    "save_path": os.getenv("MODEL_SAVE_PATH", str(MODELS_DIR)),
    "cache_dir": os.getenv("CACHE_DIR", str(CACHE_DIR)),
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "batch_size": int(os.getenv("BATCH_SIZE", 32)),
    "epochs": int(os.getenv("EPOCHS", 100)),
    "validation_split": float(os.getenv("VALIDATION_SPLIT", 0.2)),
    "sequence_length": int(os.getenv("SEQUENCE_LENGTH", 60)),
    "use_gpu": bool(os.getenv("USE_GPU", True))
}

# Data Collection Configuration
DATA_CONFIG = {
    "update_interval": int(os.getenv("UPDATE_INTERVAL", 300)),  # 5 minutes
    "max_retries": int(os.getenv("MAX_RETRIES", 3)),
    "timeout": int(os.getenv("REQUEST_TIMEOUT", 30)),
    "cache_expiry": int(os.getenv("CACHE_EXPIRY", 3600)),
    "symbols": os.getenv("SYMBOLS", "BTC,ETH,BNB").split(",")
}

# Web Interface Configuration
WEB_CONFIG = {
    "host": os.getenv("WEB_HOST", "0.0.0.0"),
    "port": int(os.getenv("WEB_PORT", 8000)),
    "debug": bool(os.getenv("WEB_DEBUG", False)),
    "secret_key": os.getenv("SECRET_KEY", "your-secret-key"),
    "cors_origins": os.getenv("CORS_ORIGINS", "*").split(",")
}

# Notification Configuration
NOTIFICATION_CONFIG = {
    "telegram_enabled": bool(os.getenv("TELEGRAM_ENABLED", False)),
    "email_enabled": bool(os.getenv("EMAIL_ENABLED", False)),
    "notification_interval": int(os.getenv("NOTIFICATION_INTERVAL", 3600)),
    "alert_thresholds": {
        "price_change": float(os.getenv("PRICE_CHANGE_THRESHOLD", 5.0)),
        "volume_change": float(os.getenv("VOLUME_CHANGE_THRESHOLD", 100.0))
    }
}

# Backtesting Configuration
BACKTEST_CONFIG = {
    "start_date": os.getenv("BACKTEST_START_DATE", "2020-01-01"),
    "end_date": os.getenv("BACKTEST_END_DATE", None),
    "initial_balance": float(os.getenv("INITIAL_BALANCE", 10000.0)),
    "commission_rate": float(os.getenv("COMMISSION_RATE", 0.001)),
    "use_leverage": bool(os.getenv("USE_LEVERAGE", False)),
    "max_leverage": float(os.getenv("MAX_LEVERAGE", 1.0))
}

# Security Configuration
SECURITY_CONFIG = {
    "jwt_secret": os.getenv("JWT_SECRET", "your-jwt-secret"),
    "jwt_algorithm": os.getenv("JWT_ALGORITHM", "HS256"),
    "jwt_expiration": int(os.getenv("JWT_EXPIRATION", 3600)),
    "rate_limit": int(os.getenv("RATE_LIMIT", 100)),
    "rate_limit_period": int(os.getenv("RATE_LIMIT_PERIOD", 3600))
}

# Logging Configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
        "file": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.FileHandler",
            "filename": str(LOGS_DIR / "sadie.log"),
            "mode": "a",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default", "file"],
            "level": "INFO",
            "propagate": True
        },
    }
} 