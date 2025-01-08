"""
Module d'analyse et de prédiction.

Ce module fournit des outils pour :
- L'analyse des données de marché
- La prédiction des prix
- L'analyse des sentiments
- La génération de signaux de trading
"""

from abc import ABC, abstractmethod
import datetime
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd

class BaseModel(ABC):
    """Classe de base pour les modèles d'analyse et de prédiction."""
    
    def __init__(self, name: str):
        """
        Initialise le modèle.
        
        Args:
            name: Nom du modèle
        """
        self.name = name
        self._is_trained = False
    
    @property
    def is_trained(self) -> bool:
        """Indique si le modèle est entraîné."""
        return self._is_trained
    
    @abstractmethod
    def preprocess(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prétraite les données pour le modèle.
        
        Args:
            data: DataFrame contenant les données brutes
            
        Returns:
            DataFrame contenant les données prétraitées
        """
        pass
    
    @abstractmethod
    def train(
        self,
        data: pd.DataFrame,
        **kwargs
    ) -> Dict[str, float]:
        """
        Entraîne le modèle.
        
        Args:
            data: DataFrame contenant les données d'entraînement
            **kwargs: Arguments additionnels pour l'entraînement
            
        Returns:
            Dictionnaire contenant les métriques d'entraînement
        """
        pass
    
    @abstractmethod
    def predict(
        self,
        data: pd.DataFrame,
        **kwargs
    ) -> pd.DataFrame:
        """
        Génère des prédictions.
        
        Args:
            data: DataFrame contenant les données d'entrée
            **kwargs: Arguments additionnels pour la prédiction
            
        Returns:
            DataFrame contenant les prédictions
        """
        pass
    
    @abstractmethod
    def evaluate(
        self,
        data: pd.DataFrame,
        predictions: pd.DataFrame,
        **kwargs
    ) -> Dict[str, float]:
        """
        Évalue les performances du modèle.
        
        Args:
            data: DataFrame contenant les données réelles
            predictions: DataFrame contenant les prédictions
            **kwargs: Arguments additionnels pour l'évaluation
            
        Returns:
            Dictionnaire contenant les métriques d'évaluation
        """
        pass
    
    def save(self, path: str) -> None:
        """
        Sauvegarde le modèle.
        
        Args:
            path: Chemin de sauvegarde
        """
        raise NotImplementedError("La méthode save() doit être implémentée")
    
    def load(self, path: str) -> None:
        """
        Charge le modèle.
        
        Args:
            path: Chemin du modèle à charger
        """
        raise NotImplementedError("La méthode load() doit être implémentée")
    
    def __str__(self) -> str:
        """Retourne une représentation textuelle du modèle."""
        return f"{self.__class__.__name__}(name={self.name}, trained={self.is_trained})"
    
    def __repr__(self) -> str:
        """Retourne une représentation détaillée du modèle."""
        return self.__str__() 