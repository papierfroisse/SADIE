# Analyse Technique

Ce module fournit des outils avancés pour l'analyse technique des marchés financiers.

## Indicateurs Techniques

La classe `TechnicalIndicators` calcule les indicateurs techniques les plus courants :

### Bandes de Bollinger
```python
from sadie.analysis.indicators import TechnicalIndicators

# Initialisation
data = pd.DataFrame(...)  # DataFrame avec colonnes OHLCV
indicators = TechnicalIndicators(data)

# Calcul des bandes
bb_mid, bb_up, bb_low, bb_b = indicators.bollinger_bands(
    window=20,  # Période de la moyenne mobile
    std_dev=2.0  # Nombre d'écarts-types
)
```

### MACD (Moving Average Convergence Divergence)
```python
macd, signal, hist = indicators.macd(
    fast=12,    # Période rapide
    slow=26,    # Période lente
    signal=9    # Période du signal
)
```

### Stochastique
```python
k, d = indicators.stochastic(
    k_period=14,  # Période %K
    d_period=3,   # Période %D
    smooth_k=3    # Lissage de %K
)
```

### RSI (Relative Strength Index)
```python
rsi = indicators.rsi(period=14)
```

### ATR (Average True Range)
```python
atr = indicators.atr(period=14)
```

### Profil de Volume
```python
profile = indicators.volume_profile(price_levels=100)
```

### Niveaux de Fibonacci
```python
levels = indicators.fibonacci_levels(high=100, low=90)
```

### Détection des Divergences
```python
divergences = indicators.detect_divergences(
    indicator=rsi,  # Série de l'indicateur
    window=10       # Fenêtre d'analyse
)
```

## Patterns Harmoniques

Le module `harmonic_patterns` permet de détecter automatiquement les patterns harmoniques :

### Types de Patterns Supportés
- Gartley
- Butterfly
- Bat
- Crab
- Shark
- Cypher

### Utilisation
```python
from sadie.analysis.harmonic_patterns import HarmonicAnalyzer

# Initialisation
analyzer = HarmonicAnalyzer(data)

# Détection des patterns
patterns = analyzer.identify_patterns(
    min_swing=0.01,      # Mouvement minimum
    min_confidence=0.75  # Confiance minimum
)

# Analyse des résultats
for pattern in patterns:
    print(f"Pattern: {pattern.pattern_type.value}")
    print(f"Tendance: {pattern.trend.value}")
    print(f"Confiance: {pattern.confidence:.1%}")
    print(f"Zone de retournement: {pattern.potential_reversal_zone}")
```

## Visualisation

La classe `ChartVisualizer` crée des graphiques interactifs avec Plotly :

### Graphique Complet
```python
from sadie.analysis.visualization import ChartVisualizer

# Initialisation
visualizer = ChartVisualizer(data)

# Création du graphique
fig = visualizer.create_chart(
    show_volume=True,   # Afficher le volume
    show_bb=True,       # Bandes de Bollinger
    show_macd=True,     # MACD
    show_stoch=True,    # Stochastique
    show_patterns=True  # Patterns harmoniques
)

# Sauvegarde
fig.write_html("analysis.html")
```

### Personnalisation
Le thème et les couleurs sont entièrement personnalisables :
```python
visualizer.colors.update({
    'up': '#00ff00',      # Couleur haussière
    'down': '#ff0000',    # Couleur baissière
    'volume': '#2196f3',  # Couleur du volume
    # etc.
})
```

## Exemple Complet

Voir `examples/analysis_example.py` pour un exemple complet d'utilisation :
- Collecte de données depuis Binance
- Stockage dans Redis
- Calcul des indicateurs
- Détection des patterns
- Visualisation interactive 