"""
Exemple d'utilisation des modèles d'analyse et de prédiction.
"""

import datetime
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from sadie import SADIE
from sadie.models.manager import ModelManager

def main():
    # Chargement des variables d'environnement
    load_dotenv()
    
    # Initialisation de SADIE
    sadie = SADIE()
    
    # Création du gestionnaire de modèles
    models_dir = Path("models/saved")
    model_manager = ModelManager(models_dir)
    
    # Récupération des données historiques
    market_data = sadie.market.get_market_data(
        symbol="BTC/USDT",
        interval="1h",
        start_time=datetime.datetime.now() - datetime.timedelta(days=30),
        include_sentiment=True,
        include_technical=True
    )
    
    print("\n1. Entraînement du modèle LSTM")
    print("-" * 50)
    
    # Création et entraînement du modèle LSTM
    lstm_model = model_manager.create_model(
        name="btc_lstm",
        model_type="lstm",
        sequence_length=24,  # 24 heures
        n_layers=2,
        n_units=50
    )
    
    lstm_metrics = model_manager.train_model(
        name="btc_lstm",
        data=market_data,
        epochs=10,
        batch_size=32,
        validation_split=0.2
    )
    
    print("Métriques d'entraînement LSTM:")
    for metric, value in lstm_metrics.items():
        print(f"- {metric}: {value:.4f}")
    
    print("\n2. Entraînement du modèle de sentiment")
    print("-" * 50)
    
    # Création du jeu de données pour le sentiment
    news_data = pd.DataFrame({
        "text": [
            "Bitcoin reaches new all-time high as institutional adoption grows",
            "Major cryptocurrency exchange faces regulatory challenges",
            "Bitcoin mining difficulty increases amid growing network activity",
            "Cryptocurrency market shows signs of recovery after recent dip"
        ]
    })
    
    # Création et utilisation du modèle de sentiment
    sentiment_model = model_manager.create_model(
        name="crypto_sentiment",
        model_type="sentiment",
        model_type_name="finbert"
    )
    
    sentiment_predictions = model_manager.predict(
        name="crypto_sentiment",
        data=news_data
    )
    
    print("Analyse des sentiments:")
    for text, sentiment in zip(news_data["text"], sentiment_predictions.itertuples()):
        print(f"\nTexte: {text}")
        for col in sentiment_predictions.columns:
            print(f"- {col}: {getattr(sentiment, col):.4f}")
    
    print("\n3. Utilisation du modèle hybride")
    print("-" * 50)
    
    # Création et entraînement du modèle hybride
    hybrid_model = model_manager.create_model(
        name="btc_hybrid",
        model_type="hybrid",
        lstm_params={
            "sequence_length": 24,
            "n_layers": 2,
            "n_units": 50
        },
        sentiment_params={
            "model_type": "finbert",
            "device": "cpu"
        }
    )
    
    # Ajout des actualités aux données de marché
    market_data_with_news = market_data.copy()
    market_data_with_news["text"] = "Bitcoin trading volume increases as market sentiment improves"
    
    hybrid_metrics = model_manager.train_model(
        name="btc_hybrid",
        data=market_data_with_news,
        epochs=10,
        batch_size=32,
        validation_split=0.2
    )
    
    print("Métriques d'entraînement du modèle hybride:")
    for metric, value in hybrid_metrics.items():
        print(f"- {metric}: {value:.4f}")
    
    # Prédictions avec le modèle hybride
    predictions = model_manager.predict(
        name="btc_hybrid",
        data=market_data_with_news.iloc[-24:]  # Dernières 24 heures
    )
    
    print("\nPrédictions du modèle hybride:")
    print(predictions)
    
    print("\n4. Sauvegarde et chargement des modèles")
    print("-" * 50)
    
    # Sauvegarde des modèles
    model_manager.save_model("btc_lstm")
    model_manager.save_model("crypto_sentiment")
    model_manager.save_model("btc_hybrid")
    
    print("Modèles sauvegardés avec succès")
    
    # Chargement d'un modèle
    loaded_model = model_manager.load_model(
        name="btc_hybrid",
        model_type="hybrid"  # Requis seulement si le modèle n'existe pas en mémoire
    )
    
    print("Modèle hybride chargé avec succès")
    
    # Liste des modèles disponibles
    print("\nModèles disponibles:")
    for model_name in model_manager.list_models():
        model = model_manager.get_model(model_name)
        print(f"- {model_name} ({model.__class__.__name__})")

if __name__ == "__main__":
    main() 