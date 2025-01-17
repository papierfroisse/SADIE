"""Tests de résilience du collecteur de transactions."""

import asyncio
import pytest
import time
from datetime import datetime
import logging
from unittest.mock import patch, AsyncMock

from SADIE.core.collectors.trade_collector import TradeCollector
from SADIE.core.models.events import Exchange, Symbol, Timeframe

logger = logging.getLogger(__name__)

@pytest.fixture
async def collector():
    """Fixture du collecteur de transactions."""
    symbols = [Symbol.BTC_USDT.value]
    collector = TradeCollector(
        name="resilience_test",
        symbols=symbols,
        max_trades_per_symbol=1000,
        connection_pool_size=1,
        max_retries=3,
        retry_delay=0.1,
        cache_enabled=False  # Désactivation du cache
    )
    yield collector
    await collector.disconnect()  # Nettoyage propre

@pytest.mark.asyncio
async def test_network_error_handling(collector):
    """Test de la gestion des erreurs réseau."""
    logger.info("Démarrage du test de gestion des erreurs réseau")
    
    # Configuration du mock
    mock_exchange = AsyncMock()
    mock_exchange.fetch_ohlcv = AsyncMock(side_effect=[
        Exception("Network error"),  # Première tentative échoue
        Exception("Network error"),  # Deuxième tentative échoue
        [[  # Troisième tentative réussit
            int(datetime.now().timestamp() * 1000),
            100.0, 101.0, 99.0, 100.5, 1000.0
        ]]
    ])
    mock_exchange.load_markets = AsyncMock(return_value={})
    mock_exchange.close = AsyncMock()  # Ajout du mock pour close()
    
    with patch('ccxt.async_support.binance', return_value=mock_exchange):
        await collector.connect("binance")  # Connexion explicite
        
        # Tentative de récupération des données
        data = await collector.get_historical_data(
            exchange=Exchange.BINANCE,
            symbol=Symbol.BTC_USDT,
            timeframe=Timeframe.M1,
            limit=1
        )
        
        # Vérifications
        assert data is not None
        assert len(data) > 0
        assert mock_exchange.fetch_ohlcv.call_count == 3
        
        logger.info("Test de gestion des erreurs réseau terminé avec succès")

@pytest.mark.asyncio
async def test_timeout_recovery(collector):
    """Test de la récupération après timeout."""
    logger.info("Démarrage du test de récupération après timeout")
    
    # Configuration du mock
    mock_exchange = AsyncMock()
    mock_exchange.fetch_ohlcv = AsyncMock(side_effect=[
        asyncio.TimeoutError(),  # Premier appel timeout
        [[  # Deuxième appel réussit
            int(datetime.now().timestamp() * 1000),
            100.0, 101.0, 99.0, 100.5, 1000.0
        ]]
    ])
    mock_exchange.load_markets = AsyncMock(return_value={})
    mock_exchange.close = AsyncMock()  # Ajout du mock pour close()
    
    with patch('ccxt.async_support.binance', return_value=mock_exchange):
        await collector.connect("binance")  # Connexion explicite
        
        # Tentative de récupération des données
        data = await collector.get_historical_data(
            exchange=Exchange.BINANCE,
            symbol=Symbol.BTC_USDT,
            timeframe=Timeframe.M1,
            limit=1
        )
        
        # Vérifications
        assert data is not None
        assert len(data) > 0
        assert mock_exchange.fetch_ohlcv.call_count == 2
        
        logger.info("Test de récupération après timeout terminé avec succès")

@pytest.mark.asyncio
async def test_invalid_data_handling(collector):
    """Test de la gestion des données invalides."""
    logger.info("Démarrage du test de gestion des données invalides")
    
    # Test avec un trade invalide
    invalid_trade = {"invalid": "data"}
    error_caught = False
    
    try:
        await collector.process_trade(Symbol.BTC_USDT.value, invalid_trade)
    except KeyError as e:
        error_caught = True
        logger.info(f"Exception attendue capturée : {str(e)}")
    
    assert error_caught, "Une KeyError aurait dû être levée"
    
    # Vérification que le buffer est vide
    trades = collector.get_trades(Symbol.BTC_USDT.value)
    assert len(trades) == 0, "Le buffer devrait être vide après une erreur"
    
    # Vérification que le collecteur est toujours fonctionnel
    valid_trade = {
        "trade_id": "1",
        "symbol": Symbol.BTC_USDT.value,
        "price": "50000.0",
        "amount": "1.0",
        "side": "buy",
        "timestamp": datetime.now().isoformat()
    }
    
    # Traitement d'un trade valide
    await collector.process_trade(Symbol.BTC_USDT.value, valid_trade)
    
    # Vérification du traitement correct
    trades = collector.get_trades(Symbol.BTC_USDT.value)
    assert len(trades) == 1, "Le trade valide devrait être dans le buffer"
    assert trades[0]["trade_id"] == "1", "Le trade dans le buffer devrait être le trade valide"
    
    logger.info("Test de gestion des données invalides terminé avec succès") 