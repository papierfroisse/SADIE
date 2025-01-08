"""
Configuration pour les collecteurs de données.
"""

import os
from typing import Dict, List, Optional

from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

class DataConfig:
    """Configuration pour les collecteurs de données."""
    
    # Clés API
    BINANCE_API_KEY: str = os.getenv("BINANCE_API_KEY", "")
    BINANCE_API_SECRET: str = os.getenv("BINANCE_API_SECRET", "")
    ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    
    # Configuration des symboles
    SYMBOLS: List[str] = [
        "BTC/USDT",
        "ETH/USDT",
        "BNB/USDT",
        "ADA/USDT",
        "SOL/USDT",
        "DOT/USDT",
        "AVAX/USDT",
        "MATIC/USDT",
        "LINK/USDT",
        "UNI/USDT"
    ]
    
    # Intervalles de temps supportés
    INTERVALS: List[str] = [
        "1m",
        "5m",
        "15m",
        "30m",
        "1h",
        "4h",
        "1d",
        "1w"
    ]
    
    # Configuration des sources de données
    SOURCES: Dict[str, Dict] = {
        "binance": {
            "enabled": True,
            "api_key": BINANCE_API_KEY,
            "api_secret": BINANCE_API_SECRET,
            "rate_limit": 1200,  # Requêtes par minute
            "symbols": SYMBOLS,
            "intervals": INTERVALS,
            "features": ["historical", "current", "orderbook"]
        },
        "alpha_vantage": {
            "enabled": True,
            "api_key": ALPHA_VANTAGE_API_KEY,
            "api_secret": None,
            "rate_limit": 5,  # Requêtes par minute
            "symbols": SYMBOLS,
            "intervals": ["1m", "5m", "15m", "30m", "1h", "1d", "1w", "1M"],
            "features": ["historical", "current"]
        }
    }
    
    @classmethod
    def get_source_config(cls, source: str) -> Optional[Dict]:
        """
        Récupère la configuration d'une source de données.
        
        Args:
            source: Nom de la source de données
            
        Returns:
            Configuration de la source ou None si non trouvée
        """
        return cls.SOURCES.get(source.lower())
    
    @classmethod
    def get_enabled_sources(cls) -> List[str]:
        """
        Récupère la liste des sources de données activées.
        
        Returns:
            Liste des noms des sources activées
        """
        return [
            source for source, config in cls.SOURCES.items()
            if config.get("enabled", False)
        ]
    
    @classmethod
    def validate_symbol(cls, symbol: str) -> bool:
        """
        Vérifie si un symbole est supporté.
        
        Args:
            symbol: Symbole à vérifier
            
        Returns:
            True si le symbole est supporté, False sinon
        """
        return symbol in cls.SYMBOLS
    
    @classmethod
    def validate_interval(cls, interval: str, source: Optional[str] = None) -> bool:
        """
        Vérifie si un intervalle est supporté.
        
        Args:
            interval: Intervalle à vérifier
            source: Source de données spécifique (optionnel)
            
        Returns:
            True si l'intervalle est supporté, False sinon
        """
        if source:
            config = cls.get_source_config(source)
            return config and interval in config["intervals"]
        return interval in cls.INTERVALS
    
    @classmethod
    def supports_feature(cls, source: str, feature: str) -> bool:
        """
        Vérifie si une source supporte une fonctionnalité.
        
        Args:
            source: Nom de la source de données
            feature: Nom de la fonctionnalité
            
        Returns:
            True si la fonctionnalité est supportée, False sinon
        """
        config = cls.get_source_config(source)
        return config and feature in config.get("features", []) 