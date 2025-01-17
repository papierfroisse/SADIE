"""
Modèles d'événements pour les données de marché.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any

class Exchange(str, Enum):
    """Exchanges supportés."""
    BINANCE = "binance"
    BYBIT = "bybit"
    KUCOIN = "kucoin"
    BITGET = "bitget"
    OKEX = "okex"

class Symbol(str, Enum):
    """Symboles supportés."""
    BTC_USDT = "BTC/USDT"
    ETH_USDT = "ETH/USDT"
    BNB_USDT = "BNB/USDT"
    XRP_USDT = "XRP/USDT"
    ADA_USDT = "ADA/USDT"
    SOL_USDT = "SOL/USDT"
    DOGE_USDT = "DOGE/USDT"
    DOT_USDT = "DOT/USDT"
    MATIC_USDT = "MATIC/USDT"
    LINK_USDT = "LINK/USDT"

class Timeframe(str, Enum):
    """Timeframes supportés."""
    M1 = "1m"
    M3 = "3m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H2 = "2h"
    H4 = "4h"
    H6 = "6h"
    H8 = "8h"
    H12 = "12h"
    D1 = "1d"
    D3 = "3d"
    W1 = "1w"
    MO1 = "1M"

@dataclass
class MarketEvent:
    """Événement de marché."""
    exchange: Exchange
    symbol: Symbol
    timestamp: datetime
    price: float
    volume: float
    side: str  # "buy" ou "sell"
    type: str = field(default="market")  # "trade", "order", "liquidation"
    data: Optional[Dict[str, Any]] = field(default_factory=dict)

@dataclass
class Trade(MarketEvent):
    """
    Représente un trade exécuté.
    Hérite de MarketEvent avec type="trade" par défaut.
    """
    trade_id: str = field(default=None)
    maker: bool = field(default=False)
    liquidation: bool = field(default=False)

    def __post_init__(self):
        """Initialise le type comme 'trade'."""
        self.type = "trade"
        if not isinstance(self.timestamp, datetime):
            self.timestamp = datetime.fromtimestamp(self.timestamp) 