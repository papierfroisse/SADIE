"""Exemple d'utilisation du collecteur de sentiment Twitter."""

import asyncio
import json
import os
from datetime import datetime

from SADIE.data.sentiment import SentimentCollector, SentimentSource, SentimentAnalyzer

async def main():
    """Point d'entrée principal."""
    # Configuration
    symbols = ["BTC", "ETH", "EUR", "JPY"]
    api_keys = {
        "twitter_api_key": os.getenv("TWITTER_API_KEY"),
        "twitter_api_secret": os.getenv("TWITTER_API_SECRET"),
        "twitter_bearer_token": os.getenv("TWITTER_BEARER_TOKEN")
    }
    
    # Initialisation des collecteurs
    collector = SentimentCollector(
        name="twitter_sentiment",
        symbols=symbols,
        sources=[SentimentSource.TWITTER],
        update_interval=60.0,
        api_keys=api_keys
    )
    
    analyzer = SentimentAnalyzer(window_size=50)
    
    print(f"[{datetime.now()}] Démarrage de la collecte...")
    
    try:
        # Collecte des données
        data = await collector.collect()
        print(f"\nDonnées collectées:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Analyse des données
        for symbol in symbols:
            if symbol not in data:
                continue
                
            scores = collector._scores[symbol][SentimentSource.TWITTER]
            analysis = analyzer.analyze_symbol(symbol, scores)
            
            print(f"\nAnalyse pour {symbol}:")
            print(json.dumps(analysis, indent=2, ensure_ascii=False))
            
    except Exception as e:
        print(f"Erreur: {e}")
        
if __name__ == "__main__":
    asyncio.run(main()) 