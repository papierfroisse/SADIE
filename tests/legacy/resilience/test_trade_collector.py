"""Tests de résilience du collecteur de trades."""

import pytest
from datetime import datetime, timedelta

from sadie.data.collectors.trades import TradeCollector, Trade, TradeManager
from sadie.core.monitoring import get_logger

logger = get_logger(__name__)

class MockWebSocket:
    """Mock d'une connexion WebSocket."""
    
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.connected = False
        self.messages = []
        
    async def connect(self):
        if self.should_fail:
            raise ConnectionError("Erreur de connexion simulée")
        self.connected = True
        
    async def disconnect(self):
        self.connected = False
        
    async def send_message(self, message):
        if not self.connected:
            raise ConnectionError("Non connecté")
        self.messages.append(message)
        
    async def receive_message(self):
        if not self.connected:
            raise ConnectionError("Non connecté")
        return self.messages.pop(0) if self.messages else None

@pytest.fixture
def collector():
    """Fixture du collecteur de transactions."""
    symbols = ["BTC-USD", "ETH-USD"]
    return TradeCollector(
        name="test",
        symbols=symbols,
        update_interval=0.1,
        max_trades=100
    )

@pytest.mark.asyncio
async def test_connection_resilience(collector):
    """Teste la résilience aux problèmes de connexion."""
    mock_ws = MockWebSocket(should_fail=True)
    
    with patch.object(collector, '_create_websocket', return_value=mock_ws):
        # Premier essai - échec attendu
        with pytest.raises(ConnectionError):
            await collector.connect()
            
        # Deuxième essai - succès après modification
        mock_ws.should_fail = False
        await collector.connect()
        assert collector.is_connected()

@pytest.mark.asyncio
async def test_message_processing_resilience(collector):
    """Teste la résilience au traitement des messages."""
    # Message valide
    valid_message = {
        "trade_id": "1",
        "symbol": "BTC-USD",
        "price": "50000.00",
        "amount": "1.0",
        "side": "buy",
        "timestamp": datetime.now().isoformat()
    }
    
    # Message invalide
    invalid_message = {
        "trade_id": "2",
        "symbol": "BTC-USD",
        "price": "invalid",
        "amount": "1.0",
        "side": "buy",
        "timestamp": datetime.now().isoformat()
    }
    
    # Test du traitement des messages
    await collector.process_message(valid_message)
    assert len(collector.managers["BTC-USD"].trades) == 1
    
    # Le message invalide ne devrait pas faire planter le collecteur
    await collector.process_message(invalid_message)
    assert len(collector.managers["BTC-USD"].trades) == 1

@pytest.mark.asyncio
async def test_recovery_after_disconnect(collector):
    """Teste la récupération après une déconnexion."""
    mock_ws = MockWebSocket()
    
    with patch.object(collector, '_create_websocket', return_value=mock_ws):
        # Connexion initiale
        await collector.connect()
        assert collector.is_connected()
        
        # Simulation d'une déconnexion
        await mock_ws.disconnect()
        assert not collector.is_connected()
        
        # Vérification de la reconnexion automatique
        await collector.connect()
        assert collector.is_connected()

@pytest.mark.asyncio
async def test_data_consistency(collector):
    """Teste la cohérence des données pendant les perturbations."""
    # Ajout de données initiales
    initial_trade = {
        "trade_id": "1",
        "symbol": "BTC-USD",
        "price": "50000.00",
        "amount": "1.0",
        "side": "buy",
        "timestamp": datetime.now().isoformat()
    }
    await collector.process_message(initial_trade)
    
    # Simulation de perturbations
    mock_ws = MockWebSocket(should_fail=True)
    with patch.object(collector, '_create_websocket', return_value=mock_ws):
        try:
            await collector.connect()
        except ConnectionError:
            pass
    
    # Vérification que les données existantes sont préservées
    assert len(collector.managers["BTC-USD"].trades) == 1
    trade = collector.managers["BTC-USD"].trades[0]
    assert trade.price == Decimal("50000.00")
    assert trade.amount == Decimal("1.0") 