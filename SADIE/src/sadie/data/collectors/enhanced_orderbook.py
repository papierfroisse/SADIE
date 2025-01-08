"""Enhanced order book collector with real-time metrics."""
import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Callable, Any
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict

from sadie.data.collectors.orderbook import OrderBookCollector
from sadie.analysis.orderbook_metrics import OrderBookAnalyzer, OrderBookMetrics

logger = logging.getLogger(__name__)

@dataclass
class OrderBookUpdate:
    """Container for order book updates with metrics."""
    symbol: str
    timestamp: float
    bids: List[Tuple[float, float]]
    asks: List[Tuple[float, float]]
    metrics: OrderBookMetrics

class EnhancedOrderBookCollector:
    """Order book collector with real-time metrics computation."""
    
    def __init__(
        self,
        symbols: List[str],
        depth: int = 1000,
        update_interval: float = 0.1,
        metrics_window: int = 100,
        metrics_levels: int = 10,
        callback_interval: float = 1.0
    ):
        """Initialize the enhanced collector.
        
        Args:
            symbols: List of trading pairs to monitor
            depth: Depth of order book to maintain
            update_interval: Interval between updates in seconds
            metrics_window: Window size for metrics computation
            metrics_levels: Price levels to consider for metrics
            callback_interval: Interval between callback executions
        """
        self.symbols = symbols
        self.depth = depth
        self.update_interval = update_interval
        self.callback_interval = callback_interval
        
        # Initialize base collector and analyzers
        self.collector = OrderBookCollector(
            symbols=symbols,
            depth=depth,
            update_interval=update_interval
        )
        
        self.analyzers = {
            symbol: OrderBookAnalyzer(
                window_size=metrics_window,
                depth_levels=metrics_levels
            )
            for symbol in symbols
        }
        
        # Callbacks for metrics updates
        self.callbacks: Dict[str, List[Callable[[OrderBookUpdate], None]]] = defaultdict(list)
        
        # Tasks and state
        self._callback_tasks: Dict[str, asyncio.Task] = {}
        self._running = False
        
    async def start(self):
        """Start the collector and metric computation."""
        if self._running:
            return
            
        self._running = True
        
        try:
            # Start base collector
            await self.collector.start()
            
            # Start callback tasks for each symbol
            for symbol in self.symbols:
                self._callback_tasks[symbol] = asyncio.create_task(
                    self._run_callbacks(symbol)
                )
                
        except Exception as e:
            logger.error(f"Error starting enhanced collector: {str(e)}")
            await self.stop()
            raise
            
    async def stop(self):
        """Stop the collector and all tasks."""
        self._running = False
        
        # Cancel callback tasks
        for task in self._callback_tasks.values():
            task.cancel()
            
        try:
            await asyncio.gather(*self._callback_tasks.values(), return_exceptions=True)
        except Exception as e:
            logger.error(f"Error stopping callback tasks: {str(e)}")
            
        # Stop base collector
        await self.collector.stop()
        
    def register_callback(
        self,
        callback: Callable[[OrderBookUpdate], None],
        symbol: Optional[str] = None
    ):
        """Register a callback for order book updates.
        
        Args:
            callback: Function to call with updates
            symbol: Optional symbol to filter updates
        """
        if symbol is None:
            # Register for all symbols
            for sym in self.symbols:
                self.callbacks[sym].append(callback)
        else:
            if symbol not in self.symbols:
                raise ValueError(f"Unknown symbol: {symbol}")
            self.callbacks[symbol].append(callback)
            
    def unregister_callback(
        self,
        callback: Callable[[OrderBookUpdate], None],
        symbol: Optional[str] = None
    ):
        """Unregister a callback.
        
        Args:
            callback: Function to unregister
            symbol: Optional symbol to unregister from
        """
        if symbol is None:
            # Unregister from all symbols
            for callbacks in self.callbacks.values():
                if callback in callbacks:
                    callbacks.remove(callback)
        else:
            if symbol in self.callbacks and callback in self.callbacks[symbol]:
                self.callbacks[symbol].remove(callback)
                
    async def get_orderbook_with_metrics(
        self,
        symbol: str
    ) -> OrderBookUpdate:
        """Get current order book with computed metrics.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            OrderBookUpdate containing current state and metrics
        """
        # Get current order book
        bids, asks = await self.collector.get_order_book(symbol)
        
        # Compute metrics
        metrics = self.analyzers[symbol].compute_metrics(
            bids=bids,
            asks=asks,
            timestamp=datetime.now().timestamp()
        )
        
        return OrderBookUpdate(
            symbol=symbol,
            timestamp=datetime.now().timestamp(),
            bids=bids,
            asks=asks,
            metrics=metrics
        )
        
    async def _run_callbacks(self, symbol: str):
        """Run callbacks for a symbol at regular intervals."""
        while self._running:
            try:
                if self.callbacks[symbol]:
                    update = await self.get_orderbook_with_metrics(symbol)
                    
                    # Execute callbacks
                    for callback in self.callbacks[symbol]:
                        try:
                            callback(update)
                        except Exception as e:
                            logger.error(f"Error in callback for {symbol}: {str(e)}")
                            
            except Exception as e:
                logger.error(f"Error processing callbacks for {symbol}: {str(e)}")
                
            await asyncio.sleep(self.callback_interval)
            
    async def get_metrics_history(
        self,
        symbol: str,
        metric_name: str
    ) -> List[float]:
        """Get historical values for a specific metric.
        
        Args:
            symbol: Trading pair symbol
            metric_name: Name of the metric to retrieve
            
        Returns:
            List of historical values for the metric
        """
        if symbol not in self.analyzers:
            raise ValueError(f"Unknown symbol: {symbol}")
            
        analyzer = self.analyzers[symbol]
        
        if metric_name == "volatility":
            return list(analyzer.price_history)
        else:
            raise ValueError(f"Unknown metric: {metric_name}")
            
    def get_all_metrics(self, symbol: str) -> Dict[str, Any]:
        """Get all available metrics for a symbol.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Dictionary of metric names and their current values
        """
        if symbol not in self.analyzers:
            raise ValueError(f"Unknown symbol: {symbol}")
            
        analyzer = self.analyzers[symbol]
        return {
            "price_history": list(analyzer.price_history),
            "window_size": analyzer.window_size,
            "depth_levels": analyzer.depth_levels
        } 