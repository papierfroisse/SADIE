"""
Tests unitaires pour le stockage des données.
"""

import pytest
from datetime import datetime, timedelta

from sadie.storage import BaseStorage, MemoryStorage
from sadie.data.exceptions import StorageError

@pytest.fixture
def memory_storage():
    """Fixture pour le stockage en mémoire."""
    return MemoryStorage()

@pytest.fixture
def sample_data():
    """Fixture pour les données de test."""
    return {
        "symbol": "BTCUSDT",
        "price": 50000.0,
        "volume": 1.5
    }

@pytest.mark.asyncio
async def test_memory_storage_init(memory_storage):
    """Teste l'initialisation du stockage en mémoire."""
    assert isinstance(memory_storage, BaseStorage)
    assert isinstance(memory_storage.data, list)
    assert len(memory_storage.data) == 0

@pytest.mark.asyncio
async def test_memory_storage_store(memory_storage, sample_data):
    """Teste le stockage des données en mémoire."""
    timestamp = datetime.utcnow()
    await memory_storage.store(sample_data, timestamp)
    
    assert len(memory_storage.data) == 1
    assert memory_storage.data[0]["timestamp"] == timestamp
    assert memory_storage.data[0]["data"] == sample_data

@pytest.mark.asyncio
async def test_memory_storage_retrieve(memory_storage, sample_data):
    """Teste la récupération des données en mémoire."""
    now = datetime.utcnow()
    
    # Stockage de données de test
    await memory_storage.store(sample_data, now - timedelta(hours=2))
    await memory_storage.store(sample_data, now - timedelta(hours=1))
    await memory_storage.store(sample_data, now)
    
    # Test de récupération avec filtre temporel
    data = await memory_storage.retrieve(
        start_time=now - timedelta(hours=1),
        end_time=now
    )
    assert len(data) == 2
    
    # Test de récupération avec critères
    data = await memory_storage.retrieve(symbol="BTCUSDT")
    assert len(data) == 3
    assert all(d["symbol"] == "BTCUSDT" for d in data)

@pytest.mark.asyncio
async def test_memory_storage_delete(memory_storage, sample_data):
    """Teste la suppression des données en mémoire."""
    now = datetime.utcnow()
    
    # Stockage de données de test
    await memory_storage.store(sample_data, now - timedelta(hours=2))
    await memory_storage.store(sample_data, now - timedelta(hours=1))
    await memory_storage.store(sample_data, now)
    
    # Test de suppression avec filtre temporel
    deleted = await memory_storage.delete(
        start_time=now - timedelta(hours=1),
        end_time=now
    )
    assert deleted == 2
    assert len(memory_storage.data) == 1

@pytest.mark.asyncio
async def test_memory_storage_count(memory_storage, sample_data):
    """Teste le comptage des données en mémoire."""
    now = datetime.utcnow()
    
    # Stockage de données de test
    await memory_storage.store(sample_data, now - timedelta(hours=2))
    await memory_storage.store(sample_data, now - timedelta(hours=1))
    await memory_storage.store(sample_data, now)
    
    # Test de comptage avec filtre temporel
    count = await memory_storage.count(
        start_time=now - timedelta(hours=1),
        end_time=now
    )
    assert count == 2
    
    # Test de comptage avec critères
    count = await memory_storage.count(symbol="BTCUSDT")
    assert count == 3

@pytest.mark.asyncio
async def test_memory_storage_clear(memory_storage, sample_data):
    """Teste la réinitialisation du stockage en mémoire."""
    await memory_storage.store(sample_data)
    assert len(memory_storage.data) > 0
    
    await memory_storage.disconnect()
    assert len(memory_storage.data) == 0 