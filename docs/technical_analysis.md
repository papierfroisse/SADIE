# Documentation sur l'Analyse Technique

## Introduction

L'analyse technique est une méthode d'évaluation des marchés financiers basée sur l'étude des graphiques et des patterns de prix. Le module d'analyse technique de sadie fournit un ensemble complet d'outils pour identifier les tendances, les points d'entrée/sortie potentiels et les signaux de trading.

## Indicateurs Techniques Disponibles

### Indicateurs de Tendance
- **Moyennes Mobiles (MA)**
  - Simple (SMA)
  - Exponentielle (EMA)
  - Pondérée (WMA)
  - Adaptative (AMA)
- **MACD (Moving Average Convergence Divergence)**
  - Paramètres classiques (12, 26, 9)
  - Personnalisation des périodes
- **Indicateur Directionnel (ADX)**
  - Identification de la force de tendance

### Oscillateurs
- **RSI (Relative Strength Index)**
  - Détection des conditions de surachat/survente
  - Divergences avec le prix
- **Stochastique**
  - Stochastique rapide et lent
  - Divergences et croisements
- **CCI (Commodity Channel Index)**
  - Identification des extrêmes de marché

### Bandes et Canaux
- **Bandes de Bollinger**
  - Écarts-types personnalisables
  - Calcul de largeur des bandes (squeeze)
- **Canaux de Keltner**
  - Comparaison avec les Bandes de Bollinger
- **Canaux de Donchian**
  - Identification des cassures de volatilité

### Indicateurs de Volume
- **OBV (On-Balance Volume)**
  - Confirmation des mouvements de prix
- **Money Flow Index**
  - Identification de la pression acheteur/vendeur
- **Accumulation/Distribution**
  - Divergences avec le prix

### Indicateurs de Volatilité
- **ATR (Average True Range)**
  - Mesure de la volatilité
  - Paramétrage des stops
- **Bollinger Bandwidth**
  - Détection de la contraction/expansion de volatilité

### Études Complexes
- **Ichimoku Cloud**
  - Analyse complète (Tenkan-sen, Kijun-sen, Senkou Span A/B, Chikou Span)
  - Interprétation des signaux
- **Fibonacci Retracement**
  - Niveaux automatiques sur les swings
  - Projections et extensions

## Détection de Patterns

### Patterns Classiques
- **Chandeliers Japonais**
  - Doji, Marteau, Étoile du Matin/Soir, etc.
  - Configurations multi-chandeliers
- **Patterns Chartistes**
  - Tête et Épaules
  - Doubles/Triples Sommets et Creux
  - Triangles (Ascendant, Descendant, Symétrique)
  - Rectangles, Fanions, Drapeaux

### Systèmes Automatisés
- **Détection Algorithmique**
  - Reconnaissance automatique des patterns
  - Alertes sur formation de patterns
- **Calcul de Probabilités**
  - Analyse statistique des patterns détectés
  - Taux de réussite historique

## Utilisation des Indicateurs

### API d'Analyse Technique

Pour utiliser les indicateurs techniques :

```python
from sadie.analysis.technical import indicators

# Calcul du RSI sur une série de prix
rsi_values = indicators.rsi(prices, period=14)

# Calcul des Bandes de Bollinger
upper, middle, lower = indicators.bollinger_bands(
    prices, 
    period=20, 
    std_dev=2.0
)

# Analyse avec plusieurs indicateurs
analysis_result = indicators.multi_indicator_analysis(
    prices,
    indicators=['rsi', 'macd', 'bollinger'],
    periods={'rsi': 14, 'macd': [12, 26, 9], 'bollinger': 20}
)
```

### Interprétation Automatique

Le module d'interprétation permet d'obtenir des signaux de trading basés sur les indicateurs techniques :

```python
from sadie.analysis.technical import signals

# Obtenir des signaux basés sur un indicateur
rsi_signals = signals.get_rsi_signals(prices, period=14, 
                                     overbought=70, oversold=30)

# Combiner des signaux de plusieurs indicateurs
combined_signals = signals.combine_signals(
    prices,
    indicators=['rsi', 'macd', 'bollinger'],
    weights={'rsi': 0.4, 'macd': 0.4, 'bollinger': 0.2}
)
```

## Configuration des Alertes

Configuration d'alertes basées sur les indicateurs techniques :

```python
from sadie.web.api.alerts import create_alert

# Alerte sur croisement de moyennes mobiles
create_alert(
    symbol="BTC/USD",
    alert_type="indicator_cross",
    parameters={
        "indicator1": "ema",
        "indicator1_params": {"period": 50},
        "indicator2": "ema", 
        "indicator2_params": {"period": 200},
        "cross_direction": "above"  # ou "below"
    },
    notification_channels=["email", "app"]
)

# Alerte sur condition RSI
create_alert(
    symbol="ETH/USD",
    alert_type="indicator_threshold",
    parameters={
        "indicator": "rsi",
        "indicator_params": {"period": 14},
        "condition": "less_than",
        "threshold": 30
    },
    notification_channels=["app"]
)
```

## Visualisation des Indicateurs

L'interface utilisateur permet de visualiser et d'interagir avec les indicateurs techniques :

- Superposition de plusieurs indicateurs sur le même graphique
- Personnalisation des paramètres des indicateurs
- Sauvegarde des configurations d'analyse préférées
- Partage des configurations avec d'autres utilisateurs
- Exportation des graphiques et analyses

## Prochaines Fonctionnalités

- **Screener d'indicateurs techniques** : Filtrage des actifs selon des critères techniques
- **Indicateurs personnalisés** : Création d'indicateurs sur mesure via une interface graphique
- **Backtesting intégré** : Test des signaux des indicateurs sur données historiques
- **Apprentissage automatique** : Optimisation des paramètres des indicateurs
- **Tableaux de bord d'analyse** : Configurations prédéfinies pour différents styles de trading

## Exemples d'Utilisation

### Exemple 1 : Stratégie de Trading Simple

```python
from sadie.analysis.technical import backtest

# Définir une stratégie basée sur le croisement de moyennes mobiles
strategy = backtest.Strategy(
    name="MA Crossover",
    entry_rule=lambda data: data['ema_9'][-1] > data['ema_21'][-1] and 
                          data['ema_9'][-2] <= data['ema_21'][-2],
    exit_rule=lambda data: data['ema_9'][-1] < data['ema_21'][-1] and 
                         data['ema_9'][-2] >= data['ema_21'][-2],
    indicators=[
        ('ema_9', {'price': 'close', 'period': 9}),
        ('ema_21', {'price': 'close', 'period': 21})
    ],
    stop_loss=2.0,  # en pourcentage
    take_profit=6.0  # en pourcentage
)

# Backtest de la stratégie
result = backtest.run(
    strategy=strategy,
    symbol="BTC/USD",
    timeframe="1h",
    start_date="2023-01-01",
    end_date="2023-12-31"
)

# Afficher les résultats
print(f"Profit total: {result.total_profit}%")
print(f"Ratio de Sharpe: {result.sharpe_ratio}")
print(f"Drawdown maximal: {result.max_drawdown}%")
print(f"Transactions gagnantes: {result.win_rate}%")
```

### Exemple 2 : Analyse Multi-Indicateurs

```python
from sadie.analysis.technical import indicators, plots

# Obtenir les données
data = sadie.get_historical_data("ETH/USD", timeframe="1d", limit=365)

# Calculer plusieurs indicateurs
results = indicators.calculate_multiple([
    {"name": "rsi", "params": {"period": 14}},
    {"name": "macd", "params": {"fast_period": 12, "slow_period": 26, "signal_period": 9}},
    {"name": "bollinger", "params": {"period": 20, "std_dev": 2.0}}
], data)

# Générer un graphique d'analyse complet
fig = plots.create_advanced_chart(
    data, 
    results, 
    title="Analyse technique ETH/USD",
    save_path="eth_analysis.png"
)
```

## Ressources d'Apprentissage

- **Tutoriels intégrés** : Apprenez à utiliser chaque indicateur efficacement
- **Études de cas** : Exemples concrets d'application des indicateurs
- **Glossaire technique** : Définitions des termes d'analyse technique
- **Bibliothèque de patterns** : Galerie visuelle des patterns chartistes couramment recherchés 