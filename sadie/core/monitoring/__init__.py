"""Module de monitoring."""

import logging
import sys
from typing import Optional

def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """Crée un logger configuré.
    
    Args:
        name: Nom du logger
        level: Niveau de log optionnel
        
    Returns:
        Logger configuré
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
        logger.addHandler(handler)
    
    if level:
        logger.setLevel(level)
    elif not logger.level:
        logger.setLevel(logging.INFO)
    
    return logger
