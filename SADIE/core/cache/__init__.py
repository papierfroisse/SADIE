"""
Module de gestion du cache.
"""

from .redis_cache import RedisCache

Cache = RedisCache  # Alias pour la compatibilité
__all__ = ['Cache', 'RedisCache'] 