"""
Module de gestion des données historiques.
"""

import datetime
import logging
from typing import Dict, List, Optional, Union

import pandas as pd

from sadie.data.cache import DataCache
from sadie.data.collectors.exceptions import ValidationError
from sadie.data.collectors.factory import DataCollectorFactory
from sadie.data.config import DataConfig
from sadie.data.database import Database

logger = logging.getLogger(__name__)

class HistoricalManager:
    """Gestionnaire de données historiques."""
    
    def __init__(
        self,
        db_url: str,
        cache_dir: str,
        max_cache_age: int = 3600
    ):
        """
        Initialise le gestionnaire de données historiques.
        
        Args:
            db_url: URL de connexion à la base de données
            cache_dir: Chemin du répertoire de cache
            max_cache_age: Âge maximum des données en cache (en secondes)
        """
        self.db = Database(db_url)
        self.cache = DataCache(cache_dir)
        self.max_cache_age = max_cache_age
        self.collectors = {}
    
    def _get_collector(self, source: str):
        """
        Récupère ou crée un collecteur de données.
        
        Args:
            source: Source des données
            
        Returns:
            Instance du collecteur
            
        Raises:
            ValidationError: Si la source n'est pas supportée
        """
        if source not in self.collectors:
            config = DataConfig.get_source_config(source)
            if not config:
                raise ValidationError(f"Source non supportée: {source}")
            
            self.collectors[source] = DataCollectorFactory.create(
                source=source,
                api_key=config["api_key"],
                api_secret=config.get("api_secret")
            )
        
        return self.collectors[source]
    
    def get_historical_data(
        self,
        symbol: str,
        interval: str,
        start_time: datetime.datetime,
        end_time: Optional[datetime.datetime] = None,
        source: Optional[str] = None,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Récupère des données historiques.
        
        Args:
            symbol: Symbole
            interval: Intervalle de temps
            start_time: Date de début
            end_time: Date de fin (optionnel)
            source: Source des données (optionnel)
            use_cache: Utiliser le cache (par défaut True)
            
        Returns:
            DataFrame contenant les données historiques
            
        Raises:
            ValidationError: Si les paramètres sont invalides
        """
        # Validation des paramètres
        if not DataConfig.validate_symbol(symbol):
            raise ValidationError(f"Symbole non supporté: {symbol}")
        
        # Sélection de la source
        if not source:
            sources = DataConfig.get_enabled_sources()
            if not sources:
                raise ValidationError("Aucune source de données activée")
            source = sources[0]
        elif not DataConfig.get_source_config(source):
            raise ValidationError(f"Source non supportée: {source}")
        
        # Validation de l'intervalle
        if not DataConfig.validate_interval(interval, source):
            raise ValidationError(f"Intervalle non supporté: {interval}")
        
        # Tentative de récupération depuis le cache
        if use_cache:
            cache_data = self.cache.load(
                source=source,
                symbol=symbol,
                data_type="ohlcv",
                interval=interval,
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
        df = self.db.get_ohlcv(
            source=source,
            symbol=symbol,
            interval=interval,
            start_time=start_time,
            end_time=end_time
        )
        if not df.empty:
            return df
        
        # Récupération depuis l'API
        collector = self._get_collector(source)
        data = collector.get_historical_data(
            symbol=symbol,
            interval=interval,
            start_time=start_time,
            end_time=end_time
        )
        
        # Sauvegarde dans la base de données
        self.db.save_ohlcv(
            data=data,
            source=source,
            symbol=symbol,
            interval=interval
        )
        
        # Sauvegarde dans le cache
        self.cache.save(
            data=data,
            source=source,
            symbol=symbol,
            data_type="ohlcv",
            interval=interval
        )
        
        # Conversion en DataFrame
        df = pd.DataFrame(data)
        if not df.empty:
            df.set_index("timestamp", inplace=True)
            df.index = pd.to_datetime(df.index, unit="s")
        return df
    
    def get_order_book_history(
        self,
        symbol: str,
        start_time: datetime.datetime,
        end_time: Optional[datetime.datetime] = None,
        source: Optional[str] = None
    ) -> List[Dict[str, Union[int, List[List[float]]]]]:
        """
        Récupère l'historique des carnets d'ordres.
        
        Args:
            symbol: Symbole
            start_time: Date de début
            end_time: Date de fin (optionnel)
            source: Source des données (optionnel)
            
        Returns:
            Liste des carnets d'ordres
            
        Raises:
            ValidationError: Si les paramètres sont invalides
        """
        # Validation des paramètres
        if not DataConfig.validate_symbol(symbol):
            raise ValidationError(f"Symbole non supporté: {symbol}")
        
        # Sélection de la source
        if not source:
            sources = DataConfig.get_enabled_sources()
            if not sources:
                raise ValidationError("Aucune source de données activée")
            source = sources[0]
        elif not DataConfig.get_source_config(source):
            raise ValidationError(f"Source non supportée: {source}")
        
        # Vérification du support de la fonctionnalité
        if not DataConfig.supports_feature(source, "orderbook"):
            raise ValidationError(
                f"Les carnets d'ordres ne sont pas supportés par {source}"
            )
        
        # Récupération depuis la base de données
        collector = self._get_collector(source)
        current_book = collector.get_order_book(symbol=symbol)
        
        if current_book:
            # Sauvegarde dans la base de données
            self.db.save_order_book(
                data=current_book,
                source=source,
                symbol=symbol
            )
        
        return [current_book] if current_book else []
    
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
        # Nettoyage de la base de données
        self.db.clean(
            source=source,
            symbol=symbol,
            before=before
        )
        
        # Nettoyage du cache
        self.cache.clear(
            source=source,
            symbol=symbol
        ) 