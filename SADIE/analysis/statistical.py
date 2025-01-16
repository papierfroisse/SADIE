"""Module d'analyse statistique pour SADIE."""

from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.tsa.seasonal import seasonal_decompose
from datetime import datetime, timedelta

class StatisticalAnalyzer:
    """Classe pour l'analyse statistique des données de marché."""
    
    def __init__(self, data: pd.DataFrame):
        """Initialise l'analyseur statistique.
        
        Args:
            data: DataFrame avec colonnes ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        """
        self._data = data.copy()
        self._validate_data()
        
    def _validate_data(self):
        """Valide le format des données d'entrée."""
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        if not all(col in self._data.columns for col in required_columns):
            raise ValueError(f"Les données doivent contenir les colonnes: {required_columns}")
            
    def basic_stats(self) -> Dict[str, float]:
        """Calcule les statistiques de base.
        
        Returns:
            Dictionnaire des statistiques descriptives
        """
        returns = self._data['close'].pct_change().dropna()
        
        return {
            'mean': float(returns.mean()),
            'std': float(returns.std()),
            'skew': float(returns.skew()),
            'kurtosis': float(returns.kurtosis()),
            'sharpe': float(returns.mean() / returns.std() * np.sqrt(252)),
            'var_95': float(np.percentile(returns, 5)),
            'var_99': float(np.percentile(returns, 1))
        }
        
    def volatility_analysis(self, window: int = 20) -> Dict[str, Union[float, pd.Series]]:
        """Analyse la volatilité.
        
        Args:
            window: Fenêtre de calcul
            
        Returns:
            Dictionnaire avec les mesures de volatilité
        """
        returns = self._data['close'].pct_change().dropna()
        rolling_vol = returns.rolling(window=window).std() * np.sqrt(252)
        
        return {
            'current_vol': float(rolling_vol.iloc[-1]),
            'historical_vol': rolling_vol,
            'vol_of_vol': float(rolling_vol.std()),
            'annualized_vol': float(returns.std() * np.sqrt(252))
        }
        
    def correlation_analysis(self, other_data: pd.DataFrame, window: int = 20) -> Dict[str, Union[float, pd.Series]]:
        """Analyse la corrélation avec une autre série.
        
        Args:
            other_data: DataFrame de comparaison
            window: Fenêtre de calcul
            
        Returns:
            Dictionnaire avec les mesures de corrélation
        """
        returns1 = self._data['close'].pct_change().dropna()
        returns2 = other_data['close'].pct_change().dropna()
        
        # Aligner les séries
        returns1, returns2 = returns1.align(returns2, join='inner')
        
        rolling_corr = returns1.rolling(window=window).corr(returns2)
        
        return {
            'current_corr': float(rolling_corr.iloc[-1]),
            'historical_corr': rolling_corr,
            'beta': float(np.cov(returns1, returns2)[0,1] / np.var(returns2))
        }
        
    def stationarity_test(self) -> Dict[str, Union[float, bool]]:
        """Teste la stationnarité de la série (test ADF).
        
        Returns:
            Résultats du test de stationnarité
        """
        result = adfuller(self._data['close'].dropna())
        
        return {
            'adf_statistic': float(result[0]),
            'p_value': float(result[1]),
            'is_stationary': bool(result[1] < 0.05),
            'critical_values': dict(result[4])
        }
        
    def seasonality_analysis(self, period: int = 20) -> Dict[str, pd.Series]:
        """Analyse la saisonnalité.
        
        Args:
            period: Période pour la décomposition
            
        Returns:
            Composantes de la décomposition
        """
        decomposition = seasonal_decompose(
            self._data['close'].dropna(),
            period=period,
            extrapolate_trend='freq'
        )
        
        return {
            'trend': decomposition.trend,
            'seasonal': decomposition.seasonal,
            'residual': decomposition.resid
        }
        
    def autocorrelation_analysis(self, lags: int = 40) -> Dict[str, np.ndarray]:
        """Analyse l'autocorrélation.
        
        Args:
            lags: Nombre de retards à analyser
            
        Returns:
            Fonctions d'autocorrélation
        """
        returns = self._data['close'].pct_change().dropna()
        
        return {
            'acf': acf(returns, nlags=lags),
            'pacf': pacf(returns, nlags=lags)
        }
        
    def distribution_analysis(self) -> Dict[str, Union[float, str]]:
        """Analyse la distribution des rendements.
        
        Returns:
            Caractéristiques de la distribution
        """
        returns = self._data['close'].pct_change().dropna()
        
        # Test de normalité
        _, normality_p_value = stats.normaltest(returns)
        
        # Test du meilleur ajustement
        distributions = [
            stats.norm, stats.t, stats.laplace,
            stats.cauchy, stats.levy
        ]
        
        best_dist = None
        best_p = 0
        
        for dist in distributions:
            params = dist.fit(returns)
            _, p_value = stats.kstest(returns, dist.name, params)
            if p_value > best_p:
                best_p = p_value
                best_dist = dist.name
                
        return {
            'is_normal': bool(normality_p_value > 0.05),
            'normality_p_value': float(normality_p_value),
            'best_fit_distribution': str(best_dist),
            'best_fit_p_value': float(best_p)
        }
        
    def extreme_events_analysis(self, threshold: float = 0.95) -> Dict[str, Union[List[datetime], float]]:
        """Analyse les événements extrêmes.
        
        Args:
            threshold: Seuil pour les événements extrêmes
            
        Returns:
            Analyse des événements extrêmes
        """
        returns = self._data['close'].pct_change().dropna()
        
        # Identifier les événements extrêmes
        upper_threshold = returns.quantile(threshold)
        lower_threshold = returns.quantile(1 - threshold)
        
        extreme_events = returns[(returns > upper_threshold) | (returns < lower_threshold)]
        
        return {
            'extreme_dates': list(extreme_events.index),
            'extreme_returns': list(extreme_events.values),
            'upper_threshold': float(upper_threshold),
            'lower_threshold': float(lower_threshold),
            'frequency': float(len(extreme_events) / len(returns))
        }
        
    def regime_detection(self, n_regimes: int = 2) -> Dict[str, Union[np.ndarray, List[Tuple[datetime, str]]]]:
        """Détecte les régimes de marché.
        
        Args:
            n_regimes: Nombre de régimes à détecter
            
        Returns:
            Régimes détectés et transitions
        """
        from sklearn.mixture import GaussianMixture
        
        returns = self._data['close'].pct_change().dropna()
        
        # Ajuster le modèle
        model = GaussianMixture(n_components=n_regimes, random_state=42)
        regimes = model.fit_predict(returns.values.reshape(-1, 1))
        
        # Identifier les transitions
        transitions = []
        current_regime = regimes[0]
        
        for i in range(1, len(regimes)):
            if regimes[i] != current_regime:
                transitions.append((
                    returns.index[i],
                    f"Transition {current_regime} -> {regimes[i]}"
                ))
                current_regime = regimes[i]
                
        return {
            'regimes': regimes,
            'transitions': transitions,
            'regime_means': model.means_.flatten(),
            'regime_variances': model.covariances_.flatten()
        } 