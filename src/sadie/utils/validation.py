"""
Fonctions de validation des données.
"""

from typing import Any, Dict
from decimal import Decimal, InvalidOperation

from ..data.exceptions import ValidationError

def validate_data(data: Dict[str, Any]) -> None:
    """
    Valide les données reçues.

    Args:
        data: Dictionnaire de données à valider

    Raises:
        ValidationError: Si les données sont invalides
    """
    if not isinstance(data, dict):
        raise ValidationError("Les données doivent être un dictionnaire")
    
    # Validation des ordres
    if "bids" in data:
        _validate_orders(data["bids"], "bids")
    if "asks" in data:
        _validate_orders(data["asks"], "asks")
    
    # Validation des mises à jour
    if "b" in data:
        _validate_orders(data["b"], "b")
    if "a" in data:
        _validate_orders(data["a"], "a")

def _validate_orders(orders: list, side: str) -> None:
    """
    Valide une liste d'ordres.

    Args:
        orders: Liste d'ordres à valider
        side: Côté de l'ordre ("bids" ou "asks")

    Raises:
        ValidationError: Si les ordres sont invalides
    """
    if not isinstance(orders, list):
        raise ValidationError(f"Les {side} doivent être une liste")
    
    for order in orders:
        if not isinstance(order, list) or len(order) < 2:
            raise ValidationError(f"Format d'ordre invalide dans {side}")
        
        try:
            price = Decimal(str(order[0]))
            quantity = Decimal(str(order[1]))
            
            if price <= 0:
                raise ValidationError(f"Prix invalide dans {side}: {price}")
            if quantity < 0:
                raise ValidationError(f"Quantité invalide dans {side}: {quantity}")
        except (InvalidOperation, TypeError) as e:
            raise ValidationError(f"Valeur numérique invalide dans {side}: {e}")

def validate_symbol(symbol: str) -> None:
    """
    Valide un symbole de trading.

    Args:
        symbol: Symbole à valider

    Raises:
        ValidationError: Si le symbole est invalide
    """
    if not isinstance(symbol, str):
        raise ValidationError("Le symbole doit être une chaîne de caractères")
    
    if not symbol:
        raise ValidationError("Le symbole ne peut pas être vide")
    
    if "/" in symbol:
        base, quote = symbol.split("/")
        if not base or not quote:
            raise ValidationError("Format de symbole invalide")
    elif len(symbol) < 2:
        raise ValidationError("Symbole trop court")
    
    if not symbol.isalnum():
        raise ValidationError("Le symbole ne doit contenir que des caractères alphanumériques") 