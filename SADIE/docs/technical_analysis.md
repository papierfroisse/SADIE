# Module d'Analyse Technique de SADIE

Ce document décrit en détail le module d'analyse technique de SADIE, ses fonctionnalités, et comment l'utiliser pour analyser les données de marché et tester des stratégies de trading.

## Table des matières

1. [Introduction](#introduction)
2. [Installation et Prérequis](#installation-et-prérequis)
3. [Indicateurs Techniques](#indicateurs-techniques)
4. [Détection de Patterns](#détection-de-patterns)
5. [Support et Résistance](#support-et-résistance)
6. [Backtesting](#backtesting)
7. [API Web](#api-web)
8. [Interface Utilisateur](#interface-utilisateur)
9. [Exemples d'utilisation](#exemples-dutilisation)

## Introduction

Le module d'analyse technique de SADIE fournit des outils pour l'analyse des marchés financiers en utilisant des méthodes d'analyse technique. Il comprend des indicateurs techniques courants, une détection de patterns, une identification des niveaux de support et de résistance, et un moteur de backtesting complet pour tester et optimiser les stratégies de trading.

## Installation et Prérequis

Les fonctionnalités d'analyse technique sont incluses dans l'installation standard de SADIE. Assurez-vous que les dépendances suivantes sont installées :

```bash
pip install pandas numpy matplotlib scikit-learn ta plotly
```

Les modules d'analyse technique se trouvent dans le package `sadie.core.technical` et les modules de backtesting dans `sadie.core.backtest`.

## Indicateurs Techniques

### Indicateurs disponibles

Le module fournit les indicateurs techniques suivants :

- **Moyennes Mobiles** : Simple (SMA), Exponentielle (EMA), Pondérée (WMA)
- **Oscillateurs** : RSI, Stochastique, MACD, OBV
- **Bandes de Bollinger**
- **Ichimoku Kinko Hyo**
- **Momentum** : ROC, CCI
- **Volumes** : OBV, VWAP

### Utilisation des indicateurs

```python
from sadie.core.technical.indicators import calculate_rsi, calculate_macd, calculate_bollinger_bands

# Calculer le RSI
rsi = calculate_rsi(df, period=14)

# Calculer le MACD
macd, signal, histogram = calculate_macd(df, short_period=12, long_period=26, signal_period=9)

# Calculer les bandes de Bollinger
upper, middle, lower = calculate_bollinger_bands(df, period=20, std_dev=2.0)

# Générer plusieurs indicateurs à la fois
indicators = generate_technical_indicators(df, indicators=['rsi', 'macd', 'bollinger_bands'])
```

## Détection de Patterns

### Types de patterns disponibles

Le module permet de détecter différents types de patterns :

- **Patterns de chandeliers japonais** : Doji, Marteau, Étoile du matin/soir, Englobant
- **Patterns graphiques** : Tête et épaules, Double sommet/creux, Triangles, Drapeaux

### Utilisation de la détection de patterns

```python
from sadie.core.technical.patterns import identify_candlestick_patterns, detect_patterns

# Détecter des patterns de chandeliers japonais
candlestick_patterns = identify_candlestick_patterns(df)

# Détecter différents types de patterns
patterns = detect_patterns(df, pattern_types=['candlestick', 'head_and_shoulders', 'double_top_bottom'])
```

## Support et Résistance

Le module permet d'identifier les niveaux de support et de résistance dans les données de prix.

```python
from sadie.core.technical.patterns import detect_support_resistance

# Détecter les niveaux de support et résistance
support_levels, resistance_levels = detect_support_resistance(df, window_size=10, sensitivity=0.01)
```

## Backtesting

Le module de backtesting permet de tester des stratégies de trading sur des données historiques.

### Création d'une stratégie

Pour créer une stratégie personnalisée, héritez de la classe `Strategy` et implémentez la méthode `execute()` :

```python
from sadie.core.backtest.strategy import Strategy, PositionType, Position

class MyCrossingStrategy(Strategy):
    def __init__(self, fast_period=10, slow_period=30, name="My Strategy"):
        parameters = {"fast_period": fast_period, "slow_period": slow_period}
        super().__init__(name=name, parameters=parameters)
        self.fast_period = fast_period
        self.slow_period = slow_period
    
    def execute(self, data):
        # Implémentation de la logique de la stratégie
        # Voir la documentation pour un exemple complet
        return self.result
```

### Exécution d'un backtest

```python
from sadie.core.backtest.engine import BacktestEngine, BacktestConfig
from sadie.core.backtest.strategy import SimpleMovingAverageCrossover

# Créer une configuration
config = BacktestConfig(
    initial_capital=10000.0,
    commission_rate=0.001,
    use_stop_loss=True
)

# Créer le moteur de backtesting
engine = BacktestEngine(config=config)

# Créer une stratégie
strategy = SimpleMovingAverageCrossover(
    fast_period=10,
    slow_period=30,
    use_stop_loss=True,
    stop_loss_pct=0.02
)

# Exécuter le backtest
result = engine.run(strategy, historical_data)

# Analyser les résultats
print(f"Rendement total: {result.metrics.total_return:.2%}")
print(f"Ratio de Sharpe: {result.metrics.sharpe_ratio:.2f}")
print(f"Drawdown maximum: {result.metrics.max_drawdown:.2%}")

# Visualiser les résultats
fig = result.plot_equity_curve()
fig.savefig("equity_curve.png")
```

### Optimisation des paramètres

```python
from sadie.core.backtest.optimizer import optimize_strategy, StrategyOptimizer, OptimizationConfig

# Méthode simple
result = optimize_strategy(
    strategy_class=SimpleMovingAverageCrossover,
    data=historical_data,
    parameters={
        "fast_period": [5, 10, 15, 20],
        "slow_period": [20, 30, 40, 50],
        "stop_loss_pct": [0.01, 0.02, 0.03]
    },
    metric="sharpe_ratio",
    maximize=True,
    n_jobs=-1  # Utiliser tous les cores disponibles
)

# Ou via la classe StrategyOptimizer pour plus de contrôle
config = OptimizationConfig(
    parameters={
        "fast_period": [5, 10, 15, 20],
        "slow_period": [20, 30, 40, 50]
    },
    metric="total_return",
    maximize=True,
    n_jobs=4
)

optimizer = StrategyOptimizer(
    strategy_class=SimpleMovingAverageCrossover,
    config=config
)

result = optimizer.optimize(historical_data)

# Afficher les meilleurs paramètres
print(f"Meilleurs paramètres: {result.best_parameters}")
print(f"Valeur de la métrique: {result.metric_value:.4f}")

# Sauvegarder les résultats
result.save("optimization_results.json")
```

## API Web

L'API Web permet d'accéder aux fonctionnalités d'analyse technique via des endpoints REST.

### Endpoints disponibles

- `GET /api/technical/indicators` - Liste des indicateurs disponibles
- `POST /api/technical/indicator` - Calculer un indicateur technique
- `POST /api/technical/patterns` - Détecter des patterns
- `POST /api/technical/support-resistance` - Calculer les niveaux de support et résistance

### Exemples d'utilisation de l'API

```python
import requests

# Récupérer la liste des indicateurs disponibles
response = requests.get("http://localhost:8000/api/technical/indicators")
indicators = response.json()

# Calculer un indicateur
response = requests.post(
    "http://localhost:8000/api/technical/indicator",
    json={
        "data": historical_data,
        "indicator": "rsi",
        "parameters": {"period": 14}
    }
)
result = response.json()

# Détecter des patterns
response = requests.post(
    "http://localhost:8000/api/technical/patterns",
    json={
        "data": historical_data,
        "pattern_types": ["candlestick"]
    }
)
patterns = response.json()
```

## Interface Utilisateur

L'interface utilisateur d'analyse technique est accessible via le frontend web à l'adresse `http://localhost:3000/technical-analysis`.

L'interface permet :
- D'afficher et comparer différents indicateurs techniques
- De détecter des patterns dans les données
- D'identifier les niveaux de support et de résistance
- De visualiser les résultats de backtesting

## Exemples d'utilisation

Voici quelques exemples concrets d'utilisation du module d'analyse technique de SADIE :

### Exemple 1 : Calcul d'indicateurs techniques

```python
import pandas as pd
from sadie.core.technical.indicators import generate_technical_indicators

# Charger les données
df = pd.read_csv("btc_data.csv")

# Calculer plusieurs indicateurs
indicators = generate_technical_indicators(
    df,
    indicators=["rsi", "macd", "bollinger_bands", "sma"]
)

# Afficher le DataFrame avec les indicateurs
print(indicators.tail())
```

### Exemple 2 : Backtesting d'une stratégie de croisement de moyennes mobiles

```python
import pandas as pd
from sadie.core.backtest.engine import BacktestEngine
from sadie.core.backtest.strategy import SimpleMovingAverageCrossover

# Charger les données
df = pd.read_csv("eth_data.csv")

# Créer la stratégie
strategy = SimpleMovingAverageCrossover(
    fast_period=10,
    slow_period=30,
    use_stop_loss=True,
    stop_loss_pct=0.02,
    name="ETH SMA Crossover"
)

# Exécuter le backtest
engine = BacktestEngine()
result = engine.run(strategy, df)

# Afficher les résultats
print(f"Rendement total: {result.metrics.total_return:.2%}")
print(f"Nombre de trades: {result.metrics.total_trades}")
print(f"Win rate: {result.metrics.win_rate:.2%}")

# Sauvegarder le graphique
fig = result.plot_equity_curve()
fig.savefig("eth_strategy_result.png")
```

### Exemple 3 : Comparaison de plusieurs stratégies

```python
import pandas as pd
from sadie.core.backtest.engine import BacktestEngine
from sadie.core.backtest.strategy import SimpleMovingAverageCrossover

# Charger les données
df = pd.read_csv("btc_data.csv")

# Créer différentes configurations de la stratégie
strategy1 = SimpleMovingAverageCrossover(fast_period=5, slow_period=20, name="SMA 5-20")
strategy2 = SimpleMovingAverageCrossover(fast_period=10, slow_period=30, name="SMA 10-30")
strategy3 = SimpleMovingAverageCrossover(fast_period=20, slow_period=50, name="SMA 20-50")

# Comparer les stratégies
engine = BacktestEngine()
results = engine.compare_strategies([strategy1, strategy2, strategy3], df)

# Afficher les rendements
for name, result in results.items():
    print(f"{name}: {result.metrics.total_return:.2%}")

# Visualiser la comparaison
fig = engine.plot_comparison(results)
fig.savefig("strategy_comparison.png")
```

---

Pour plus d'informations, consultez la documentation complète de l'API ou contactez l'équipe de développement. 