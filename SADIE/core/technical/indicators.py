"""
Implémentation des indicateurs techniques pour l'analyse des marchés financiers.

Ce module contient les fonctions pour calculer divers indicateurs techniques
qui peuvent être utilisés pour l'analyse des données de marché et la génération
de signaux de trading.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Union, Optional


def calculate_sma(data: Union[pd.DataFrame, pd.Series, List[float]], period: int = 14) -> np.ndarray:
    """
    Calcule la moyenne mobile simple (Simple Moving Average - SMA).

    Args:
        data: Série de données de prix (généralement prix de clôture)
        period: Période pour le calcul de la moyenne mobile

    Returns:
        np.ndarray: Valeurs SMA calculées
    """
    if isinstance(data, list):
        data = pd.Series(data)
    elif isinstance(data, pd.DataFrame):
        if 'close' in data.columns:
            data = data['close']
        else:
            raise ValueError("DataFrame fourni doit contenir une colonne 'close'")

    return data.rolling(window=period).mean().to_numpy()


def calculate_ema(data: Union[pd.DataFrame, pd.Series, List[float]], period: int = 14, smoothing: float = 2.0) -> np.ndarray:
    """
    Calcule la moyenne mobile exponentielle (Exponential Moving Average - EMA).

    Args:
        data: Série de données de prix
        period: Période pour le calcul de l'EMA
        smoothing: Facteur de lissage

    Returns:
        np.ndarray: Valeurs EMA calculées
    """
    if isinstance(data, list):
        data = pd.Series(data)
    elif isinstance(data, pd.DataFrame):
        if 'close' in data.columns:
            data = data['close']
        else:
            raise ValueError("DataFrame fourni doit contenir une colonne 'close'")

    return data.ewm(span=period, adjust=False).mean().to_numpy()


def calculate_rsi(data: Union[pd.DataFrame, pd.Series, List[float]], period: int = 14) -> np.ndarray:
    """
    Calcule l'indice de force relative (Relative Strength Index - RSI).

    Args:
        data: Série de données de prix
        period: Période pour le calcul du RSI

    Returns:
        np.ndarray: Valeurs RSI calculées (entre 0 et 100)
    """
    if isinstance(data, list):
        data = pd.Series(data)
    elif isinstance(data, pd.DataFrame):
        if 'close' in data.columns:
            data = data['close']
        else:
            raise ValueError("DataFrame fourni doit contenir une colonne 'close'")

    # Calcul des différences de prix
    delta = data.diff()
    
    # Séparation des gains et des pertes
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # Calcul des moyennes mobiles exponentielles des gains et des pertes
    avg_gain = gain.ewm(com=period-1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period-1, min_periods=period).mean()
    
    # Calcul de la force relative (RS)
    rs = avg_gain / avg_loss
    
    # Calcul du RSI
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.to_numpy()


def calculate_macd(data: Union[pd.DataFrame, pd.Series, List[float]], 
                   fast_period: int = 12, 
                   slow_period: int = 26, 
                   signal_period: int = 9) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Calcule l'indicateur MACD (Moving Average Convergence Divergence).

    Args:
        data: Série de données de prix
        fast_period: Période pour l'EMA rapide
        slow_period: Période pour l'EMA lente
        signal_period: Période pour la ligne de signal

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray]: MACD, ligne de signal, histogramme
    """
    if isinstance(data, list):
        data = pd.Series(data)
    elif isinstance(data, pd.DataFrame):
        if 'close' in data.columns:
            data = data['close']
        else:
            raise ValueError("DataFrame fourni doit contenir une colonne 'close'")

    # Calcul des EMAs
    ema_fast = data.ewm(span=fast_period, adjust=False).mean()
    ema_slow = data.ewm(span=slow_period, adjust=False).mean()
    
    # Calcul du MACD
    macd_line = ema_fast - ema_slow
    
    # Calcul de la ligne de signal
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    
    # Calcul de l'histogramme
    histogram = macd_line - signal_line
    
    return macd_line.to_numpy(), signal_line.to_numpy(), histogram.to_numpy()


def calculate_bollinger_bands(data: Union[pd.DataFrame, pd.Series, List[float]], 
                              period: int = 20, 
                              std_dev: float = 2.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Calcule les bandes de Bollinger.

    Args:
        data: Série de données de prix
        period: Période pour le calcul de la moyenne mobile
        std_dev: Nombre d'écarts-types pour les bandes supérieure et inférieure

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray]: Bande supérieure, moyenne mobile, bande inférieure
    """
    if isinstance(data, list):
        data = pd.Series(data)
    elif isinstance(data, pd.DataFrame):
        if 'close' in data.columns:
            data = data['close']
        else:
            raise ValueError("DataFrame fourni doit contenir une colonne 'close'")

    # Calcul de la moyenne mobile
    middle_band = data.rolling(window=period).mean()
    
    # Calcul de l'écart-type
    rolling_std = data.rolling(window=period).std()
    
    # Calcul des bandes
    upper_band = middle_band + (rolling_std * std_dev)
    lower_band = middle_band - (rolling_std * std_dev)
    
    return upper_band.to_numpy(), middle_band.to_numpy(), lower_band.to_numpy()


def calculate_stochastic(data: pd.DataFrame, 
                         k_period: int = 14, 
                         d_period: int = 3, 
                         slowing: int = 3) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calcule l'oscillateur stochastique.

    Args:
        data: DataFrame contenant les colonnes 'high', 'low', et 'close'
        k_period: Période pour le calcul de %K
        d_period: Période pour le calcul de %D
        slowing: Période de ralentissement

    Returns:
        Tuple[np.ndarray, np.ndarray]: %K et %D
    """
    if not all(col in data.columns for col in ['high', 'low', 'close']):
        raise ValueError("DataFrame doit contenir les colonnes 'high', 'low', et 'close'")

    # Calcul du plus bas et du plus haut sur la période
    low_min = data['low'].rolling(window=k_period).min()
    high_max = data['high'].rolling(window=k_period).max()
    
    # Calcul de %K (Stochastic rapide)
    k_fast = 100 * ((data['close'] - low_min) / (high_max - low_min))
    
    # Application du ralentissement
    k = k_fast.rolling(window=slowing).mean()
    
    # Calcul de %D (moyenne mobile de %K)
    d = k.rolling(window=d_period).mean()
    
    return k.to_numpy(), d.to_numpy()


def calculate_atr(data: pd.DataFrame, period: int = 14) -> np.ndarray:
    """
    Calcule l'Average True Range (ATR).

    Args:
        data: DataFrame contenant les colonnes 'high', 'low', et 'close'
        period: Période pour le calcul de l'ATR

    Returns:
        np.ndarray: Valeurs ATR calculées
    """
    if not all(col in data.columns for col in ['high', 'low', 'close']):
        raise ValueError("DataFrame doit contenir les colonnes 'high', 'low', et 'close'")

    # Calcul du True Range
    high_low = data['high'] - data['low']
    high_close_prev = abs(data['high'] - data['close'].shift(1))
    low_close_prev = abs(data['low'] - data['close'].shift(1))
    
    true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
    
    # Calcul de l'ATR (moyenne mobile exponentielle du True Range)
    atr = true_range.ewm(span=period, adjust=False).mean()
    
    return atr.to_numpy()


def calculate_adx(data: pd.DataFrame, period: int = 14) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Calcule l'Average Directional Index (ADX).

    Args:
        data: DataFrame contenant les colonnes 'high', 'low', et 'close'
        period: Période pour le calcul de l'ADX

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray]: ADX, +DI, -DI
    """
    if not all(col in data.columns for col in ['high', 'low', 'close']):
        raise ValueError("DataFrame doit contenir les colonnes 'high', 'low', et 'close'")

    # Calcul de l'ATR
    atr = calculate_atr(data, period)
    
    # Calcul du Directional Movement (DM)
    high_diff = data['high'].diff()
    low_diff = data['low'].diff()
    
    # +DM et -DM
    plus_dm = pd.Series(0, index=data.index)
    minus_dm = pd.Series(0, index=data.index)
    
    # Conditions pour +DM
    condition1 = (high_diff > 0) & (high_diff > low_diff.abs())
    plus_dm[condition1] = high_diff[condition1]
    
    # Conditions pour -DM
    condition2 = (low_diff < 0) & (low_diff.abs() > high_diff)
    minus_dm[condition2] = low_diff.abs()[condition2]
    
    # Calcul de +DI et -DI
    plus_di = 100 * plus_dm.ewm(span=period, adjust=False).mean() / atr
    minus_di = 100 * minus_dm.ewm(span=period, adjust=False).mean() / atr
    
    # Calcul du Directional Index (DX)
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    
    # Calcul de l'ADX (moyenne mobile du DX)
    adx = dx.ewm(span=period, adjust=False).mean()
    
    return adx.to_numpy(), plus_di.to_numpy(), minus_di.to_numpy()


def generate_technical_indicators(data: pd.DataFrame, 
                                 indicators: List[str] = None) -> Dict[str, np.ndarray]:
    """
    Génère plusieurs indicateurs techniques pour un DataFrame de données.

    Args:
        data: DataFrame avec les données OHLC
        indicators: Liste des indicateurs à calculer (None = tous)

    Returns:
        Dict[str, np.ndarray]: Dictionnaire des indicateurs calculés
    """
    available_indicators = {
        'sma': lambda: calculate_sma(data),
        'ema': lambda: calculate_ema(data),
        'rsi': lambda: calculate_rsi(data),
        'macd': lambda: calculate_macd(data),
        'bollinger_bands': lambda: calculate_bollinger_bands(data),
        'stochastic': lambda: calculate_stochastic(data),
        'atr': lambda: calculate_atr(data),
        'adx': lambda: calculate_adx(data)
    }
    
    if indicators is None:
        indicators = list(available_indicators.keys())
    
    result = {}
    for indicator in indicators:
        if indicator in available_indicators:
            if indicator == 'macd':
                macd, signal, hist = available_indicators[indicator]()
                result['macd'] = macd
                result['macd_signal'] = signal
                result['macd_histogram'] = hist
            elif indicator == 'bollinger_bands':
                upper, middle, lower = available_indicators[indicator]()
                result['bb_upper'] = upper
                result['bb_middle'] = middle
                result['bb_lower'] = lower
            elif indicator == 'stochastic':
                k, d = available_indicators[indicator]()
                result['stoch_k'] = k
                result['stoch_d'] = d
            elif indicator == 'adx':
                adx, plus_di, minus_di = available_indicators[indicator]()
                result['adx'] = adx
                result['plus_di'] = plus_di
                result['minus_di'] = minus_di
            else:
                result[indicator] = available_indicators[indicator]()
    
    return result 