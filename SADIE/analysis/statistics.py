"""Module d'analyse statistique pour SADIE."""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from datetime import datetime, timedelta
from scipy import stats
from typing import Dict, List, Optional, Tuple, Union

@dataclass
class StatisticalSummary:
    """Résumé statistique d'une série de données."""
    mean: float
    median: float
    std: float
    skewness: float
    kurtosis: float
    min_value: float
    max_value: float
    is_normal: bool
    p_value: float

class StatisticalAnalyzer:
    """Analyseur statistique pour les données financières."""
    
    def __init__(self, data: pd.DataFrame):
        """Initialise l'analyseur avec les données."""
        self._validate_data(data)
        self._data = data.copy()
        
    def _validate_data(self, data: pd.DataFrame) -> None:
        """Valide les données d'entrée."""
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Les données doivent être un DataFrame pandas")
        if len(data) == 0:
            raise ValueError("Le DataFrame ne peut pas être vide")
            
    def calculate_returns(self, column: str) -> pd.Series:
        """Calcule les rendements logarithmiques."""
        if column not in self._data.columns:
            raise ValueError(f"La colonne {column} n'existe pas dans les données")
        prices = self._data[column]
        return np.log(prices / prices.shift(1)).dropna()
        
    def analyze_distribution(self, column: str) -> StatisticalSummary:
        """Analyse la distribution d'une série de données."""
        if column not in self._data.columns:
            raise ValueError(f"La colonne {column} n'existe pas dans les données")
            
        data = self._data[column]
        statistic, p_value = stats.normaltest(data)
        
        return StatisticalSummary(
            mean=data.mean(),
            median=data.median(),
            std=data.std(),
            skewness=stats.skew(data),
            kurtosis=stats.kurtosis(data),
            min_value=data.min(),
            max_value=data.max(),
            is_normal=p_value > 0.05,
            p_value=p_value
        )
        
    def detect_outliers(self, column: str, method: str = 'iqr') -> pd.Series:
        """Détecte les outliers dans une série de données."""
        if column not in self._data.columns:
            raise ValueError(f"La colonne {column} n'existe pas dans les données")
            
        data = self._data[column]
        
        if method == 'iqr':
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            return pd.Series((data < lower_bound) | (data > upper_bound), index=data.index)
            
        elif method == 'zscore':
            z_scores = pd.Series((data - data.mean()) / data.std(), index=data.index)
            return pd.Series(abs(z_scores) > 3, index=data.index)
            
        else:
            raise ValueError("Méthode invalide. Utilisez 'iqr' ou 'zscore'")
            
    def calculate_volatility(self, column: str, window: int = 20) -> pd.Series:
        """Calcule la volatilité historique."""
        returns = self.calculate_returns(column)
        return returns.rolling(window=window).std() * np.sqrt(252)
        
    def calculate_correlation(self, column1: str, column2: str) -> Tuple[float, float]:
        """Calcule la corrélation entre deux séries."""
        if column1 not in self._data.columns or column2 not in self._data.columns:
            raise ValueError("Une ou plusieurs colonnes n'existent pas")
            
        data1 = self._data[column1].dropna()
        data2 = self._data[column2].dropna()
        
        if len(data1) != len(data2):
            raise ValueError("Les séries doivent avoir la même longueur")
            
        correlation, p_value = stats.pearsonr(data1, data2)
        return correlation, p_value
        
    def calculate_beta(self, returns: pd.Series, market_returns: pd.Series) -> Tuple[float, float]:
        """Calcule le bêta et l'alpha par rapport au marché."""
        if len(returns) != len(market_returns):
            raise ValueError("Les séries doivent avoir la même longueur")
            
        slope, intercept, _, _, _ = stats.linregress(market_returns, returns)
        return slope, intercept
        
    def calculate_var(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """Calcule la Value at Risk (VaR)."""
        if not 0 < confidence_level < 1:
            raise ValueError("Le niveau de confiance doit être entre 0 et 1")
            
        return np.percentile(returns, (1 - confidence_level) * 100)
        
    def calculate_cvar(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """Calcule la Conditional Value at Risk (CVaR)."""
        if not 0 < confidence_level < 1:
            raise ValueError("Le niveau de confiance doit être entre 0 et 1")
            
        var = self.calculate_var(returns, confidence_level)
        return returns[returns <= var].mean()
        
    def calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.0) -> float:
        """Calcule le ratio de Sharpe."""
        excess_returns = returns - risk_free_rate / 252  # Annualisé
        return np.sqrt(252) * excess_returns.mean() / returns.std()
        
    def calculate_sortino_ratio(self, returns: pd.Series, risk_free_rate: float = 0.0) -> float:
        """Calcule le ratio de Sortino."""
        excess_returns = returns - risk_free_rate / 252  # Annualisé
        downside_returns = returns[returns < 0]
        
        if len(downside_returns) == 0:
            return float('inf')
            
        downside_std = np.sqrt(np.mean(downside_returns**2))
        if downside_std == 0:
            return float('inf')
            
        return np.sqrt(252) * excess_returns.mean() / downside_std 