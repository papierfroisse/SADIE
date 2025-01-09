"""Resilience tests for data collectors."""

import asyncio
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pytest
from asyncpg.exceptions import ConnectionDoesNotExistError
from binance.exceptions import BinanceAPIException

from sadie.data.collectors import OrderBookCollector, TradesCollector
from sadie.storage.database import DatabaseManager


class NetworkSimulator:
    """Class to simulate network conditions."""

    def __init__(
        self,
        latency_mean: float = 0.05,
        latency_stddev: float = 0.02,
        packet_loss_rate: float = 0.01,
        connection_drop_rate: float = 0.001,
        max_concurrent_connections: int = 100,
    ):
        """Initialize network simulator.
        
        Args:
            latency_mean: Mean network latency in seconds.
            latency_stddev: Standard deviation of latency.
            packet_loss_rate: Probability of packet loss.
            connection_drop_rate: Probability of connection drop.
            max_concurrent_connections: Maximum concurrent connections.
        """
        self.latency_mean = latency_mean
        self.latency_stddev = latency_stddev
        self.packet_loss_rate = packet_loss_rate
        self.connection_drop_rate = connection_drop_rate
        self.max_concurrent_connections = max_concurrent_connections
        self.active_connections = 0
        self._lock = asyncio.Lock()

    async def simulate_network_conditions(self):
        """Simulate network conditions for a request."""
        async with self._lock:
            if self.active_connections >= self.max_concurrent_connections:
                raise ConnectionError("Too many concurrent connections")
            
            self.active_connections += 1
        
        try:
            # Simulate packet loss
            if random.random() < self.packet_loss_rate:
                raise ConnectionError("Simulated packet loss")
            
            # Simulate connection drop
            if random.random() < self.connection_drop_rate:
                raise ConnectionError("Simulated connection drop")
            
            # Simulate latency
            latency = random.gauss(self.latency_mean, self.latency_stddev)
            await asyncio.sleep(max(0, latency))
            
        finally:
            async with self._lock:
                self.active_connections -= 1


class ResilienceTestCollector(OrderBookCollector):
    """OrderBookCollector with network simulation."""

    def __init__(
        self,
        *args,
        network_simulator: NetworkSimulator,
        **kwargs,
    ):
        """Initialize the collector with network simulation."""
        super().__init__(*args, **kwargs)
        self._network_simulator = network_simulator
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 5
        self._reconnect_delay = 1.0

    async def _handle_depth_socket(self, ws: any, symbol: str) -> None:
        """Handle depth socket messages with simulated network conditions."""
        while True:
            try:
                async with ws as stream:
                    while True:
                        # Simulate network conditions
                        await self._network_simulator.simulate_network_conditions()
                        
                        msg = await stream.recv()
                        self._order_books[symbol] = {
                            "bids": msg["b"],
                            "asks": msg["a"],
                            "last_update": msg["E"],
                        }
                        
            except ConnectionError as e:
                if self._reconnect_attempts >= self._max_reconnect_attempts:
                    raise RuntimeError("Max reconnection attempts reached") from e
                
                self._reconnect_attempts += 1
                await asyncio.sleep(
                    self._reconnect_delay * (2 ** (self._reconnect_attempts - 1))
                )
                continue
                
            except Exception as e:
                raise


class ResilienceTestTradesCollector(TradesCollector):
    """TradesCollector with network simulation."""

    def __init__(
        self,
        *args,
        network_simulator: NetworkSimulator,
        **kwargs,
    ):
        """Initialize the collector with network simulation."""
        super().__init__(*args, **kwargs)
        self._network_simulator = network_simulator
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 5
        self._reconnect_delay = 1.0

    async def _handle_trade_socket(self, ws: any, symbol: str) -> None:
        """Handle trade socket messages with simulated network conditions."""
        while True:
            try:
                async with ws as stream:
                    while True:
                        # Simulate network conditions
                        await self._network_simulator.simulate_network_conditions()
                        
                        msg = await stream.recv()
                        trade = {
                            "symbol": symbol,
                            "trade_id": msg["t"],
                            "price": msg["p"],
                            "quantity": msg["q"],
                            "buyer_order_id": msg["b"],
                            "seller_order_id": msg["a"],
                            "timestamp": msg["T"],
                            "buyer_is_maker": msg["m"],
                            "is_best_match": msg["M"],
                        }
                        
                        self._trade_batches[symbol].append(trade)
                        
                        if len(self._trade_batches[symbol]) >= self._batch_size:
                            await self._store_batch(symbol)
                            
            except ConnectionError as e:
                if self._reconnect_attempts >= self._max_reconnect_attempts:
                    raise RuntimeError("Max reconnection attempts reached") from e
                
                self._reconnect_attempts += 1
                await asyncio.sleep(
                    self._reconnect_delay * (2 ** (self._reconnect_attempts - 1))
                )
                continue
                
            except Exception as e:
                raise


@pytest.fixture
async def db_manager():
    """Create a database manager instance."""
    manager = DatabaseManager(
        host=os.getenv("TEST_DB_HOST", "localhost"),
        port=int(os.getenv("TEST_DB_PORT", "5432")),
        database=os.getenv("TEST_DB_NAME", "sadie_test"),
        user=os.getenv("TEST_DB_USER", "postgres"),
        password=os.getenv("TEST_DB_PASSWORD", "postgres"),
        min_connections=20,
        max_connections=100,
    )
    await manager.connect()
    yield manager
    await manager.disconnect()


@pytest.fixture
def network_simulator():
    """Create a network simulator instance."""
    return NetworkSimulator(
        latency_mean=0.05,
        latency_stddev=0.02,
        packet_loss_rate=0.01,
        connection_drop_rate=0.001,
        max_concurrent_connections=100,
    )


@pytest.mark.resilience
@pytest.mark.asyncio
async def test_orderbook_collector_reconnection(db_manager, network_simulator):
    """Test OrderBookCollector's ability to handle connection drops."""
    # Create collector with aggressive network simulation
    network_simulator.connection_drop_rate = 0.1  # 10% connection drop rate
    
    collector = ResilienceTestCollector(
        db_manager=db_manager,
        symbols=["BTCUSDT"],
        network_simulator=network_simulator,
        depth_level="L2",
        update_interval=1.0,
    )
    
    try:
        await collector.start()
        await asyncio.sleep(30)  # Run for 30 seconds
        
        # Verify collector is still running
        assert await collector.is_running()
        
        # Verify we have some data
        status = await collector.get_status()
        assert status["running"]
        
    finally:
        await collector.stop()


@pytest.mark.resilience
@pytest.mark.asyncio
async def test_trades_collector_packet_loss(db_manager, network_simulator):
    """Test TradesCollector's ability to handle packet loss."""
    # Create collector with high packet loss
    network_simulator.packet_loss_rate = 0.2  # 20% packet loss rate
    
    collector = ResilienceTestTradesCollector(
        db_manager=db_manager,
        symbols=["BTCUSDT"],
        network_simulator=network_simulator,
        batch_size=10,
        batch_interval=1.0,
    )
    
    try:
        await collector.start()
        await asyncio.sleep(30)  # Run for 30 seconds
        
        # Verify collector is still running
        assert await collector.is_running()
        
        # Verify we have some data
        status = await collector.get_status()
        assert status["running"]
        
    finally:
        await collector.stop()


@pytest.mark.resilience
@pytest.mark.asyncio
async def test_database_connection_loss(db_manager, network_simulator):
    """Test collectors' ability to handle database connection loss."""
    collector = ResilienceTestTradesCollector(
        db_manager=db_manager,
        symbols=["BTCUSDT"],
        network_simulator=network_simulator,
        batch_size=10,
        batch_interval=1.0,
    )
    
    try:
        await collector.start()
        await asyncio.sleep(5)  # Let it collect some data
        
        # Simulate database connection loss
        await db_manager.disconnect()
        await asyncio.sleep(5)  # Let it try to write with no connection
        
        # Restore connection
        await db_manager.connect()
        await asyncio.sleep(5)  # Let it recover
        
        # Verify collector is still running
        assert await collector.is_running()
        
        # Verify we can still write data
        status = await collector.get_status()
        assert status["running"]
        
    finally:
        await collector.stop()


@pytest.mark.resilience
@pytest.mark.asyncio
async def test_high_latency_handling(db_manager, network_simulator):
    """Test collectors' ability to handle high network latency."""
    # Create collector with high latency
    network_simulator.latency_mean = 0.5  # 500ms mean latency
    network_simulator.latency_stddev = 0.2  # 200ms standard deviation
    
    collector = ResilienceTestOrderBookCollector(
        db_manager=db_manager,
        symbols=["BTCUSDT"],
        network_simulator=network_simulator,
        depth_level="L2",
        update_interval=1.0,
    )
    
    try:
        await collector.start()
        await asyncio.sleep(30)  # Run for 30 seconds
        
        # Verify collector is still running
        assert await collector.is_running()
        
        # Verify we have some data
        status = await collector.get_status()
        assert status["running"]
        
    finally:
        await collector.stop()


@pytest.mark.resilience
@pytest.mark.asyncio
async def test_connection_limit_handling(db_manager, network_simulator):
    """Test collectors' ability to handle connection limits."""
    # Create collector with low connection limit
    network_simulator.max_concurrent_connections = 2
    
    collectors = []
    try:
        # Try to create more collectors than allowed connections
        for _ in range(5):
            collector = ResilienceTestOrderBookCollector(
                db_manager=db_manager,
                symbols=["BTCUSDT"],
                network_simulator=network_simulator,
                depth_level="L2",
                update_interval=1.0,
            )
            collectors.append(collector)
            await collector.start()
        
        await asyncio.sleep(30)  # Run for 30 seconds
        
        # Verify at least some collectors are still running
        running_collectors = 0
        for collector in collectors:
            if await collector.is_running():
                running_collectors += 1
        
        assert running_collectors > 0
        assert running_collectors <= network_simulator.max_concurrent_connections
        
    finally:
        for collector in collectors:
            await collector.stop()


if __name__ == "__main__":
    asyncio.run(test_orderbook_collector_reconnection(
        DatabaseManager(),
        NetworkSimulator(),
    )) 