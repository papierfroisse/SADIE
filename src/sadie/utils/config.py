"""
Gestion de la configuration.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger(__name__)

class Config:
    """Gestionnaire de configuration."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialise le gestionnaire de configuration.

        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.config_path = config_path or os.getenv("SADIE_CONFIG", "config/config.yml")
        self.config: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        """Charge la configuration depuis le fichier."""
        try:
            path = Path(self.config_path)
            if not path.exists():
                logger.warning(f"Fichier de configuration non trouvé: {self.config_path}")
                return
            
            with path.open("r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}
            
            logger.info(f"Configuration chargée depuis {self.config_path}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration: {e}")
            self.config = {}
    
    def save(self) -> None:
        """Sauvegarde la configuration dans le fichier."""
        try:
            path = Path(self.config_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with path.open("w", encoding="utf-8") as f:
                yaml.safe_dump(self.config, f, default_flow_style=False)
            
            logger.info(f"Configuration sauvegardée dans {self.config_path}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la configuration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Récupère une valeur de configuration.

        Args:
            key: Clé de configuration
            default: Valeur par défaut

        Returns:
            Valeur de configuration
        """
        try:
            value = self.config
            for part in key.split("."):
                value = value[part]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Définit une valeur de configuration.

        Args:
            key: Clé de configuration
            value: Valeur à définir
        """
        parts = key.split(".")
        config = self.config
        
        for part in parts[:-1]:
            if part not in config or not isinstance(config[part], dict):
                config[part] = {}
            config = config[part]
        
        config[parts[-1]] = value
    
    def update(self, config: Dict[str, Any]) -> None:
        """
        Met à jour la configuration.

        Args:
            config: Nouvelles valeurs de configuration
        """
        def deep_update(d: Dict[str, Any], u: Dict[str, Any]) -> Dict[str, Any]:
            for k, v in u.items():
                if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                    d[k] = deep_update(d[k], v)
                else:
                    d[k] = v
            return d
        
        self.config = deep_update(self.config, config)
    
    def reset(self) -> None:
        """Réinitialise la configuration."""
        self.config = {}
        self.save()

# Configuration par défaut
default_config = {
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "logs/sadie.log"
    },
    "data": {
        "collectors": {
            "websocket": {
                "reconnect_delay": 5,
                "max_retries": 3
            },
            "rest": {
                "timeout": 10,
                "rate_limit": 60
            }
        },
        "storage": {
            "type": "memory",
            "path": "data"
        }
    },
    "analysis": {
        "window_size": 20,
        "confidence_level": 0.95
    }
}

# Instance globale de configuration
config = Config()

# Initialisation avec la configuration par défaut
if not config.config:
    config.update(default_config)
    config.save() 