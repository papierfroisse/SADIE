import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class HarmonicPattern:
    """Représente un motif harmonique détecté."""
    type: str
    trend: str
    points: List[Tuple[int, float]]
    description: str
    reversal_zone: float

def find_swing_points(data: pd.DataFrame, window: int = 5) -> Tuple[List[int], List[int]]:
    """Trouve les points de swing (pivots) dans les données.
    
    Args:
        data: DataFrame avec colonnes OHLC
        window: Taille de la fenêtre pour la détection des pivots
        
    Returns:
        Tuple contenant les indices des pivots hauts et bas
    """
    highs = []
    lows = []
    
    for i in range(window, len(data) - window):
        # Vérification des pivots hauts
        if all(data['high'].iloc[i] > data['high'].iloc[i-window:i]) and \
           all(data['high'].iloc[i] > data['high'].iloc[i+1:i+window+1]):
            highs.append(i)
        
        # Vérification des pivots bas
        if all(data['low'].iloc[i] < data['low'].iloc[i-window:i]) and \
           all(data['low'].iloc[i] < data['low'].iloc[i+1:i+window+1]):
            lows.append(i)
    
    return highs, lows

def calculate_ratios(points: List[Tuple[int, float]]) -> List[float]:
    """Calcule les ratios de Fibonacci entre les points."""
    ratios = []
    for i in range(1, len(points) - 1):
        move = points[i][1] - points[i-1][1]
        retracement = points[i+1][1] - points[i][1]
        if move != 0:
            ratios.append(abs(retracement / move))
    return ratios

def is_gartley(ratios: List[float], tolerance: float = 0.1) -> bool:
    """Vérifie si les ratios correspondent à un motif Gartley."""
    expected = [0.618, 0.382, 1.618]
    return all(abs(r - e) <= tolerance for r, e in zip(ratios, expected))

def is_butterfly(ratios: List[float], tolerance: float = 0.1) -> bool:
    """Vérifie si les ratios correspondent à un motif Butterfly."""
    expected = [0.786, 0.382, 1.618]
    return all(abs(r - e) <= tolerance for r, e in zip(ratios, expected))

def is_bat(ratios: List[float], tolerance: float = 0.1) -> bool:
    """Vérifie si les ratios correspondent à un motif Bat."""
    expected = [0.382, 0.382, 2.618]
    return all(abs(r - e) <= tolerance for r, e in zip(ratios, expected))

def is_crab(ratios: List[float], tolerance: float = 0.1) -> bool:
    """Vérifie si les ratios correspondent à un motif Crab."""
    expected = [0.618, 0.382, 3.618]
    return all(abs(r - e) <= tolerance for r, e in zip(ratios, expected))

def identify_pattern(points: List[Tuple[int, float]]) -> Tuple[str, str, float]:
    """Identifie le type de motif harmonique.
    
    Returns:
        Tuple (type, trend, zone_retournement)
    """
    ratios = calculate_ratios(points)
    
    if len(ratios) != 3:
        return None, None, 0
    
    # Détermination de la tendance
    trend = "Bullish" if points[0][1] < points[-1][1] else "Bearish"
    
    # Calcul de la zone de retournement potentielle
    last_move = abs(points[-1][1] - points[-2][1])
    reversal_zone = points[-1][1] + (last_move * 0.618 * (-1 if trend == "Bearish" else 1))
    
    # Identification du motif
    if is_gartley(ratios):
        return "Gartley", trend, reversal_zone
    elif is_butterfly(ratios):
        return "Butterfly", trend, reversal_zone
    elif is_bat(ratios):
        return "Bat", trend, reversal_zone
    elif is_crab(ratios):
        return "Crab", trend, reversal_zone
    
    return None, None, 0

def find_patterns(trades: pd.DataFrame) -> List[Dict[str, Any]]:
    """Trouve les motifs harmoniques dans les données.
    
    Args:
        trades: DataFrame avec les trades
        
    Returns:
        Liste des motifs détectés
    """
    # Conversion en bougies
    ohlcv = trades.resample('1min').agg({
        'price': ['first', 'max', 'min', 'last'],
        'quantity': 'sum'
    })
    ohlcv.columns = ['open', 'high', 'low', 'close', 'volume']
    
    # Recherche des points de swing
    highs, lows = find_swing_points(ohlcv)
    
    patterns = []
    window_size = 5  # Nombre de points à considérer
    
    # Analyse des derniers points de swing
    for i in range(len(highs) - window_size + 1):
        points = []
        for j in range(window_size):
            idx = highs[i + j]
            points.append((idx, ohlcv['high'].iloc[idx]))
        
        pattern_type, trend, reversal = identify_pattern(points)
        if pattern_type:
            patterns.append({
                'type': pattern_type,
                'trend': trend,
                'points': points,
                'description': f"Motif {pattern_type} {'haussier' if trend == 'Bullish' else 'baissier'}",
                'reversal_zone': reversal
            })
    
    # Même chose pour les points bas
    for i in range(len(lows) - window_size + 1):
        points = []
        for j in range(window_size):
            idx = lows[i + j]
            points.append((idx, ohlcv['low'].iloc[idx]))
        
        pattern_type, trend, reversal = identify_pattern(points)
        if pattern_type:
            patterns.append({
                'type': pattern_type,
                'trend': trend,
                'points': points,
                'description': f"Motif {pattern_type} {'haussier' if trend == 'Bullish' else 'baissier'}",
                'reversal_zone': reversal
            })
    
    return patterns 