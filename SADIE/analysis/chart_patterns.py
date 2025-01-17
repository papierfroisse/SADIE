"""Module de détection des figures chartistes classiques."""

from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import numpy as np
import pandas as pd
from typing import List, Tuple, Optional

class PatternType(Enum):
    """Types de figures chartistes."""
    HEAD_AND_SHOULDERS = "Tête et Épaules"
    INVERSE_HEAD_AND_SHOULDERS = "Tête et Épaules Inversé"
    DOUBLE_TOP = "Double Top"
    DOUBLE_BOTTOM = "Double Bottom"
    TRIPLE_TOP = "Triple Top"
    TRIPLE_BOTTOM = "Triple Bottom"
    ASCENDING_TRIANGLE = "Triangle Ascendant"
    DESCENDING_TRIANGLE = "Triangle Descendant"
    SYMMETRICAL_TRIANGLE = "Triangle Symétrique"
    RECTANGLE = "Rectangle"
    FLAG = "Drapeau"
    PENNANT = "Fanion"
    CUP_AND_HANDLE = "Coupe et Anse"

@dataclass
class ChartPattern:
    """Représente une figure chartiste identifiée."""
    pattern_type: PatternType
    start_date: datetime
    end_date: datetime
    points: List[Tuple[datetime, float]]
    trend: str
    confidence: float
    target_price: float
    stop_loss: float
    volume_confirmation: bool
    breakout_level: float
    support_resistance: List[float]
    technical_confirmation: bool = False
    technical_score: float = 0.0
    rsi_confirmation: bool = False
    bb_confirmation: bool = False
    macd_confirmation: bool = False
    # Valeurs détaillées des indicateurs
    rsi_value: float = 0.0
    rsi_min: float = 0.0
    rsi_max: float = 0.0
    price_vs_ma: float = 0.0
    bb_test: bool = False
    macd_hist: float = 0.0
    macd_vs_signal: float = 0.0
    id: int = 0  # Pour l'affichage
    # Indices pour l'analyse technique
    start_idx: int = 0
    end_idx: int = 0

    def __post_init__(self):
        """Initialisation après la création."""
        self.id = ChartPattern._next_id
        ChartPattern._next_id += 1

# Variable de classe pour générer des IDs uniques
ChartPattern._next_id = 1

class ChartPatternAnalyzer:
    """Analyseur de figures chartistes."""
    
    def __init__(self, data: pd.DataFrame, tolerance: float = 0.02):
        """
        Initialise l'analyseur.
        
        Args:
            data: DataFrame avec colonnes OHLCV
            tolerance: Tolérance pour la détection des niveaux (%)
        """
        self.data = data
        self.tolerance = tolerance
        self._validate_data()
    
    def _validate_data(self) -> None:
        """Vérifie que les données sont valides."""
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"Les données doivent contenir les colonnes: {required_columns}")
        
        if not isinstance(self.data.index, pd.DatetimeIndex):
            raise ValueError("L'index doit être de type DatetimeIndex")
    
    def _find_peaks_and_troughs(self, window: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """
        Trouve les sommets et creux locaux.
        
        Args:
            window: Taille de la fenêtre pour la détection
            
        Returns:
            Tuple contenant les indices des sommets et creux
        """
        prices = self.data['close'].values
        peaks = []
        troughs = []
        
        # Calcul des moyennes mobiles pour lisser les prix
        ma = pd.Series(prices).rolling(window=5).mean().bfill().values
        
        for i in range(window, len(prices) - window):
            # Utilisation des prix lissés pour la détection
            window_left = ma[i-window:i]
            window_right = ma[i+1:i+window+1]
            current = ma[i]
            
            # Détection des sommets
            if (current > max(window_left) and 
                current > max(window_right) and 
                current > ma[i-1] and 
                current > ma[i+1]):
                peaks.append(i)
            
            # Détection des creux
            if (current < min(window_left) and 
                current < min(window_right) and 
                current < ma[i-1] and 
                current < ma[i+1]):
                troughs.append(i)
        
        return np.array(peaks), np.array(troughs)
    
    def _calculate_trend_line(self, points: List[Tuple[int, float]]) -> Tuple[float, float]:
        """
        Calcule la ligne de tendance passant par les points.
        
        Args:
            points: Liste de tuples (index, prix)
            
        Returns:
            Tuple (pente, ordonnée à l'origine)
        """
        x = np.array([p[0] for p in points])
        y = np.array([p[1] for p in points])
        
        if len(x) < 2:
            return 0, 0
        
        slope, intercept = np.polyfit(x, y, 1)
        return slope, intercept
    
    def _calculate_price_target(self, pattern: ChartPattern) -> float:
        """
        Calcule l'objectif de prix basé sur la figure.
        
        Args:
            pattern: Figure chartiste détectée
            
        Returns:
            Objectif de prix
        """
        if pattern.pattern_type in [PatternType.HEAD_AND_SHOULDERS, PatternType.INVERSE_HEAD_AND_SHOULDERS]:
            # Distance de la tête à la ligne de cou
            head_to_neckline = abs(pattern.points[2][1] - pattern.breakout_level)
            return pattern.breakout_level + (head_to_neckline * (-1 if pattern.trend == 'bearish' else 1))
        
        elif pattern.pattern_type in [PatternType.DOUBLE_TOP, PatternType.DOUBLE_BOTTOM,
                                    PatternType.TRIPLE_TOP, PatternType.TRIPLE_BOTTOM]:
            # Hauteur de la figure
            height = abs(max(p[1] for p in pattern.points) - min(p[1] for p in pattern.points))
            return pattern.breakout_level + (height * (-1 if pattern.trend == 'bearish' else 1))
        
        elif pattern.pattern_type in [PatternType.ASCENDING_TRIANGLE, PatternType.DESCENDING_TRIANGLE,
                                    PatternType.SYMMETRICAL_TRIANGLE]:
            # Hauteur du triangle
            height = abs(pattern.support_resistance[0] - pattern.support_resistance[1])
            return pattern.breakout_level + height
        
        return pattern.breakout_level
    
    def _validate_volume(self, start_idx: int, end_idx: int) -> bool:
        """
        Vérifie si le volume confirme la figure.
        
        Args:
            start_idx: Index de début
            end_idx: Index de fin
            
        Returns:
            True si le volume confirme la figure
        """
        volume = self.data['volume'].values[start_idx:end_idx]
        avg_volume = np.mean(volume)
        breakout_volume = volume[-1]
        
        return breakout_volume > avg_volume * 1.5
    
    def _calculate_confidence(self, 
                            shoulder_diff: float,
                            neckline_slope: float,
                            head_relative_height: float,
                            time_symmetry: float,
                            volume_confirmation: bool) -> float:
        """
        Calcule le niveau de confiance pour une figure.
        
        Args:
            shoulder_diff: Différence relative entre les épaules
            neckline_slope: Pente de la ligne de cou
            head_relative_height: Hauteur relative de la tête
            time_symmetry: Symétrie temporelle
            volume_confirmation: Confirmation par le volume
            
        Returns:
            Niveau de confiance entre 0 et 1
        """
        confidence = 0.0
        
        # 1. Symétrie des épaules (25%)
        shoulder_symmetry = max(0, 1.0 - (shoulder_diff / (self.tolerance * 1.5)))
        confidence += 0.25 * shoulder_symmetry
        
        # 2. Horizontalité de la ligne de cou (25%)
        neckline_horizontality = max(0, 1.0 - abs(neckline_slope))
        confidence += 0.25 * neckline_horizontality
        
        # 3. Position relative de la tête (25%)
        head_score = min(head_relative_height, 0.1) / 0.1  # Normalisation à 10%
        confidence += 0.25 * head_score
        
        # 4. Symétrie temporelle (15%)
        time_symmetry_score = max(0, 1.0 - (time_symmetry / 0.5))
        confidence += 0.15 * time_symmetry_score
        
        # 5. Confirmation du volume (10%)
        confidence += 0.10 if volume_confirmation else 0.0
        
        return max(0, min(1, confidence))  # Assurer que la confiance est entre 0 et 1
    
    def detect_head_and_shoulders(self, min_pattern_size: int = 20) -> List[ChartPattern]:
        """
        Détecte les figures en Tête et Épaules (classiques et inversées).
        
        Args:
            min_pattern_size: Taille minimale de la figure en périodes
            
        Returns:
            Liste des figures détectées
        """
        patterns = []
        
        # Détection des pics et creux
        peaks = self._find_peaks(self.data['high'].values)
        troughs = self._find_peaks(-self.data['low'].values)
        
        # Validation des figures
        for i in range(len(peaks) - 2):  # -2 car il nous faut 3 pics
            # Vérification de la taille minimale
            if peaks[i+2] - peaks[i] < min_pattern_size:
                continue
                
            # Extraction des points clés
            left_shoulder = (peaks[i], self.data['high'].iloc[peaks[i]])
            head = (peaks[i+1], self.data['high'].iloc[peaks[i+1]])
            right_shoulder = (peaks[i+2], self.data['high'].iloc[peaks[i+2]])
            
            # Recherche des creux entre les épaules et la tête
            left_trough = None
            right_trough = None
            for t in troughs:
                if peaks[i] < t < peaks[i+1]:
                    if left_trough is None or self.data['low'].iloc[t] < self.data['low'].iloc[left_trough]:
                        left_trough = t
                elif peaks[i+1] < t < peaks[i+2]:
                    if right_trough is None or self.data['low'].iloc[t] < self.data['low'].iloc[right_trough]:
                        right_trough = t
            
            if left_trough is None or right_trough is None:
                continue
                
            # Validation des critères
            left_trough_point = (left_trough, self.data['low'].iloc[left_trough])
            right_trough_point = (right_trough, self.data['low'].iloc[right_trough])
            
            # 1. La tête doit être plus haute que les épaules
            if not (head[1] > left_shoulder[1] * 1.02 and head[1] > right_shoulder[1] * 1.02):
                continue
                
            # 2. Les épaules doivent être à peu près au même niveau (±2%)
            shoulder_diff = abs(left_shoulder[1] - right_shoulder[1]) / left_shoulder[1]
            if shoulder_diff > 0.02:
                continue
                
            # 3. Les creux doivent former une ligne horizontale (±1%)
            trough_diff = abs(left_trough_point[1] - right_trough_point[1]) / left_trough_point[1]
            if trough_diff > 0.01:
                continue
                
            # 4. Symétrie temporelle (±20%)
            left_width = head[0] - left_shoulder[0]
            right_width = right_shoulder[0] - head[0]
            width_diff = abs(left_width - right_width) / left_width
            if width_diff > 0.20:
                continue
            
            # Calcul de la ligne de cou (neckline)
            neckline = (left_trough_point[1] + right_trough_point[1]) / 2
            
            # Calcul de la hauteur de la tête
            head_height = head[1] - neckline
            
            # Calcul de l'objectif de prix et du stop loss
            target_price = neckline - head_height  # Objectif = neckline - hauteur
            stop_loss = head[1] * 1.01  # Stop 1% au-dessus de la tête
            
            # Calcul du score de confiance
            confidence = (
                (1 - shoulder_diff) * 0.30 +  # Symétrie des épaules
                (1 - trough_diff) * 0.30 +    # Alignement des creux
                (1 - width_diff) * 0.20 +     # Symétrie temporelle
                min(head_height / left_shoulder[1], 0.20) * 1.00  # Hauteur relative de la tête
            ) * 100  # Conversion en pourcentage
            
            # Vérification du volume
            volume_confirmation = self._check_volume_confirmation(
                [left_shoulder[0], head[0], right_shoulder[0]],
                [left_trough, right_trough],
                'bearish'
            )
            
            # Création du pattern
            pattern = ChartPattern(
                pattern_type=PatternType.HEAD_AND_SHOULDERS,
                start_date=self.data.index[left_shoulder[0]],
                end_date=self.data.index[right_shoulder[0]],
                points=[
                    (self.data.index[left_shoulder[0]], left_shoulder[1]),
                    (self.data.index[left_trough], left_trough_point[1]),
                    (self.data.index[head[0]], head[1]),
                    (self.data.index[right_trough], right_trough_point[1]),
                    (self.data.index[right_shoulder[0]], right_shoulder[1])
                ],
                trend='bearish',
                confidence=confidence,
                target_price=target_price,
                stop_loss=stop_loss,
                volume_confirmation=volume_confirmation,
                breakout_level=neckline,
                support_resistance=[neckline, head[1]],
                start_idx=left_shoulder[0],
                end_idx=right_shoulder[0]
            )
            
            # Vérification des indicateurs techniques
            self._check_technical_confirmation(pattern)
            
            # Ajout du pattern si la confiance est suffisante
            if confidence >= 40:
                patterns.append(pattern)
            
            # Recherche de figures inversées (IHS)
            # ... (même logique mais inversée)
        
        return patterns
    
    def detect_double_formations(self, pattern_type: PatternType, min_pattern_size: int = 20) -> List[ChartPattern]:
        """
        Détecte les doubles tops et doubles bottoms.
        
        Args:
            pattern_type: Type de figure à détecter (DOUBLE_TOP ou DOUBLE_BOTTOM)
            min_pattern_size: Taille minimale de la figure (par défaut 20 périodes)
            
        Returns:
            Liste des figures détectées
        """
        patterns = []
        peaks, troughs = self._find_peaks_and_troughs()
        
        # Sélection des points selon le type de figure
        if pattern_type == PatternType.DOUBLE_TOP:
            extremes = peaks
            opposite_extremes = troughs
            trend = 'bearish'
        else:  # DOUBLE_BOTTOM
            extremes = troughs
            opposite_extremes = peaks
            trend = 'bullish'
        
        # Si pas assez de points pour former une figure
        if len(extremes) < 2 or len(opposite_extremes) < 1:
            return patterns
        
        for i in range(len(extremes) - 1):
            try:
                # Points principaux
                first_peak_idx = extremes[i]
                second_peak_idx = extremes[i + 1]
                
                # Vérification du creux/sommet intermédiaire
                middle_candidates = opposite_extremes[
                    (opposite_extremes > first_peak_idx) & 
                    (opposite_extremes < second_peak_idx)
                ]
                
                if len(middle_candidates) == 0:
                    continue
                
                # Sélection du creux/sommet le plus significatif
                middle_idx = middle_candidates[
                    np.argmin(self.data['close'].values[middle_candidates])
                    if pattern_type == PatternType.DOUBLE_TOP
                    else np.argmax(self.data['close'].values[middle_candidates])
                ]
                
                prices = self.data['close'].values
                first_peak = prices[first_peak_idx]
                second_peak = prices[second_peak_idx]
                middle_point = prices[middle_idx]
                
                # Validation avec critères stricts
                # 1. Les sommets/creux doivent être au même niveau (±1%)
                peak_diff = abs(first_peak - second_peak) / first_peak
                
                # 2. Le point intermédiaire doit être suffisamment éloigné (>2%)
                if pattern_type == PatternType.DOUBLE_TOP:
                    middle_diff = (min(first_peak, second_peak) - middle_point) / middle_point
                else:  # DOUBLE_BOTTOM
                    middle_diff = (middle_point - max(first_peak, second_peak)) / middle_point
                
                # 3. Taille minimale de la figure
                size_ok = (second_peak_idx - first_peak_idx) >= min_pattern_size
                
                # 4. Symétrie temporelle (±20%)
                time_symmetry = abs(
                    (middle_idx - first_peak_idx) - 
                    (second_peak_idx - middle_idx)
                ) / (middle_idx - first_peak_idx)
                
                if (peak_diff < self.tolerance and
                    middle_diff >= 0.02 and
                    size_ok and
                    time_symmetry < 0.2):
                    
                    # Points clés de la figure
                    points = [
                        (self.data.index[first_peak_idx], first_peak),
                        (self.data.index[middle_idx], middle_point),
                        (self.data.index[second_peak_idx], second_peak)
                    ]
                    
                    # Niveau de cassure
                    breakout_level = middle_point
                    
                    # Vérification du volume
                    volume_confirmation = (
                        self.data['volume'].values[second_peak_idx] > 
                        self.data['volume'].values[first_peak_idx] * 1.2
                    )
                    
                    # Calcul de la confiance
                    confidence = 0.0
                    
                    # 1. Égalité des sommets/creux (30%)
                    peak_symmetry = max(0, 1.0 - (peak_diff / self.tolerance))
                    confidence += 0.30 * peak_symmetry
                    
                    # 2. Profondeur du point intermédiaire (30%)
                    depth_score = min(middle_diff, 0.05) / 0.05  # Normalisation à 5%
                    confidence += 0.30 * depth_score
                    
                    # 3. Symétrie temporelle (25%)
                    time_symmetry_score = max(0, 1.0 - (time_symmetry / 0.2))
                    confidence += 0.25 * time_symmetry_score
                    
                    # 4. Confirmation du volume (15%)
                    confidence += 0.15 if volume_confirmation else 0.0
                    
                    # Création de la figure uniquement si la confiance est suffisante
                    if confidence >= 0.4:  # Seuil minimum de 40%
                        height = abs(max(first_peak, second_peak) - middle_point)
                        
                        pattern = ChartPattern(
                            pattern_type=pattern_type,
                            start_date=self.data.index[first_peak_idx],
                            end_date=self.data.index[second_peak_idx],
                            points=points,
                            trend=trend,
                            confidence=confidence,
                            target_price=breakout_level + (height * (-1 if trend == 'bearish' else 1)),
                            stop_loss=max(first_peak, second_peak) * (1.01 if trend == 'bearish' else 0.99),
                            volume_confirmation=volume_confirmation,
                            breakout_level=breakout_level,
                            support_resistance=[
                                min(first_peak, second_peak, middle_point),
                                max(first_peak, second_peak, middle_point)
                            ]
                        )
                        
                        patterns.append(pattern)
            
            except Exception as e:
                print(f"Erreur lors de la détection d'une figure: {str(e)}")
                continue
        
        return patterns
    
    def detect_triangles(self, min_pattern_size: int = 20) -> List[ChartPattern]:
        """
        Détecte les différents types de triangles (Ascendant, Descendant, Symétrique).
        
        Args:
            min_pattern_size: Taille minimale de la figure (par défaut 20 périodes)
            
        Returns:
            Liste des figures détectées
        """
        patterns = []
        peaks, troughs = self._find_peaks_and_troughs()
        
        # Si pas assez de points pour former un triangle
        if len(peaks) < 2 or len(troughs) < 2:
            return patterns
        
        # Analyse sur des fenêtres glissantes
        for i in range(len(peaks) - 1):
            for j in range(len(troughs) - 1):
                try:
                    # Sélection des points pour former les lignes de tendance
                    peak_indices = peaks[i:i+2]
                    trough_indices = troughs[j:j+2]
                    
                    # Vérification de l'ordre chronologique
                    all_points = sorted(list(peak_indices) + list(trough_indices))
                    if len(all_points) < 4:
                        continue
                    
                    # Vérification de la taille minimale
                    if all_points[-1] - all_points[0] < min_pattern_size:
                        continue
                    
                    prices = self.data['close'].values
                    peak_prices = prices[peak_indices]
                    trough_prices = prices[trough_indices]
                    
                    # Calcul des lignes de tendance
                    upper_slope, upper_intercept = self._calculate_trend_line([
                        (peak_indices[0], peak_prices[0]),
                        (peak_indices[1], peak_prices[1])
                    ])
                    
                    lower_slope, lower_intercept = self._calculate_trend_line([
                        (trough_indices[0], trough_prices[0]),
                        (trough_indices[1], trough_prices[1])
                    ])
                    
                    # Validation des pentes pour chaque type de triangle
                    is_ascending = (
                        abs(upper_slope) < self.tolerance and  # Ligne supérieure horizontale
                        lower_slope > 0.001  # Ligne inférieure montante
                    )
                    
                    is_descending = (
                        upper_slope < -0.001 and  # Ligne supérieure descendante
                        abs(lower_slope) < self.tolerance  # Ligne inférieure horizontale
                    )
                    
                    is_symmetrical = (
                        upper_slope < -0.001 and  # Ligne supérieure descendante
                        lower_slope > 0.001 and  # Ligne inférieure montante
                        abs(abs(upper_slope) - abs(lower_slope)) < self.tolerance  # Pentes similaires
                    )
                    
                    # Points de convergence
                    if any([is_ascending, is_descending, is_symmetrical]):
                        # Calcul du point de convergence
                        x_convergence = int((lower_intercept - upper_intercept) / (upper_slope - lower_slope))
                        
                        # Vérification que le point de convergence est dans un futur raisonnable
                        if x_convergence <= all_points[-1] or x_convergence >= all_points[-1] + min_pattern_size * 2:
                            continue
                        
                        # Points clés de la figure
                        points = [
                            (self.data.index[all_points[0]], prices[all_points[0]]),
                            (self.data.index[all_points[1]], prices[all_points[1]]),
                            (self.data.index[all_points[2]], prices[all_points[2]]),
                            (self.data.index[all_points[3]], prices[all_points[3]])
                        ]
                        
                        # Calcul de la hauteur actuelle du triangle
                        current_upper = upper_slope * all_points[-1] + upper_intercept
                        current_lower = lower_slope * all_points[-1] + lower_intercept
                        height = current_upper - current_lower
                        
                        # Vérification du volume
                        volume_decreasing = (
                            self.data['volume'].values[all_points[-1]] <
                            self.data['volume'].values[all_points[0]] * 0.8
                        )
                        
                        # Calcul de la confiance
                        confidence = 0.0
                        
                        # 1. Qualité des lignes de tendance (30%)
                        trend_quality = min(
                            1.0,
                            (x_convergence - all_points[-1]) / (min_pattern_size * 2)
                        )
                        confidence += 0.30 * trend_quality
                        
                        # 2. Hauteur minimale (25%)
                        height_score = min(height / prices[all_points[0]], 0.05) / 0.05
                        confidence += 0.25 * height_score
                        
                        # 3. Nombre de touchés des lignes (25%)
                        touches = len(set(all_points))
                        touch_score = min(touches / 4, 1.0)
                        confidence += 0.25 * touch_score
                        
                        # 4. Volume décroissant (20%)
                        confidence += 0.20 if volume_decreasing else 0.0
                        
                        # Création de la figure uniquement si la confiance est suffisante
                        if confidence >= 0.4:  # Seuil minimum de 40%
                            if is_ascending:
                                pattern_type = PatternType.ASCENDING_TRIANGLE
                                trend = 'bullish'
                                target = current_upper + height
                            elif is_descending:
                                pattern_type = PatternType.DESCENDING_TRIANGLE
                                trend = 'bearish'
                                target = current_lower - height
                            else:  # Symétrique
                                pattern_type = PatternType.SYMMETRICAL_TRIANGLE
                                # Tendance basée sur le contexte précédent
                                prev_trend = prices[all_points[0]] > prices[all_points[0] - min_pattern_size]
                                trend = 'bullish' if prev_trend else 'bearish'
                                target = current_upper + height if trend == 'bullish' else current_lower - height
                            
                            pattern = ChartPattern(
                                pattern_type=pattern_type,
                                start_date=self.data.index[all_points[0]],
                                end_date=self.data.index[all_points[-1]],
                                points=points,
                                trend=trend,
                                confidence=confidence,
                                target_price=target,
                                stop_loss=current_lower * 0.99 if trend == 'bullish' else current_upper * 1.01,
                                volume_confirmation=volume_decreasing,
                                breakout_level=current_upper if trend == 'bullish' else current_lower,
                                support_resistance=[current_lower, current_upper]
                            )
                            
                            patterns.append(pattern)
                
                except Exception as e:
                    print(f"Erreur lors de la détection d'un triangle: {str(e)}")
                    continue
        
        return patterns
    
    def detect_flags_and_pennants(self, min_pattern_size: int = 20) -> List[ChartPattern]:
        """
        Détecte les drapeaux et fanions.
        
        Args:
            min_pattern_size: Taille minimale de la figure (par défaut 20 périodes)
            
        Returns:
            Liste des figures détectées
        """
        patterns = []
        peaks, troughs = self._find_peaks_and_troughs()
        
        # Si pas assez de points pour former une figure
        if len(peaks) < 2 or len(troughs) < 2:
            return patterns
        
        # Analyse sur des fenêtres glissantes
        for i in range(len(self.data) - min_pattern_size):
            try:
                # Fenêtre d'analyse
                window = slice(i, i + min_pattern_size)
                prices = self.data['close'].values[window]
                volumes = self.data['volume'].values[window]
                
                # Identification du mât (forte tendance précédente)
                pole_start = i - min_pattern_size
                if pole_start < 0:
                    continue
                    
                pole_prices = self.data['close'].values[pole_start:i]
                pole_return = (pole_prices[-1] - pole_prices[0]) / pole_prices[0]
                
                # Vérification d'une forte tendance (>5%)
                is_bullish = pole_return > 0.05
                is_bearish = pole_return < -0.05
                
                if not (is_bullish or is_bearish):
                    continue
                
                # Calcul des lignes de tendance
                upper_points = []
                lower_points = []
                
                for j in range(len(prices) - 1):
                    if j > 0:
                        if prices[j] > prices[j-1] and prices[j] > prices[j+1]:
                            upper_points.append((j, prices[j]))
                        elif prices[j] < prices[j-1] and prices[j] < prices[j+1]:
                            lower_points.append((j, prices[j]))
                
                if len(upper_points) < 2 or len(lower_points) < 2:
                    continue
                
                # Calcul des pentes
                upper_slope, upper_intercept = self._calculate_trend_line(upper_points)
                lower_slope, lower_intercept = self._calculate_trend_line(lower_points)
                
                # Validation des critères pour drapeau/fanion
                is_flag = (
                    abs(upper_slope - lower_slope) < self.tolerance and  # Lignes parallèles
                    abs(upper_slope) > 0.001  # Pente significative
                )
                
                is_pennant = (
                    upper_slope < -0.001 and  # Ligne supérieure descendante
                    lower_slope > 0.001 and  # Ligne inférieure montante
                    abs(abs(upper_slope) - abs(lower_slope)) < self.tolerance  # Convergence symétrique
                )
                
                if is_flag or is_pennant:
                    # Points clés de la figure
                    points = [
                        (self.data.index[pole_start], pole_prices[0]),  # Début du mât
                        (self.data.index[i], pole_prices[-1]),  # Fin du mât
                        (self.data.index[i + min_pattern_size - 1], prices[-1])  # Fin de la figure
                    ]
                    
                    # Calcul de la hauteur du mât
                    pole_height = abs(pole_prices[-1] - pole_prices[0])
                    
                    # Vérification du volume
                    volume_pattern = (
                        np.mean(volumes) < np.mean(self.data['volume'].values[pole_start:i]) and
                        np.all(np.diff(volumes) <= 0)  # Volume décroissant
                    )
                    
                    # Calcul de la confiance
                    confidence = 0.0
                    
                    # 1. Force de la tendance précédente (30%)
                    trend_strength = min(abs(pole_return), 0.15) / 0.15  # Normalisation à 15%
                    confidence += 0.30 * trend_strength
                    
                    # 2. Qualité des lignes de tendance (25%)
                    if is_flag:
                        trend_quality = 1.0 - abs(upper_slope - lower_slope) / self.tolerance
                    else:  # Pennant
                        trend_quality = 1.0 - abs(abs(upper_slope) - abs(lower_slope)) / self.tolerance
                    confidence += 0.25 * trend_quality
                    
                    # 3. Durée de la consolidation (25%)
                    duration_score = min(len(prices) / min_pattern_size, 1.0)
                    confidence += 0.25 * duration_score
                    
                    # 4. Volume décroissant (20%)
                    confidence += 0.20 if volume_pattern else 0.0
                    
                    # Création de la figure uniquement si la confiance est suffisante
                    if confidence >= 0.4:  # Seuil minimum de 40%
                        pattern_type = PatternType.FLAG if is_flag else PatternType.PENNANT
                        trend = 'bullish' if is_bullish else 'bearish'
                        
                        # Calcul de l'objectif (projection du mât)
                        target_price = prices[-1] + (pole_height * (1 if is_bullish else -1))
                        
                        pattern = ChartPattern(
                            pattern_type=pattern_type,
                            start_date=self.data.index[pole_start],
                            end_date=self.data.index[i + min_pattern_size - 1],
                            points=points,
                            trend=trend,
                            confidence=confidence,
                            target_price=target_price,
                            stop_loss=min(prices) * 0.99 if is_bullish else max(prices) * 1.01,
                            volume_confirmation=volume_pattern,
                            breakout_level=max(prices) if is_bullish else min(prices),
                            support_resistance=[min(prices), max(prices)]
                        )
                        
                        patterns.append(pattern)
            
            except Exception as e:
                print(f"Erreur lors de la détection d'un drapeau/fanion: {str(e)}")
                continue
        
        return patterns
    
    def detect_all_patterns(self) -> List[ChartPattern]:
        """
        Détecte toutes les figures chartistes possibles.
        
        Returns:
            Liste de toutes les figures détectées
        """
        patterns = []
        
        # Détection des figures en Tête et Épaules
        patterns.extend(self.detect_head_and_shoulders())
        
        # Détection des Double Top/Bottom
        patterns.extend(self.detect_double_formations(PatternType.DOUBLE_TOP))
        patterns.extend(self.detect_double_formations(PatternType.DOUBLE_BOTTOM))
        
        # Détection des triangles
        patterns.extend(self.detect_triangles())
        
        # Détection des drapeaux et fanions
        patterns.extend(self.detect_flags_and_pennants())
        
        # Vérification des confirmations techniques pour chaque pattern
        for pattern in patterns:
            self._check_technical_confirmation(pattern)
        
        return patterns 
    
    def _calculate_rsi(self, period: int = 14) -> pd.Series:
        """
        Calcule le RSI (Relative Strength Index).
        
        Args:
            period: Période pour le calcul du RSI
            
        Returns:
            Série des valeurs du RSI
        """
        close = self.data['close']
        delta = close.diff()
        
        # Séparer les variations positives et négatives
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        
        # Calculer les moyennes mobiles exponentielles
        avg_gain = gain.ewm(span=period, adjust=False).mean()
        avg_loss = loss.ewm(span=period, adjust=False).mean()
        
        # Calculer le RS et le RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_bollinger_bands(self, period: int = 20, num_std: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calcule les bandes de Bollinger.
        
        Args:
            period: Période pour la moyenne mobile
            num_std: Nombre d'écarts-types pour les bandes
            
        Returns:
            Tuple (bande supérieure, moyenne mobile, bande inférieure)
        """
        close = self.data['close']
        
        # Calculer la moyenne mobile et l'écart-type
        middle = close.rolling(window=period).mean()
        std = close.rolling(window=period).std()
        
        # Calculer les bandes
        upper = middle + (std * num_std)
        lower = middle - (std * num_std)
        
        return upper, middle, lower
    
    def _calculate_macd(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calcule le MACD (Moving Average Convergence Divergence).
        
        Args:
            fast_period: Période courte pour l'EMA
            slow_period: Période longue pour l'EMA
            signal_period: Période pour la ligne de signal
            
        Returns:
            Tuple (ligne MACD, ligne de signal, histogramme)
        """
        close = self.data['close']
        
        # Calculer les moyennes mobiles exponentielles
        ema_fast = close.ewm(span=fast_period, adjust=False).mean()
        ema_slow = close.ewm(span=slow_period, adjust=False).mean()
        
        # Calculer la ligne MACD
        macd_line = ema_fast - ema_slow
        
        # Calculer la ligne de signal
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        
        # Calculer l'histogramme
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def _check_technical_confirmation(self, pattern: ChartPattern) -> float:
        """Vérifie les confirmations techniques pour un pattern donné."""
        # Récupérer les données pour la fenêtre d'analyse
        start_idx = max(0, pattern.start_idx - 20)  # 20 périodes avant le début du pattern
        window_data = self.data.iloc[start_idx:pattern.end_idx + 1]
        
        # Calculer les indicateurs sur la fenêtre d'analyse
        rsi = self._calculate_rsi()  # Calculer sur toutes les données
        bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands()  # Calculer sur toutes les données
        macd_line, signal_line, histogram = self._calculate_macd()  # Calculer sur toutes les données
        
        # Extraire les valeurs pour la fenêtre d'analyse
        window_rsi = rsi.loc[window_data.index]
        window_bb_upper = bb_upper.loc[window_data.index]
        window_bb_middle = bb_middle.loc[window_data.index]
        window_bb_lower = bb_lower.loc[window_data.index]
        window_macd = macd_line.loc[window_data.index]
        window_signal = signal_line.loc[window_data.index]
        window_hist = histogram.loc[window_data.index]
        
        # Vérifier les confirmations en fonction de la tendance
        trend = pattern.trend
        score = 0.0
        confirmations = 0
        
        # RSI
        rsi_last = float(window_rsi.iloc[-1])
        rsi_min = float(window_rsi.min())
        rsi_max = float(window_rsi.max())
        print(f"RSI : {rsi_last:.2f} (min={rsi_min:.2f}, max={rsi_max:.2f})")
        
        if trend == "bullish":
            rsi_conf = rsi_last > 50 or rsi_min < 30
        else:
            rsi_conf = rsi_last < 50 or rsi_max > 70
        
        if rsi_conf:
            score += 0.33
            confirmations += 1
        
        # Bandes de Bollinger
        last_close = float(window_data['close'].iloc[-1])
        last_ma = float(window_bb_middle.iloc[-1])
        ratio = last_close / last_ma - 1
        print(f"BB : prix={last_close:.2f}, MM20={last_ma:.2f}, ratio={ratio:.2%}")
        
        if trend == "bullish":
            bb_conf = last_close > last_ma or (window_data['close'] < window_bb_lower).any()
        else:
            bb_conf = last_close < last_ma or (window_data['close'] > window_bb_upper).any()
        
        if bb_conf:
            score += 0.33
            confirmations += 1
        
        # MACD
        hist_last = float(window_hist.iloc[-1])
        macd_last = float(window_macd.iloc[-1])
        signal_last = float(window_signal.iloc[-1])
        print(f"MACD : hist={hist_last:.2f}, MACD vs Signal={macd_last - signal_last:.2f}")
        
        if trend == "bullish":
            macd_conf = hist_last > 0 or macd_last > signal_last
        else:
            macd_conf = hist_last < 0 or macd_last < signal_last
        
        if macd_conf:
            score += 0.34
            confirmations += 1
        
        # Afficher les confirmations
        print(f"Confirmations : RSI={rsi_conf}, BB={bb_conf}, MACD={macd_conf}")
        print(f"Score technique : {score:.2%}")
        
        return score
    
    def _find_peaks(self, data: np.ndarray, min_distance: int = 5) -> np.ndarray:
        """
        Trouve les pics (maximums locaux) dans une série de données.
        
        Args:
            data: Série de données à analyser
            min_distance: Distance minimale entre deux pics
            
        Returns:
            Indices des pics trouvés
        """
        # Initialisation
        peaks = []
        last_peak = -min_distance
        
        # Parcours des données (sauf premier et dernier points)
        for i in range(1, len(data)-1):
            # Un point est un pic s'il est plus grand que ses voisins
            if data[i] > data[i-1] and data[i] > data[i+1]:
                # Vérification de la distance minimale avec le dernier pic
                if i - last_peak >= min_distance:
                    peaks.append(i)
                    last_peak = i
                # Si le nouveau pic est plus haut que le dernier, on remplace
                elif data[i] > data[last_peak]:
                    peaks[-1] = i
                    last_peak = i
        
        return np.array(peaks) 