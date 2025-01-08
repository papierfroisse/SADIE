"""
Module pour le modèle hybride combinant analyse technique et sentiment.
"""

from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd

from sadie.models import BaseModel
from sadie.models.lstm import LSTMModel
from sadie.models.sentiment import SentimentModel

class HybridModel(BaseModel):
    """Modèle hybride combinant LSTM et analyse des sentiments."""
    
    def __init__(
        self,
        name: str,
        lstm_params: Optional[Dict] = None,
        sentiment_params: Optional[Dict] = None
    ):
        """
        Initialise le modèle hybride.
        
        Args:
            name: Nom du modèle
            lstm_params: Paramètres pour le modèle LSTM
            sentiment_params: Paramètres pour le modèle de sentiment
        """
        super().__init__(name)
        
        # Paramètres par défaut
        self.lstm_params = lstm_params or {
            "sequence_length": 60,
            "n_layers": 2,
            "n_units": 50,
            "dropout": 0.2
        }
        
        self.sentiment_params = sentiment_params or {
            "model_type": "finbert",
            "device": "cpu"
        }
        
        # Initialisation des sous-modèles
        self.lstm_model = LSTMModel(
            name=f"{name}_lstm",
            **self.lstm_params
        )
        
        self.sentiment_model = SentimentModel(
            name=f"{name}_sentiment",
            **self.sentiment_params
        )
        
        # Poids pour la combinaison des prédictions
        self.price_weight = 0.7
        self.sentiment_weight = 0.3
    
    def preprocess(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prétraite les données pour le modèle.
        
        Args:
            data: DataFrame contenant les données brutes
            
        Returns:
            DataFrame contenant les données prétraitées
        """
        # Séparation des données techniques et textuelles
        price_data = data.drop(columns=["text"], errors="ignore")
        text_data = data[["text"]] if "text" in data.columns else None
        
        # Prétraitement des données de prix
        processed_price = self.lstm_model.preprocess(price_data)
        
        # Prétraitement des données textuelles si disponibles
        if text_data is not None:
            processed_text = self.sentiment_model.preprocess(text_data)
            # Fusion des données prétraitées
            return pd.concat([processed_price, processed_text], axis=1)
        
        return processed_price
    
    def train(
        self,
        data: pd.DataFrame,
        validation_split: float = 0.2,
        epochs: int = 100,
        batch_size: int = 32,
        **kwargs
    ) -> Dict[str, float]:
        """
        Entraîne le modèle.
        
        Args:
            data: DataFrame contenant les données d'entraînement
            validation_split: Proportion des données pour la validation
            epochs: Nombre d'époques
            batch_size: Taille des batchs
            **kwargs: Arguments additionnels pour l'entraînement
            
        Returns:
            Dictionnaire contenant les métriques d'entraînement
        """
        # Séparation des données techniques et textuelles
        price_data = data.drop(columns=["text"], errors="ignore")
        text_data = data[["text"]] if "text" in data.columns else None
        
        # Entraînement du modèle LSTM
        lstm_metrics = self.lstm_model.train(
            data=price_data,
            validation_split=validation_split,
            epochs=epochs,
            batch_size=batch_size,
            **kwargs
        )
        
        # Entraînement du modèle de sentiment si des données sont disponibles
        sentiment_metrics = {}
        if text_data is not None:
            sentiment_metrics = self.sentiment_model.train(
                data=text_data,
                **kwargs
            )
        
        # Combinaison des métriques
        metrics = {
            "lstm_" + k: v for k, v in lstm_metrics.items()
        }
        metrics.update({
            "sentiment_" + k: v for k, v in sentiment_metrics.items()
        })
        
        self._is_trained = True
        return metrics
    
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
        if not self.is_trained:
            raise RuntimeError("Le modèle doit être entraîné avant de faire des prédictions")
        
        # Séparation des données techniques et textuelles
        price_data = data.drop(columns=["text"], errors="ignore")
        text_data = data[["text"]] if "text" in data.columns else None
        
        # Prédiction des prix
        price_pred = self.lstm_model.predict(price_data, **kwargs)
        
        # Prédiction du sentiment si des données sont disponibles
        if text_data is not None:
            sentiment_pred = self.sentiment_model.predict(text_data, **kwargs)
            
            # Normalisation du sentiment
            if "compound" in sentiment_pred.columns:
                sentiment_score = sentiment_pred["compound"]
            elif "polarity" in sentiment_pred.columns:
                sentiment_score = sentiment_pred["polarity"]
            else:
                sentiment_score = sentiment_pred["score"]
            
            # Ajustement des prédictions de prix en fonction du sentiment
            sentiment_adjustment = sentiment_score * 0.01  # 1% d'ajustement max
            price_pred["predicted_close"] *= (1 + sentiment_adjustment)
        
        return price_pred
    
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
        # Évaluation des prédictions de prix
        price_metrics = self.lstm_model.evaluate(
            data=data,
            predictions=predictions,
            **kwargs
        )
        
        # Évaluation du sentiment si disponible
        sentiment_metrics = {}
        if "text" in data.columns and "sentiment" in data.columns:
            text_data = data[["text", "sentiment"]]
            sentiment_pred = self.sentiment_model.predict(text_data)
            sentiment_metrics = self.sentiment_model.evaluate(
                data=text_data,
                predictions=sentiment_pred,
                **kwargs
            )
        
        # Combinaison des métriques
        metrics = {
            "price_" + k: v for k, v in price_metrics.items()
        }
        metrics.update({
            "sentiment_" + k: v for k, v in sentiment_metrics.items()
        })
        
        return metrics
    
    def save(self, path: str) -> None:
        """
        Sauvegarde le modèle.
        
        Args:
            path: Chemin de sauvegarde
        """
        if not self.is_trained:
            raise RuntimeError("Le modèle doit être entraîné avant d'être sauvegardé")
        
        # Sauvegarde des sous-modèles
        self.lstm_model.save(f"{path}_lstm")
        self.sentiment_model.save(f"{path}_sentiment")
        
        # Sauvegarde des paramètres
        import joblib
        params = {
            "lstm_params": self.lstm_params,
            "sentiment_params": self.sentiment_params,
            "price_weight": self.price_weight,
            "sentiment_weight": self.sentiment_weight
        }
        joblib.dump(params, f"{path}_params.joblib")
    
    def load(self, path: str) -> None:
        """
        Charge le modèle.
        
        Args:
            path: Chemin du modèle à charger
        """
        # Chargement des sous-modèles
        self.lstm_model.load(f"{path}_lstm")
        self.sentiment_model.load(f"{path}_sentiment")
        
        # Chargement des paramètres
        import joblib
        params = joblib.load(f"{path}_params.joblib")
        
        self.lstm_params = params["lstm_params"]
        self.sentiment_params = params["sentiment_params"]
        self.price_weight = params["price_weight"]
        self.sentiment_weight = params["sentiment_weight"]
        
        self._is_trained = True 