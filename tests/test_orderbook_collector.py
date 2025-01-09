"""Tests for the OrderBook collector."""

import asyncio
import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from binance import AsyncClient, BinanceSocketManager

from sadie.data.collectors.orderbook import OrderBookCollector
from sadie.storage.database import DatabaseManager


@pytest.fixture
def db_manager():
    """Create a mock database manager."""
    manager = AsyncMock(spec=DatabaseManager)
    manager.insert_order_book = AsyncMock()
    return manager


@pytest.fixture
def mock_binance_client():
    """Create a mock Binance client."""
    client = AsyncMock(spec=AsyncClient)
    return client


@pytest.fixture
def mock_binance_socket_manager():
    """Create a mock Binance socket manager."""
    bm = MagicMock(spec=BinanceSocketManager)
    return bm


@pytest.fixture
def mock_websocket():
    """Create a mock websocket."""
    ws = AsyncMock()
    ws.__aenter__ = AsyncMock()
    ws.__aexit__ = AsyncMock()
    ws.__aenter__.return_value = ws
    return ws


@pytest.fixture
async def collector(db_manager):
    """Create an OrderBookCollector instance."""
    collector = OrderBookCollector(
        db_manager=db_manager,
        symbols=["BTCUSDT", "ETHUSDT"],
        depth_level="L2",
        update_interval=0.1,
        exchange="binance",
    )
    yield collector
    await collector.stop()


@pytest.mark.asyncio
async def test_initialization(collector):
    """Test collector initialization."""
    assert collector._symbols == ["BTCUSDT", "ETHUSDT"]
    assert collector._depth_level == "L2"
    assert collector._update_interval == 0.1
    assert collector._exchange == "binance"
    assert collector._client is None
    assert collector._bm is None
    assert collector._ws_tasks == []
    assert collector._order_books == {}


@pytest.mark.asyncio
async def test_initialize_success(
    collector, mock_binance_client, mock_binance_socket_manager
):
    """Test successful initialization."""
    with patch("sadie.data.collectors.orderbook.AsyncClient") as mock_client_class, \
         patch("sadie.data.collectors.orderbook.BinanceSocketManager") as mock_bm_class:
        mock_client_class.create.return_value = mock_binance_client
        mock_bm_class.return_value = mock_binance_socket_manager
        
        await collector._initialize()
        
        mock_client_class.create.assert_called_once()
        mock_bm_class.assert_called_once_with(mock_binance_client)
        assert collector._client == mock_binance_client
        assert collector._bm == mock_binance_socket_manager


@pytest.mark.asyncio
async def test_initialize_unsupported_exchange():
    """Test initialization with unsupported exchange."""
    db_manager = AsyncMock(spec=DatabaseManager)
    collector = OrderBookCollector(
        db_manager=db_manager,
        symbols=["BTCUSDT"],
        exchange="unsupported",
    )
    
    with pytest.raises(ValueError, match="Unsupported exchange: unsupported"):
        await collector._initialize()


@pytest.mark.asyncio
async def test_collect_and_store(
    collector,
    mock_binance_socket_manager,
    mock_websocket,
    db_manager,
):
    """Test collecting and storing order book data."""
    # Mock the depth socket
    mock_binance_socket_manager.depth_socket.return_value = mock_websocket
    collector._bm = mock_binance_socket_manager
    collector._running = True
    
    # Mock WebSocket messages
    mock_messages = [
        {
            "e": "depthUpdate",
            "E": 123456789,
            "s": "BTCUSDT",
            "b": [["50000.00", "1.000"]],
            "a": [["50001.00", "0.500"]],
        }
    ]
    mock_websocket.recv.side_effect = mock_messages + [asyncio.CancelledError]
    
    # Start collection
    collect_task = asyncio.create_task(collector._collect())
    await asyncio.sleep(0.2)  # Allow some time for processing
    
    # Stop collection
    collector._running = False
    await collect_task
    
    # Verify data was stored
    db_manager.insert_order_book.assert_called()
    call_args = db_manager.insert_order_book.call_args_list[0][1]
    assert call_args["symbol"] == "BTCUSDT"
    assert isinstance(call_args["timestamp"], datetime)
    assert call_args["exchange"] == "binance"
    assert call_args["depth_level"] == "L2"
    assert call_args["bids"] == [["50000.00", "1.000"]]
    assert call_args["asks"] == [["50001.00", "0.500"]]


@pytest.mark.asyncio
async def test_cleanup(collector, mock_binance_client):
    """Test cleanup process."""
    # Setup mock client and tasks
    collector._client = mock_binance_client
    mock_task = AsyncMock()
    collector._ws_tasks = [mock_task]
    
    await collector._cleanup()
    
    # Verify tasks were cancelled
    mock_task.cancel.assert_called_once()
    mock_binance_client.close_connection.assert_called_once()
    assert collector._ws_tasks == []


@pytest.mark.asyncio
async def test_handle_depth_socket(collector, mock_websocket):
    """Test handling of depth socket messages."""
    symbol = "BTCUSDT"
    mock_message = {
        "e": "depthUpdate",
        "E": 123456789,
        "s": "BTCUSDT",
        "b": [["50000.00", "1.000"]],
        "a": [["50001.00", "0.500"]],
    }
    mock_websocket.recv.side_effect = [mock_message, Exception("Test end")]
    
    with pytest.raises(Exception, match="Test end"):
        await collector._handle_depth_socket(mock_websocket, symbol)
    
    assert collector._order_books[symbol]["bids"] == [["50000.00", "1.000"]]
    assert collector._order_books[symbol]["asks"] == [["50001.00", "0.500"]]
    assert collector._order_books[symbol]["last_update"] == 123456789 