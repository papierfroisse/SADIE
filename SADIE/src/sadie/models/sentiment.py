"""
Module pour l'analyse des sentiments.
"""

from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd
from textblob import TextBlob
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    pipeline
)
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from sadie.models import BaseModel

class SentimentModel(BaseModel):
    """Modèle d'analyse des sentiments."""
    
    MODELS = {
        "finbert": "ProsusAI/finbert",
        "roberta": "cardiffnlp/twitter-roberta-base-sentiment",
        "vader": "vader",
        "textblob": "textblob"
    }
    
    def __init__(
        self,
        name: str,
        model_type: str = "finbert",
        device: str = "cpu"
    ):
        """
        Initialise le modèle d'analyse des sentiments.
        
        Args:
            name: Nom du modèle
            model_type: Type de modèle ("finbert", "roberta", "vader", "textblob")
            device: Périphérique de calcul ("cpu" ou "cuda")
        """
        super().__init__(name)
        
        if model_type not in self.MODELS:
            raise ValueError(f"Type de modèle non supporté: {model_type}")
        
        self.model_type = model_type
        self.device = device
        self.model = None
        self.tokenizer = None
        
        # Initialisation immédiate pour les modèles légers
        if model_type in ["vader", "textblob"]:
            self._initialize_model()
            self._is_trained = True
    
    def _initialize_model(self) -> None:
        """Initialise le modèle de traitement du langage naturel."""
        if self.model_type == "vader":
            self.model = SentimentIntensityAnalyzer()
        
        elif self.model_type == "textblob":
            self.model = TextBlob
        
        else:
            model_name = self.MODELS[self.model_type]
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.to(self.device)
            
            self.pipeline = pipeline(
                "sentiment-analysis",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1
            )
    
    def _analyze_vader(self, text: str) -> Dict[str, float]:
        """
        Analyse le sentiment avec VADER.
        
        Args:
            text: Texte à analyser
            
        Returns:
            Dictionnaire contenant les scores de sentiment
        """
        scores = self.model.polarity_scores(text)
        return {
            "negative": scores["neg"],
            "neutral": scores["neu"],
            "positive": scores["pos"],
            "compound": scores["compound"]
        }
    
    def _analyze_textblob(self, text: str) -> Dict[str, float]:
        """
        Analyse le sentiment avec TextBlob.
        
        Args:
            text: Texte à analyser
            
        Returns:
            Dictionnaire contenant les scores de sentiment
        """
        blob = self.model(text)
        return {
            "polarity": blob.sentiment.polarity,
            "subjectivity": blob.sentiment.subjectivity
        }
    
    def _analyze_transformer(self, text: str) -> Dict[str, float]:
        """
        Analyse le sentiment avec un modèle Transformer.
        
        Args:
            text: Texte à analyser
            
        Returns:
            Dictionnaire contenant les scores de sentiment
        """
        result = self.pipeline(text)[0]
        return {
            "label": result["label"],
            "score": result["score"]
        }
    
    def preprocess(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prétraite les données pour le modèle.
        
        Args:
            data: DataFrame contenant les données brutes
            
        Returns:
            DataFrame contenant les données prétraitées
        """
        if "text" not in data.columns:
            raise ValueError("La colonne 'text' est requise")
        
        # Nettoyage basique du texte
        df = data.copy()
        df["text"] = df["text"].str.lower()
        df["text"] = df["text"].str.replace(r"http\S+|www.\S+", "", regex=True)
        df["text"] = df["text"].str.replace(r"[^\w\s]", "", regex=True)
        
        return df
    
    def train(
        self,
        data: pd.DataFrame,
        **kwargs
    ) -> Dict[str, float]:
        """
        Entraîne le modèle.
        Note: Cette méthode n'est pas utilisée car nous utilisons des modèles pré-entraînés.
        
        Args:
            data: DataFrame contenant les données d'entraînement
            **kwargs: Arguments additionnels pour l'entraînement
            
        Returns:
            Dictionnaire vide (pas d'entraînement)
        """
        if not self.model:
            self._initialize_model()
            self._is_trained = True
        return {}
    
    def predict(
        self,
        data: pd.DataFrame,
        batch_size: int = 32,
        **kwargs
    ) -> pd.DataFrame:
        """
        Génère des prédictions de sentiment.
        
        Args:
            data: DataFrame contenant les textes à analyser
            batch_size: Taille des batchs pour les modèles Transformer
            **kwargs: Arguments additionnels pour la prédiction
            
        Returns:
            DataFrame contenant les scores de sentiment
        """
        if not self.is_trained:
            raise RuntimeError("Le modèle doit être initialisé")
        
        # Prétraitement
        processed_data = self.preprocess(data)
        
        # Analyse des sentiments
        results = []
        for text in processed_data["text"]:
            if self.model_type == "vader":
                sentiment = self._analyze_vader(text)
            elif self.model_type == "textblob":
                sentiment = self._analyze_textblob(text)
            else:
                sentiment = self._analyze_transformer(text)
            results.append(sentiment)
        
        # Conversion en DataFrame
        sentiment_df = pd.DataFrame(results, index=data.index)
        
        return sentiment_df
    
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
        if "sentiment" not in data.columns:
            raise ValueError("La colonne 'sentiment' est requise pour l'évaluation")
        
        metrics = {}
        
        if self.model_type in ["vader", "textblob"]:
            # Calcul de la corrélation pour les scores continus
            for col in predictions.columns:
                correlation = data["sentiment"].corr(predictions[col])
                metrics[f"correlation_{col}"] = correlation
        
        else:
            # Calcul de l'exactitude pour les prédictions catégorielles
            accuracy = (data["sentiment"] == predictions["label"]).mean()
            metrics["accuracy"] = accuracy
        
        return metrics
    
    def save(self, path: str) -> None:
        """
        Sauvegarde le modèle.
        Note: Cette méthode n'est pas nécessaire car nous utilisons des modèles pré-entraînés.
        
        Args:
            path: Chemin de sauvegarde
        """
        pass
    
    def load(self, path: str) -> None:
        """
        Charge le modèle.
        Note: Cette méthode n'est pas nécessaire car nous utilisons des modèles pré-entraînés.
        
        Args:
            path: Chemin du modèle à charger
        """
        pass 