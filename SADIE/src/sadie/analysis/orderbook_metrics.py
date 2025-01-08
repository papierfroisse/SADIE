"""Advanced order book metrics calculation."""
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import numpy as np
from collections import deque
import logging

logger = logging.getLogger(__name__)

@dataclass
class OrderBookMetrics:
    """Container for order book metrics."""
    spread: float
    mid_price: float
    weighted_mid_price: float
    bid_depth: float
    ask_depth: float
    imbalance: float
    pressure: float
    volatility: float
    liquidity_score: float

class OrderBookAnalyzer:
    """Analyzer for computing advanced order book metrics."""
    
    def __init__(self, window_size: int = 100, depth_levels: int = 10):
        """Initialize the analyzer.
        
        Args:
            window_size: Number of historical snapshots to keep for volatility
            depth_levels: Number of price levels to consider for metrics
        """
        self.window_size = window_size
        self.depth_levels = depth_levels
        self.price_history = deque(maxlen=window_size)
        
    def compute_metrics(
        self,
        bids: List[Tuple[float, float]],
        asks: List[Tuple[float, float]],
        timestamp: Optional[float] = None
    ) -> OrderBookMetrics:
        """Compute comprehensive metrics from order book data.
        
        Args:
            bids: List of (price, quantity) tuples for bids
            asks: List of (price, quantity) tuples for asks
            timestamp: Optional timestamp of the snapshot
            
        Returns:
            OrderBookMetrics containing all computed metrics
        """
        try:
            # Ensure we have enough data
            if not bids or not asks:
                raise ValueError("Empty order book")
                
            # Basic metrics
            spread = self._compute_spread(bids[0][0], asks[0][0])
            mid_price = (bids[0][0] + asks[0][0]) / 2
            
            # Store for volatility calculation
            self.price_history.append(mid_price)
            
            # Advanced metrics
            weighted_mid = self._compute_weighted_mid_price(bids, asks)
            bid_depth = self._compute_depth(bids)
            ask_depth = self._compute_depth(asks)
            imbalance = self._compute_imbalance(bid_depth, ask_depth)
            pressure = self._compute_pressure(bids, asks)
            volatility = self._compute_volatility()
            liquidity = self._compute_liquidity_score(spread, bid_depth, ask_depth)
            
            return OrderBookMetrics(
                spread=spread,
                mid_price=mid_price,
                weighted_mid_price=weighted_mid,
                bid_depth=bid_depth,
                ask_depth=ask_depth,
                imbalance=imbalance,
                pressure=pressure,
                volatility=volatility,
                liquidity_score=liquidity
            )
            
        except Exception as e:
            logger.error(f"Error computing metrics: {str(e)}")
            raise
            
    def _compute_spread(self, best_bid: float, best_ask: float) -> float:
        """Compute the bid-ask spread."""
        return best_ask - best_bid
        
    def _compute_weighted_mid_price(
        self,
        bids: List[Tuple[float, float]],
        asks: List[Tuple[float, float]]
    ) -> float:
        """Compute volume-weighted mid price."""
        bid_volume = sum(qty for _, qty in bids[:self.depth_levels])
        ask_volume = sum(qty for _, qty in asks[:self.depth_levels])
        
        weighted_bid = sum(price * qty for price, qty in bids[:self.depth_levels]) / bid_volume
        weighted_ask = sum(price * qty for price, qty in asks[:self.depth_levels]) / ask_volume
        
        return (weighted_bid + weighted_ask) / 2
        
    def _compute_depth(self, orders: List[Tuple[float, float]]) -> float:
        """Compute total depth up to specified levels."""
        return sum(qty for _, qty in orders[:self.depth_levels])
        
    def _compute_imbalance(self, bid_depth: float, ask_depth: float) -> float:
        """Compute order book imbalance."""
        total_depth = bid_depth + ask_depth
        if total_depth == 0:
            return 0
        return (bid_depth - ask_depth) / total_depth
        
    def _compute_pressure(
        self,
        bids: List[Tuple[float, float]],
        asks: List[Tuple[float, float]]
    ) -> float:
        """Compute buying/selling pressure indicator."""
        bid_pressure = sum(
            qty / (i + 1) for i, (_, qty) in enumerate(bids[:self.depth_levels])
        )
        ask_pressure = sum(
            qty / (i + 1) for i, (_, qty) in enumerate(asks[:self.depth_levels])
        )
        
        total_pressure = bid_pressure + ask_pressure
        if total_pressure == 0:
            return 0
        return (bid_pressure - ask_pressure) / total_pressure
        
    def _compute_volatility(self) -> float:
        """Compute price volatility over the window."""
        if len(self.price_history) < 2:
            return 0
            
        prices = np.array(self.price_history)
        returns = np.diff(np.log(prices))
        return np.std(returns) * np.sqrt(len(returns))
        
    def _compute_liquidity_score(
        self,
        spread: float,
        bid_depth: float,
        ask_depth: float
    ) -> float:
        """Compute overall liquidity score."""
        # Normalize components
        norm_spread = 1 / (1 + spread)  # Lower spread = higher liquidity
        norm_depth = np.log1p(bid_depth + ask_depth)  # Higher depth = higher liquidity
        
        # Combine into single score (0-1)
        return (norm_spread + norm_depth) / 2 