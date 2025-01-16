"""Décorateurs utilitaires."""

import asyncio
import functools
import time
from typing import Any, Callable, Optional, TypeVar, Union, cast

from ..core.monitoring import get_logger

logger = get_logger(__name__)

F = TypeVar('F', bound=Callable[..., Any])

def log_execution(func: Optional[F] = None) -> Union[F, Callable[[F], F]]:
    """Décore une fonction pour logger son exécution.
    
    Args:
        func: Fonction à décorer (optionnel)
        
    Returns:
        Fonction décorée ou décorateur
    """
    def decorator(f: F) -> F:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            try:
                result = f(*args, **kwargs)
                duration = time.time() - start_time
                logger.debug(
                    f"{f.__name__} exécuté en {duration:.3f}s"
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Erreur dans {f.__name__} après {duration:.3f}s: {e}"
                )
                raise
        return cast(F, wrapper)
        
    if func is None:
        return decorator
    return decorator(func)

def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable[[F], F]:
    """Décore une fonction pour réessayer en cas d'erreur.
    
    Args:
        max_attempts: Nombre maximum de tentatives
        delay: Délai initial entre les tentatives
        backoff: Facteur multiplicatif du délai
        exceptions: Exceptions à intercepter
        
    Returns:
        Décorateur de fonction
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        raise
                    logger.warning(
                        f"Tentative {attempt + 1}/{max_attempts} "
                        f"échouée pour {func.__name__}: {e}"
                    )
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
                    
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        raise
                    logger.warning(
                        f"Tentative {attempt + 1}/{max_attempts} "
                        f"échouée pour {func.__name__}: {e}"
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff
                    
        return cast(F, async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper)
    return decorator 