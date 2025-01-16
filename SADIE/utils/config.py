"""Module de configuration pour SADIE."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from . import deep_get, deep_update, load_json, save_json
from ..monitoring import get_logger

logger = get_logger(__name__)

class Config:
    """Gestionnaire de configuration."""
    
    def __init__(
        self,
        config_dir: Optional[str] = None,
        env_prefix: str = "SADIE_"
    ):
        self._config: Dict[str, Any] = {}
        self._config_dir = Path(config_dir or os.getenv("SADIE_CONFIG_DIR", "config"))
        self._env_prefix = env_prefix
        self.logger = get_logger(__name__)
        
        # Charge la configuration par défaut
        self.load_defaults()
        
        # Charge la configuration depuis les fichiers
        self.load_from_files()
        
        # Charge la configuration depuis les variables d'environnement
        self.load_from_env()
    
    def load_defaults(self) -> None:
        """Charge la configuration par défaut."""
        self._config = {
            "app": {
                "name": "SADIE",
                "version": "0.1.0",
                "debug": False,
                "log_level": "INFO"
            },
            "database": {
                "url": "postgresql+asyncpg://postgres:postgres@localhost/sadie",
                "pool_size": 20,
                "max_overflow": 10,
                "pool_timeout": 30
            },
            "cache": {
                "type": "memory",
                "redis_url": "redis://localhost",
                "prefix": "sadie:",
                "ttl": 3600
            },
            "api": {
                "host": "0.0.0.0",
                "port": 8000,
                "workers": 4,
                "cors_origins": ["*"],
                "rate_limit": 100
            }
        }
    
    def load_from_files(self) -> None:
        """Charge la configuration depuis les fichiers."""
        try:
            # Configuration de base
            base_config = self._config_dir / "config.json"
            if base_config.exists():
                self._config = deep_update(
                    self._config,
                    load_json(base_config)
                )
                self.logger.info(f"Configuration chargée depuis {base_config}")
            
            # Configuration spécifique à l'environnement
            env = os.getenv("SADIE_ENV", "development")
            env_config = self._config_dir / f"config.{env}.json"
            if env_config.exists():
                self._config = deep_update(
                    self._config,
                    load_json(env_config)
                )
                self.logger.info(f"Configuration {env} chargée depuis {env_config}")
                
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement des fichiers de config: {e}")
    
    def load_from_env(self) -> None:
        """Charge la configuration depuis les variables d'environnement."""
        for key, value in os.environ.items():
            if key.startswith(self._env_prefix):
                # Convertit SADIE_DATABASE_URL en database.url
                config_key = key[len(self._env_prefix):].lower().replace("_", ".")
                self.set(config_key, value)
                self.logger.debug(f"Configuration mise à jour depuis {key}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur de configuration."""
        return deep_get(self._config, key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Définit une valeur de configuration."""
        keys = key.split(".")
        current = self._config
        for k in keys[:-1]:
            current = current.setdefault(k, {})
        current[keys[-1]] = value
        self.logger.debug(f"Configuration mise à jour: {key}={value}")
    
    def save(self) -> None:
        """Sauvegarde la configuration actuelle."""
        try:
            self._config_dir.mkdir(parents=True, exist_ok=True)
            config_file = self._config_dir / "config.json"
            save_json(self._config, config_file)
            self.logger.info(f"Configuration sauvegardée dans {config_file}")
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde de la config: {e}")
    
    @property
    def config(self) -> Dict[str, Any]:
        """Retourne la configuration complète."""
        return self._config.copy()

# Instance globale de configuration
config = Config() 