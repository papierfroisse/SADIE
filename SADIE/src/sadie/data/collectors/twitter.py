"""
Module de collecte de données Twitter pour l'analyse de sentiment.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta

import tweepy
from textblob import TextBlob

from sadie.data.collectors.base import BaseCollector
from sadie.data.config import DataConfig

logger = logging.getLogger(__name__)

class TwitterCollector(BaseCollector):
    """Collecteur de données Twitter avec support de l'API v2."""
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        access_token: Optional[str] = None,
        access_token_secret: Optional[str] = None,
        bearer_token: Optional[str] = None,
        window_size: int = 1000,
        update_interval: float = 1.0
    ):
        """
        Initialise le collecteur Twitter.
        
        Args:
            api_key: Clé API Twitter
            api_secret: Secret API Twitter
            access_token: Token d'accès (optionnel)
            access_token_secret: Secret du token d'accès (optionnel)
            bearer_token: Token Bearer pour l'API v2 (optionnel)
            window_size: Taille de la fenêtre de cache
            update_interval: Intervalle de mise à jour en secondes
        """
        super().__init__(api_key, api_secret)
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.bearer_token = bearer_token
        self.window_size = window_size
        self.update_interval = update_interval
        self.tweets = {}
        self._running = False
        self._stream_tasks = {}
        
    def _initialize_client(self) -> None:
        """Initialise le client Twitter."""
        # Client v2 avec authentification Bearer token
        if self.bearer_token:
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                wait_on_rate_limit=True
            )
        else:
            # Client v2 avec authentification OAuth 1.0a
            self.client = tweepy.Client(
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                wait_on_rate_limit=True
            )
            
        # Streaming client
        self.stream_client = tweepy.StreamingClient(
            bearer_token=self.bearer_token,
            wait_on_rate_limit=True
        )
        
    async def start_stream(self, symbols: List[str], callback: Callable) -> None:
        """
        Démarre le flux de tweets en temps réel.
        
        Args:
            symbols: Liste des symboles à suivre
            callback: Fonction de callback pour les nouveaux tweets
        """
        if not self._running:
            self._running = True
            
            # Créer les règles de filtrage
            rules = []
            for symbol in symbols:
                base_asset = symbol.split('/')[0]
                rules.append(tweepy.StreamRule(f"#{base_asset} OR ${base_asset}"))
                
            # Ajouter les règles au stream
            await self.stream_client.add_rules(rules)
            
            # Démarrer le stream dans une tâche asyncio
            for symbol in symbols:
                task = asyncio.create_task(
                    self._maintain_stream(symbol, callback)
                )
                self._stream_tasks[symbol] = task
                
    async def stop_stream(self) -> None:
        """Arrête le flux de tweets."""
        if self._running:
            self._running = False
            
            # Arrêter toutes les tâches de streaming
            for task in self._stream_tasks.values():
                task.cancel()
            self._stream_tasks.clear()
            
            # Supprimer toutes les règles
            rules = await self.stream_client.get_rules()
            if rules and rules.data:
                rule_ids = [rule.id for rule in rules.data]
                await self.stream_client.delete_rules(rule_ids)
                
    async def get_historical_tweets(
        self,
        symbol: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Récupère les tweets historiques pour un symbole.
        
        Args:
            symbol: Symbole (ex: "BTC/USDT")
            start_time: Date de début
            end_time: Date de fin (optionnel)
            limit: Nombre maximum de tweets à récupérer
            
        Returns:
            Liste de tweets avec leur sentiment
        """
        base_asset = symbol.split('/')[0]
        query = f"#{base_asset} OR ${base_asset}"
        
        tweets = []
        try:
            # Récupérer les tweets
            response = await self.client.search_recent_tweets(
                query=query,
                start_time=start_time,
                end_time=end_time,
                max_results=min(limit, 100),
                tweet_fields=['created_at', 'public_metrics']
            )
            
            if not response.data:
                return []
                
            # Analyser le sentiment de chaque tweet
            for tweet in response.data:
                sentiment = TextBlob(tweet.text).sentiment
                tweets.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'retweets': tweet.public_metrics['retweet_count'],
                    'likes': tweet.public_metrics['like_count'],
                    'replies': tweet.public_metrics['reply_count'],
                    'polarity': sentiment.polarity,
                    'subjectivity': sentiment.subjectivity
                })
                
            return tweets
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des tweets: {str(e)}")
            return []
            
    async def _maintain_stream(self, symbol: str, callback: Callable) -> None:
        """
        Maintient le flux de tweets pour un symbole.
        
        Args:
            symbol: Symbole à suivre
            callback: Fonction de callback pour les nouveaux tweets
        """
        while self._running:
            try:
                async for tweet in self.stream_client.filter():
                    if not self._running:
                        break
                        
                    # Analyser le sentiment
                    sentiment = TextBlob(tweet.text).sentiment
                    
                    # Créer l'objet tweet
                    tweet_obj = {
                        'id': tweet.id,
                        'text': tweet.text,
                        'created_at': tweet.created_at,
                        'polarity': sentiment.polarity,
                        'subjectivity': sentiment.subjectivity
                    }
                    
                    # Ajouter au cache
                    if symbol not in self.tweets:
                        self.tweets[symbol] = []
                    self.tweets[symbol].append(tweet_obj)
                    
                    # Maintenir la taille de la fenêtre
                    if len(self.tweets[symbol]) > self.window_size:
                        self.tweets[symbol].pop(0)
                        
                    # Appeler le callback
                    await callback(symbol, tweet_obj)
                    
            except Exception as e:
                logger.error(f"Erreur dans le stream Twitter: {str(e)}")
                await asyncio.sleep(self.update_interval)
                
    async def get_sentiment_metrics(self, symbol: str) -> Dict:
        """
        Calcule les métriques de sentiment pour un symbole.
        
        Args:
            symbol: Symbole
            
        Returns:
            Dictionnaire des métriques de sentiment
        """
        if symbol not in self.tweets or not self.tweets[symbol]:
            return {
                'average_polarity': 0.0,
                'average_subjectivity': 0.0,
                'tweet_count': 0,
                'bullish_ratio': 0.0
            }
            
        tweets = self.tweets[symbol]
        polarities = [t['polarity'] for t in tweets]
        subjectivities = [t['subjectivity'] for t in tweets]
        bullish_count = sum(1 for p in polarities if p > 0)
        
        return {
            'average_polarity': sum(polarities) / len(polarities),
            'average_subjectivity': sum(subjectivities) / len(subjectivities),
            'tweet_count': len(tweets),
            'bullish_ratio': bullish_count / len(tweets)
        } 