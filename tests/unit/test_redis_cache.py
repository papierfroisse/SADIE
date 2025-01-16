"""Tests unitaires pour le cache Redis."""

import pytest
import asyncio
from datetime import timedelta

from SADIE.core.cache.redis import RedisCache

@pytest.fixture
async def redis_cache():
    """Fixture pour le cache Redis."""
    cache = RedisCache(
        url="redis://localhost",
        prefix="test:",
        decode_responses=True
    )
    yield cache
    await cache.clear()
    await cache.close()

@pytest.mark.asyncio
async def test_set_get(redis_cache):
    """Test de base set/get."""
    await redis_cache.set("test_key", "test_value")
    value = await redis_cache.get("test_key")
    assert value == "test_value"

@pytest.mark.asyncio
async def test_ttl(redis_cache):
    """Test du TTL."""
    await redis_cache.set("ttl_key", "ttl_value", ttl=timedelta(seconds=1))
    value = await redis_cache.get("ttl_key")
    assert value == "ttl_value"
    
    await asyncio.sleep(1.1)
    value = await redis_cache.get("ttl_key")
    assert value is None

@pytest.mark.asyncio
async def test_delete(redis_cache):
    """Test de suppression."""
    await redis_cache.set("delete_key", "delete_value")
    assert await redis_cache.exists("delete_key")
    
    await redis_cache.delete("delete_key")
    assert not await redis_cache.exists("delete_key")

@pytest.mark.asyncio
async def test_clear(redis_cache):
    """Test de nettoyage complet."""
    await redis_cache.set("clear_key1", "value1")
    await redis_cache.set("clear_key2", "value2")
    
    await redis_cache.clear()
    
    assert not await redis_cache.exists("clear_key1")
    assert not await redis_cache.exists("clear_key2")

@pytest.mark.asyncio
async def test_complex_data(redis_cache):
    """Test avec données complexes."""
    data = {
        "string": "test",
        "number": 42,
        "list": [1, 2, 3],
        "dict": {"key": "value"},
        "bool": True,
        "null": None
    }
    
    await redis_cache.set("complex_key", data)
    result = await redis_cache.get("complex_key")
    assert result == data

@pytest.mark.asyncio
async def test_prefix_isolation(redis_cache):
    """Test d'isolation des préfixes."""
    cache1 = RedisCache(prefix="prefix1:")
    cache2 = RedisCache(prefix="prefix2:")
    
    await cache1.set("key", "value1")
    await cache2.set("key", "value2")
    
    assert await cache1.get("key") == "value1"
    assert await cache2.get("key") == "value2"
    
    await cache1.close()
    await cache2.close()

@pytest.mark.asyncio
async def test_context_manager():
    """Test du context manager."""
    async with RedisCache() as cache:
        await cache.set("ctx_key", "ctx_value")
        value = await cache.get("ctx_key")
        assert value == "ctx_value" 