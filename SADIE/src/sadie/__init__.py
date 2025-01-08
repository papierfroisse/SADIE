"""
SADIE - Système d'Analyse et de Décision pour l'Investissement en Cryptomonnaies.

Ce package fournit des outils avancés pour :
- Collecte de données multi-sources (marchés, réseaux sociaux, blockchain)
- Analyse de sentiments et traitement du langage naturel
- Calcul d'indicateurs techniques et fondamentaux
- Modèles prédictifs (LSTM, Transformers, GAN)
- Gestion de portefeuille optimisée
- Backtesting et validation des stratégies

Architecture principale :
- data/ : Gestion des données et connecteurs API
- models/ : Modèles prédictifs et d'optimisation
- analysis/ : Indicateurs et analyses techniques
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Union, Dict, Any

from sadie.data.market import MarketManager
from sadie.exceptions import SADIEConfigError, SADIEInitError

# Configuration du logging avancée
def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Configure le système de logging.
    
    Args:
        log_level: Niveau de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Chemin du fichier de log (optionnel)
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers
    )

logger = logging.getLogger(__name__)

class SADIE:
    """
    Classe principale du système SADIE.
    
    Cette classe gère l'initialisation et la coordination de tous les composants :
    - Gestion des données de marché
    - Modèles prédictifs
    - Analyse technique
    - Optimisation de portefeuille
    """
    
    def __init__(
        self,
        db_url: Optional[str] = None,
        cache_dir: Optional[str] = None,
        max_cache_age: int = 3600,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialise le système SADIE.
        
        Args:
            db_url: URL de connexion à la base de données
            cache_dir: Chemin du répertoire de cache
            max_cache_age: Âge maximum des données en cache (secondes)
            config: Configuration additionnelle (dict)
        
        Raises:
            SADIEConfigError: Erreur de configuration
            SADIEInitError: Erreur d'initialisation
        """
        try:
            # Configuration des chemins
            self.root_dir = Path(__file__).parent.parent.parent
            self.data_dir = self.root_dir / "data"
            self.cache_dir = Path(cache_dir) if cache_dir else self.data_dir / "cache"
            self.db_url = db_url or f"sqlite:///{self.data_dir}/sadie.db"
            
            # Validation de la configuration
            self._validate_config(config or {})
            
            # Création des répertoires
            self._setup_directories()
            
            # Initialisation des composants
            self.market = MarketManager(
                db_url=self.db_url,
                cache_dir=str(self.cache_dir),
                max_cache_age=max_cache_age
            )
            
            logger.info("Système SADIE initialisé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation: {str(e)}")
            raise SADIEInitError(f"Échec de l'initialisation: {str(e)}")
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """
        Valide la configuration fournie.
        
        Args:
            config: Dictionnaire de configuration
            
        Raises:
            SADIEConfigError: Configuration invalide
        """
        required_keys = []  # Liste des clés requises
        for key in required_keys:
            if key not in config:
                raise SADIEConfigError(f"Configuration manquante: {key}")
    
    def _setup_directories(self) -> None:
        """
        Crée et vérifie les répertoires nécessaires.
        
        Raises:
            SADIEInitError: Erreur lors de la création des répertoires
        """
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise SADIEInitError(f"Erreur création répertoires: {str(e)}")
    
    async def start(self) -> None:
        """
        Démarre le système SADIE.
        
        Raises:
            SADIEInitError: Erreur au démarrage
        """
        try:
            await self.market.start()
            logger.info("Système SADIE démarré")
        except Exception as e:
            logger.error(f"Erreur au démarrage: {str(e)}")
            raise SADIEInitError(f"Échec du démarrage: {str(e)}")
    
    async def stop(self) -> None:
        """
        Arrête le système SADIE.
        
        Raises:
            SADIEInitError: Erreur à l'arrêt
        """
        try:
            await self.market.stop()
            logger.info("Système SADIE arrêté")
        except Exception as e:
            logger.error(f"Erreur à l'arrêt: {str(e)}")
            raise SADIEInitError(f"Échec de l'arrêt: {str(e)}")
    
    def clean_old_data(
        self,
        before: Union[str, datetime],
        source: Optional[str] = None,
        symbol: Optional[str] = None
    ) -> None:
        """
        Nettoie les anciennes données.
        
        Args:
            before: Date limite (format ISO ou datetime)
            source: Source des données (optionnel)
            symbol: Symbole (optionnel)
            
        Raises:
            ValueError: Format de date invalide
            SADIEInitError: Erreur pendant le nettoyage
        """
        try:
            if isinstance(before, str):
                before_dt = datetime.fromisoformat(before)
            else:
                before_dt = before
                
            self.market.clean_old_data(before_dt, source, symbol)
            logger.info(f"Données antérieures à {before} nettoyées")
            
        except ValueError as e:
            logger.error(f"Format de date invalide: {str(e)}")
            raise ValueError(f"Format de date invalide: {str(e)}")
        except Exception as e:
            logger.error(f"Erreur pendant le nettoyage: {str(e)}")
            raise SADIEInitError(f"Échec du nettoyage: {str(e)}")

# Version du package
__version__ = "0.1.1" 