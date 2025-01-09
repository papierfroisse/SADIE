"""
Décorateurs utilitaires.
"""

import asyncio
import functools
import logging
import time
from typing import Any, Callable, Optional, TypeVar, cast

from .logging import get_logger

logger = get_logger(__name__)

F = TypeVar("F", bound=Callable[..., Any])

def retry(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable[[F], F]:
    """
    Décore une fonction pour réessayer en cas d'échec.

    Args:
        max_retries: Nombre maximum de tentatives
        delay: Délai initial entre les tentatives
        backoff: Facteur multiplicatif du délai
        exceptions: Exceptions à intercepter

    Returns:
        Fonction décorée
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Tentative {attempt + 1}/{max_retries} échouée pour {func.__name__}: {e}"
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"Toutes les tentatives ont échoué pour {func.__name__}: {e}"
                        )
            
            raise last_exception  # type: ignore
        
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Tentative {attempt + 1}/{max_retries} échouée pour {func.__name__}: {e}"
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"Toutes les tentatives ont échoué pour {func.__name__}: {e}"
                        )
            
            raise last_exception  # type: ignore
        
        return cast(F, async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper)
    
    return decorator

def log_execution(level: int = logging.INFO) -> Callable[[F], F]:
    """
    Décore une fonction pour logger son exécution.

    Args:
        level: Niveau de logging

    Returns:
        Fonction décorée
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            logger.log(level, f"Début de {func.__name__}")
            
            try:
                result = await func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.log(
                    level,
                    f"Fin de {func.__name__} en {elapsed:.2f}s"
                )
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(
                    f"Erreur dans {func.__name__} après {elapsed:.2f}s: {e}"
                )
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            logger.log(level, f"Début de {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.log(
                    level,
                    f"Fin de {func.__name__} en {elapsed:.2f}s"
                )
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(
                    f"Erreur dans {func.__name__} après {elapsed:.2f}s: {e}"
                )
                raise
        
        return cast(F, async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper)
    
    return decorator

def singleton(cls: Any) -> Any:
    """
    Décore une classe pour en faire un singleton.

    Args:
        cls: Classe à décorer

    Returns:
        Classe décorée
    """
    instances = {}
    
    @functools.wraps(cls)
    def get_instance(*args: Any, **kwargs: Any) -> Any:
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

def deprecated(func: Optional[F] = None, message: Optional[str] = None) -> Callable[[F], F]:
    """
    Décore une fonction pour la marquer comme dépréciée.

    Args:
        func: Fonction à décorer
        message: Message d'avertissement personnalisé

    Returns:
        Fonction décorée
    """
    if func is None:
        return lambda f: deprecated(f, message)
    
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        warning = message or f"{func.__name__} est déprécié"
        logger.warning(warning)
        return func(*args, **kwargs)
    
    return cast(F, wrapper) 