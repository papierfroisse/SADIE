"""Unit tests for Binance transaction collector."""
import pytest
import json
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from sadie.data.collectors.binance_transactions import (
    BinanceTransactionCollector,
    Transaction
)

@pytest.fixture
def sample_trade_message():
    """Create a sample Binance trade message."""
    return json.dumps({
        "e": "trade",
        "E": 1672515782136,
        "s": "BTCUSDT",
        "t": 123456789,
        "p": "50000.00",
        "q": "1.23456",
        "b": 987654321,
        "a": 123456789,
        "T": 1672515782136,
        "m": True,
        "M": True
    })

@pytest.fixture
def sample_subscription_response():
    """Create a sample subscription response."""
    return json.dumps({
        "result": None,
        "id": 1
    })

class MockWebSocket:
    """Mock WebSocket for testing."""
    def __init__(self, messages):
        self.messages = messages
        self.sent_messages = []
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
        
    async def send(self, message):
        """Record sent messages."""
        self.sent_messages.append(message)
        
    async def recv(self):
        """Return next message."""
        return self.messages.pop(0) if self.messages else None

@pytest.fixture
async def collector():
    """Create a collector instance for testing."""
    collector = BinanceTransactionCollector(
        symbols=["BTCUSDT"],
        window_size=100,
        update_interval=0.1
    )
    yield collector
    await collector.stop()

async def test_initialization():
    """Test collector initialization."""
    collector = BinanceTransactionCollector(
        symbols=["BTCUSDT", "ETHUSDT"],
        window_size=100
    )
    
    assert collector.symbols == ["BTCUSDT", "ETHUSDT"]
    assert collector.window_size == 100
    assert not collector._running
    assert isinstance(collector.transactions["BTCUSDT"], list)

async def test_websocket_connection(
    collector,
    sample_trade_message,
    sample_subscription_response
):
    """Test WebSocket connection and subscription."""
    mock_ws = MockWebSocket([sample_subscription_response, sample_trade_message])
    
    with patch('websockets.connect', AsyncMock(return_value=mock_ws)):
        ws = await collector._connect_websocket("BTCUSDT")
        
        # Verify subscription message
        subscribe_msg = json.loads(mock_ws.sent_messages[0])
        assert subscribe_msg["method"] == "SUBSCRIBE"
        assert "btcusdt@trade" in subscribe_msg["params"]
        
        # Verify connection is returned
        assert ws == mock_ws

async def test_parse_transaction(collector, sample_trade_message):
    """Test transaction parsing from WebSocket message."""
    transaction = collector._parse_transaction("BTCUSDT", sample_trade_message)
    
    assert isinstance(transaction, Transaction)
    assert transaction.symbol == "BTCUSDT"
    assert transaction.price == 50000.00
    assert transaction.quantity == 1.23456
    assert transaction.is_buyer_maker is True
    assert transaction.trade_id == 123456789
    assert isinstance(transaction.timestamp, float)

async def test_parse_invalid_message(collector):
    """Test parsing invalid messages."""
    # Invalid JSON
    assert collector._parse_transaction("BTCUSDT", "{invalid}") is None
    
    # Wrong message type
    wrong_type = json.dumps({"e": "kline", "E": 123456789})
    assert collector._parse_transaction("BTCUSDT", wrong_type) is None
    
    # Missing required fields
    missing_fields = json.dumps({"e": "trade", "E": 123456789})
    assert collector._parse_transaction("BTCUSDT", missing_fields) is None

async def test_verify_subscription(collector, sample_subscription_response):
    """Test subscription response verification."""
    assert collector._verify_subscription(sample_subscription_response) is True
    
    # Invalid response
    assert collector._verify_subscription("{invalid}") is False
    
    # Error response
    error_response = json.dumps({"error": "Invalid subscription"})
    assert collector._verify_subscription(error_response) is False

async def test_start_stop(collector, sample_subscription_response):
    """Test starting and stopping the collector."""
    mock_ws = MockWebSocket([sample_subscription_response])
    
    with patch('websockets.connect', AsyncMock(return_value=mock_ws)):
        await collector.start()
        assert collector._running
        assert collector._ws_connections
        
        await collector.stop()
        assert not collector._running
        assert all(task.cancelled() for task in collector._ws_connections.values())

async def test_message_processing(
    collector,
    sample_trade_message,
    sample_subscription_response
):
    """Test processing of trade messages."""
    messages = [sample_subscription_response, sample_trade_message]
    mock_ws = MockWebSocket(messages)
    
    with patch('websockets.connect', AsyncMock(return_value=mock_ws)):
        await collector.start()
        
        # Wait for message processing
        await asyncio.sleep(0.2)
        
        # Verify transaction was recorded
        transactions = await collector.get_recent_transactions("BTCUSDT")
        assert len(transactions) > 0
        assert isinstance(transactions[0], Transaction)
        
        await collector.stop()

async def test_error_handling(collector):
    """Test error handling during WebSocket operations."""
    # Test connection error
    with patch('websockets.connect', AsyncMock(side_effect=Exception("Connection failed"))):
        with pytest.raises(Exception):
            await collector._connect_websocket("BTCUSDT")
            
    # Test message processing error
    mock_ws = MockWebSocket(["{invalid}"])
    with patch('websockets.connect', AsyncMock(return_value=mock_ws)):
        await collector._maintain_transaction_stream("BTCUSDT")
        # Should not raise exception

async def test_multiple_symbols():
    """Test collector with multiple symbols."""
    collector = BinanceTransactionCollector(
        symbols=["BTCUSDT", "ETHUSDT"],
        window_size=10
    )
    
    mock_ws = MockWebSocket([json.dumps({"result": None, "id": 1})])
    with patch('websockets.connect', AsyncMock(return_value=mock_ws)):
        await collector.start()
        
        try:
            assert len(collector._ws_connections) == 2
            assert "BTCUSDT" in collector.transactions
            assert "ETHUSDT" in collector.transactions
            
        finally:
            await collector.stop()

async def test_historical_trades(collector):
    """Test historical trades retrieval."""
    with pytest.raises(NotImplementedError):
        await collector.get_historical_trades("BTCUSDT") 