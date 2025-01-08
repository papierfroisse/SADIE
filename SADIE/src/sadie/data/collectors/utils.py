"""
Utilitaires pour les collecteurs de données.
"""

import datetime
import time
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

from sadie.data.collectors.exceptions import (
    RateLimitError,
    ValidationError,
    DataNotFoundError
)
from sadie.data.config import DataConfig

T = TypeVar("T")

def rate_limit(calls: int, period: int = 60) -> Callable:
    """
    Décorateur pour limiter le taux d'appels à une fonction.
    
    Args:
        calls: Nombre d'appels autorisés
        period: Période en secondes
        
    Returns:
        Fonction décorée
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        last_reset = time.time()
        calls_made = 0
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            nonlocal last_reset, calls_made
            
            # Réinitialisation du compteur si la période est écoulée
            now = time.time()
            if now - last_reset >= period:
                calls_made = 0
                last_reset = now
            
            # Vérification de la limite
            if calls_made >= calls:
                wait_time = period - (now - last_reset)
                raise RateLimitError(
                    source=args[0].__class__.__name__,
                    message=f"Limite de taux atteinte. Réessayez dans {wait_time:.1f}s"
                )
            
            # Appel de la fonction
            calls_made += 1
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def validate_params(
    symbol: Optional[str] = None,
    interval: Optional[str] = None,
    source: Optional[str] = None
) -> Callable:
    """
    Décorateur pour valider les paramètres d'une fonction.
    
    Args:
        symbol: Symbole à valider
        interval: Intervalle à valider
        source: Source de données à valider
        
    Returns:
        Fonction décorée
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Validation du symbole
            if symbol:
                symbol_value = kwargs.get(symbol)
                if not DataConfig.validate_symbol(symbol_value):
                    raise ValidationError(
                        f"Symbole non supporté: {symbol_value}",
                        parameter=symbol
                    )
            
            # Validation de l'intervalle
            if interval:
                interval_value = kwargs.get(interval)
                source_value = kwargs.get(source) if source else None
                if not DataConfig.validate_interval(interval_value, source_value):
                    raise ValidationError(
                        f"Intervalle non supporté: {interval_value}",
                        parameter=interval
                    )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def format_ohlcv(
    data: List[Dict[str, Any]],
    timestamp_key: str = "timestamp",
    timestamp_format: Optional[str] = None
) -> List[Dict[str, Union[float, int]]]:
    """
    Formate les données OHLCV dans un format standard.
    
    Args:
        data: Données à formater
        timestamp_key: Clé pour le timestamp
        timestamp_format: Format du timestamp si c'est une chaîne
        
    Returns:
        Données formatées
    """
    result = []
    for entry in data:
        # Conversion du timestamp
        if timestamp_format and isinstance(entry[timestamp_key], str):
            dt = datetime.datetime.strptime(entry[timestamp_key], timestamp_format)
            timestamp = dt.timestamp()
        else:
            timestamp = float(entry[timestamp_key])
        
        # Formatage des valeurs
        formatted = {
            "timestamp": timestamp,
            "open": float(entry.get("open", 0)),
            "high": float(entry.get("high", 0)),
            "low": float(entry.get("low", 0)),
            "close": float(entry.get("close", 0)),
            "volume": float(entry.get("volume", 0))
        }
        
        # Ajout des champs optionnels
        for key in ["trades", "quote_volume", "taker_buy_base", "taker_buy_quote"]:
            if key in entry:
                formatted[key] = float(entry[key])
        
        result.append(formatted)
    
    return sorted(result, key=lambda x: x["timestamp"])

def format_order_book(
    data: Dict[str, Any],
    timestamp_key: str = "timestamp"
) -> Dict[str, Union[int, List[List[float]]]]:
    """
    Formate le carnet d'ordres dans un format standard.
    
    Args:
        data: Données à formater
        timestamp_key: Clé pour le timestamp
        
    Returns:
        Carnet d'ordres formaté
    """
    return {
        "timestamp": int(data[timestamp_key]),
        "bids": [[float(price), float(qty)] for price, qty in data.get("bids", [])],
        "asks": [[float(price), float(qty)] for price, qty in data.get("asks", [])]
    }

def check_response(
    response: Dict[str, Any],
    required_fields: List[str],
    error_field: Optional[str] = "error"
) -> None:
    """
    Vérifie la validité d'une réponse API.
    
    Args:
        response: Réponse à vérifier
        required_fields: Champs requis
        error_field: Champ contenant le message d'erreur
        
    Raises:
        DataNotFoundError: Si les données ne sont pas trouvées
        ValidationError: Si la réponse est invalide
    """
    # Vérification des erreurs
    if error_field and error_field in response:
        raise ValidationError(str(response[error_field]))
    
    # Vérification des champs requis
    missing = [field for field in required_fields if field not in response]
    if missing:
        raise DataNotFoundError(
            "unknown",
            f"Champs manquants dans la réponse: {', '.join(missing)}"
        ) 