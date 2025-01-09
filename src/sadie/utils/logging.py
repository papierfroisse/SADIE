"""
Configuration du logging.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional

from .config import config

def setup_logging(
    level: Optional[str] = None,
    format_str: Optional[str] = None,
    log_file: Optional[str] = None
) -> None:
    """
    Configure le système de logging.

    Args:
        level: Niveau de logging
        format_str: Format des messages
        log_file: Chemin vers le fichier de log
    """
    # Récupération des paramètres depuis la configuration
    level = level or config.get("logging.level", "INFO")
    format_str = format_str or config.get(
        "logging.format",
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    log_file = log_file or config.get("logging.file", "logs/sadie.log")
    
    # Configuration du niveau de logging
    logging.root.setLevel(level)
    
    # Création du formateur
    formatter = logging.Formatter(format_str)
    
    # Configuration du handler pour la console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logging.root.addHandler(console_handler)
    
    # Configuration du handler pour le fichier
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logging.root.addHandler(file_handler)
    
    # Logger de démarrage
    logger = logging.getLogger(__name__)
    logger.info("Logging configuré avec succès")
    logger.debug(f"Niveau: {level}")
    logger.debug(f"Format: {format_str}")
    if log_file:
        logger.debug(f"Fichier: {log_file}")

def get_logger(name: str) -> logging.Logger:
    """
    Récupère un logger configuré.

    Args:
        name: Nom du logger

    Returns:
        Logger configuré
    """
    return logging.getLogger(name) 