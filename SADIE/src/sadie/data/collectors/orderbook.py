"""Advanced order book data collector for SADIE."""
from typing import Dict, List, Optional, Tuple, Callable, Any
import asyncio
import logging
from datetime import datetime
from decimal import Decimal
import json
from collections import defaultdict

import aiohttp
from websockets.client import connect as ws_connect
import numpy as np
from sortedcontainers import SortedDict

from .base import BaseCollector
from .exceptions import CollectorError, ValidationError
from .utils import RateLimiter

logger = logging.getLogger(__name__)

class OrderBookMetrics:
    """Class for computing order book metrics."""
    
    @staticmethod
    def compute_spread(bids: List[Tuple[Decimal, Decimal]], 
                      asks: List[Tuple[Decimal, Decimal]]) -> Decimal:
        """Compute bid-ask spread."""
        if not bids or not asks:
            return Decimal('0')
        return asks[0][0] - bids[0][0]
        
    @staticmethod
    def compute_depth(bids: List[Tuple[Decimal, Decimal]], 
                     asks: List[Tuple[Decimal, Decimal]], 
                     price_range: Decimal) -> Tuple[Decimal, Decimal]:
        """Compute order book depth within price range."""
        bid_depth = sum(qty for price, qty in bids 
                       if price >= bids[0][0] - price_range)
        ask_depth = sum(qty for price, qty in asks 
                       if price <= asks[0][0] + price_range)
        return Decimal(str(bid_depth)), Decimal(str(ask_depth))
        
    @staticmethod
    def compute_imbalance(bids: List[Tuple[Decimal, Decimal]], 
                         asks: List[Tuple[Decimal, Decimal]], 
                         levels: int = 10) -> Decimal:
        """Compute order book imbalance."""
        bid_vol = sum(qty for _, qty in bids[:levels])
        ask_vol = sum(qty for _, qty in asks[:levels])
        total_vol = bid_vol + ask_vol
        return Decimal(str((bid_vol - ask_vol) / total_vol if total_vol > 0 else 0))

class OrderBook:
    """Internal order book representation."""
    
    def __init__(self, depth: int = 1000):
        """Initialize order book."""
        self.bids = SortedDict()
        self.asks = SortedDict()
        self.depth = depth
        self.last_update_id = 0
        self.metrics = OrderBookMetrics()
        
    def update(self, bids: List[Tuple[str, str]], 
               asks: List[Tuple[str, str]], update_id: int) -> None:
        """Update order book with new data."""
        if update_id <= self.last_update_id:
            return
            
        # Update bids
        for price_str, qty_str in bids:
            price = Decimal(price_str)
            qty = Decimal(qty_str)
            if qty == 0:
                self.bids.pop(price, None)
            else:
                self.bids[price] = qty
                
        # Update asks
        for price_str, qty_str in asks:
            price = Decimal(price_str)
            qty = Decimal(qty_str)
            if qty == 0:
                self.asks.pop(price, None)
            else:
                self.asks[price] = qty
                
        # Maintain depth
        if len(self.bids) > self.depth:
            for price in list(self.bids.keys())[self.depth:]:
                del self.bids[price]
        if len(self.asks) > self.depth:
            for price in list(self.asks.keys())[self.depth:]:
                del self.asks[price]
                
        self.last_update_id = update_id
        
    def get_snapshot(self, depth: Optional[int] = None) -> Tuple[List[Tuple[Decimal, Decimal]], 
                                                                List[Tuple[Decimal, Decimal]]]:
        """Get order book snapshot."""
        max_depth = depth or self.depth
        bids = [(price, qty) for price, qty in self.bids.items()][:max_depth]
        asks = [(price, qty) for price, qty in self.asks.items()][:max_depth]
        return bids, asks
        
    def get_metrics(self, price_range: Decimal = Decimal('100'), 
                   levels: int = 10) -> Dict[str, Decimal]:
        """Get order book metrics."""
        bids, asks = self.get_snapshot(levels)
        return {
            'spread': self.metrics.compute_spread(bids, asks),
            'bid_depth': self.metrics.compute_depth(bids, asks, price_range)[0],
            'ask_depth': self.metrics.compute_depth(bids, asks, price_range)[1],
            'imbalance': self.metrics.compute_imbalance(bids, asks, levels)
        }

class OrderBookCollector(BaseCollector):
    """Enhanced collector for L2/L3 order book data."""
    
    def __init__(
        self,
        symbols: List[str],
        depth: int = 1000,
        update_interval: float = 0.1,
        rate_limit: int = 20,
        metrics_callback: Optional[Callable[[str, Dict[str, Decimal]], None]] = None
    ):
        """Initialize order book collector.
        
        Args:
            symbols: List of trading pairs to collect
            depth: Order book depth (up to 5000)
            update_interval: Update frequency in seconds
            rate_limit: Maximum requests per second
            metrics_callback: Optional callback for order book metrics updates
        """
        super().__init__()
        self.symbols = symbols
        self.depth = depth
        self.update_interval = update_interval
        self.rate_limiter = RateLimiter(rate_limit)
        self.metrics_callback = metrics_callback
        
        self._order_books: Dict[str, OrderBook] = {}
        self._ws_connections: Dict[str, asyncio.Task] = {}
        self._metrics_tasks: Dict[str, asyncio.Task] = {}
        
    async def start(self) -> None:
        """Start order book data collection."""
        try:
            # Initialize order books
            for symbol in self.symbols:
                await self._init_order_book(symbol)
                
            # Start WebSocket connections and metrics tasks
            for symbol in self.symbols:
                self._ws_connections[symbol] = asyncio.create_task(
                    self._maintain_ws_connection(symbol)
                )
                if self.metrics_callback:
                    self._metrics_tasks[symbol] = asyncio.create_task(
                        self._compute_metrics_loop(symbol)
                    )
                
            logger.info(f"Started enhanced order book collection for {len(self.symbols)} symbols")
            
        except Exception as e:
            raise CollectorError(f"Failed to start order book collector: {str(e)}")
            
    async def stop(self) -> None:
        """Stop order book data collection."""
        try:
            # Cancel all tasks
            for task in self._ws_connections.values():
                task.cancel()
            for task in self._metrics_tasks.values():
                task.cancel()
                
            # Wait for tasks to complete
            await asyncio.gather(
                *self._ws_connections.values(),
                *self._metrics_tasks.values(),
                return_exceptions=True
            )
            
            self._ws_connections.clear()
            self._metrics_tasks.clear()
            self._order_books.clear()
            
            logger.info("Stopped order book collection")
            
        except Exception as e:
            raise CollectorError(f"Failed to stop order book collector: {str(e)}")
            
    async def get_order_book(
        self,
        symbol: str,
        depth: Optional[int] = None
    ) -> Tuple[List[Tuple[Decimal, Decimal]], List[Tuple[Decimal, Decimal]]]:
        """Get current order book snapshot.
        
        Args:
            symbol: Trading pair
            depth: Number of price levels to return
            
        Returns:
            Tuple of (bids, asks) where each is a list of (price, quantity) tuples
        """
        if symbol not in self._order_books:
            raise CollectorError(f"Order book not available for {symbol}")
            
        return self._order_books[symbol].get_snapshot(depth)
        
    async def get_metrics(
        self,
        symbol: str,
        price_range: Decimal = Decimal('100'),
        levels: int = 10
    ) -> Dict[str, Decimal]:
        """Get current order book metrics.
        
        Args:
            symbol: Trading pair
            price_range: Price range for depth calculation
            levels: Number of levels for imbalance calculation
            
        Returns:
            Dictionary of order book metrics
        """
        if symbol not in self._order_books:
            raise CollectorError(f"Order book not available for {symbol}")
            
        return self._order_books[symbol].get_metrics(price_range, levels)
        
    async def _init_order_book(self, symbol: str) -> None:
        """Initialize order book for a symbol."""
        async with aiohttp.ClientSession() as session:
            # Get initial snapshot with maximum depth
            url = f"https://api.binance.com/api/v3/depth?symbol={symbol}&limit={self.depth}"
            async with session.get(url) as response:
                if response.status != 200:
                    raise CollectorError(
                        f"Failed to get order book snapshot: {response.status}"
                    )
                data = await response.json()
                
            # Initialize order book
            book = OrderBook(self.depth)
            book.update(
                [(bid[0], bid[1]) for bid in data["bids"]],
                [(ask[0], ask[1]) for ask in data["asks"]],
                data["lastUpdateId"]
            )
            self._order_books[symbol] = book
            
    async def _maintain_ws_connection(self, symbol: str) -> None:
        """Maintain WebSocket connection for order book updates."""
        while True:
            try:
                uri = f"wss://stream.binance.com:9443/ws/{symbol.lower()}@depth@100ms"
                async with ws_connect(uri) as ws:
                    logger.info(f"Connected to order book stream for {symbol}")
                    
                    async for message in ws:
                        await self._handle_ws_message(symbol, message)
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"WebSocket error for {symbol}: {str(e)}")
                # Reinitialize order book on connection error
                try:
                    await self._init_order_book(symbol)
                except Exception as init_error:
                    logger.error(f"Failed to reinitialize order book: {str(init_error)}")
                await asyncio.sleep(5)  # Wait before reconnecting
                
    async def _handle_ws_message(self, symbol: str, message: str) -> None:
        """Handle order book update message."""
        try:
            data = json.loads(message)
            book = self._order_books[symbol]
            
            # Update order book
            book.update(
                [(bid[0], bid[1]) for bid in data["b"]],
                [(ask[0], ask[1]) for ask in data["a"]],
                data["u"]
            )
            
        except Exception as e:
            logger.error(f"Failed to process message for {symbol}: {str(e)}")
            
    async def _compute_metrics_loop(self, symbol: str) -> None:
        """Compute and publish order book metrics periodically."""
        while True:
            try:
                metrics = await self.get_metrics(symbol)
                if self.metrics_callback:
                    self.metrics_callback(symbol, metrics)
                await asyncio.sleep(self.update_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Failed to compute metrics for {symbol}: {str(e)}")
                await asyncio.sleep(1)  # Wait before retrying 