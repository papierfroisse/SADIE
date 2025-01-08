"""Real-time transaction flow collector for SADIE."""
from typing import Dict, List, Optional, Tuple, Callable, Any
import asyncio
import logging
from datetime import datetime
from decimal import Decimal
import json
from collections import deque

import aiohttp
from websockets.client import connect as ws_connect
import numpy as np

from .base import BaseCollector
from .exceptions import CollectorError, ValidationError
from .utils import RateLimiter

logger = logging.getLogger(__name__)

class Transaction:
    """Represents a single market transaction."""
    
    def __init__(
        self,
        price: Decimal,
        quantity: Decimal,
        timestamp: datetime,
        is_buyer_maker: bool,
        trade_id: int
    ):
        """Initialize transaction.
        
        Args:
            price: Transaction price
            quantity: Transaction quantity
            timestamp: Transaction timestamp
            is_buyer_maker: Whether buyer was the maker
            trade_id: Unique trade identifier
        """
        self.price = price
        self.quantity = quantity
        self.timestamp = timestamp
        self.is_buyer_maker = is_buyer_maker
        self.trade_id = trade_id
        
    @property
    def side(self) -> str:
        """Get the transaction side (buy/sell)."""
        return "sell" if self.is_buyer_maker else "buy"
        
    @property
    def volume(self) -> Decimal:
        """Get transaction volume (price * quantity)."""
        return self.price * self.quantity

class TransactionMetrics:
    """Class for computing transaction flow metrics."""
    
    @staticmethod
    def compute_vwap(transactions: List[Transaction]) -> Decimal:
        """Compute volume-weighted average price."""
        if not transactions:
            return Decimal('0')
            
        total_volume = sum(tx.volume for tx in transactions)
        if total_volume == 0:
            return Decimal('0')
            
        weighted_sum = sum(tx.price * tx.volume for tx in transactions)
        return weighted_sum / total_volume
        
    @staticmethod
    def compute_buy_sell_ratio(transactions: List[Transaction]) -> Decimal:
        """Compute buy/sell volume ratio."""
        buy_volume = sum(tx.volume for tx in transactions if not tx.is_buyer_maker)
        sell_volume = sum(tx.volume for tx in transactions if tx.is_buyer_maker)
        total_volume = buy_volume + sell_volume
        
        if total_volume == 0:
            return Decimal('1')
            
        return buy_volume / sell_volume if sell_volume > 0 else Decimal('inf')
        
    @staticmethod
    def compute_trade_stats(
        transactions: List[Transaction]
    ) -> Tuple[Decimal, Decimal, int]:
        """Compute basic trade statistics.
        
        Returns:
            Tuple of (avg_trade_size, total_volume, trade_count)
        """
        if not transactions:
            return Decimal('0'), Decimal('0'), 0
            
        trade_count = len(transactions)
        total_volume = sum(tx.volume for tx in transactions)
        avg_trade_size = total_volume / trade_count if trade_count > 0 else Decimal('0')
        
        return avg_trade_size, total_volume, trade_count

class TransactionCollector(BaseCollector):
    """Collector for real-time transaction data."""
    
    def __init__(
        self,
        symbols: List[str],
        window_size: int = 1000,
        update_interval: float = 0.1,
        rate_limit: int = 20,
        metrics_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None
    ):
        """Initialize transaction collector.
        
        Args:
            symbols: List of trading pairs to collect
            window_size: Number of transactions to keep in memory
            update_interval: Update frequency in seconds
            rate_limit: Maximum requests per second
            metrics_callback: Optional callback for transaction metrics updates
        """
        super().__init__()
        self.symbols = symbols
        self.window_size = window_size
        self.update_interval = update_interval
        self.rate_limiter = RateLimiter(rate_limit)
        self.metrics_callback = metrics_callback
        
        self._transactions: Dict[str, deque[Transaction]] = {}
        self._ws_connections: Dict[str, asyncio.Task] = {}
        self._metrics_tasks: Dict[str, asyncio.Task] = {}
        self._metrics = TransactionMetrics()
        
    async def start(self) -> None:
        """Start transaction data collection."""
        try:
            # Initialize transaction queues
            for symbol in self.symbols:
                self._transactions[symbol] = deque(maxlen=self.window_size)
                
            # Start WebSocket connections and metrics tasks
            for symbol in self.symbols:
                self._ws_connections[symbol] = asyncio.create_task(
                    self._maintain_ws_connection(symbol)
                )
                if self.metrics_callback:
                    self._metrics_tasks[symbol] = asyncio.create_task(
                        self._compute_metrics_loop(symbol)
                    )
                
            logger.info(f"Started transaction collection for {len(self.symbols)} symbols")
            
        except Exception as e:
            raise CollectorError(f"Failed to start transaction collector: {str(e)}")
            
    async def stop(self) -> None:
        """Stop transaction data collection."""
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
            self._transactions.clear()
            
            logger.info("Stopped transaction collection")
            
        except Exception as e:
            raise CollectorError(f"Failed to stop transaction collector: {str(e)}")
            
    async def get_transactions(
        self,
        symbol: str,
        limit: Optional[int] = None
    ) -> List[Transaction]:
        """Get recent transactions.
        
        Args:
            symbol: Trading pair
            limit: Maximum number of transactions to return
            
        Returns:
            List of recent transactions
        """
        if symbol not in self._transactions:
            raise CollectorError(f"Transactions not available for {symbol}")
            
        transactions = list(self._transactions[symbol])
        if limit:
            transactions = transactions[-limit:]
            
        return transactions
        
    async def get_metrics(
        self,
        symbol: str,
        window: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get current transaction metrics.
        
        Args:
            symbol: Trading pair
            window: Number of recent transactions to consider
            
        Returns:
            Dictionary of transaction metrics
        """
        if symbol not in self._transactions:
            raise CollectorError(f"Transactions not available for {symbol}")
            
        transactions = await self.get_transactions(symbol, window)
        
        avg_size, volume, count = self._metrics.compute_trade_stats(transactions)
        
        return {
            'vwap': self._metrics.compute_vwap(transactions),
            'buy_sell_ratio': self._metrics.compute_buy_sell_ratio(transactions),
            'avg_trade_size': avg_size,
            'total_volume': volume,
            'trade_count': count,
            'timestamp': datetime.utcnow()
        }
        
    async def _maintain_ws_connection(self, symbol: str) -> None:
        """Maintain WebSocket connection for transaction updates."""
        while True:
            try:
                uri = f"wss://stream.binance.com:9443/ws/{symbol.lower()}@trade"
                async with ws_connect(uri) as ws:
                    logger.info(f"Connected to trade stream for {symbol}")
                    
                    async for message in ws:
                        await self._handle_ws_message(symbol, message)
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"WebSocket error for {symbol}: {str(e)}")
                await asyncio.sleep(5)  # Wait before reconnecting
                
    async def _handle_ws_message(self, symbol: str, message: str) -> None:
        """Handle trade message."""
        try:
            data = json.loads(message)
            
            # Create transaction object
            transaction = Transaction(
                price=Decimal(str(data['p'])),
                quantity=Decimal(str(data['q'])),
                timestamp=datetime.fromtimestamp(data['T'] / 1000),
                is_buyer_maker=data['m'],
                trade_id=data['t']
            )
            
            # Add to queue
            self._transactions[symbol].append(transaction)
            
        except Exception as e:
            logger.error(f"Failed to process message for {symbol}: {str(e)}")
            
    async def _compute_metrics_loop(self, symbol: str) -> None:
        """Compute and publish transaction metrics periodically."""
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