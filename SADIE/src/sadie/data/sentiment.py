"""
Module de gestion des données de sentiment.
"""

import datetime
import logging
from typing import Dict, List, Optional, Union

import pandas as pd
import requests
from textblob import TextBlob

from sadie.data.cache import DataCache
from sadie.data.collectors.exceptions import ValidationError
from sadie.data.config import DataConfig
from sadie.data.database import Database

logger = logging.getLogger(__name__)

class SentimentManager:
    """Gestionnaire de données de sentiment."""
    
    def __init__(
        self,
        db_url: str,
        cache_dir: str,
        max_cache_age: int = 3600
    ):
        """
        Initialise le gestionnaire de données de sentiment.
        
        Args:
            db_url: URL de connexion à la base de données
            cache_dir: Chemin du répertoire de cache
            max_cache_age: Âge maximum des données en cache (en secondes)
        """
        self.db = Database(db_url)
        self.cache = DataCache(cache_dir)
        self.max_cache_age = max_cache_age
    
    def get_news_sentiment(
        self,
        symbol: str,
        start_time: datetime.datetime,
        end_time: Optional[datetime.datetime] = None,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Récupère le sentiment des actualités.
        
        Args:
            symbol: Symbole
            start_time: Date de début
            end_time: Date de fin (optionnel)
            use_cache: Utiliser le cache (par défaut True)
            
        Returns:
            DataFrame contenant les sentiments
            
        Raises:
            ValidationError: Si les paramètres sont invalides
        """
        # Validation des paramètres
        if not DataConfig.validate_symbol(symbol):
            raise ValidationError(f"Symbole non supporté: {symbol}")
        
        # Tentative de récupération depuis le cache
        if use_cache:
            cache_data = self.cache.load(
                source="news",
                symbol=symbol,
                data_type="sentiment",
                max_age=self.max_cache_age
            )
            if cache_data:
                df = pd.DataFrame(cache_data["data"])
                if not df.empty:
                    df.set_index("timestamp", inplace=True)
                    df.index = pd.to_datetime(df.index, unit="s")
                    mask = (df.index >= start_time)
                    if end_time:
                        mask &= (df.index <= end_time)
                    df = df[mask]
                    if not df.empty:
                        return df
        
        # Récupération depuis la base de données
        # TODO: Implémenter la récupération depuis la base de données
        
        # Récupération depuis l'API de CryptoCompare
        api_key = DataConfig.get_source_config("cryptocompare")["api_key"]
        url = "https://min-api.cryptocompare.com/data/v2/news/"
        params = {
            "api_key": api_key,
            "categories": symbol.split("/")[0].lower()
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "Data" not in data:
                return pd.DataFrame()
            
            # Analyse du sentiment
            sentiments = []
            for article in data["Data"]:
                timestamp = article["published_on"]
                dt = datetime.datetime.fromtimestamp(timestamp)
                
                if dt < start_time or (end_time and dt > end_time):
                    continue
                
                # Analyse du sentiment avec TextBlob
                text = f"{article['title']} {article['body']}"
                blob = TextBlob(text)
                sentiment = blob.sentiment
                
                sentiments.append({
                    "timestamp": timestamp,
                    "title": article["title"],
                    "source": article["source"],
                    "url": article["url"],
                    "polarity": sentiment.polarity,
                    "subjectivity": sentiment.subjectivity
                })
            
            # Sauvegarde dans le cache
            if sentiments:
                self.cache.save(
                    data=sentiments,
                    source="news",
                    symbol=symbol,
                    data_type="sentiment"
                )
            
            # Conversion en DataFrame
            df = pd.DataFrame(sentiments)
            if not df.empty:
                df.set_index("timestamp", inplace=True)
                df.index = pd.to_datetime(df.index, unit="s")
            return df
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération des actualités: {e}")
            return pd.DataFrame()
    
    def get_social_sentiment(
        self,
        symbol: str,
        start_time: datetime.datetime,
        end_time: Optional[datetime.datetime] = None,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Récupère le sentiment des réseaux sociaux.
        
        Args:
            symbol: Symbole
            start_time: Date de début
            end_time: Date de fin (optionnel)
            use_cache: Utiliser le cache (par défaut True)
            
        Returns:
            DataFrame contenant les sentiments
            
        Raises:
            ValidationError: Si les paramètres sont invalides
        """
        # Validation des paramètres
        if not DataConfig.validate_symbol(symbol):
            raise ValidationError(f"Symbole non supporté: {symbol}")
        
        # Tentative de récupération depuis le cache
        if use_cache:
            cache_data = self.cache.load(
                source="social",
                symbol=symbol,
                data_type="sentiment",
                max_age=self.max_cache_age
            )
            if cache_data:
                df = pd.DataFrame(cache_data["data"])
                if not df.empty:
                    df.set_index("timestamp", inplace=True)
                    df.index = pd.to_datetime(df.index, unit="s")
                    mask = (df.index >= start_time)
                    if end_time:
                        mask &= (df.index <= end_time)
                    df = df[mask]
                    if not df.empty:
                        return df
        
        # Récupération depuis la base de données
        # TODO: Implémenter la récupération depuis la base de données
        
        # Récupération depuis l'API de CryptoCompare
        api_key = DataConfig.get_source_config("cryptocompare")["api_key"]
        url = "https://min-api.cryptocompare.com/data/social/coin/latest"
        params = {
            "api_key": api_key,
            "coinId": symbol.split("/")[0].lower()
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "Data" not in data:
                return pd.DataFrame()
            
            social_data = data["Data"]
            timestamp = int(datetime.datetime.now().timestamp())
            
            sentiment = {
                "timestamp": timestamp,
                "reddit_posts_per_day": social_data.get("Reddit", {}).get("posts_per_day", 0),
                "reddit_comments_per_day": social_data.get("Reddit", {}).get("comments_per_day", 0),
                "reddit_active_users": social_data.get("Reddit", {}).get("active_users", 0),
                "twitter_followers": social_data.get("Twitter", {}).get("followers", 0),
                "twitter_statuses": social_data.get("Twitter", {}).get("statuses", 0),
                "twitter_following": social_data.get("Twitter", {}).get("following", 0),
                "github_stars": social_data.get("GitHub", {}).get("stars", 0),
                "github_subscribers": social_data.get("GitHub", {}).get("subscribers", 0),
                "github_forks": social_data.get("GitHub", {}).get("forks", 0)
            }
            
            # Sauvegarde dans le cache
            self.cache.save(
                data=[sentiment],
                source="social",
                symbol=symbol,
                data_type="sentiment"
            )
            
            # Conversion en DataFrame
            df = pd.DataFrame([sentiment])
            if not df.empty:
                df.set_index("timestamp", inplace=True)
                df.index = pd.to_datetime(df.index, unit="s")
            return df
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération des données sociales: {e}")
            return pd.DataFrame()
    
    def clean_old_data(
        self,
        before: datetime.datetime,
        symbol: Optional[str] = None
    ) -> None:
        """
        Nettoie les anciennes données.
        
        Args:
            before: Date limite pour la suppression
            symbol: Symbole (optionnel)
        """
        # Nettoyage du cache
        self.cache.clear(
            source="news",
            symbol=symbol
        )
        self.cache.clear(
            source="social",
            symbol=symbol
        ) 