"""
Routes API pour l'analyse technique dans SADIE.

Ce module fournit des endpoints pour accéder aux fonctionnalités d'analyse technique,
incluant des indicateurs, des patterns et des niveaux de support/résistance.
"""

from typing import Dict, List, Optional, Any, Union
import pandas as pd
import numpy as np
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field

from sadie.core.technical.indicators import (
    calculate_rsi, calculate_macd, calculate_bollinger_bands,
    calculate_ema, calculate_sma, calculate_stochastic,
    generate_technical_indicators
)
from sadie.core.technical.patterns import (
    detect_patterns, identify_candlestick_patterns,
    detect_support_resistance
)
from sadie.web.auth import get_current_active_user, User, get_read_data_user

router = APIRouter(prefix="/api/technical", tags=["technical"])


class IndicatorRequest(BaseModel):
    """Modèle pour une requête d'indicateur technique."""
    
    data: List[Dict[str, float]] = Field(
        ..., description="Données OHLC au format [{timestamp, open, high, low, close, volume}, ...]"
    )
    indicator: str = Field(..., description="Type d'indicateur (rsi, macd, bollinger_bands, etc.)")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Paramètres spécifiques à l'indicateur")


class PatternRequest(BaseModel):
    """Modèle pour une requête de détection de patterns."""
    
    data: List[Dict[str, float]] = Field(
        ..., description="Données OHLC au format [{timestamp, open, high, low, close, volume}, ...]"
    )
    pattern_types: List[str] = Field(
        default_factory=lambda: ["candlestick"],
        description="Types de patterns à détecter"
    )


class SupportResistanceRequest(BaseModel):
    """Modèle pour une requête de niveaux de support/résistance."""
    
    data: List[Dict[str, float]] = Field(
        ..., description="Données OHLC au format [{timestamp, open, high, low, close, volume}, ...]"
    )
    window_size: int = Field(default=10, description="Taille de la fenêtre pour la détection")
    sensitivity: float = Field(default=0.01, description="Sensibilité pour le regroupement des niveaux")


class TechnicalResponse(BaseModel):
    """Modèle pour la réponse d'analyse technique."""
    
    success: bool = Field(..., description="Statut de la requête")
    data: Dict[str, Any] = Field(default=None, description="Données de l'analyse")
    message: Optional[str] = Field(default=None, description="Message informatif")
    error: Optional[str] = Field(default=None, description="Message d'erreur si success=False")


@router.post("/indicator", response_model=TechnicalResponse)
async def calculate_indicator(
    request: IndicatorRequest,
    current_user: User = Depends(get_read_data_user)
) -> TechnicalResponse:
    """
    Calcule un indicateur technique pour les données fournies.
    
    Args:
        request: Requête contenant les données et l'indicateur à calculer
        current_user: Utilisateur authentifié
        
    Returns:
        TechnicalResponse: Résultat du calcul de l'indicateur
    """
    try:
        # Conversion des données en DataFrame pandas
        df = pd.DataFrame(request.data)
        
        # Validation des colonnes minimales requises
        if not all(col in df.columns for col in ['timestamp', 'close']):
            return TechnicalResponse(
                success=False,
                error="Les données doivent contenir au moins les colonnes 'timestamp' et 'close'"
            )
        
        # Définition des indicateurs disponibles
        indicators = {
            'rsi': lambda: calculate_rsi(df, **request.parameters),
            'macd': lambda: calculate_macd(df, **request.parameters),
            'bollinger_bands': lambda: calculate_bollinger_bands(df, **request.parameters),
            'ema': lambda: calculate_ema(df, **request.parameters),
            'sma': lambda: calculate_sma(df, **request.parameters),
            'stochastic': lambda: calculate_stochastic(df, **request.parameters),
            'all': lambda: generate_technical_indicators(df, indicators=None)
        }
        
        # Vérification de l'indicateur demandé
        if request.indicator not in indicators:
            return TechnicalResponse(
                success=False,
                error=f"Indicateur '{request.indicator}' non disponible. Options: {', '.join(indicators.keys())}"
            )
        
        # Calcul de l'indicateur
        result = indicators[request.indicator]()
        
        # Formatage du résultat
        if isinstance(result, tuple):
            # Pour les indicateurs qui retournent plusieurs valeurs (comme MACD)
            if request.indicator == 'macd':
                data = {
                    'macd': result[0].tolist(),
                    'signal': result[1].tolist(),
                    'histogram': result[2].tolist()
                }
            elif request.indicator == 'bollinger_bands':
                data = {
                    'upper': result[0].tolist(),
                    'middle': result[1].tolist(),
                    'lower': result[2].tolist()
                }
            elif request.indicator == 'stochastic':
                data = {
                    'k': result[0].tolist(),
                    'd': result[1].tolist()
                }
            else:
                data = {f'value{i}': val.tolist() for i, val in enumerate(result)}
        elif isinstance(result, dict):
            # Pour generate_technical_indicators
            data = {k: v.tolist() if isinstance(v, np.ndarray) else v for k, v in result.items()}
        else:
            # Pour les indicateurs qui retournent une seule valeur
            data = {request.indicator: result.tolist()}
        
        return TechnicalResponse(
            success=True,
            data=data,
            message=f"Indicateur '{request.indicator}' calculé avec succès"
        )
        
    except Exception as e:
        return TechnicalResponse(
            success=False,
            error=f"Erreur lors du calcul de l'indicateur: {str(e)}"
        )


@router.post("/patterns", response_model=TechnicalResponse)
async def detect_price_patterns(
    request: PatternRequest,
    current_user: User = Depends(get_read_data_user)
) -> TechnicalResponse:
    """
    Détecte les patterns de prix dans les données fournies.
    
    Args:
        request: Requête contenant les données et les types de patterns à détecter
        current_user: Utilisateur authentifié
        
    Returns:
        TechnicalResponse: Résultat de la détection
    """
    try:
        # Conversion des données en DataFrame pandas
        df = pd.DataFrame(request.data)
        
        # Validation des colonnes requises
        if not all(col in df.columns for col in ['timestamp', 'open', 'high', 'low', 'close']):
            return TechnicalResponse(
                success=False,
                error="Les données doivent contenir les colonnes 'timestamp', 'open', 'high', 'low', 'close'"
            )
        
        # Détection des patterns
        patterns = detect_patterns(df, pattern_types=request.pattern_types)
        
        # Formatage du résultat pour eviter les erreurs de sérialisation
        formatted_patterns = {}
        for pattern_name, pattern_data in patterns.items():
            if isinstance(pattern_data, np.ndarray):
                formatted_patterns[pattern_name] = pattern_data.tolist()
            else:
                formatted_patterns[pattern_name] = pattern_data
        
        return TechnicalResponse(
            success=True,
            data=formatted_patterns,
            message=f"Patterns détectés avec succès: {', '.join(formatted_patterns.keys())}"
        )
        
    except Exception as e:
        return TechnicalResponse(
            success=False,
            error=f"Erreur lors de la détection des patterns: {str(e)}"
        )


@router.post("/support-resistance", response_model=TechnicalResponse)
async def calculate_support_resistance(
    request: SupportResistanceRequest,
    current_user: User = Depends(get_read_data_user)
) -> TechnicalResponse:
    """
    Calcule les niveaux de support et de résistance pour les données fournies.
    
    Args:
        request: Requête contenant les données et les paramètres
        current_user: Utilisateur authentifié
        
    Returns:
        TechnicalResponse: Niveaux de support et résistance calculés
    """
    try:
        # Conversion des données en DataFrame pandas
        df = pd.DataFrame(request.data)
        
        # Validation des colonnes requises
        if not all(col in df.columns for col in ['high', 'low']):
            return TechnicalResponse(
                success=False,
                error="Les données doivent contenir au moins les colonnes 'high' et 'low'"
            )
        
        # Calcul des niveaux
        support, resistance = detect_support_resistance(
            df, 
            window_size=request.window_size,
            sensitivity=request.sensitivity
        )
        
        return TechnicalResponse(
            success=True,
            data={
                'support': support,
                'resistance': resistance
            },
            message="Niveaux de support et résistance calculés avec succès"
        )
        
    except Exception as e:
        return TechnicalResponse(
            success=False,
            error=f"Erreur lors du calcul des niveaux: {str(e)}"
        )


@router.get("/indicators", response_model=List[str])
async def list_available_indicators(
    current_user: User = Depends(get_current_active_user)
) -> List[str]:
    """
    Retourne la liste des indicateurs techniques disponibles.
    
    Args:
        current_user: Utilisateur authentifié
        
    Returns:
        List[str]: Liste des indicateurs disponibles
    """
    return [
        "rsi", "macd", "bollinger_bands", "ema", "sma", 
        "stochastic", "all"
    ]


@router.get("/patterns", response_model=List[str])
async def list_available_patterns(
    current_user: User = Depends(get_current_active_user)
) -> List[str]:
    """
    Retourne la liste des types de patterns disponibles.
    
    Args:
        current_user: Utilisateur authentifié
        
    Returns:
        List[str]: Liste des types de patterns disponibles
    """
    return [
        "candlestick", "head_and_shoulders", "double_top_bottom",
        "triangle", "flag"
    ] 