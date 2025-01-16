"""Tests de performance du collecteur de transactions."""

import asyncio
import pytest
import time
import psutil
import os
from datetime import datetime
from random import uniform

from SADIE.data.collectors.trades import TradeCollector
from SADIE.core.monitoring import get_logger

logger = get_logger(__name__)

def get_process_memory():
    """Retourne l'utilisation mémoire du processus en MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

@pytest.fixture
def collector():
    """Fixture du collecteur de transactions."""
    symbols = ["BTC-USD", "ETH-USD"]
    return TradeCollector(
        name="perf_test",
        symbols=symbols,
        update_interval=0.1,
        max_trades=10000
    )

def generate_trade(symbol: str, trade_id: int):
    """Génère une transaction de test."""
    return {
        "trade_id": str(trade_id),
        "symbol": symbol,
        "price": str(uniform(45000, 55000)),
        "amount": str(uniform(0.1, 2.0)),
        "side": "buy" if uniform(0, 1) > 0.5 else "sell",
        "timestamp": datetime.now().isoformat()
    }

@pytest.mark.asyncio
async def test_message_processing_speed(collector):
    """Teste la vitesse de traitement des messages."""
    n_messages = 1000
    total_time = 0
    
    # Traitement de messages en lot
    for i in range(n_messages):
        trade = generate_trade("BTC-USD", i)
        start_time = time.time()
        await collector.process_message(trade)
        total_time += time.time() - start_time
        
    avg_time = total_time / n_messages * 1000  # en millisecondes
    logger.info(f"Temps moyen de traitement: {avg_time:.2f}ms par message")
    
    # Le temps moyen devrait être inférieur à 1ms
    assert avg_time < 1.0

@pytest.mark.asyncio
async def test_memory_usage_under_load(collector):
    """Teste l'utilisation mémoire sous charge."""
    n_messages = 5000
    initial_memory = get_process_memory()
    
    # Génération et traitement d'un grand nombre de messages
    for i in range(n_messages):
        symbol = "BTC-USD" if i % 2 == 0 else "ETH-USD"
        trade = generate_trade(symbol, i)
        await collector.process_message(trade)
        
        if i % 1000 == 0:
            # Vérification périodique de l'utilisation mémoire
            current_memory = get_process_memory()
            memory_increase = current_memory - initial_memory
            logger.info(
                f"Utilisation mémoire après {i} messages: "
                f"{current_memory:.2f}MB (+{memory_increase:.2f}MB)"
            )
            
    # L'augmentation de mémoire ne devrait pas dépasser 100MB
    final_memory = get_process_memory()
    memory_increase = final_memory - initial_memory
    logger.info(f"Augmentation totale de mémoire: {memory_increase:.2f}MB")
    assert memory_increase < 100

@pytest.mark.asyncio
async def test_concurrent_processing(collector):
    """Teste le traitement concurrent des messages."""
    n_messages = 1000
    start_time = time.time()
    
    # Création des tâches de traitement
    tasks = []
    for i in range(n_messages):
        symbol = "BTC-USD" if i % 2 == 0 else "ETH-USD"
        trade = generate_trade(symbol, i)
        task = asyncio.create_task(collector.process_message(trade))
        tasks.append(task)
    
    # Attente de la fin du traitement
    await asyncio.gather(*tasks)
    total_time = time.time() - start_time
    
    # Calcul des métriques
    messages_per_second = n_messages / total_time
    logger.info(f"Messages traités par seconde: {messages_per_second:.2f}")
    
    # Vérification des résultats
    assert len(collector.managers["BTC-USD"].trades) == n_messages // 2
    assert len(collector.managers["ETH-USD"].trades) == n_messages // 2
    
    # Le débit devrait être d'au moins 1000 messages par seconde
    assert messages_per_second > 1000

@pytest.mark.asyncio
async def test_sustained_load(collector):
    """Teste le comportement sous charge soutenue."""
    duration = 10  # secondes
    messages_per_second = 100
    start_time = time.time()
    message_count = 0
    
    while time.time() - start_time < duration:
        # Envoi de messages à intervalles réguliers
        batch_start = time.time()
        tasks = []
        
        for _ in range(messages_per_second):
            trade = generate_trade("BTC-USD", message_count)
            task = asyncio.create_task(collector.process_message(trade))
            tasks.append(task)
            message_count += 1
            
        await asyncio.gather(*tasks)
        
        # Attente pour maintenir le débit cible
        elapsed = time.time() - batch_start
        if elapsed < 1.0:
            await asyncio.sleep(1.0 - elapsed)
            
    # Calcul des métriques finales
    total_time = time.time() - start_time
    actual_rate = message_count / total_time
    logger.info(
        f"Débit moyen maintenu: {actual_rate:.2f} messages/s "
        f"sur {duration} secondes"
    )
    
    # Le débit réel devrait être proche du débit cible
    assert abs(actual_rate - messages_per_second) < messages_per_second * 0.1 