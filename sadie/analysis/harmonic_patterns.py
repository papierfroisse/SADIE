"""Module de détection des motifs harmoniques."""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple

class HarmonicAnalyzer:
    """Détection des motifs harmoniques."""
    
    # Ratios de Fibonacci
    RATIOS = {
        '0.382': 0.382,
        '0.500': 0.500,
        '0.618': 0.618,
        '0.786': 0.786,
        '1.272': 1.272,
        '1.618': 1.618
    }
    
    # Définitions des motifs
    PATTERNS = {
        'Gartley': {
            'XA': (0.618, 0.618),
            'AB': (0.382, 0.886),
            'BC': (0.382, 0.886),
            'CD': (1.272, 1.618)
        },
        'Butterfly': {
            'XA': (0.786, 0.786),
            'AB': (0.382, 0.886),
            'BC': (0.382, 0.886),
            'CD': (1.618, 2.618)
        },
        'Bat': {
            'XA': (0.382, 0.500),
            'AB': (0.382, 0.886),
            'BC': (0.382, 0.886),
            'CD': (1.618, 2.618)
        }
    }
    
    def __init__(self, data: pd.DataFrame):
        """Initialisation de l'analyseur.
        
        Args:
            data: DataFrame avec colonnes high, low, close
        """
        self.data = data
        self.patterns = []
        
    def find_patterns(self) -> List[Dict]:
        """Recherche les motifs harmoniques.
        
        Returns:
            Liste des motifs trouvés avec leurs caractéristiques
        """
        self.patterns = []
        
        # Recherche des pivots
        pivots = self._find_pivots()
        
        # Pour chaque séquence de 5 points (XABCD)
        for i in range(len(pivots) - 4):
            points = pivots[i:i+5]
            
            # Vérification des motifs
            for pattern_name, ratios in self.PATTERNS.items():
                if self._check_pattern(points, ratios):
                    self.patterns.append({
                        'type': pattern_name,
                        'points': points,
                        'trend': 'Bullish' if points[-1]['price'] > points[-2]['price'] else 'Bearish',
                        'reversal_zone': points[-1]['price'],
                        'description': f"Motif {pattern_name} {'haussier' if points[-1]['price'] > points[-2]['price'] else 'baissier'}"
                    })
        
        return self.patterns
    
    def _find_pivots(self) -> List[Dict]:
        """Trouve les points pivots dans les données.
        
        Returns:
            Liste des points pivots avec leur prix et position
        """
        pivots = []
        
        for i in range(2, len(self.data) - 2):
            if self._is_pivot_high(i):
                pivots.append({
                    'type': 'high',
                    'price': self.data['high'].iloc[i],
                    'position': i
                })
            elif self._is_pivot_low(i):
                pivots.append({
                    'type': 'low',
                    'price': self.data['low'].iloc[i],
                    'position': i
                })
        
        return pivots
    
    def _is_pivot_high(self, idx: int) -> bool:
        """Vérifie si le point est un pivot haut.
        
        Args:
            idx: Index du point à vérifier
            
        Returns:
            True si c'est un pivot haut
        """
        return (self.data['high'].iloc[idx] > self.data['high'].iloc[idx-1] and
                self.data['high'].iloc[idx] > self.data['high'].iloc[idx-2] and
                self.data['high'].iloc[idx] > self.data['high'].iloc[idx+1] and
                self.data['high'].iloc[idx] > self.data['high'].iloc[idx+2])
    
    def _is_pivot_low(self, idx: int) -> bool:
        """Vérifie si le point est un pivot bas.
        
        Args:
            idx: Index du point à vérifier
            
        Returns:
            True si c'est un pivot bas
        """
        return (self.data['low'].iloc[idx] < self.data['low'].iloc[idx-1] and
                self.data['low'].iloc[idx] < self.data['low'].iloc[idx-2] and
                self.data['low'].iloc[idx] < self.data['low'].iloc[idx+1] and
                self.data['low'].iloc[idx] < self.data['low'].iloc[idx+2])
    
    def _check_pattern(self, points: List[Dict], ratios: Dict[str, Tuple[float, float]]) -> bool:
        """Vérifie si les points forment un motif valide.
        
        Args:
            points: Liste des points XABCD
            ratios: Ratios attendus pour le motif
            
        Returns:
            True si les points forment le motif
        """
        # Calcul des ratios entre les points
        xa = abs(points[1]['price'] - points[0]['price'])
        ab = abs(points[2]['price'] - points[1]['price'])
        bc = abs(points[3]['price'] - points[2]['price'])
        cd = abs(points[4]['price'] - points[3]['price'])
        
        # Vérification des ratios
        return (self._is_in_range(ab/xa, *ratios['XA']) and
                self._is_in_range(bc/ab, *ratios['AB']) and
                self._is_in_range(cd/bc, *ratios['BC']))
    
    def _is_in_range(self, value: float, min_ratio: float, max_ratio: float, tolerance: float = 0.1) -> bool:
        """Vérifie si une valeur est dans la plage attendue.
        
        Args:
            value: Valeur à vérifier
            min_ratio: Ratio minimum
            max_ratio: Ratio maximum
            tolerance: Tolérance acceptable
            
        Returns:
            True si la valeur est dans la plage
        """
        return min_ratio * (1-tolerance) <= value <= max_ratio * (1+tolerance)