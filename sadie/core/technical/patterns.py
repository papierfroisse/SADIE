"""
Implémentation des détecteurs de patterns de chandeliers et de niveaux de support/résistance.

Ce module contient les fonctions pour identifier divers patterns de chandeliers
et détecter les niveaux de support et de résistance dans les données de marché.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Union, Optional


def identify_candlestick_patterns(data: pd.DataFrame) -> Dict[str, np.ndarray]:
    """
    Identifie les patterns de chandeliers courants.
    
    Args:
        data: DataFrame avec colonnes 'open', 'high', 'low', 'close'
        
    Returns:
        Dict[str, np.ndarray]: Dictionnaire des patterns détectés (1 = bullish, -1 = bearish, 0 = pas de pattern)
    """
    if not all(col in data.columns for col in ['open', 'high', 'low', 'close']):
        raise ValueError("DataFrame doit contenir les colonnes 'open', 'high', 'low', 'close'")
    
    # Calcul des tailles des corps et mèches
    data = data.copy()
    data['body_size'] = abs(data['close'] - data['open'])
    data['shadow_upper'] = data.apply(lambda x: x['high'] - max(x['open'], x['close']), axis=1)
    data['shadow_lower'] = data.apply(lambda x: min(x['open'], x['close']) - x['low'], axis=1)
    data['body_direction'] = np.where(data['close'] > data['open'], 1, -1)  # 1 = bullish, -1 = bearish
    data['avg_body_size'] = data['body_size'].rolling(window=14).mean()
    
    # Initialisation des résultats
    patterns = {
        'doji': np.zeros(len(data)),
        'hammer': np.zeros(len(data)),
        'inverted_hammer': np.zeros(len(data)),
        'engulfing': np.zeros(len(data)),
        'morning_star': np.zeros(len(data)),
        'evening_star': np.zeros(len(data)),
        'shooting_star': np.zeros(len(data)),
        'three_white_soldiers': np.zeros(len(data)),
        'three_black_crows': np.zeros(len(data)),
        'piercing_line': np.zeros(len(data)),
        'dark_cloud_cover': np.zeros(len(data))
    }
    
    # Détection des Dojis
    doji_condition = data['body_size'] <= 0.05 * (data['high'] - data['low'])
    patterns['doji'][doji_condition] = 1
    
    # Détection des Hammers (bullish)
    hammer_condition = (
        (data['body_size'] <= 0.5 * (data['high'] - data['low'])) & 
        (data['shadow_lower'] >= 2 * data['body_size']) & 
        (data['shadow_upper'] <= 0.2 * data['body_size']) &
        (data['body_direction'] == 1)
    )
    patterns['hammer'][hammer_condition] = 1
    
    # Détection des Hammers inversés (bearish)
    inverted_hammer_condition = (
        (data['body_size'] <= 0.5 * (data['high'] - data['low'])) & 
        (data['shadow_upper'] >= 2 * data['body_size']) & 
        (data['shadow_lower'] <= 0.2 * data['body_size']) &
        (data['body_direction'] == -1)
    )
    patterns['inverted_hammer'][inverted_hammer_condition] = -1
    
    # Détection des chandeliers englobants
    for i in range(1, len(data)):
        # Bullish engulfing
        if (data['body_direction'].iloc[i] == 1 and 
            data['body_direction'].iloc[i-1] == -1 and
            data['open'].iloc[i] <= data['close'].iloc[i-1] and
            data['close'].iloc[i] >= data['open'].iloc[i-1]):
            patterns['engulfing'][i] = 1
        
        # Bearish engulfing
        elif (data['body_direction'].iloc[i] == -1 and 
              data['body_direction'].iloc[i-1] == 1 and
              data['open'].iloc[i] >= data['close'].iloc[i-1] and
              data['close'].iloc[i] <= data['open'].iloc[i-1]):
            patterns['engulfing'][i] = -1
    
    # Détection des Morning Stars et Evening Stars
    for i in range(2, len(data)):
        # Morning Star (bullish pattern)
        if (data['body_direction'].iloc[i-2] == -1 and
            data['body_size'].iloc[i-1] <= 0.3 * data['avg_body_size'].iloc[i-1] and
            data['body_direction'].iloc[i] == 1 and
            data['close'].iloc[i] > (data['open'].iloc[i-2] + data['close'].iloc[i-2]) / 2):
            patterns['morning_star'][i] = 1
        
        # Evening Star (bearish pattern)
        elif (data['body_direction'].iloc[i-2] == 1 and
              data['body_size'].iloc[i-1] <= 0.3 * data['avg_body_size'].iloc[i-1] and
              data['body_direction'].iloc[i] == -1 and
              data['close'].iloc[i] < (data['open'].iloc[i-2] + data['close'].iloc[i-2]) / 2):
            patterns['evening_star'][i] = -1
    
    # Détection des Shooting Stars
    shooting_star_condition = (
        (data['body_size'] <= 0.3 * (data['high'] - data['low'])) &
        (data['shadow_upper'] >= 2 * data['body_size']) &
        (data['shadow_lower'] <= 0.1 * (data['high'] - data['low'])) &
        (data['body_direction'] == -1)
    )
    patterns['shooting_star'][shooting_star_condition] = -1
    
    # Détection des Three White Soldiers et Three Black Crows
    for i in range(2, len(data)):
        # Three White Soldiers (bullish pattern)
        if (data['body_direction'].iloc[i-2] == 1 and
            data['body_direction'].iloc[i-1] == 1 and
            data['body_direction'].iloc[i] == 1 and
            data['open'].iloc[i-1] > data['open'].iloc[i-2] and
            data['open'].iloc[i] > data['open'].iloc[i-1] and
            data['close'].iloc[i-1] > data['close'].iloc[i-2] and
            data['close'].iloc[i] > data['close'].iloc[i-1]):
            patterns['three_white_soldiers'][i] = 1
        
        # Three Black Crows (bearish pattern)
        elif (data['body_direction'].iloc[i-2] == -1 and
              data['body_direction'].iloc[i-1] == -1 and
              data['body_direction'].iloc[i] == -1 and
              data['open'].iloc[i-1] < data['open'].iloc[i-2] and
              data['open'].iloc[i] < data['open'].iloc[i-1] and
              data['close'].iloc[i-1] < data['close'].iloc[i-2] and
              data['close'].iloc[i] < data['close'].iloc[i-1]):
            patterns['three_black_crows'][i] = -1
    
    # Détection des Piercing Lines et Dark Cloud Covers
    for i in range(1, len(data)):
        # Piercing Line (bullish pattern)
        if (data['body_direction'].iloc[i-1] == -1 and
            data['body_direction'].iloc[i] == 1 and
            data['open'].iloc[i] < data['low'].iloc[i-1] and
            data['close'].iloc[i] > (data['open'].iloc[i-1] + data['close'].iloc[i-1]) / 2 and
            data['close'].iloc[i] < data['open'].iloc[i-1]):
            patterns['piercing_line'][i] = 1
        
        # Dark Cloud Cover (bearish pattern)
        elif (data['body_direction'].iloc[i-1] == 1 and
              data['body_direction'].iloc[i] == -1 and
              data['open'].iloc[i] > data['high'].iloc[i-1] and
              data['close'].iloc[i] < (data['open'].iloc[i-1] + data['close'].iloc[i-1]) / 2 and
              data['close'].iloc[i] > data['close'].iloc[i-1]):
            patterns['dark_cloud_cover'][i] = -1
    
    return {pattern: values for pattern, values in patterns.items()}


def detect_support_resistance(data: pd.DataFrame, 
                              window_size: int = 10, 
                              sensitivity: float = 0.01) -> Tuple[List[float], List[float]]:
    """
    Détecte les niveaux de support et de résistance.
    
    Args:
        data: DataFrame avec colonnes OHLC
        window_size: Taille de la fenêtre pour détecter les points pivots
        sensitivity: Sensibilité pour la détection (pourcentage de la fourchette des prix)
        
    Returns:
        Tuple[List[float], List[float]]: Niveaux de support et de résistance
    """
    if not all(col in data.columns for col in ['high', 'low']):
        raise ValueError("DataFrame doit contenir au moins les colonnes 'high' et 'low'")
    
    # Calcul des pivots hauts et bas
    pivot_high = []
    pivot_low = []
    
    for i in range(window_size, len(data) - window_size):
        # Vérification des pivots hauts (résistance)
        if data['high'].iloc[i] == max(data['high'].iloc[i-window_size:i+window_size+1]):
            pivot_high.append(data['high'].iloc[i])
        
        # Vérification des pivots bas (support)
        if data['low'].iloc[i] == min(data['low'].iloc[i-window_size:i+window_size+1]):
            pivot_low.append(data['low'].iloc[i])
    
    # Regroupement des niveaux similaires
    support_levels = cluster_levels(pivot_low, sensitivity, data)
    resistance_levels = cluster_levels(pivot_high, sensitivity, data)
    
    return support_levels, resistance_levels


def cluster_levels(levels: List[float], sensitivity: float, data: pd.DataFrame) -> List[float]:
    """
    Regroupe les niveaux similaires pour éviter les doublons.
    
    Args:
        levels: Liste des niveaux
        sensitivity: Seuil de sensibilité en pourcentage
        data: DataFrame original pour calculer la fourchette de prix
        
    Returns:
        List[float]: Niveaux regroupés
    """
    if not levels:
        return []
    
    # Calcul de la fourchette de prix
    price_range = data['high'].max() - data['low'].min()
    threshold = price_range * sensitivity
    
    # Tri des niveaux
    sorted_levels = sorted(levels)
    clustered = [sorted_levels[0]]
    
    for i in range(1, len(sorted_levels)):
        if sorted_levels[i] - clustered[-1] > threshold:
            clustered.append(sorted_levels[i])
    
    return clustered


def detect_patterns(data: pd.DataFrame,
                   pattern_types: List[str] = None) -> Dict[str, np.ndarray]:
    """
    Détecte les patterns et formations de prix courants.
    
    Args:
        data: DataFrame avec colonnes OHLC
        pattern_types: Liste des types de patterns à détecter
        
    Returns:
        Dict[str, np.ndarray]: Patterns détectés
    """
    if not all(col in data.columns for col in ['open', 'high', 'low', 'close']):
        raise ValueError("DataFrame doit contenir les colonnes 'open', 'high', 'low', 'close'")
    
    available_patterns = {
        'candlestick': lambda: identify_candlestick_patterns(data),
        'head_and_shoulders': lambda: detect_head_and_shoulders(data),
        'double_top_bottom': lambda: detect_double_top_bottom(data),
        'triangle': lambda: detect_triangle_patterns(data),
        'flag': lambda: detect_flag_patterns(data)
    }
    
    if pattern_types is None:
        pattern_types = ['candlestick']
    
    results = {}
    for pattern_type in pattern_types:
        if pattern_type in available_patterns:
            pattern_results = available_patterns[pattern_type]()
            if isinstance(pattern_results, dict):
                results.update(pattern_results)
            else:
                results[pattern_type] = pattern_results
    
    return results


def detect_head_and_shoulders(data: pd.DataFrame) -> np.ndarray:
    """
    Détecte les patterns tête-et-épaules et tête-et-épaules inversés.
    
    Args:
        data: DataFrame avec colonnes OHLC
        
    Returns:
        np.ndarray: Array avec 1 pour tête-et-épaules, -1 pour inversé, 0 pour aucun
    """
    result = np.zeros(len(data))
    
    # Implémentation simplifiée - détecte les patterns basés sur les pivots
    window = 5  # Taille de la fenêtre pour la détection des pivots
    
    for i in range(3 * window, len(data) - window):
        # Recherche des pivots sur les 30 dernières barres
        look_back = min(30, i)
        segment = data.iloc[i-look_back:i+1]
        
        # Identification des pivots hauts
        pivot_highs = []
        for j in range(window, len(segment) - window):
            if segment['high'].iloc[j] == max(segment['high'].iloc[j-window:j+window+1]):
                pivot_highs.append((j, segment['high'].iloc[j]))
        
        # Il faut au moins 3 pivots hauts pour un pattern tête-et-épaules
        if len(pivot_highs) >= 3:
            # Extraction des 3 derniers pivots hauts
            last_three = sorted(pivot_highs[-3:], key=lambda x: x[0])
            
            # Vérification si c'est un pattern tête-et-épaules
            if last_three[1][1] > last_three[0][1] and last_three[1][1] > last_three[2][1]:
                # Vérification si les épaules sont à des niveaux similaires (± 5%)
                shoulder_diff = abs(last_three[0][1] - last_three[2][1])
                if shoulder_diff <= 0.05 * last_three[1][1]:
                    result[i] = 1
        
        # Même logique pour les tête-et-épaules inversés (pivots bas)
        pivot_lows = []
        for j in range(window, len(segment) - window):
            if segment['low'].iloc[j] == min(segment['low'].iloc[j-window:j+window+1]):
                pivot_lows.append((j, segment['low'].iloc[j]))
        
        if len(pivot_lows) >= 3:
            last_three = sorted(pivot_lows[-3:], key=lambda x: x[0])
            
            if last_three[1][1] < last_three[0][1] and last_three[1][1] < last_three[2][1]:
                shoulder_diff = abs(last_three[0][1] - last_three[2][1])
                if shoulder_diff <= 0.05 * last_three[1][1]:
                    result[i] = -1
    
    return result


def detect_double_top_bottom(data: pd.DataFrame) -> Dict[str, np.ndarray]:
    """
    Détecte les patterns double sommet et double creux.
    
    Args:
        data: DataFrame avec colonnes OHLC
        
    Returns:
        Dict[str, np.ndarray]: Double sommets et doubles creux détectés
    """
    double_top = np.zeros(len(data))
    double_bottom = np.zeros(len(data))
    
    window = 5  # Taille de la fenêtre pour la détection des pivots
    
    for i in range(2 * window, len(data) - window):
        # Recherche des pivots sur les 20 dernières barres
        look_back = min(20, i)
        segment = data.iloc[i-look_back:i+1]
        
        # Identification des pivots hauts
        pivot_highs = []
        for j in range(window, len(segment) - window):
            if segment['high'].iloc[j] == max(segment['high'].iloc[j-window:j+window+1]):
                pivot_highs.append((j, segment['high'].iloc[j]))
        
        # Il faut au moins 2 pivots hauts pour un double sommet
        if len(pivot_highs) >= 2:
            # Extraction des 2 derniers pivots hauts
            last_two = sorted(pivot_highs[-2:], key=lambda x: x[0])
            
            # Vérification si c'est un double sommet
            high_diff = abs(last_two[0][1] - last_two[1][1])
            if high_diff <= 0.01 * last_two[0][1]:  # Les sommets sont proches (± 1%)
                double_top[i] = 1
        
        # Même logique pour les doubles creux (pivots bas)
        pivot_lows = []
        for j in range(window, len(segment) - window):
            if segment['low'].iloc[j] == min(segment['low'].iloc[j-window:j+window+1]):
                pivot_lows.append((j, segment['low'].iloc[j]))
        
        if len(pivot_lows) >= 2:
            last_two = sorted(pivot_lows[-2:], key=lambda x: x[0])
            
            # Vérification si c'est un double creux
            low_diff = abs(last_two[0][1] - last_two[1][1])
            if low_diff <= 0.01 * last_two[0][1]:  # Les creux sont proches (± 1%)
                double_bottom[i] = 1
    
    return {
        'double_top': double_top,
        'double_bottom': double_bottom
    }


def detect_triangle_patterns(data: pd.DataFrame) -> Dict[str, np.ndarray]:
    """
    Détecte les patterns de triangles (ascendant, descendant, symétrique).
    
    Args:
        data: DataFrame avec colonnes OHLC
        
    Returns:
        Dict[str, np.ndarray]: Patterns de triangles détectés
    """
    ascending = np.zeros(len(data))
    descending = np.zeros(len(data))
    symmetric = np.zeros(len(data))
    
    # Taille minimum du pattern (en barres)
    min_pattern_size = 10
    
    for i in range(min_pattern_size, len(data)):
        # Analyse des min_pattern_size dernières barres
        segment = data.iloc[i-min_pattern_size:i+1]
        
        # Recherche de tendances sur les hauts et les bas
        highs = segment['high'].values
        lows = segment['low'].values
        
        # Régression linéaire simple pour détecter les tendances
        x = np.arange(len(highs))
        
        # Tendance des hauts
        high_coef = np.polyfit(x, highs, 1)[0]
        
        # Tendance des bas
        low_coef = np.polyfit(x, lows, 1)[0]
        
        # Classification des triangles
        if low_coef > 0.001 and abs(high_coef) < 0.001:
            # Triangle ascendant (bas montants, hauts plats)
            ascending[i] = 1
        elif high_coef < -0.001 and abs(low_coef) < 0.001:
            # Triangle descendant (hauts descendants, bas plats)
            descending[i] = 1
        elif low_coef > 0.001 and high_coef < -0.001:
            # Triangle symétrique (bas montants, hauts descendants)
            symmetric[i] = 1
    
    return {
        'triangle_ascending': ascending,
        'triangle_descending': descending,
        'triangle_symmetric': symmetric
    }


def detect_flag_patterns(data: pd.DataFrame) -> Dict[str, np.ndarray]:
    """
    Détecte les patterns de drapeaux et fanions.
    
    Args:
        data: DataFrame avec colonnes OHLC
        
    Returns:
        Dict[str, np.ndarray]: Patterns de drapeaux et fanions détectés
    """
    bull_flag = np.zeros(len(data))
    bear_flag = np.zeros(len(data))
    
    # Taille minimum du pattern (en barres)
    min_pattern_size = 5
    pole_size = 5  # Taille du "mât" avant le drapeau
    
    for i in range(min_pattern_size + pole_size, len(data)):
        # Analyse du mât (tendance forte)
        pole = data.iloc[i-min_pattern_size-pole_size:i-min_pattern_size]
        
        # Analyse du drapeau/fanion (consolidation)
        flag = data.iloc[i-min_pattern_size:i+1]
        
        # Vérification d'un fort mouvement dans le mât
        pole_body_sizes = abs(pole['close'] - pole['open'])
        pole_avg_body = pole_body_sizes.mean()
        
        # Vérification d'une consolidation dans le drapeau
        flag_body_sizes = abs(flag['close'] - flag['open'])
        flag_avg_body = flag_body_sizes.mean()
        
        # Calcul des tendances
        pole_trend = pole['close'].iloc[-1] - pole['close'].iloc[0]
        flag_range = max(flag['high']) - min(flag['low'])
        
        # Identification des drapeaux haussiers
        if (pole_trend > 0 and 
            pole_avg_body > 1.5 * flag_avg_body and 
            flag_range < 0.5 * abs(pole_trend)):
            bull_flag[i] = 1
        
        # Identification des drapeaux baissiers
        elif (pole_trend < 0 and 
              pole_avg_body > 1.5 * flag_avg_body and 
              flag_range < 0.5 * abs(pole_trend)):
            bear_flag[i] = 1
    
    return {
        'bull_flag': bull_flag,
        'bear_flag': bear_flag
    } 