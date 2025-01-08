"""
Module de collecte de données Reddit pour l'analyse communautaire.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta

import praw
from textblob import TextBlob

from sadie.data.collectors.base import BaseCollector
from sadie.data.config import DataConfig

logger = logging.getLogger(__name__)

class RedditCollector(BaseCollector):
    """Collecteur de données Reddit avec support de l'API PRAW."""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        user_agent: str,
        window_size: int = 1000,
        update_interval: float = 60.0,
        subreddits: Optional[List[str]] = None
    ):
        """
        Initialise le collecteur Reddit.
        
        Args:
            client_id: ID client Reddit
            client_secret: Secret client Reddit
            user_agent: User agent pour l'API Reddit
            window_size: Taille de la fenêtre de cache
            update_interval: Intervalle de mise à jour en secondes
            subreddits: Liste des subreddits à suivre (par défaut: crypto, CryptoCurrency, etc.)
        """
        super().__init__(client_id, client_secret)
        self.user_agent = user_agent
        self.window_size = window_size
        self.update_interval = update_interval
        self.subreddits = subreddits or [
            "crypto", "CryptoCurrency", "CryptoMarkets",
            "Bitcoin", "ethereum", "binance"
        ]
        self.posts = {}
        self._running = False
        self._stream_tasks = {}
        
    def _initialize_client(self) -> None:
        """Initialise le client Reddit."""
        self.client = praw.Reddit(
            client_id=self.api_key,
            client_secret=self.api_secret,
            user_agent=self.user_agent
        )
        
    async def start_stream(self, symbols: List[str], callback: Callable) -> None:
        """
        Démarre le flux de posts Reddit en temps réel.
        
        Args:
            symbols: Liste des symboles à suivre
            callback: Fonction de callback pour les nouveaux posts
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
        """Arrête le flux de posts."""
        if self._running:
            self._running = False
            
            # Arrêter toutes les tâches de streaming
            for task in self._stream_tasks.values():
                task.cancel()
            self._stream_tasks.clear()
            
    async def get_historical_posts(
        self,
        symbol: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Récupère les posts historiques pour un symbole.
        
        Args:
            symbol: Symbole (ex: "BTC/USDT")
            start_time: Date de début
            end_time: Date de fin (optionnel)
            limit: Nombre maximum de posts à récupérer
            
        Returns:
            Liste de posts avec leur sentiment
        """
        base_asset = symbol.split('/')[0].lower()
        posts = []
        
        try:
            # Parcourir les subreddits configurés
            for subreddit_name in self.subreddits:
                subreddit = self.client.subreddit(subreddit_name)
                
                # Rechercher les posts contenant le symbole
                search_query = f"title:{base_asset} OR selftext:{base_asset}"
                submissions = subreddit.search(
                    search_query,
                    sort='new',
                    time_filter='week',
                    limit=limit
                )
                
                for submission in submissions:
                    post_time = datetime.fromtimestamp(submission.created_utc)
                    
                    # Vérifier la plage temporelle
                    if post_time < start_time or (end_time and post_time > end_time):
                        continue
                        
                    # Analyser le sentiment du titre et du texte
                    text = f"{submission.title} {submission.selftext}"
                    sentiment = TextBlob(text).sentiment
                    
                    posts.append({
                        'id': submission.id,
                        'title': submission.title,
                        'text': submission.selftext,
                        'created_at': post_time,
                        'subreddit': subreddit_name,
                        'score': submission.score,
                        'upvote_ratio': submission.upvote_ratio,
                        'num_comments': submission.num_comments,
                        'polarity': sentiment.polarity,
                        'subjectivity': sentiment.subjectivity
                    })
                    
            return posts
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des posts: {str(e)}")
            return []
            
    async def _maintain_stream(self, symbol: str, callback: Callable) -> None:
        """
        Maintient le flux de posts pour un symbole.
        
        Args:
            symbol: Symbole à suivre
            callback: Fonction de callback pour les nouveaux posts
        """
        base_asset = symbol.split('/')[0].lower()
        
        while self._running:
            try:
                # Créer un multi-subreddit pour le streaming
                subreddits = '+'.join(self.subreddits)
                multi_subreddit = self.client.subreddit(subreddits)
                
                # Stream les nouveaux posts
                for submission in multi_subreddit.stream.submissions():
                    if not self._running:
                        break
                        
                    # Vérifier si le post concerne le symbole
                    if base_asset not in submission.title.lower() and \
                       base_asset not in submission.selftext.lower():
                        continue
                        
                    # Analyser le sentiment
                    text = f"{submission.title} {submission.selftext}"
                    sentiment = TextBlob(text).sentiment
                    
                    # Créer l'objet post
                    post_obj = {
                        'id': submission.id,
                        'title': submission.title,
                        'text': submission.selftext,
                        'created_at': datetime.fromtimestamp(submission.created_utc),
                        'subreddit': submission.subreddit.display_name,
                        'score': submission.score,
                        'upvote_ratio': submission.upvote_ratio,
                        'num_comments': submission.num_comments,
                        'polarity': sentiment.polarity,
                        'subjectivity': sentiment.subjectivity
                    }
                    
                    # Ajouter au cache
                    if symbol not in self.posts:
                        self.posts[symbol] = []
                    self.posts[symbol].append(post_obj)
                    
                    # Maintenir la taille de la fenêtre
                    if len(self.posts[symbol]) > self.window_size:
                        self.posts[symbol].pop(0)
                        
                    # Appeler le callback
                    await callback(symbol, post_obj)
                    
            except Exception as e:
                logger.error(f"Erreur dans le stream Reddit: {str(e)}")
                await asyncio.sleep(self.update_interval)
                
    async def get_community_metrics(self, symbol: str) -> Dict:
        """
        Calcule les métriques communautaires pour un symbole.
        
        Args:
            symbol: Symbole
            
        Returns:
            Dictionnaire des métriques communautaires
        """
        if symbol not in self.posts or not self.posts[symbol]:
            return {
                'average_polarity': 0.0,
                'average_subjectivity': 0.0,
                'post_count': 0,
                'average_score': 0.0,
                'average_comments': 0.0,
                'bullish_ratio': 0.0,
                'engagement_rate': 0.0
            }
            
        posts = self.posts[symbol]
        polarities = [p['polarity'] for p in posts]
        subjectivities = [p['subjectivity'] for p in posts]
        scores = [p['score'] for p in posts]
        comments = [p['num_comments'] for p in posts]
        bullish_count = sum(1 for p in polarities if p > 0)
        
        total_engagement = sum(scores) + sum(comments)
        post_count = len(posts)
        
        return {
            'average_polarity': sum(polarities) / post_count,
            'average_subjectivity': sum(subjectivities) / post_count,
            'post_count': post_count,
            'average_score': sum(scores) / post_count,
            'average_comments': sum(comments) / post_count,
            'bullish_ratio': bullish_count / post_count,
            'engagement_rate': total_engagement / (post_count * 2)  # Normalisé entre 0 et 1
        } 