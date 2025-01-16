"""Décorateurs utilitaires pour SADIE."""

import asyncio
import functools
import time
import warnings
from typing import Any, Callable, Optional, Type, TypeVar, Union

from ..monitoring import get_logger

logger = get_logger(__name__)

F = TypeVar('F', bound=Callable[..., Any])

def deprecated(reason: str) -> Callable[[F], F]:
    """Marque une fonction comme dépréciée."""
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            warnings.warn(
                f"{func.__name__} est déprécié: {reason}",
                category=DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator

def singleton(cls: Type[Any]) -> Type[Any]:
    """Décore une classe pour en faire un singleton."""
    instances = {}
    
    @functools.wraps(cls)
    def get_instance(*args: Any, **kwargs: Any) -> Any:
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
        
    return get_instance

def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    exceptions: tuple = (Exception,),
    logger: Optional[Any] = None
) -> Callable[[F], F]:
    """Réessaie une fonction en cas d'échec."""
    if logger is None:
        logger = get_logger(__name__)
    
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Tentative {attempt + 1}/{max_attempts} échouée: {e}"
                        )
                        await asyncio.sleep(delay * (attempt + 1))
                    else:
                        logger.error(
                            f"Toutes les tentatives ont échoué: {e}"
                        )
            raise last_exception
            
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Tentative {attempt + 1}/{max_attempts} échouée: {e}"
                        )
                        time.sleep(delay * (attempt + 1))
                    else:
                        logger.error(
                            f"Toutes les tentatives ont échoué: {e}"
                        )
            raise last_exception
            
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def log_execution(
    level: str = "DEBUG",
    show_args: bool = True,
    show_result: bool = False
) -> Callable[[F], F]:
    """Log l'exécution d'une fonction."""
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = get_logger(func.__module__)
            log = getattr(logger, level.lower())
            
            # Log avant l'exécution
            if show_args:
                log(
                    f"Appel de {func.__name__} avec "
                    f"args={args}, kwargs={kwargs}"
                )
            else:
                log(f"Appel de {func.__name__}")
            
            # Exécution
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log après l'exécution
                if show_result:
                    log(
                        f"{func.__name__} terminé en {duration:.2f}s "
                        f"avec résultat: {result}"
                    )
                else:
                    log(f"{func.__name__} terminé en {duration:.2f}s")
                    
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"{func.__name__} échoué après {duration:.2f}s: {e}"
                )
                raise
                
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = get_logger(func.__module__)
            log = getattr(logger, level.lower())
            
            # Log avant l'exécution
            if show_args:
                log(
                    f"Appel de {func.__name__} avec "
                    f"args={args}, kwargs={kwargs}"
                )
            else:
                log(f"Appel de {func.__name__}")
            
            # Exécution
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log après l'exécution
                if show_result:
                    log(
                        f"{func.__name__} terminé en {duration:.2f}s "
                        f"avec résultat: {result}"
                    )
                else:
                    log(f"{func.__name__} terminé en {duration:.2f}s")
                    
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"{func.__name__} échoué après {duration:.2f}s: {e}"
                )
                raise
                
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator 