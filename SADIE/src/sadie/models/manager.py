"""
Module de gestion des modèles.
"""

import datetime
import logging
from pathlib import Path
from typing import Dict, List, Optional, Type, Union

import pandas as pd

from sadie.models import BaseModel
from sadie.models.lstm import LSTMModel
from sadie.models.sentiment import SentimentModel
from sadie.models.hybrid import HybridModel

logger = logging.getLogger(__name__)

class ModelManager:
    """Gestionnaire de modèles."""
    
    MODEL_TYPES = {
        "lstm": LSTMModel,
        "sentiment": SentimentModel,
        "hybrid": HybridModel
    }
    
    def __init__(self, models_dir: Union[str, Path]):
        """
        Initialise le gestionnaire de modèles.
        
        Args:
            models_dir: Chemin du répertoire des modèles
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.models: Dict[str, BaseModel] = {}
    
    def create_model(
        self,
        name: str,
        model_type: str,
        **kwargs
    ) -> BaseModel:
        """
        Crée un nouveau modèle.
        
        Args:
            name: Nom du modèle
            model_type: Type de modèle ("lstm", "sentiment", "hybrid")
            **kwargs: Arguments spécifiques au modèle
            
        Returns:
            Instance du modèle créé
            
        Raises:
            ValueError: Si le type de modèle n'est pas supporté
        """
        if model_type not in self.MODEL_TYPES:
            raise ValueError(
                f"Type de modèle non supporté: {model_type}. "
                f"Types disponibles: {', '.join(self.MODEL_TYPES.keys())}"
            )
        
        model_class = self.MODEL_TYPES[model_type]
        model = model_class(name=name, **kwargs)
        
        self.models[name] = model
        logger.info(f"Modèle créé: {name} ({model_type})")
        
        return model
    
    def get_model(self, name: str) -> Optional[BaseModel]:
        """
        Récupère un modèle par son nom.
        
        Args:
            name: Nom du modèle
            
        Returns:
            Instance du modèle ou None si non trouvé
        """
        return self.models.get(name)
    
    def list_models(self) -> List[str]:
        """
        Liste les modèles disponibles.
        
        Returns:
            Liste des noms des modèles
        """
        return list(self.models.keys())
    
    def train_model(
        self,
        name: str,
        data: pd.DataFrame,
        **kwargs
    ) -> Dict[str, float]:
        """
        Entraîne un modèle.
        
        Args:
            name: Nom du modèle
            data: DataFrame contenant les données d'entraînement
            **kwargs: Arguments pour l'entraînement
            
        Returns:
            Dictionnaire contenant les métriques d'entraînement
            
        Raises:
            ValueError: Si le modèle n'existe pas
        """
        model = self.get_model(name)
        if not model:
            raise ValueError(f"Modèle non trouvé: {name}")
        
        logger.info(f"Début de l'entraînement du modèle {name}")
        metrics = model.train(data, **kwargs)
        logger.info(f"Entraînement terminé. Métriques: {metrics}")
        
        return metrics
    
    def predict(
        self,
        name: str,
        data: pd.DataFrame,
        **kwargs
    ) -> pd.DataFrame:
        """
        Génère des prédictions avec un modèle.
        
        Args:
            name: Nom du modèle
            data: DataFrame contenant les données d'entrée
            **kwargs: Arguments pour la prédiction
            
        Returns:
            DataFrame contenant les prédictions
            
        Raises:
            ValueError: Si le modèle n'existe pas
        """
        model = self.get_model(name)
        if not model:
            raise ValueError(f"Modèle non trouvé: {name}")
        
        if not model.is_trained:
            raise RuntimeError(f"Le modèle {name} doit être entraîné avant de faire des prédictions")
        
        return model.predict(data, **kwargs)
    
    def evaluate(
        self,
        name: str,
        data: pd.DataFrame,
        predictions: pd.DataFrame,
        **kwargs
    ) -> Dict[str, float]:
        """
        Évalue les performances d'un modèle.
        
        Args:
            name: Nom du modèle
            data: DataFrame contenant les données réelles
            predictions: DataFrame contenant les prédictions
            **kwargs: Arguments pour l'évaluation
            
        Returns:
            Dictionnaire contenant les métriques d'évaluation
            
        Raises:
            ValueError: Si le modèle n'existe pas
        """
        model = self.get_model(name)
        if not model:
            raise ValueError(f"Modèle non trouvé: {name}")
        
        return model.evaluate(data, predictions, **kwargs)
    
    def save_model(
        self,
        name: str,
        version: Optional[str] = None
    ) -> None:
        """
        Sauvegarde un modèle.
        
        Args:
            name: Nom du modèle
            version: Version du modèle (optionnel)
            
        Raises:
            ValueError: Si le modèle n'existe pas
        """
        model = self.get_model(name)
        if not model:
            raise ValueError(f"Modèle non trouvé: {name}")
        
        # Génération du nom de version si non spécifié
        if not version:
            version = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Création du répertoire pour le modèle
        model_dir = self.models_dir / name
        model_dir.mkdir(exist_ok=True)
        
        # Sauvegarde du modèle
        model_path = model_dir / f"v{version}"
        model.save(str(model_path))
        
        logger.info(f"Modèle {name} sauvegardé (version {version})")
    
    def load_model(
        self,
        name: str,
        version: Optional[str] = None,
        model_type: Optional[str] = None,
        **kwargs
    ) -> BaseModel:
        """
        Charge un modèle.
        
        Args:
            name: Nom du modèle
            version: Version du modèle (optionnel, dernière version par défaut)
            model_type: Type de modèle (requis si le modèle n'existe pas)
            **kwargs: Arguments pour l'initialisation du modèle
            
        Returns:
            Instance du modèle chargé
            
        Raises:
            ValueError: Si le modèle ou la version n'existe pas
        """
        # Vérification du répertoire du modèle
        model_dir = self.models_dir / name
        if not model_dir.exists():
            raise ValueError(f"Modèle non trouvé: {name}")
        
        # Recherche de la dernière version si non spécifiée
        if not version:
            versions = sorted(
                [p.name for p in model_dir.glob("v*")],
                reverse=True
            )
            if not versions:
                raise ValueError(f"Aucune version trouvée pour le modèle {name}")
            version = versions[0].replace("v", "")
        
        # Création ou récupération du modèle
        model = self.get_model(name)
        if not model:
            if not model_type:
                raise ValueError("Le type de modèle doit être spécifié pour charger un nouveau modèle")
            model = self.create_model(name, model_type, **kwargs)
        
        # Chargement du modèle
        model_path = model_dir / f"v{version}"
        model.load(str(model_path))
        
        logger.info(f"Modèle {name} chargé (version {version})")
        return model
    
    def delete_model(
        self,
        name: str,
        version: Optional[str] = None
    ) -> None:
        """
        Supprime un modèle.
        
        Args:
            name: Nom du modèle
            version: Version du modèle (optionnel, toutes les versions si None)
            
        Raises:
            ValueError: Si le modèle n'existe pas
        """
        model_dir = self.models_dir / name
        if not model_dir.exists():
            raise ValueError(f"Modèle non trouvé: {name}")
        
        if version:
            # Suppression d'une version spécifique
            version_path = model_dir / f"v{version}"
            if not version_path.exists():
                raise ValueError(f"Version {version} non trouvée pour le modèle {name}")
            
            import shutil
            shutil.rmtree(version_path)
            logger.info(f"Version {version} du modèle {name} supprimée")
            
            # Suppression du répertoire du modèle s'il est vide
            if not any(model_dir.iterdir()):
                model_dir.rmdir()
        else:
            # Suppression de toutes les versions
            import shutil
            shutil.rmtree(model_dir)
            logger.info(f"Modèle {name} et toutes ses versions supprimés")
        
        # Suppression de l'instance en mémoire
        self.models.pop(name, None) 