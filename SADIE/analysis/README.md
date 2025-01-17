# Analysis SADIE

Composants d'analyse et de traitement des données de SADIE.

## Structure

```
analysis/
├── market_cycles.py     # Analyse des cycles de marché
├── chart_patterns.py    # Détection de patterns techniques
├── harmonic_patterns.py # Patterns harmoniques (Gartley, etc.)
└── advanced_cycles.py   # Analyse avancée des cycles
```

## Fonctionnalités

### Analyse des Cycles
- Décomposition des cycles de marché
- Détection des points de retournement
- Analyse des tendances
- Prédiction de durée

### Patterns Techniques
- Patterns classiques (Triangle, Head & Shoulders, etc.)
- Divergences
- Niveaux clés
- Validation statistique

### Patterns Harmoniques
- Gartley, Butterfly, Bat
- Ratios de Fibonacci
- Points de pivot
- Validation géométrique

## Utilisation

```python
from SADIE.analysis import MarketCycleAnalyzer
from SADIE.analysis import ChartPatternDetector

# Analyse des cycles
analyzer = MarketCycleAnalyzer(data)
cycles = analyzer.detect_cycles()
predictions = analyzer.predict_next_cycle()

# Détection de patterns
detector = ChartPatternDetector(data)
patterns = detector.detect_patterns()
```

## Performance

- Analyse en temps réel
- Optimisation vectorielle avec NumPy
- Cache des résultats intermédiaires
- Parallélisation des calculs lourds

## Configuration

```python
# Configuration de l'analyseur
analyzer = MarketCycleAnalyzer(
    min_cycle_length=20,
    max_cycle_length=200,
    confidence_threshold=0.8
)

# Configuration du détecteur
detector = ChartPatternDetector(
    patterns=["triangle", "head_shoulders"],
    min_pattern_size=10,
    validation_threshold=0.7
)
```

## Tests

```bash
# Tests unitaires
pytest tests/analysis/test_market_cycles.py
pytest tests/analysis/test_patterns.py

# Tests de performance
pytest tests/analysis/test_performance.py
``` 