"""Module de détection des patterns harmoniques (Gartley, Butterfly, etc.)."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Dict
import numpy as np
import pandas as pd
from datetime import datetime

class FibonacciRatio:
    """Ratios de Fibonacci utilisés dans l'analyse des patterns harmoniques."""
    
    def __init__(self):
        """Initialise les ratios et tolérances."""
        self.RATIOS = {
            'GARTLEY': {
                'XA/AB': 0.618,  # 61.8%
                'BC/AB': 0.382,  # 38.2%
                'CD/BC': 0.786   # 78.6%
            },
            'BUTTERFLY': {
                'XA/AB': 0.786,  # 78.6%
                'BC/AB': 0.382,  # 38.2%
                'CD/BC': 1.618   # 161.8%
            },
            'BAT': {
                'XA/AB': 0.886,  # 88.6%
                'BC/AB': 0.382,  # 38.2%
                'CD/BC': 1.618   # 161.8%
            },
            'CRAB': {
                'XA/AB': 0.886,  # 88.6%
                'BC/AB': 0.382,  # 38.2%
                'CD/BC': 2.618   # 261.8%
            },
            'SHARK': {
                'XA/AB': 0.886,  # 88.6%
                'BC/AB': 1.130,  # 113.0%
                'CD/BC': 1.618   # 161.8%
            },
            'CYPHER': {
                'XA/AB': 0.786,  # 78.6%
                'BC/AB': 1.272,  # 127.2%
                'CD/BC': 0.786   # 78.6%
            }
        }
        
        # Tolérances augmentées pour chaque ratio
        self.TOLERANCES = {
            'XA/AB': 0.25,  # ±25%
            'BC/AB': 0.25,  # ±25%
            'CD/BC': 0.25   # ±25%
        }

class PatternType(Enum):
    """Types de patterns harmoniques supportés."""
    GARTLEY = "GARTLEY"
    BUTTERFLY = "BUTTERFLY"
    BAT = "BAT"
    CRAB = "CRAB"
    SHARK = "SHARK"
    CYPHER = "CYPHER"

@dataclass
class HarmonicPattern:
    """Représente un pattern harmonique identifié."""
    pattern_type: PatternType
    start_date: datetime
    end_date: datetime
    points: List[Tuple[datetime, float]]  # [(date, price), ...]
    ratios: Dict[str, float]
    trend: str  # "bullish" ou "bearish"
    confidence: float
    potential_reversal_zone: Tuple[float, float]

class HarmonicAnalyzer:
    """Analyseur de patterns harmoniques."""
    
    def __init__(self, data: pd.DataFrame, tolerance: float = 0.20):
        """Initialise l'analyseur avec les données de prix."""
        self.data = data
        self.tolerance = tolerance
        self.fib = FibonacciRatio()
    
    def _calculate_ratios(self, points: List[Tuple[datetime, float]]) -> Dict[str, float]:
        """Calcule les ratios entre les points du pattern."""
        x, a, b, c, d = [p[1] for p in points]  # Prix aux points X, A, B, C, D
        
        # Calcul des mouvements
        xa = abs(a - x)
        ab = abs(b - a)
        bc = abs(c - b)
        cd = abs(d - c)
        
        return {
            'XA': xa,
            'AB': ab,
            'BC': bc,
            'CD': cd,
            'XA/AB': xa / ab if ab != 0 else 0,
            'BC/AB': bc / ab if ab != 0 else 0,
            'CD/BC': cd / bc if bc != 0 else 0
        }
    
    def _check_pattern(self, points: List[Tuple[datetime, float]], pattern_type: PatternType) -> Tuple[bool, float]:
        """Vérifie si les points correspondent à un pattern spécifique."""
        ratios = self._calculate_ratios(points)
        target_ratios = self.fib.RATIOS[pattern_type.value]
        tolerances = self.fib.TOLERANCES
        
        # Calcul de la confiance basé sur la proximité aux ratios cibles
        confidence = 0.0
        matches = 0
        total_deviation = 0.0
        
        for ratio_name, target in target_ratios.items():
            actual = ratios[ratio_name]
            tolerance = tolerances[ratio_name]
            
            # Calcul de la déviation relative
            deviation = abs(actual - target) / target
            total_deviation += deviation
            
            # Vérification plus souple des ratios
            if deviation <= tolerance:
                matches += 1
                # Plus le ratio est proche de la cible, plus la confiance est élevée
                confidence += 1.0 - (deviation / tolerance)
        
        # Calcul de la confiance moyenne
        confidence = confidence / len(target_ratios) if matches > 0 else 0.0
        
        # Ajustement de la confiance en fonction de la déviation totale
        confidence *= (1.0 - min(total_deviation / len(target_ratios), 0.5))
        
        # Vérification des conditions spécifiques à chaque pattern
        if pattern_type == PatternType.SHARK:
            # Le point C doit être plus haut que A pour un SHARK
            _, a, _, c, _ = [p[1] for p in points]
            if c <= a:
                return False, 0.0
        
        elif pattern_type == PatternType.CYPHER:
            # Le point C doit être entre X et A pour un CYPHER
            x, a, _, c, _ = [p[1] for p in points]
            min_xc = min(x, a)
            max_xc = max(x, a)
            if not (min_xc <= c <= max_xc):
                return False, 0.0
        
        # Un pattern est valide si au moins 2 ratios sur 3 correspondent
        # et si la confiance est suffisante
        min_confidence = {
            PatternType.GARTLEY: 0.25,   # Réduit de 0.3
            PatternType.BUTTERFLY: 0.25,  # Réduit de 0.3
            PatternType.BAT: 0.30,        # Réduit de 0.35
            PatternType.CRAB: 0.35,       # Réduit de 0.4
            PatternType.SHARK: 0.35,      # Réduit de 0.4
            PatternType.CYPHER: 0.30      # Réduit de 0.35
        }
        
        is_valid = matches >= 2 and confidence >= min_confidence[pattern_type]
        
        return is_valid, confidence
    
    def _find_swings(self, min_swing: float = 0.005) -> List[Tuple[datetime, float]]:
        """Trouve les points de swing (extrema locaux) dans les données."""
        # Conversion des données en numpy arrays
        prices = self.data['close'].values
        highs = self.data['high'].values
        lows = self.data['low'].values
        dates = self.data.index.values
        swings = []
        last_swing_price = None
        
        # Réduction du nombre de points minimum entre les swings
        min_points = 2  # Minimum de points pour confirmer un swing
        
        for i in range(min_points, len(prices) - min_points):
            # Point haut potentiel
            is_high = (highs[i] == max(highs[i-min_points:i+min_points+1]))
            
            # Point bas potentiel
            is_low = (lows[i] == min(lows[i-min_points:i+min_points+1]))
            
            # Vérification du swing minimum
            if is_high or is_low:
                current_price = prices[i]
                if last_swing_price is None or abs(current_price - last_swing_price) > min_swing * current_price:
                    # Conversion de numpy.datetime64 en datetime
                    date = pd.Timestamp(dates[i]).to_pydatetime()
                    swings.append((date, float(current_price)))
                    last_swing_price = float(current_price)
        
        # Filtrage supplémentaire des swings trop proches
        if len(swings) > 0:
            filtered_swings = [swings[0]]
            min_time_diff = pd.Timedelta(hours=1)  # Minimum 1 heure entre les swings
            
            for i in range(1, len(swings)):
                time_diff = swings[i][0] - filtered_swings[-1][0]
                if time_diff >= min_time_diff:
                    filtered_swings.append(swings[i])
            
            return filtered_swings
        
        return swings
    
    def identify_patterns(self, min_swing: float = 0.005) -> List[HarmonicPattern]:
        """Identifie les patterns harmoniques dans les données."""
        patterns = []
        swings = self._find_swings(min_swing)
        
        if len(swings) < 5:  # Vérification du nombre minimum de points
            return patterns
        
        # Réduction de la fenêtre minimale entre les points
        min_window = 2  # Réduction de la fenêtre minimale
        
        for i in range(len(swings) - 4):
            points = swings[i:i+5]  # X, A, B, C, D
            
            # Vérification de l'ordre temporel
            if all(points[j][0] < points[j+1][0] for j in range(4)):
                time_diff = (points[-1][0] - points[0][0]).days
                if time_diff >= min_window:
                    # Détermination de la tendance
                    trend = "bullish" if points[0][1] < points[1][1] else "bearish"
                    
                    # Vérification des patterns possibles
                    for pattern_type in PatternType:  # Test de tous les patterns
                        is_valid, confidence = self._check_pattern(points, pattern_type)
                        
                        if is_valid:
                            # Calcul de la zone de renversement potentielle
                            last_price = points[-1][1]
                            prz_range = (
                                last_price * (1 - self.tolerance),
                                last_price * (1 + self.tolerance)
                            )
                            
                            patterns.append(HarmonicPattern(
                                pattern_type=pattern_type,
                                start_date=points[0][0],
                                end_date=points[-1][0],
                                points=points,
                                ratios=self._calculate_ratios(points),
                                trend=trend,
                                confidence=confidence,
                                potential_reversal_zone=prz_range
                            ))
        
        return patterns 