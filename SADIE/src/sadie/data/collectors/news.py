"""
Module de collecte d'actualités en temps réel.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta

import aiohttp
from textblob import TextBlob

from sadie.data.collectors.base import BaseCollector
from sadie.data.config import DataConfig

logger = logging.getLogger(__name__)

class NewsCollector(BaseCollector):
    """Collecteur d'actualités avec support de NewsAPI."""
    
    def __init__(
        self,
        api_key: str,
        window_size: int = 1000,
        update_interval: float = 300.0,
        languages: Optional[List[str]] = None
    ):
        """
        Initialise le collecteur d'actualités.
        
        Args:
            api_key: Clé API NewsAPI
            window_size: Taille de la fenêtre de cache
            update_interval: Intervalle de mise à jour en secondes
            languages: Liste des langues (par défaut: en, fr)
        """
        super().__init__(api_key, None)
        self.window_size = window_size
        self.update_interval = update_interval
        self.languages = languages or ["en", "fr"]
        self.articles = {}
        self._running = False
        self._stream_tasks = {}
        self.base_url = "https://newsapi.org/v2"
        
    async def start_stream(self, symbols: List[str], callback: Callable) -> None:
        """
        Démarre le flux d'actualités en temps réel.
        
        Args:
            symbols: Liste des symboles à suivre
            callback: Fonction de callback pour les nouvelles actualités
        """
        if not self._running:
            self._running = True
            
            # Créer une tâche de streaming pour chaque symbole
            for symbol in symbols:
                task = asyncio.create_task(
                    self._maintain_stream(symbol, callback)
                )
                self._stream_tasks[symbol] = task
                
    async def stop_stream(self) -> None:
        """Arrête le flux d'actualités."""
        if self._running:
            self._running = False
            
            # Arrêter toutes les tâches de streaming
            for task in self._stream_tasks.values():
                task.cancel()
            self._stream_tasks.clear()
            
    async def get_historical_news(
        self,
        symbol: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Récupère les actualités historiques pour un symbole.
        
        Args:
            symbol: Symbole (ex: "BTC/USDT")
            start_time: Date de début
            end_time: Date de fin (optionnel)
            limit: Nombre maximum d'articles à récupérer
            
        Returns:
            Liste d'articles avec leur sentiment
        """
        base_asset = symbol.split('/')[0].lower()
        articles = []
        
        try:
            async with aiohttp.ClientSession() as session:
                # Construire la requête
                params = {
                    'q': f"{base_asset} OR cryptocurrency OR crypto",
                    'apiKey': self.api_key,
                    'language': ','.join(self.languages),
                    'sortBy': 'publishedAt',
                    'pageSize': min(limit, 100)  # Maximum 100 par requête
                }
                
                if end_time:
                    params['to'] = end_time.isoformat()
                params['from'] = start_time.isoformat()
                
                # Faire la requête
                async with session.get(
                    f"{self.base_url}/everything",
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for article in data.get('articles', []):
                            # Analyser le sentiment
                            text = f"{article['title']} {article.get('description', '')}"
                            sentiment = TextBlob(text).sentiment
                            
                            articles.append({
                                'title': article['title'],
                                'description': article.get('description', ''),
                                'url': article['url'],
                                'source': article['source']['name'],
                                'published_at': datetime.fromisoformat(
                                    article['publishedAt'].replace('Z', '+00:00')
                                ),
                                'polarity': sentiment.polarity,
                                'subjectivity': sentiment.subjectivity
                            })
                            
            return articles
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des actualités: {str(e)}")
            return []
            
    async def _maintain_stream(self, symbol: str, callback: Callable) -> None:
        """
        Maintient le flux d'actualités pour un symbole.
        
        Args:
            symbol: Symbole à suivre
            callback: Fonction de callback pour les nouvelles actualités
        """
        base_asset = symbol.split('/')[0].lower()
        last_update = datetime.utcnow()
        
        while self._running:
            try:
                # Récupérer les nouvelles actualités depuis la dernière mise à jour
                articles = await self.get_historical_news(
                    symbol=symbol,
                    start_time=last_update,
                    limit=100
                )
                
                # Mettre à jour le cache et appeler les callbacks
                if symbol not in self.articles:
                    self.articles[symbol] = []
                    
                for article in articles:
                    self.articles[symbol].append(article)
                    await callback(symbol, article)
                    
                # Maintenir la taille de la fenêtre
                if len(self.articles[symbol]) > self.window_size:
                    self.articles[symbol] = self.articles[symbol][-self.window_size:]
                    
                # Mettre à jour le timestamp
                last_update = datetime.utcnow()
                
                # Attendre avant la prochaine mise à jour
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Erreur dans le stream d'actualités: {str(e)}")
                await asyncio.sleep(self.update_interval)
                
    async def get_news_metrics(self, symbol: str) -> Dict:
        """
        Calcule les métriques d'actualités pour un symbole.
        
        Args:
            symbol: Symbole
            
        Returns:
            Dictionnaire des métriques d'actualités
        """
        if symbol not in self.articles or not self.articles[symbol]:
            return {
                'average_polarity': 0.0,
                'average_subjectivity': 0.0,
                'article_count': 0,
                'source_diversity': 0.0,
                'bullish_ratio': 0.0,
                'hourly_volume': 0.0
            }
            
        articles = self.articles[symbol]
        polarities = [a['polarity'] for a in articles]
        subjectivities = [a['subjectivity'] for a in articles]
        sources = set(a['source'] for a in articles)
        bullish_count = sum(1 for p in polarities if p > 0)
        
        # Calculer le volume horaire
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        hourly_articles = [
            a for a in articles 
            if a['published_at'] >= hour_ago
        ]
        
        return {
            'average_polarity': sum(polarities) / len(articles),
            'average_subjectivity': sum(subjectivities) / len(articles),
            'article_count': len(articles),
            'source_diversity': len(sources) / len(articles),  # Normalisé entre 0 et 1
            'bullish_ratio': bullish_count / len(articles),
            'hourly_volume': len(hourly_articles)
        } 