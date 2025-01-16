"""Module d'analyse des patterns dans les cycles de marché."""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from scipy import stats
from scipy.signal import find_peaks
from sklearn.cluster import KMeans

from .advanced_cycles import AdvancedCycleAnalyzer, CycleCharacteristics

@dataclass
class CyclePattern:
    """Représente un pattern de cycle identifié."""
    pattern_type: str  # 'ABC', 'ABCD', '123', 'Head&Shoulders', etc.
    start_date: pd.Timestamp
    end_date: pd.Timestamp
    confidence: float
    points: List[Tuple[pd.Timestamp, float]]  # Points clés du pattern
    description: str

class CyclePatternAnalyzer(AdvancedCycleAnalyzer):
    """Analyseur de patterns dans les cycles de marché."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.patterns: List[CyclePattern] = []
        
    def detect_divergences(self, indicator_column: str = 'volume') -> List[Dict]:
        """Détecte les divergences entre prix et indicateur.
        
        Args:
            indicator_column: Colonne de l'indicateur à comparer
            
        Returns:
            Liste des divergences détectées
        """
        if indicator_column not in self.data.columns:
            raise ValueError(f"Colonne {indicator_column} non trouvée")
            
        # Normalisation des séries
        price_norm = (self.data[self.price_column] - self.data[self.price_column].mean()) / self.data[self.price_column].std()
        indicator_norm = (self.data[indicator_column] - self.data[indicator_column].mean()) / self.data[indicator_column].std()
        
        # Identification des extrema
        price_peaks, _ = find_peaks(price_norm.values, distance=20)
        price_troughs, _ = find_peaks(-price_norm.values, distance=20)
        ind_peaks, _ = find_peaks(indicator_norm.values, distance=20)
        ind_troughs, _ = find_peaks(-indicator_norm.values, distance=20)
        
        divergences = []
        window = 20  # Fenêtre de recherche
        
        # Recherche des divergences
        for i in range(len(price_peaks)-1):
            p1, p2 = price_peaks[i], price_peaks[i+1]
            price_trend = price_norm.iloc[p2] - price_norm.iloc[p1]
            
            # Recherche des pics d'indicateur correspondants
            ind_p1 = ind_peaks[
                (ind_peaks >= max(0, p1-window)) & 
                (ind_peaks <= min(len(indicator_norm), p1+window))
            ]
            ind_p2 = ind_peaks[
                (ind_peaks >= max(0, p2-window)) & 
                (ind_peaks <= min(len(indicator_norm), p2+window))
            ]
            
            if len(ind_p1) > 0 and len(ind_p2) > 0:
                ind_trend = indicator_norm.iloc[ind_p2[0]] - indicator_norm.iloc[ind_p1[0]]
                
                if price_trend * ind_trend < 0:  # Divergence détectée
                    divergences.append({
                        'type': 'bearish' if price_trend > 0 else 'bullish',
                        'start_date': self.data.index[p1],
                        'end_date': self.data.index[p2],
                        'price_change': price_trend,
                        'indicator_change': ind_trend,
                        'confidence': abs(price_trend - ind_trend) / 2
                    })
                    
        return divergences
        
    def identify_patterns(self, window_size: int = 20) -> List[CyclePattern]:
        """Identifie les patterns dans les cycles.
        
        Args:
            window_size: Taille de la fenêtre d'analyse
            
        Returns:
            Liste des patterns identifiés
        """
        self.patterns = []
        cycles = self.identify_cycles()
        
        for cycle in cycles:
            # Extraction des données du cycle
            cycle_data = self.data[
                (self.data.index >= cycle.start_date) & 
                (self.data.index <= cycle.end_date)
            ][self.price_column]
            
            # Normalisation des prix
            prices_norm = (cycle_data - cycle_data.min()) / (cycle_data.max() - cycle_data.min())
            
            # Détection des points pivots
            peaks, _ = find_peaks(prices_norm.values, distance=window_size//4)
            troughs, _ = find_peaks(-prices_norm.values, distance=window_size//4)
            
            # Analyse des patterns
            if len(peaks) == 1 and len(troughs) == 2:
                # Pattern ABC potentiel
                points = [
                    (cycle_data.index[0], cycle_data.iloc[0]),  # A
                    (cycle_data.index[peaks[0]], cycle_data.iloc[peaks[0]]),  # B
                    (cycle_data.index[-1], cycle_data.iloc[-1])  # C
                ]
                
                self.patterns.append(CyclePattern(
                    pattern_type='ABC',
                    start_date=cycle.start_date,
                    end_date=cycle.end_date,
                    confidence=cycle.confidence,
                    points=points,
                    description="Pattern ABC classique"
                ))
                
            elif len(peaks) == 2 and len(troughs) == 2:
                # Pattern ABCD potentiel
                points = [
                    (cycle_data.index[0], cycle_data.iloc[0]),  # A
                    (cycle_data.index[peaks[0]], cycle_data.iloc[peaks[0]]),  # B
                    (cycle_data.index[troughs[-1]], cycle_data.iloc[troughs[-1]]),  # C
                    (cycle_data.index[-1], cycle_data.iloc[-1])  # D
                ]
                
                self.patterns.append(CyclePattern(
                    pattern_type='ABCD',
                    start_date=cycle.start_date,
                    end_date=cycle.end_date,
                    confidence=cycle.confidence * 0.9,  # Légèrement moins confiant
                    points=points,
                    description="Pattern ABCD"
                ))
                
            # Détection Head & Shoulders
            if len(peaks) == 3 and len(troughs) >= 2:
                peak_heights = prices_norm.iloc[peaks]
                if peak_heights.iloc[1] > peak_heights.iloc[0] and peak_heights.iloc[1] > peak_heights.iloc[2]:
                    points = [
                        (cycle_data.index[peaks[0]], cycle_data.iloc[peaks[0]]),  # Left shoulder
                        (cycle_data.index[peaks[1]], cycle_data.iloc[peaks[1]]),  # Head
                        (cycle_data.index[peaks[2]], cycle_data.iloc[peaks[2]])   # Right shoulder
                    ]
                    
                    self.patterns.append(CyclePattern(
                        pattern_type='Head&Shoulders',
                        start_date=cycle.start_date,
                        end_date=cycle.end_date,
                        confidence=cycle.confidence * 0.8,  # Plus complexe, moins confiant
                        points=points,
                        description="Formation Head & Shoulders"
                    ))
                    
        return self.patterns
        
    def cluster_cycles(self, n_clusters: int = 3) -> Dict[str, List[int]]:
        """Regroupe les cycles similaires.
        
        Args:
            n_clusters: Nombre de clusters à identifier
            
        Returns:
            Dictionnaire des cycles par cluster
        """
        cycles = self.identify_cycles()
        if not cycles:
            return {}
            
        # Préparation des données pour le clustering
        cycle_features = []
        for cycle in cycles:
            cycle_data = self.data[
                (self.data.index >= cycle.start_date) & 
                (self.data.index <= cycle.end_date)
            ][self.price_column]
            
            # Normalisation et rééchantillonnage
            prices_norm = (cycle_data - cycle_data.min()) / (cycle_data.max() - cycle_data.min())
            resampled = np.interp(
                np.linspace(0, 1, 20),
                np.linspace(0, 1, len(prices_norm)),
                prices_norm.values
            )
            
            cycle_features.append(resampled)
            
        # Clustering
        kmeans = KMeans(n_clusters=min(n_clusters, len(cycle_features)), random_state=42)
        clusters = kmeans.fit_predict(cycle_features)
        
        # Organisation des résultats
        cycle_clusters = {}
        for i in range(kmeans.n_clusters):
            cycle_clusters[f'cluster_{i}'] = [
                j for j, cluster in enumerate(clusters) if cluster == i
            ]
            
        return cycle_clusters
        
    def analyze_cycle_correlations(self) -> pd.DataFrame:
        """Analyse les corrélations entre cycles consécutifs.
        
        Returns:
            DataFrame des corrélations
        """
        cycles = self.identify_cycles()
        if len(cycles) < 2:
            return pd.DataFrame()
            
        correlations = []
        for i in range(len(cycles)-1):
            cycle1 = self.data[
                (self.data.index >= cycles[i].start_date) & 
                (self.data.index <= cycles[i].end_date)
            ][self.price_column]
            
            cycle2 = self.data[
                (self.data.index >= cycles[i+1].start_date) & 
                (self.data.index <= cycles[i+1].end_date)
            ][self.price_column]
            
            # Normalisation et rééchantillonnage
            c1_norm = (cycle1 - cycle1.min()) / (cycle1.max() - cycle1.min())
            c2_norm = (cycle2 - cycle2.min()) / (cycle2.max() - cycle2.min())
            
            # Rééchantillonnage pour avoir la même longueur
            length = min(len(c1_norm), len(c2_norm))
            if length > 1:
                c1_resampled = np.interp(
                    np.linspace(0, 1, 20),
                    np.linspace(0, 1, len(c1_norm)),
                    c1_norm.values
                )
                c2_resampled = np.interp(
                    np.linspace(0, 1, 20),
                    np.linspace(0, 1, len(c2_norm)),
                    c2_norm.values
                )
                
                # Calcul des corrélations
                corr = np.corrcoef(c1_resampled, c2_resampled)[0, 1]
                
                # Calcul de la distance euclidienne
                distance = np.sqrt(np.sum((c1_resampled - c2_resampled) ** 2))
                
                correlations.append({
                    'cycle_pair': f"{i}-{i+1}",
                    'correlation': corr,
                    'distance': distance,
                    'duration_ratio': cycles[i+1].duration / cycles[i].duration,
                    'amplitude_ratio': abs(cycles[i+1].amplitude / cycles[i].amplitude),
                    'trend_match': cycles[i].trend == cycles[i+1].trend
                })
            
        return pd.DataFrame(correlations) 