"""
Module pour les modèles LSTM de prédiction des prix.
"""

import datetime
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler

from sadie.models import BaseModel

class LSTMModel(BaseModel):
    """Modèle LSTM pour la prédiction des prix."""
    
    def __init__(
        self,
        name: str,
        sequence_length: int = 60,
        n_features: Optional[int] = None,
        n_layers: int = 2,
        n_units: int = 50,
        dropout: float = 0.2
    ):
        """
        Initialise le modèle LSTM.
        
        Args:
            name: Nom du modèle
            sequence_length: Longueur des séquences d'entrée
            n_features: Nombre de caractéristiques (calculé automatiquement si None)
            n_layers: Nombre de couches LSTM
            n_units: Nombre d'unités par couche
            dropout: Taux de dropout
        """
        super().__init__(name)
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.n_layers = n_layers
        self.n_units = n_units
        self.dropout = dropout
        
        self.model = None
        self.scaler = MinMaxScaler()
        self.feature_columns = None
    
    def _build_model(self) -> None:
        """Construit l'architecture du modèle."""
        if not self.n_features:
            raise ValueError("n_features doit être défini avant de construire le modèle")
        
        self.model = tf.keras.Sequential()
        
        # Première couche LSTM
        self.model.add(tf.keras.layers.LSTM(
            units=self.n_units,
            return_sequences=self.n_layers > 1,
            input_shape=(self.sequence_length, self.n_features)
        ))
        self.model.add(tf.keras.layers.Dropout(self.dropout))
        
        # Couches LSTM intermédiaires
        for i in range(self.n_layers - 2):
            self.model.add(tf.keras.layers.LSTM(
                units=self.n_units,
                return_sequences=True
            ))
            self.model.add(tf.keras.layers.Dropout(self.dropout))
        
        # Dernière couche LSTM
        if self.n_layers > 1:
            self.model.add(tf.keras.layers.LSTM(units=self.n_units))
            self.model.add(tf.keras.layers.Dropout(self.dropout))
        
        # Couche de sortie
        self.model.add(tf.keras.layers.Dense(units=1))
        
        # Compilation
        self.model.compile(
            optimizer="adam",
            loss="mse",
            metrics=["mae"]
        )
    
    def _create_sequences(
        self,
        data: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Crée les séquences pour l'entraînement.
        
        Args:
            data: Données normalisées
            
        Returns:
            Tuple contenant les séquences X et y
        """
        X, y = [], []
        for i in range(len(data) - self.sequence_length):
            X.append(data[i:(i + self.sequence_length)])
            y.append(data[i + self.sequence_length, 0])
        return np.array(X), np.array(y)
    
    def preprocess(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prétraite les données pour le modèle.
        
        Args:
            data: DataFrame contenant les données brutes
            
        Returns:
            DataFrame contenant les données prétraitées
        """
        # Sélection des caractéristiques
        if self.feature_columns is None:
            self.feature_columns = [
                "close", "volume",
                "rsi", "macd", "bb_width",
                "adx", "cci", "mfi"
            ]
        
        # Vérification des colonnes
        missing = [col for col in self.feature_columns if col not in data.columns]
        if missing:
            raise ValueError(f"Colonnes manquantes: {missing}")
        
        # Mise à jour du nombre de caractéristiques
        if not self.n_features:
            self.n_features = len(self.feature_columns)
        
        return data[self.feature_columns].copy()
    
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
        # Prétraitement
        processed_data = self.preprocess(data)
        
        # Normalisation
        scaled_data = self.scaler.fit_transform(processed_data)
        
        # Création des séquences
        X, y = self._create_sequences(scaled_data)
        
        # Construction du modèle si nécessaire
        if not self.model:
            self._build_model()
        
        # Entraînement
        history = self.model.fit(
            X, y,
            validation_split=validation_split,
            epochs=epochs,
            batch_size=batch_size,
            verbose=1,
            **kwargs
        )
        
        self._is_trained = True
        
        return {
            "loss": history.history["loss"][-1],
            "val_loss": history.history["val_loss"][-1],
            "mae": history.history["mae"][-1],
            "val_mae": history.history["val_mae"][-1]
        }
    
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
        
        # Prétraitement
        processed_data = self.preprocess(data)
        
        # Normalisation
        scaled_data = self.scaler.transform(processed_data)
        
        # Création des séquences
        X = np.array([scaled_data[-self.sequence_length:]])
        
        # Prédiction
        scaled_pred = self.model.predict(X, verbose=0)
        
        # Dénormalisation
        pred = self.scaler.inverse_transform(
            np.concatenate([scaled_pred, np.zeros((1, self.n_features - 1))], axis=1)
        )
        
        return pd.DataFrame(
            {"predicted_close": pred[:, 0]},
            index=[data.index[-1] + pd.Timedelta(days=1)]
        )
    
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
        # Alignement des données
        common_index = data.index.intersection(predictions.index)
        if len(common_index) == 0:
            raise ValueError("Aucune donnée commune entre réel et prédictions")
        
        y_true = data.loc[common_index, "close"]
        y_pred = predictions.loc[common_index, "predicted_close"]
        
        # Calcul des métriques
        mse = np.mean((y_true - y_pred) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(y_true - y_pred))
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        
        return {
            "mse": mse,
            "rmse": rmse,
            "mae": mae,
            "mape": mape
        }
    
    def save(self, path: str) -> None:
        """
        Sauvegarde le modèle.
        
        Args:
            path: Chemin de sauvegarde
        """
        if not self.is_trained:
            raise RuntimeError("Le modèle doit être entraîné avant d'être sauvegardé")
        
        # Sauvegarde du modèle Keras
        self.model.save(f"{path}_keras")
        
        # Sauvegarde des paramètres et du scaler
        import joblib
        params = {
            "sequence_length": self.sequence_length,
            "n_features": self.n_features,
            "n_layers": self.n_layers,
            "n_units": self.n_units,
            "dropout": self.dropout,
            "feature_columns": self.feature_columns,
            "scaler": self.scaler
        }
        joblib.dump(params, f"{path}_params.joblib")
    
    def load(self, path: str) -> None:
        """
        Charge le modèle.
        
        Args:
            path: Chemin du modèle à charger
        """
        # Chargement du modèle Keras
        self.model = tf.keras.models.load_model(f"{path}_keras")
        
        # Chargement des paramètres et du scaler
        import joblib
        params = joblib.load(f"{path}_params.joblib")
        
        self.sequence_length = params["sequence_length"]
        self.n_features = params["n_features"]
        self.n_layers = params["n_layers"]
        self.n_units = params["n_units"]
        self.dropout = params["dropout"]
        self.feature_columns = params["feature_columns"]
        self.scaler = params["scaler"]
        
        self._is_trained = True 