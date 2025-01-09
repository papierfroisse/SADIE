"""Tests for the Trades collector."""

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from binance import AsyncClient, BinanceSocketManager

from sadie.data.collectors.trades import TradesCollector
from sadie.storage.database import DatabaseManager


@pytest.fixture
def db_manager():
    """Create a mock database manager."""
    manager = AsyncMock(spec=DatabaseManager)
    manager.insert_trades = AsyncMock()
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
    """Create a TradesCollector instance."""
    collector = TradesCollector(
        db_manager=db_manager,
        symbols=["BTCUSDT", "ETHUSDT"],
        batch_size=100,
        batch_interval=1.0,
        exchange="binance",
    )
    yield collector
    await collector.stop()


@pytest.mark.asyncio
async def test_initialization(collector):
    """Test collector initialization."""
    assert collector._symbols == ["BTCUSDT", "ETHUSDT"]
    assert collector._batch_size == 100
    assert collector._batch_interval == 1.0
    assert collector._exchange == "binance"
    assert collector._client is None
    assert collector._bm is None
    assert collector._ws_tasks == []
    assert collector._trade_batches == {}
    assert collector._last_batch_time == {}


@pytest.mark.asyncio
async def test_initialize_success(
    collector, mock_binance_client, mock_binance_socket_manager
):
    """Test successful initialization."""
    with patch("sadie.data.collectors.trades.AsyncClient") as mock_client_class, \
         patch("sadie.data.collectors.trades.BinanceSocketManager") as mock_bm_class:
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
    collector = TradesCollector(
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
    """Test collecting and storing trade data."""
    # Mock the trade socket
    mock_binance_socket_manager.trade_socket.return_value = mock_websocket
    collector._bm = mock_binance_socket_manager
    collector._running = True
    
    # Mock WebSocket messages
    mock_messages = [
        {
            "e": "trade",
            "E": 123456789,
            "s": "BTCUSDT",
            "t": 12345,
            "p": "50000.00",
            "q": "1.000",
            "b": 98765,
            "a": 54321,
            "T": 123456789000,
            "m": True,
            "M": True,
        }
    ]
    mock_websocket.recv.side_effect = mock_messages + [asyncio.CancelledError]
    
    # Start collection
    collect_task = asyncio.create_task(collector._collect())
    await asyncio.sleep(0.2)  # Allow some time for processing
    
    # Force batch processing
    await collector._process_batches(force=True)
    
    # Stop collection
    collector._running = False
    await collect_task
    
    # Verify data was stored
    db_manager.insert_trades.assert_called()
    call_args = db_manager.insert_trades.call_args_list[0][1]
    assert len(call_args["trades"]) == 1
    trade = call_args["trades"][0]
    assert trade["symbol"] == "BTCUSDT"
    assert trade["trade_id"] == 12345
    assert trade["price"] == "50000.00"
    assert trade["quantity"] == "1.000"
    assert trade["buyer_order_id"] == 98765
    assert trade["seller_order_id"] == 54321
    assert trade["buyer_is_maker"] is True
    assert trade["is_best_match"] is True


@pytest.mark.asyncio
async def test_cleanup(collector, mock_binance_client):
    """Test cleanup process."""
    # Setup mock client and tasks
    collector._client = mock_binance_client
    mock_task = AsyncMock()
    collector._ws_tasks = [mock_task]
    
    # Add some trades to the batch
    collector._trade_batches["BTCUSDT"] = [
        {
            "trade_id": 12345,
            "symbol": "BTCUSDT",
            "price": "50000.00",
            "quantity": "1.000",
            "buyer_order_id": 98765,
            "seller_order_id": 54321,
            "timestamp": 123456789000,
            "buyer_is_maker": True,
            "is_best_match": True,
        }
    ]
    
    await collector._cleanup()
    
    # Verify remaining trades were processed
    assert collector._trade_batches["BTCUSDT"] == []
    
    # Verify tasks were cancelled
    mock_task.cancel.assert_called_once()
    mock_binance_client.close_connection.assert_called_once()
    assert collector._ws_tasks == []


@pytest.mark.asyncio
async def test_batch_processing(collector, db_manager):
    """Test batch processing logic."""
    symbol = "BTCUSDT"
    collector._trade_batches[symbol] = []
    collector._last_batch_time[symbol] = datetime.utcnow()
    
    # Add trades to fill a batch
    for i in range(collector._batch_size + 10):  # Add more than batch size
        trade = {
            "trade_id": i,
            "symbol": symbol,
            "price": "50000.00",
            "quantity": "1.000",
            "buyer_order_id": 98765,
            "seller_order_id": 54321,
            "timestamp": 123456789000,
            "buyer_is_maker": True,
            "is_best_match": True,
        }
        collector._trade_batches[symbol].append(trade)
    
    # Process batches
    await collector._process_batches()
    
    # Verify a full batch was stored
    db_manager.insert_trades.assert_called()
    call_args = db_manager.insert_trades.call_args_list[0][1]
    assert len(call_args["trades"]) == collector._batch_size
    
    # Verify remaining trades are still in the batch
    assert len(collector._trade_batches[symbol]) == 10 