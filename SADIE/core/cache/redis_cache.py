"""Redis cache implementation."""
import json
import logging
import time
from typing import Any, Dict, Optional

import redis

from ..metrics import (
    CACHE_HITS,
    CACHE_MISSES,
    CACHE_SIZE,
    ERRORS
)

logger = logging.getLogger(__name__)

class RedisCache:
    """Redis-based cache implementation."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        **kwargs
    ):
        """Initialize Redis cache.
        
        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password
            **kwargs: Additional Redis configuration
        """
        self.redis = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True,
            **kwargs
        )
        self._setup_metrics()

    def _setup_metrics(self):
        """Setup initial metrics state."""
        CACHE_SIZE.labels(type='redis').set(0)

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if exists, None otherwise
        """
        try:
            value = self.redis.get(key)
            if value is not None:
                CACHE_HITS.labels(type='redis').inc()
                return json.loads(value)
            CACHE_MISSES.labels(type='redis').inc()
            return None
        except Exception as e:
            ERRORS.labels(type='cache_get', exchange='redis').inc()
            logger.error(f"Error getting key {key} from cache: {str(e)}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            expire: Optional expiration time in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            serialized = json.dumps(value)
            if expire:
                success = self.redis.setex(key, expire, serialized)
            else:
                success = self.redis.set(key, serialized)
                
            if success:
                # Update cache size metric
                size = self.redis.memory_usage(key)
                if size:
                    CACHE_SIZE.labels(type='redis').set(size)
                    
            return bool(success)
        except Exception as e:
            ERRORS.labels(type='cache_set', exchange='redis').inc()
            logger.error(f"Error setting key {key} in cache: {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            ERRORS.labels(type='cache_delete', exchange='redis').inc()
            logger.error(f"Error deleting key {key} from cache: {str(e)}")
            return False

    async def clear(self) -> bool:
        """Clear all values from cache.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.redis.flushdb()
            CACHE_SIZE.labels(type='redis').set(0)
            return True
        except Exception as e:
            ERRORS.labels(type='cache_clear', exchange='redis').inc()
            logger.error(f"Error clearing cache: {str(e)}")
            return False

    async def get_stats(self) -> Dict[str, int]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            info = self.redis.info()
            return {
                'used_memory': info['used_memory'],
                'hits': info['keyspace_hits'],
                'misses': info['keyspace_misses'],
                'keys': info['db0']['keys']
            }
        except Exception as e:
            ERRORS.labels(type='cache_stats', exchange='redis').inc()
            logger.error(f"Error getting cache stats: {str(e)}")
            return {} 