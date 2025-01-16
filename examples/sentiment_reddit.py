"""Exemple d'utilisation du collecteur de sentiment Reddit."""

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
        "reddit_client_id": os.getenv("REDDIT_CLIENT_ID"),
        "reddit_client_secret": os.getenv("REDDIT_CLIENT_SECRET"),
        "reddit_username": os.getenv("REDDIT_USERNAME", "SADIE_Bot")
    }
    
    # Initialisation des collecteurs
    collector = SentimentCollector(
        name="reddit_sentiment",
        symbols=symbols,
        sources=[SentimentSource.REDDIT],
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
                
            scores = collector._scores[symbol][SentimentSource.REDDIT]
            analysis = analyzer.analyze_symbol(symbol, scores)
            
            print(f"\nAnalyse pour {symbol}:")
            print(json.dumps(analysis, indent=2, ensure_ascii=False))
            
            # Affichage des subreddits utilisés
            if scores and scores[-1].metadata.get("subreddits"):
                print("\nSubreddits analysés:")
                for subreddit in scores[-1].metadata["subreddits"]:
                    print(f"- r/{subreddit}")
            
    except Exception as e:
        print(f"Erreur: {e}")
        
if __name__ == "__main__":
    asyncio.run(main()) 