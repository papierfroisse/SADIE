"""Module d'analyse avancée des cycles de marché."""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from scipy import stats
from scipy.signal import welch

from .market_cycles import CycleAnalyzer, MarketCycle

@dataclass
class CycleCharacteristics:
    """Caractéristiques détaillées d'un cycle."""
    duration_mean: float
    duration_std: float
    amplitude_mean: float
    amplitude_std: float
    symmetry_score: float
    dominant_period: float
    seasonality_score: float
    trend_strength: float

class AdvancedCycleAnalyzer(CycleAnalyzer):
    """Analyseur avancé des cycles de marché."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cycle_characteristics: Optional[CycleCharacteristics] = None
        
    def analyze_cycle_characteristics(self) -> CycleCharacteristics:
        """Analyse détaillée des caractéristiques des cycles.
        
        Returns:
            Caractéristiques des cycles
        """
        cycles = self.identify_cycles()
        if not cycles:
            raise ValueError("Aucun cycle identifié")
            
        # Analyse des durées
        durations = [cycle.duration for cycle in cycles]
        duration_mean = np.mean(durations)
        duration_std = np.std(durations)
        
        # Analyse des amplitudes
        amplitudes = [abs(cycle.amplitude) for cycle in cycles]
        amplitude_mean = np.mean(amplitudes)
        amplitude_std = np.std(amplitudes)
        
        # Score de symétrie global
        symmetry_scores = []
        for cycle in cycles:
            peak_idx = self.data.index.get_loc(cycle.start_date) + cycle.duration // 2
            up_phase = peak_idx - self.data.index.get_loc(cycle.start_date)
            down_phase = self.data.index.get_loc(cycle.end_date) - peak_idx
            symmetry_scores.append(min(up_phase, down_phase) / max(up_phase, down_phase))
        symmetry_score = np.mean(symmetry_scores)
        
        # Analyse spectrale pour identifier la période dominante
        prices = self.data[self.price_column].values
        freqs, psd = welch(prices, fs=1.0, nperseg=len(prices)//4)
        dominant_idx = np.argmax(psd)
        dominant_period = 1.0 / freqs[dominant_idx] if freqs[dominant_idx] != 0 else np.inf
        
        # Score de saisonnalité
        decomp = self.decompose_trend()
        cycle_component = decomp['cycle']
        seasonality_score = 1.0 - (np.std(cycle_component) / np.std(prices))
        
        # Force de la tendance
        trend_component = decomp['trend']
        trend_strength = 1.0 - (np.std(prices - trend_component) / np.std(prices))
        
        self.cycle_characteristics = CycleCharacteristics(
            duration_mean=duration_mean,
            duration_std=duration_std,
            amplitude_mean=amplitude_mean,
            amplitude_std=amplitude_std,
            symmetry_score=symmetry_score,
            dominant_period=dominant_period,
            seasonality_score=seasonality_score,
            trend_strength=trend_strength
        )
        
        return self.cycle_characteristics
        
    def detect_regime_change(self, window: int = 20) -> pd.Series:
        """Détecte les changements de régime dans les cycles.
        
        Args:
            window: Taille de la fenêtre d'analyse
            
        Returns:
            Série indiquant les probabilités de changement de régime
        """
        # Calcul des rendements
        returns = self.data[self.price_column].pct_change()
        
        # Statistiques glissantes
        rolling_mean = returns.rolling(window=window).mean()
        rolling_std = returns.rolling(window=window).std()
        
        # Test de Kolmogorov-Smirnov glissant
        regime_changes = pd.Series(index=self.data.index, dtype=float)
        
        for i in range(window, len(returns)):
            window1 = returns.iloc[i-window:i]
            window2 = returns.iloc[i-window//2:i]
            _, p_value = stats.ks_2samp(window1, window2)
            regime_changes.iloc[i] = 1 - p_value
            
        return regime_changes
        
    def forecast_next_cycle(self) -> Dict[str, float]:
        """Prévoit les caractéristiques du prochain cycle.
        
        Returns:
            Prévisions pour le prochain cycle
        """
        if not self.cycle_characteristics:
            self.analyze_cycle_characteristics()
            
        cycles = self.identify_cycles()
        if not cycles:
            raise ValueError("Aucun cycle identifié")
            
        # Analyse des tendances récentes
        recent_cycles = cycles[-3:]  # 3 derniers cycles
        recent_durations = [c.duration for c in recent_cycles]
        recent_amplitudes = [abs(c.amplitude) for c in recent_cycles]
        
        # Calcul des tendances
        duration_trend = np.polyfit(range(len(recent_durations)), recent_durations, 1)[0]
        amplitude_trend = np.polyfit(range(len(recent_amplitudes)), recent_amplitudes, 1)[0]
        
        # Prévision du prochain cycle
        next_duration = max(
            self.min_cycle_length,
            min(
                self.max_cycle_length,
                self.cycle_characteristics.duration_mean + duration_trend
            )
        )
        
        next_amplitude = self.cycle_characteristics.amplitude_mean + amplitude_trend
        
        # Probabilité de tendance
        recent_trends = [1 if c.trend == 'bullish' else -1 for c in recent_cycles]
        trend_probability = np.mean([1 if t > 0 else 0 for t in recent_trends])
        
        return {
            'expected_duration': next_duration,
            'expected_amplitude': next_amplitude,
            'bullish_probability': trend_probability,
            'confidence': min(
                1.0,
                (1.0 - self.cycle_characteristics.duration_std / next_duration) * 
                (1.0 - self.cycle_characteristics.amplitude_std / abs(next_amplitude))
            )
        }
        
    def get_cycle_metrics(self) -> Dict[str, float]:
        """Calcule des métriques supplémentaires sur les cycles.
        
        Returns:
            Dictionnaire des métriques
        """
        if not self.cycle_characteristics:
            self.analyze_cycle_characteristics()
            
        cycles = self.identify_cycles()
        
        # Calcul des métriques
        bullish_cycles = len([c for c in cycles if c.trend == 'bullish'])
        bearish_cycles = len([c for c in cycles if c.trend == 'bearish'])
        
        return {
            'cycle_regularity': 1.0 - (
                self.cycle_characteristics.duration_std / 
                self.cycle_characteristics.duration_mean
            ),
            'amplitude_stability': 1.0 - (
                self.cycle_characteristics.amplitude_std / 
                self.cycle_characteristics.amplitude_mean
            ),
            'trend_bias': (bullish_cycles - bearish_cycles) / len(cycles),
            'cycle_quality': np.mean([c.confidence for c in cycles]),
            'seasonality_strength': self.cycle_characteristics.seasonality_score,
            'trend_strength': self.cycle_characteristics.trend_strength,
            'average_duration': self.cycle_characteristics.duration_mean,
            'average_amplitude': self.cycle_characteristics.amplitude_mean
        } 