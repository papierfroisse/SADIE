"""Modèles pour les événements."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Trade(BaseModel):
    """Modèle pour un trade."""
    
    symbol: str
    price: float
    quantity: float
    timestamp: datetime
    side: str  # 'buy' ou 'sell'
    trade_id: str
    buyer_order_id: Optional[str] = None
    seller_order_id: Optional[str] = None
    is_buyer_maker: bool = False
    is_best_match: bool = True 