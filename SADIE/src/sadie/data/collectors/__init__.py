"""Data collectors for SADIE."""
from typing import Type

from .base import BaseCollector
from .orderbook import OrderBookCollector
from .binance import BinanceCollector
from .alpha_vantage import AlphaVantageCollector
from .exceptions import CollectorError

# Map of collector names to their classes
COLLECTORS = {
    "orderbook": OrderBookCollector,
    "binance": BinanceCollector,
    "alpha_vantage": AlphaVantageCollector
}

def get_collector(name: str) -> Type[BaseCollector]:
    """Get collector class by name.
    
    Args:
        name: Name of the collector
        
    Returns:
        Collector class
        
    Raises:
        CollectorError: If collector not found
    """
    try:
        return COLLECTORS[name.lower()]
    except KeyError:
        raise CollectorError(f"Collector not found: {name}")

__all__ = [
    "BaseCollector",
    "OrderBookCollector",
    "BinanceCollector",
    "AlphaVantageCollector",
    "CollectorError",
    "get_collector"
] 