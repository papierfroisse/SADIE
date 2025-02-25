"""Module de collecte de données."""

from .trade_collector import BinanceTradeCollector
from .kraken_collector import KrakenTradeCollector

__all__ = ['BinanceTradeCollector', 'KrakenTradeCollector']