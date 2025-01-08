"""Order book data collector for SADIE."""
from typing import Dict, List, Optional, Tuple
import asyncio
import logging
from datetime import datetime
from decimal import Decimal

import aiohttp
from websockets.client import connect as ws_connect

from .base import BaseCollector
from .exceptions import CollectorError
from .utils import RateLimiter

logger = logging.getLogger(__name__)

class OrderBookCollector(BaseCollector):
    """Collector for L2/L3 order book data."""
    
    def __init__(
        self,
        symbols: List[str],
        depth: int = 100,
        update_interval: float = 1.0,
        rate_limit: int = 10
    ):
        """Initialize order book collector.
        
        Args:
            symbols: List of trading pairs to collect
            depth: Order book depth (10, 20, 50, 100, 500, 1000)
            update_interval: Update frequency in seconds
            rate_limit: Maximum requests per second
        """
        super().__init__()
        self.symbols = symbols
        self.depth = depth
        self.update_interval = update_interval
        self.rate_limiter = RateLimiter(rate_limit)
        
        self._order_books: Dict[str, Dict] = {}
        self._ws_connections: Dict[str, asyncio.Task] = {}
        
    async def start(self) -> None:
        """Start order book data collection."""
        try:
            # Initialize order books
            for symbol in self.symbols:
                await self._init_order_book(symbol)
                
            # Start WebSocket connections
            for symbol in self.symbols:
                self._ws_connections[symbol] = asyncio.create_task(
                    self._maintain_ws_connection(symbol)
                )
                
            logger.info(f"Started order book collection for {len(self.symbols)} symbols")
            
        except Exception as e:
            raise CollectorError(f"Failed to start order book collector: {str(e)}")
            
    async def stop(self) -> None:
        """Stop order book data collection."""
        try:
            # Cancel all WebSocket connections
            for task in self._ws_connections.values():
                task.cancel()
                
            # Wait for tasks to complete
            await asyncio.gather(*self._ws_connections.values(), return_exceptions=True)
            
            self._ws_connections.clear()
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
            
        book = self._order_books[symbol]
        max_depth = depth or self.depth
        
        bids = [(Decimal(str(p)), Decimal(str(q))) 
                for p, q in list(book["bids"].items())[:max_depth]]
        asks = [(Decimal(str(p)), Decimal(str(q))) 
                for p, q in list(book["asks"].items())[:max_depth]]
                
        return bids, asks
        
    async def _init_order_book(self, symbol: str) -> None:
        """Initialize order book for a symbol."""
        async with aiohttp.ClientSession() as session:
            # Get initial snapshot
            url = f"https://api.binance.com/api/v3/depth?symbol={symbol}&limit={self.depth}"
            async with session.get(url) as response:
                if response.status != 200:
                    raise CollectorError(
                        f"Failed to get order book snapshot: {response.status}"
                    )
                data = await response.json()
                
            # Initialize order book
            self._order_books[symbol] = {
                "lastUpdateId": data["lastUpdateId"],
                "bids": {float(bid[0]): float(bid[1]) for bid in data["bids"]},
                "asks": {float(ask[0]): float(ask[1]) for ask in data["asks"]}
            }
            
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
                await asyncio.sleep(5)  # Wait before reconnecting
                
    async def _handle_ws_message(self, symbol: str, message: str) -> None:
        """Handle order book update message."""
        try:
            data = eval(message)
            book = self._order_books[symbol]
            
            # Update bids
            for bid in data["b"]:
                price = float(bid[0])
                quantity = float(bid[1])
                if quantity > 0:
                    book["bids"][price] = quantity
                else:
                    book["bids"].pop(price, None)
                    
            # Update asks
            for ask in data["a"]:
                price = float(ask[0])
                quantity = float(ask[1])
                if quantity > 0:
                    book["asks"][price] = quantity
                else:
                    book["asks"].pop(price, None)
                    
            # Sort order book
            book["bids"] = dict(sorted(
                book["bids"].items(),
                key=lambda x: x[0],
                reverse=True
            )[:self.depth])
            
            book["asks"] = dict(sorted(
                book["asks"].items(),
                key=lambda x: x[0]
            )[:self.depth])
            
        except Exception as e:
            logger.error(f"Failed to process message for {symbol}: {str(e)}") 