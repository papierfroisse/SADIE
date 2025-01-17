"""Module d'analyse des cycles de marché."""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from scipy import signal
from scipy.ndimage import gaussian_filter1d

@dataclass
class MarketCycle:
    """Représente un cycle de marché identifié."""
    start_date: datetime
    end_date: datetime
    duration: int  # en jours
    amplitude: float
    trend: str  # 'bullish' ou 'bearish'
    confidence: float  # score de confiance (0-1)
    peak: float
    trough: float

class CycleAnalyzer:
    """Analyseur de cycles de marché."""
    
    def __init__(
        self,
        data: pd.DataFrame,
        price_column: str = 'close',
        min_cycle_length: int = 20,
        max_cycle_length: int = 252  # environ 1 an en jours de trading
    ):
        """Initialise l'analyseur de cycles.
        
        Args:
            data: DataFrame avec les données de prix
            price_column: Nom de la colonne contenant les prix
            min_cycle_length: Longueur minimale d'un cycle (en périodes)
            max_cycle_length: Longueur maximale d'un cycle (en périodes)
        """
        self.data = data
        self.price_column = price_column
        self.min_cycle_length = min_cycle_length
        self.max_cycle_length = max_cycle_length
        self._validate_data()
        
    def _validate_data(self) -> None:
        """Valide les données d'entrée."""
        if self.price_column not in self.data.columns:
            raise ValueError(f"Colonne {self.price_column} non trouvée")
        if not pd.api.types.is_numeric_dtype(self.data[self.price_column]):
            raise ValueError(f"La colonne {self.price_column} doit être numérique")
            
    def decompose_trend(self, sigma: float = 30) -> Dict[str, pd.Series]:
        """Décompose la série en tendance et cycle using Gaussian filter.
        
        Args:
            sigma: Écart-type du filtre gaussien
            
        Returns:
            Dictionnaire contenant la tendance et le cycle
        """
        prices = self.data[self.price_column].values
        
        # Calcul de la tendance avec un filtre gaussien
        trend = gaussian_filter1d(prices, sigma=sigma)
        
        # Calcul du cycle comme la différence entre prix et tendance
        cycle = prices - trend
        
        return {
            'trend': pd.Series(trend, index=self.data.index),
            'cycle': pd.Series(cycle, index=self.data.index)
        }
        
    def find_peaks_troughs(self, smoothing_window: int = 5) -> Dict[str, List[int]]:
        """Identifie les pics et creux dans la série.
        
        Args:
            smoothing_window: Fenêtre de lissage pour réduire le bruit
            
        Returns:
            Dictionnaire contenant les indices des pics et creux
        """
        # Lissage des données
        smoothed = self.data[self.price_column].rolling(window=smoothing_window).mean()
        
        # Identification des pics et creux
        peaks, _ = signal.find_peaks(smoothed, distance=self.min_cycle_length)
        troughs, _ = signal.find_peaks(-smoothed, distance=self.min_cycle_length)
        
        return {
            'peaks': peaks.tolist(),
            'troughs': troughs.tolist()
        }
        
    def identify_cycles(self) -> List[MarketCycle]:
        """Identifie les cycles de marché complets.
        
        Returns:
            Liste des cycles identifiés
        """
        # Décomposition tendance-cycle
        decomposition = self.decompose_trend()
        
        # Identification des pics et creux
        extrema = self.find_peaks_troughs()
        
        cycles = []
        for i in range(len(extrema['troughs']) - 1):
            start_idx = extrema['troughs'][i]
            end_idx = extrema['troughs'][i + 1]
            
            # Trouver le pic entre les deux creux
            peak_candidates = [
                p for p in extrema['peaks']
                if start_idx < p < end_idx
            ]
            
            if not peak_candidates:
                continue
                
            peak_idx = peak_candidates[0]
            
            # Calcul des caractéristiques du cycle
            cycle = MarketCycle(
                start_date=self.data.index[start_idx],
                end_date=self.data.index[end_idx],
                duration=(end_idx - start_idx),
                amplitude=self.data[self.price_column].iloc[peak_idx] - 
                         self.data[self.price_column].iloc[start_idx],
                trend='bullish' if decomposition['trend'].iloc[end_idx] > 
                      decomposition['trend'].iloc[start_idx] else 'bearish',
                confidence=self._calculate_cycle_confidence(start_idx, peak_idx, end_idx),
                peak=self.data[self.price_column].iloc[peak_idx],
                trough=min(
                    self.data[self.price_column].iloc[start_idx],
                    self.data[self.price_column].iloc[end_idx]
                )
            )
            
            cycles.append(cycle)
            
        return cycles
        
    def _calculate_cycle_confidence(
        self,
        start_idx: int,
        peak_idx: int,
        end_idx: int
    ) -> float:
        """Calcule un score de confiance pour le cycle identifié.
        
        Args:
            start_idx: Index du début du cycle
            peak_idx: Index du pic
            end_idx: Index de fin du cycle
            
        Returns:
            Score de confiance entre 0 et 1
        """
        # Vérification de la durée
        duration_score = min(
            1.0,
            (end_idx - start_idx) / self.min_cycle_length
        )
        
        # Vérification de l'amplitude
        price_series = self.data[self.price_column]
        amplitude = price_series.iloc[peak_idx] - price_series.iloc[start_idx]
        avg_price = price_series.iloc[start_idx:end_idx].mean()
        amplitude_score = min(1.0, abs(amplitude) / (avg_price * 0.1))
        
        # Vérification de la symétrie
        total_duration = end_idx - start_idx
        up_phase = peak_idx - start_idx
        down_phase = end_idx - peak_idx
        symmetry_score = min(up_phase, down_phase) / max(up_phase, down_phase)
        
        # Score composite
        return (duration_score + amplitude_score + symmetry_score) / 3
        
    def analyze_current_phase(self) -> Dict[str, any]:
        """Analyse la phase actuelle du marché.
        
        Returns:
            Dictionnaire contenant les caractéristiques de la phase actuelle
        """
        cycles = self.identify_cycles()
        if not cycles:
            return {}
            
        last_cycle = cycles[-1]
        current_price = self.data[self.price_column].iloc[-1]
        
        # Détermination de la phase actuelle
        if current_price > last_cycle.peak:
            phase = "Extension haussière"
            confidence = min(1.0, (current_price - last_cycle.peak) / last_cycle.peak)
        elif current_price < last_cycle.trough:
            phase = "Extension baissière"
            confidence = min(1.0, (last_cycle.trough - current_price) / last_cycle.trough)
        else:
            # Position relative dans le cycle
            relative_pos = (current_price - last_cycle.trough) / (last_cycle.peak - last_cycle.trough)
            if relative_pos > 0.8:
                phase = "Distribution"
            elif relative_pos > 0.2:
                phase = "Accumulation"
            else:
                phase = "Support"
            confidence = abs(0.5 - relative_pos) * 2
            
        return {
            'phase': phase,
            'confidence': confidence,
            'last_cycle': last_cycle,
            'days_since_last_peak': (
                self.data.index[-1] - last_cycle.end_date
            ).days,
            'price_from_peak': (current_price - last_cycle.peak) / last_cycle.peak,
            'price_from_trough': (current_price - last_cycle.trough) / last_cycle.trough
        } 