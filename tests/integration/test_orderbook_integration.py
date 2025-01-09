"""Integration tests for the OrderBook collector."""

import asyncio
import os
from datetime import datetime, timedelta

import pytest
from binance import AsyncClient

from sadie.data.collectors import OrderBookCollector
from sadie.storage.database import DatabaseManager


@pytest.fixture
async def db_manager():
    """Create a database manager instance."""
    manager = DatabaseManager(
        host=os.getenv("TEST_DB_HOST", "localhost"),
        port=int(os.getenv("TEST_DB_PORT", "5432")),
        database=os.getenv("TEST_DB_NAME", "sadie_test"),
        user=os.getenv("TEST_DB_USER", "postgres"),
        password=os.getenv("TEST_DB_PASSWORD", "postgres"),
    )
    await manager.connect()
    yield manager
    await manager.disconnect()


@pytest.fixture
async def collector(db_manager):
    """Create an OrderBookCollector instance."""
    collector = OrderBookCollector(
        db_manager=db_manager,
        symbols=["BTCUSDT"],
        depth_level="L2",
        update_interval=1.0,
        exchange="binance",
    )
    yield collector
    await collector.stop()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_orderbook_collection_flow(collector, db_manager):
    """Test the complete flow of collecting and storing order book data."""
    # Start the collector
    await collector.start()
    
    try:
        # Wait for some data to be collected (5 seconds)
        await asyncio.sleep(5)
        
        # Stop the collector
        await collector.stop()
        
        # Verify data was stored
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=1)
        
        data = await db_manager.get_order_book_history(
            symbol="BTCUSDT",
            start_time=start_time,
            end_time=end_time,
            exchange="binance",
        )
        
        # Verify we have collected some data
        assert len(data) > 0
        
        # Verify data structure
        first_entry = data[0]
        assert "symbol" in first_entry
        assert "timestamp" in first_entry
        assert "bids" in first_entry
        assert "asks" in first_entry
        assert first_entry["symbol"] == "BTCUSDT"
        assert first_entry["exchange"] == "binance"
        assert first_entry["depth_level"] == "L2"
        
        # Verify bid/ask structure
        assert isinstance(first_entry["bids"], list)
        assert isinstance(first_entry["asks"], list)
        if first_entry["bids"]:
            bid = first_entry["bids"][0]
            assert len(bid) == 2  # [price, quantity]
            assert float(bid[0]) > 0  # Valid price
            assert float(bid[1]) > 0  # Valid quantity
        
        if first_entry["asks"]:
            ask = first_entry["asks"][0]
            assert len(ask) == 2  # [price, quantity]
            assert float(ask[0]) > 0  # Valid price
            assert float(ask[1]) > 0  # Valid quantity
            
        # Verify order book is properly ordered
        if len(first_entry["bids"]) > 1:
            assert float(first_entry["bids"][0][0]) >= float(first_entry["bids"][1][0])
        if len(first_entry["asks"]) > 1:
            assert float(first_entry["asks"][0][0]) <= float(first_entry["asks"][1][0])
            
    except Exception as e:
        await collector.stop()
        raise


@pytest.mark.integration
@pytest.mark.asyncio
async def test_orderbook_reconnection(collector, db_manager):
    """Test the collector's ability to handle connection issues."""
    await collector.start()
    
    try:
        # Wait for initial data
        await asyncio.sleep(2)
        
        # Force a reconnection by stopping the client
        if collector._client:
            await collector._client.close_connection()
        
        # Wait for reconnection and new data
        await asyncio.sleep(3)
        
        # Verify we can still get data
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=1)
        
        data = await db_manager.get_order_book_history(
            symbol="BTCUSDT",
            start_time=start_time,
            end_time=end_time,
            exchange="binance",
        )
        
        assert len(data) > 0
        
    finally:
        await collector.stop()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_orderbook_multiple_symbols(db_manager):
    """Test collecting data for multiple symbols simultaneously."""
    collector = OrderBookCollector(
        db_manager=db_manager,
        symbols=["BTCUSDT", "ETHUSDT", "BNBUSDT"],
        depth_level="L2",
        update_interval=1.0,
        exchange="binance",
    )
    
    try:
        await collector.start()
        await asyncio.sleep(5)
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=1)
        
        # Check data for each symbol
        for symbol in ["BTCUSDT", "ETHUSDT", "BNBUSDT"]:
            data = await db_manager.get_order_book_history(
                symbol=symbol,
                start_time=start_time,
                end_time=end_time,
                exchange="binance",
            )
            assert len(data) > 0
            assert data[0]["symbol"] == symbol
            
    finally:
        await collector.stop()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_orderbook_error_handling(collector, db_manager):
    """Test the collector's error handling capabilities."""
    await collector.start()
    
    try:
        # Wait for initial data
        await asyncio.sleep(2)
        
        # Simulate a database error by closing the connection
        await db_manager.disconnect()
        
        # Wait some time
        await asyncio.sleep(2)
        
        # Restore the connection
        await db_manager.connect()
        
        # Wait for recovery
        await asyncio.sleep(2)
        
        # Verify we can still get data
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=1)
        
        data = await db_manager.get_order_book_history(
            symbol="BTCUSDT",
            start_time=start_time,
            end_time=end_time,
            exchange="binance",
        )
        
        assert len(data) > 0
        
    finally:
        await collector.stop() 