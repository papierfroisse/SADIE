"""Tests de stress du collecteur de transactions."""

import asyncio
import pytest
import time
import random
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

from SADIE.data.collectors.trades import TradeCollector
from SADIE.core.monitoring import get_logger

logger = get_logger(__name__)

@pytest.fixture
def collector():
    """Fixture du collecteur de transactions."""
    symbols = ["BTC-USD", "ETH-USD", "XRP-USD", "SOL-USD", "ADA-USD"]
    return TradeCollector(
        name="stress_test",
        symbols=symbols,
        update_interval=0.01,  # Intervalle très court
        max_trades=100000
    )

def generate_burst_trade(symbol: str, trade_id: int, timestamp=None):
    """Génère une transaction pour les tests de burst."""
    if timestamp is None:
        timestamp = datetime.now()
    return {
        "trade_id": str(trade_id),
        "symbol": symbol,
        "price": str(random.uniform(100, 100000)),
        "amount": str(random.uniform(0.0001, 10.0)),
        "side": "buy" if random.random() > 0.5 else "sell",
        "timestamp": timestamp.isoformat()
    }

@pytest.mark.asyncio
async def test_burst_processing(collector):
    """Teste le traitement en rafale de messages."""
    burst_size = 10000
    trades = []
    
    # Génération d'une rafale de messages
    logger.info(f"Génération de {burst_size} messages...")
    for i in range(burst_size):
        symbol = random.choice(collector.symbols)
        trades.append(generate_burst_trade(symbol, i))
    
    # Traitement de la rafale
    start_time = time.time()
    tasks = [
        asyncio.create_task(collector.process_message(trade))
        for trade in trades
    ]
    await asyncio.gather(*tasks)
    
    processing_time = time.time() - start_time
    rate = burst_size / processing_time
    
    logger.info(
        f"Rafale traitée en {processing_time:.2f}s "
        f"({rate:.2f} messages/s)"
    )
    
    # Vérification de la cohérence des données
    total_trades = sum(
        len(manager.trades)
        for manager in collector.managers.values()
    )
    assert total_trades == burst_size

@pytest.mark.asyncio
async def test_out_of_order_messages(collector):
    """Teste le traitement de messages désordonnés."""
    n_messages = 5000
    base_time = datetime.now()
    trades = []
    
    # Génération de messages avec horodatages aléatoires
    for i in range(n_messages):
        symbol = random.choice(collector.symbols)
        timestamp = base_time + timedelta(
            seconds=random.uniform(-3600, 3600)
        )
        trades.append(generate_burst_trade(symbol, i, timestamp))
    
    # Mélange des messages
    random.shuffle(trades)
    
    # Traitement des messages désordonnés
    start_time = time.time()
    tasks = [
        asyncio.create_task(collector.process_message(trade))
        for trade in trades
    ]
    await asyncio.gather(*tasks)
    
    processing_time = time.time() - start_time
    logger.info(f"Messages désordonnés traités en {processing_time:.2f}s")
    
    # Vérification de l'ordre des messages dans chaque gestionnaire
    for manager in collector.managers.values():
        trades = manager.get_trades()
        if trades:
            timestamps = [t.timestamp for t in trades]
            assert timestamps == sorted(timestamps)

@pytest.mark.asyncio
async def test_rapid_symbol_switching(collector):
    """Teste le changement rapide entre symboles."""
    n_messages = 10000
    start_time = time.time()
    
    # Alternance rapide entre symboles
    for i in range(n_messages):
        symbol = collector.symbols[i % len(collector.symbols)]
        trade = generate_burst_trade(symbol, i)
        await collector.process_message(trade)
        
        if i % 1000 == 0:
            logger.info(f"Traités: {i} messages")
    
    processing_time = time.time() - start_time
    rate = n_messages / processing_time
    logger.info(
        f"Changement rapide traité en {processing_time:.2f}s "
        f"({rate:.2f} messages/s)"
    )
    
    # Vérification de la distribution des messages
    trades_per_symbol = {
        symbol: len(manager.trades)
        for symbol, manager in collector.managers.items()
    }
    logger.info(f"Distribution: {trades_per_symbol}")
    
    # Chaque symbole devrait avoir approximativement le même nombre de trades
    expected = n_messages // len(collector.symbols)
    for count in trades_per_symbol.values():
        assert abs(count - expected) < expected * 0.1

@pytest.mark.asyncio
async def test_long_running_stability(collector):
    """Teste la stabilité sur une longue durée."""
    duration = 60  # secondes
    check_interval = 5  # secondes
    rate = 100  # messages par seconde
    start_time = time.time()
    message_count = 0
    
    while time.time() - start_time < duration:
        interval_start = time.time()
        tasks = []
        
        # Génération et envoi des messages pour l'intervalle
        for _ in range(rate):
            symbol = random.choice(collector.symbols)
            trade = generate_burst_trade(symbol, message_count)
            task = asyncio.create_task(collector.process_message(trade))
            tasks.append(task)
            message_count += 1
        
        # Traitement des messages
        await asyncio.gather(*tasks)
        
        # Attente pour maintenir le débit cible
        elapsed = time.time() - interval_start
        if elapsed < 1.0:
            await asyncio.sleep(1.0 - elapsed)
            
        # Vérification périodique
        if int(time.time() - start_time) % check_interval == 0:
            total_trades = sum(
                len(manager.trades)
                for manager in collector.managers.values()
            )
            current_rate = total_trades / (time.time() - start_time)
            logger.info(
                f"État après {int(time.time() - start_time)}s: "
                f"{total_trades} messages, "
                f"{current_rate:.2f} messages/s"
            )
    
    # Vérification finale
    final_time = time.time() - start_time
    total_trades = sum(
        len(manager.trades)
        for manager in collector.managers.values()
    )
    actual_rate = total_trades / final_time
    
    logger.info(
        f"Test de stabilité terminé: {total_trades} messages "
        f"en {final_time:.2f}s ({actual_rate:.2f} messages/s)"
    )
    
    # Le débit moyen devrait être proche du débit cible
    assert abs(actual_rate - rate) < rate * 0.2 