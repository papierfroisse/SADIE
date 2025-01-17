"""Tests de performance de la gestion mémoire."""

import pytest
from datetime import datetime, timedelta

from sadie.collectors.market import OrderBookCollector
from sadie.core.cache import Cache
from sadie.core.models import DataPoint

@profile
async def test_memory_orderbook():
    """Test de consommation mémoire du collecteur OrderBook."""
    collector = OrderBookCollector(
        exchange="binance",
        symbol="BTC/USDT"
    )
    
    cache = Cache()
    process = psutil.Process(os.getpid())
    
    print(f"Mémoire initiale: {process.memory_info().rss / 1024 / 1024:.2f} MB")
    
    # Simulation de collecte de données
    for i in range(1000):
        data = DataPoint(
            timestamp=time.time(),
            value=float(i),
            metadata={"type": "test"}
        )
        await cache.set(f"test_key_{i}", data)
        
        if i % 100 == 0:
            print(f"Itération {i}: {process.memory_info().rss / 1024 / 1024:.2f} MB")
            
    print(f"Mémoire finale: {process.memory_info().rss / 1024 / 1024:.2f} MB")
    
    # Nettoyage
    await cache.clear()

if __name__ == "__main__":
    asyncio.run(test_memory_orderbook()) 