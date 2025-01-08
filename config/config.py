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
    }
}

# Database Configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "name": os.getenv("DB_NAME", "sadie_db"),
    "user": os.getenv("DB_USER", "sadie_user"),
    "password": os.getenv("DB_PASSWORD")
}

# Model Configuration
MODEL_CONFIG = {
    "save_path": os.getenv("MODEL_SAVE_PATH", str(MODELS_DIR)),
    "cache_dir": os.getenv("CACHE_DIR", str(CACHE_DIR)),
    "log_level": os.getenv("LOG_LEVEL", "INFO")
}

# Training Parameters
TRAINING_CONFIG = {
    "batch_size": int(os.getenv("BATCH_SIZE", 32)),
    "epochs": int(os.getenv("EPOCHS", 100)),
    "learning_rate": float(os.getenv("LEARNING_RATE", 0.001)),
    "validation_split": float(os.getenv("VALIDATION_SPLIT", 0.2))
}

# Data Parameters
DATA_CONFIG = {
    "sequence_length": int(os.getenv("SEQUENCE_LENGTH", 10)),
    "prediction_horizon": int(os.getenv("PREDICTION_HORIZON", 5)),
    "feature_columns": os.getenv("FEATURE_COLUMNS", "open,high,low,close,volume").split(",")
}

# Backtesting Configuration
BACKTEST_CONFIG = {
    "initial_capital": float(os.getenv("INITIAL_CAPITAL", 100000)),
    "trading_fee": float(os.getenv("TRADING_FEE", 0.001))
}

# Monitoring Configuration
MONITORING_CONFIG = {
    "enabled": os.getenv("ENABLE_MONITORING", "true").lower() == "true",
    "host": os.getenv("MONITORING_HOST", "localhost"),
    "port": int(os.getenv("MONITORING_PORT", 8000))
}

# LSTM Model Architecture
LSTM_CONFIG = {
    "layers": [64, 32, 16],
    "dropout": 0.2,
    "activation": "relu",
    "recurrent_activation": "sigmoid",
    "optimizer": "adam"
}

# Technical Indicators Configuration
TECHNICAL_INDICATORS = {
    "rsi": {"period": 14},
    "macd": {"fast_period": 12, "slow_period": 26, "signal_period": 9},
    "bollinger": {"period": 20, "std_dev": 2}
}

# Sentiment Analysis Configuration
SENTIMENT_CONFIG = {
    "moving_average_window": 7,
    "sentiment_threshold": 0.5,
    "min_articles": 3
}

def get_api_key(service: str) -> Union[str, Dict[str, str]]:
    """Get API key for a specific service."""
    return API_KEYS.get(service)

def get_db_url() -> str:
    """Get database URL from configuration."""
    return f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['name']}"

def get_model_path(model_name: str) -> Path:
    """Get full path for a model file."""
    return Path(MODEL_CONFIG["save_path"]) / f"{model_name}.h5"

def get_cache_path(cache_key: str) -> Path:
    """Get full path for a cache file."""
    return Path(MODEL_CONFIG["cache_dir"]) / f"{cache_key}.pkl" 