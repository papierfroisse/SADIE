"""
Module de gestion des données de marché.
"""

import datetime
import logging
from typing import Dict, List, Optional, Union

import pandas as pd

from sadie.data.collectors.exceptions import ValidationError
from sadie.data.config import DataConfig
from sadie.data.historical import HistoricalManager
from sadie.data.realtime import RealtimeManager
from sadie.data.sentiment import SentimentManager
from sadie.data.technical import TechnicalManager

logger = logging.getLogger(__name__)

class MarketManager:
    """Gestionnaire de données de marché."""
    
    def __init__(
        self,
        db_url: str,
        cache_dir: str,
        max_cache_age: int = 3600
    ):
        """
        Initialise le gestionnaire de données de marché.
        
        Args:
            db_url: URL de connexion à la base de données
            cache_dir: Chemin du répertoire de cache
            max_cache_age: Âge maximum des données en cache (en secondes)
        """
        self.historical = HistoricalManager(db_url, cache_dir, max_cache_age)
        self.realtime = RealtimeManager()
        self.sentiment = SentimentManager(db_url, cache_dir, max_cache_age)
        self.technical = TechnicalManager()
    
    async def start(self) -> None:
        """Démarre le gestionnaire de données de marché."""
        await self.realtime.start()
    
    async def stop(self) -> None:
        """Arrête le gestionnaire de données de marché."""
        await self.realtime.stop()
    
    def get_market_data(
        self,
        symbol: str,
        interval: str,
        start_time: datetime.datetime,
        end_time: Optional[datetime.datetime] = None,
        source: Optional[str] = None,
        include_sentiment: bool = True,
        include_technical: bool = True,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Récupère les données de marché complètes.
        
        Args:
            symbol: Symbole
            interval: Intervalle de temps
            start_time: Date de début
            end_time: Date de fin (optionnel)
            source: Source des données (optionnel)
            include_sentiment: Inclure les données de sentiment
            include_technical: Inclure les indicateurs techniques
            use_cache: Utiliser le cache
            
        Returns:
            DataFrame contenant les données de marché
            
        Raises:
            ValidationError: Si les paramètres sont invalides
        """
        # Validation des paramètres
        if not DataConfig.validate_symbol(symbol):
            raise ValidationError(f"Symbole non supporté: {symbol}")
        
        # Récupération des données historiques
        df = self.historical.get_historical_data(
            symbol=symbol,
            interval=interval,
            start_time=start_time,
            end_time=end_time,
            source=source,
            use_cache=use_cache
        )
        
        if df.empty:
            return df
        
        # Ajout des données de sentiment
        if include_sentiment:
            # Sentiment des actualités
            news_df = self.sentiment.get_news_sentiment(
                symbol=symbol,
                start_time=start_time,
                end_time=end_time,
                use_cache=use_cache
            )
            if not news_df.empty:
                # Agrégation par intervalle
                news_df = news_df.resample(interval).agg({
                    "polarity": "mean",
                    "subjectivity": "mean"
                }).fillna(method="ffill")
                df = pd.merge(
                    df,
                    news_df,
                    left_index=True,
                    right_index=True,
                    how="left"
                )
            
            # Sentiment des réseaux sociaux
            social_df = self.sentiment.get_social_sentiment(
                symbol=symbol,
                start_time=start_time,
                end_time=end_time,
                use_cache=use_cache
            )
            if not social_df.empty:
                # Agrégation par intervalle
                social_df = social_df.resample(interval).agg({
                    "reddit_posts_per_day": "mean",
                    "reddit_comments_per_day": "mean",
                    "reddit_active_users": "mean",
                    "twitter_followers": "mean",
                    "twitter_statuses": "mean",
                    "twitter_following": "mean",
                    "github_stars": "mean",
                    "github_subscribers": "mean",
                    "github_forks": "mean"
                }).fillna(method="ffill")
                df = pd.merge(
                    df,
                    social_df,
                    left_index=True,
                    right_index=True,
                    how="left"
                )
        
        # Ajout des indicateurs techniques
        if include_technical:
            df = self.technical.add_all_indicators(df)
        
        return df
    
    async def subscribe_market_data(
        self,
        symbol: str,
        callback: callable,
        source: Optional[str] = None
    ) -> None:
        """
        S'abonne aux données de marché en temps réel.
        
        Args:
            symbol: Symbole
            callback: Fonction de rappel pour les données
            source: Source des données (optionnel)
            
        Raises:
            ValidationError: Si les paramètres sont invalides
        """
        await self.realtime.subscribe(
            source=source or "binance",
            symbol=symbol,
            callback=callback
        )
    
    async def unsubscribe_market_data(
        self,
        symbol: str,
        callback: Optional[callable] = None,
        source: Optional[str] = None
    ) -> None:
        """
        Se désabonne des données de marché en temps réel.
        
        Args:
            symbol: Symbole
            callback: Fonction de rappel spécifique (optionnel)
            source: Source des données (optionnel)
        """
        await self.realtime.unsubscribe(
            source=source or "binance",
            symbol=symbol,
            callback=callback
        )
    
    def clean_old_data(
        self,
        before: datetime.datetime,
        source: Optional[str] = None,
        symbol: Optional[str] = None
    ) -> None:
        """
        Nettoie les anciennes données.
        
        Args:
            before: Date limite pour la suppression
            source: Source des données (optionnel)
            symbol: Symbole (optionnel)
        """
        self.historical.clean_old_data(before, source, symbol)
        self.sentiment.clean_old_data(before, symbol) 