"""Exemple d'utilisation du collecteur de sentiment d'actualités."""

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
        "newsapi_key": os.getenv("NEWSAPI_KEY")
    }
    
    # Initialisation des collecteurs
    collector = SentimentCollector(
        name="news_sentiment",
        symbols=symbols,
        sources=[SentimentSource.NEWS],
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
                
            scores = collector._scores[symbol][SentimentSource.NEWS]
            analysis = analyzer.analyze_symbol(symbol, scores)
            
            print(f"\nAnalyse pour {symbol}:")
            print(json.dumps(analysis, indent=2, ensure_ascii=False))
            
            # Affichage des sources d'actualités
            if scores and scores[-1].metadata.get("sources"):
                print("\nSources d'actualités analysées:")
                for source in scores[-1].metadata["sources"]:
                    print(f"- {source}")
                    
            # Affichage des statistiques
            if scores and scores[-1].metadata:
                meta = scores[-1].metadata
                print(f"\nStatistiques:")
                print(f"- Nombre d'articles: {meta.get('article_count', 0)}")
                print(f"- Période analysée: {meta.get('lookback_hours', 24)}h")
            
    except Exception as e:
        print(f"Erreur: {e}")
        
if __name__ == "__main__":
    asyncio.run(main()) 