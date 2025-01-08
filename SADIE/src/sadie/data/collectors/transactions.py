"""Real-time transaction flow collector with advanced metrics."""
import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Callable, Any
from dataclasses import dataclass
from datetime import datetime
from collections import deque
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class Transaction:
    """Container for a single market transaction."""
    symbol: str
    timestamp: float
    price: float
    quantity: float
    is_buyer_maker: bool
    trade_id: int

@dataclass
class TransactionMetrics:
    """Container for transaction flow metrics."""
    vwap: float  # Volume-weighted average price
    buy_volume: float
    sell_volume: float
    buy_sell_ratio: float
    trade_count: int
    volume: float
    price_impact: float
    volatility: float

class TransactionCollector:
    """Collector for real-time transaction flows with metrics computation."""
    
    def __init__(
        self,
        symbols: List[str],
        window_size: int = 1000,
        update_interval: float = 0.1,
        callback_interval: float = 1.0
    ):
        """Initialize the transaction collector.
        
        Args:
            symbols: List of trading pairs to monitor
            window_size: Number of transactions to keep in memory
            update_interval: Interval between updates in seconds
            callback_interval: Interval between callback executions
        """
        self.symbols = symbols
        self.window_size = window_size
        self.update_interval = update_interval
        self.callback_interval = callback_interval
        
        # Transaction history per symbol
        self.transactions: Dict[str, deque[Transaction]] = {
            symbol: deque(maxlen=window_size)
            for symbol in symbols
        }
        
        # Callbacks for updates
        self.callbacks: Dict[str, List[Callable[[List[Transaction], TransactionMetrics], None]]] = {
            symbol: []
            for symbol in symbols
        }
        
        # WebSocket connections and tasks
        self._ws_connections: Dict[str, asyncio.Task] = {}
        self._callback_tasks: Dict[str, asyncio.Task] = {}
        self._running = False
        
    async def start(self):
        """Start collecting transaction data."""
        if self._running:
            return
            
        self._running = True
        
        try:
            # Start WebSocket connections for each symbol
            for symbol in self.symbols:
                self._ws_connections[symbol] = asyncio.create_task(
                    self._maintain_transaction_stream(symbol)
                )
                self._callback_tasks[symbol] = asyncio.create_task(
                    self._run_callbacks(symbol)
                )
                
        except Exception as e:
            logger.error(f"Error starting transaction collector: {str(e)}")
            await self.stop()
            raise
            
    async def stop(self):
        """Stop collecting transaction data."""
        self._running = False
        
        # Cancel all tasks
        for task in self._ws_connections.values():
            task.cancel()
        for task in self._callback_tasks.values():
            task.cancel()
            
        try:
            await asyncio.gather(
                *self._ws_connections.values(),
                *self._callback_tasks.values(),
                return_exceptions=True
            )
        except Exception as e:
            logger.error(f"Error stopping transaction collector: {str(e)}")
            
    def register_callback(
        self,
        callback: Callable[[List[Transaction], TransactionMetrics], None],
        symbol: str
    ):
        """Register a callback for transaction updates.
        
        Args:
            callback: Function to call with updates
            symbol: Trading pair symbol
        """
        if symbol not in self.symbols:
            raise ValueError(f"Unknown symbol: {symbol}")
        self.callbacks[symbol].append(callback)
        
    def unregister_callback(
        self,
        callback: Callable[[List[Transaction], TransactionMetrics], None],
        symbol: str
    ):
        """Unregister a callback.
        
        Args:
            callback: Function to unregister
            symbol: Trading pair symbol
        """
        if symbol in self.callbacks and callback in self.callbacks[symbol]:
            self.callbacks[symbol].remove(callback)
            
    async def get_recent_transactions(
        self,
        symbol: str,
        limit: Optional[int] = None
    ) -> List[Transaction]:
        """Get recent transactions for a symbol.
        
        Args:
            symbol: Trading pair symbol
            limit: Optional limit on number of transactions
            
        Returns:
            List of recent transactions
        """
        if symbol not in self.transactions:
            raise ValueError(f"Unknown symbol: {symbol}")
            
        transactions = list(self.transactions[symbol])
        if limit:
            transactions = transactions[-limit:]
            
        return transactions
        
    def compute_metrics(
        self,
        transactions: List[Transaction]
    ) -> TransactionMetrics:
        """Compute metrics from a list of transactions.
        
        Args:
            transactions: List of transactions to analyze
            
        Returns:
            TransactionMetrics containing computed metrics
        """
        if not transactions:
            return TransactionMetrics(
                vwap=0.0,
                buy_volume=0.0,
                sell_volume=0.0,
                buy_sell_ratio=1.0,
                trade_count=0,
                volume=0.0,
                price_impact=0.0,
                volatility=0.0
            )
            
        # Basic metrics
        volume = sum(t.quantity for t in transactions)
        vwap = sum(t.price * t.quantity for t in transactions) / volume if volume > 0 else 0
        
        # Buy/Sell volumes
        buy_volume = sum(t.quantity for t in transactions if not t.is_buyer_maker)
        sell_volume = sum(t.quantity for t in transactions if t.is_buyer_maker)
        buy_sell_ratio = buy_volume / sell_volume if sell_volume > 0 else float('inf')
        
        # Price impact and volatility
        prices = np.array([t.price for t in transactions])
        price_impact = (prices[-1] - prices[0]) / prices[0] if len(prices) > 1 else 0
        volatility = np.std(np.diff(np.log(prices))) if len(prices) > 1 else 0
        
        return TransactionMetrics(
            vwap=vwap,
            buy_volume=buy_volume,
            sell_volume=sell_volume,
            buy_sell_ratio=buy_sell_ratio,
            trade_count=len(transactions),
            volume=volume,
            price_impact=price_impact,
            volatility=volatility
        )
        
    async def _maintain_transaction_stream(self, symbol: str):
        """Maintain WebSocket connection for transaction stream."""
        while self._running:
            try:
                async with self._connect_websocket(symbol) as ws:
                    async for message in ws:
                        if not self._running:
                            break
                            
                        transaction = self._parse_transaction(symbol, message)
                        if transaction:
                            self.transactions[symbol].append(transaction)
                            
            except Exception as e:
                logger.error(f"Error in transaction stream for {symbol}: {str(e)}")
                if self._running:
                    await asyncio.sleep(1)  # Wait before reconnecting
                    
    async def _run_callbacks(self, symbol: str):
        """Run callbacks for a symbol at regular intervals."""
        while self._running:
            try:
                if self.callbacks[symbol]:
                    transactions = await self.get_recent_transactions(symbol)
                    metrics = self.compute_metrics(transactions)
                    
                    for callback in self.callbacks[symbol]:
                        try:
                            callback(transactions, metrics)
                        except Exception as e:
                            logger.error(f"Error in callback for {symbol}: {str(e)}")
                            
            except Exception as e:
                logger.error(f"Error processing callbacks for {symbol}: {str(e)}")
                
            await asyncio.sleep(self.callback_interval)
            
    async def _connect_websocket(self, symbol: str):
        """Create WebSocket connection for a symbol."""
        # Implementation will depend on the exchange API
        # This is a placeholder for the actual WebSocket connection
        raise NotImplementedError("WebSocket connection not implemented")
        
    def _parse_transaction(self, symbol: str, message: str) -> Optional[Transaction]:
        """Parse transaction from WebSocket message."""
        # Implementation will depend on the exchange message format
        # This is a placeholder for the actual message parsing
        raise NotImplementedError("Message parsing not implemented") 