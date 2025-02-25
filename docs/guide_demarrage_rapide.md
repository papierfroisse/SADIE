# Guide de Démarrage Rapide

Ce guide vous permettra de commencer rapidement avec les fonctionnalités principales de sadie.

## Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/yourusername/sadie.git
cd sadie
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurez votre environnement :
```bash
cp .env.example .env
# Éditez le fichier .env avec vos paramètres
```

## Démarrage de l'Application

1. Démarrez les services de base de données nécessaires (Redis et TimescaleDB)

2. Lancez l'API :
```bash
uvicorn web.app:app --reload
```

3. Dans un autre terminal, lancez l'interface web :
```bash
cd web/static
npm start
```

4. Accédez à l'application via votre navigateur : `http://localhost:3000`

## Collecte des Données

### Configuration d'un Collecteur

```python
from sadie.core.collectors import BinanceCollector

# Création d'un collecteur pour Bitcoin/USDT sur Binance
collector = BinanceCollector(
    symbol="BTCUSDT",
    interval="1m",  # Intervalle de 1 minute
    api_key="votre_api_key",  # Optionnel pour les données publiques
    api_secret="votre_api_secret"  # Optionnel pour les données publiques
)

# Démarrage de la collecte
collector.start()

# Pour arrêter la collecte
collector.stop()
```

### Collecte en Mode Batch pour Historique

```python
from sadie.core.collectors import historical

# Récupération des données historiques
historical_data = historical.get_historical_data(
    exchange="binance",
    symbol="BTCUSDT",
    interval="1h",
    start_date="2023-01-01",
    end_date="2023-12-31"
)

# Sauvegarde des données dans TimescaleDB
historical.save_to_timescaledb(historical_data, "btc_historical")
```

## Analyse Technique

### Calcul d'Indicateurs Techniques

```python
from sadie.analysis.technical import indicators
import pandas as pd

# Chargement des données (exemple avec un DataFrame)
data = pd.DataFrame({
    'open': [...],
    'high': [...],
    'low': [...],
    'close': [...],
    'volume': [...]
})

# Calcul du RSI
rsi = indicators.rsi(data['close'], period=14)

# Calcul des Bandes de Bollinger
upper, middle, lower = indicators.bollinger_bands(
    data['close'], 
    period=20, 
    std_dev=2.0
)

# Calcul du MACD
macd_line, signal_line, histogram = indicators.macd(
    data['close'],
    fast_period=12,
    slow_period=26,
    signal_period=9
)
```

### Détection de Patterns

```python
from sadie.analysis.technical import patterns

# Détection de patterns de chandeliers japonais
doji_patterns = patterns.find_candlestick_patterns(
    data,
    pattern_types=['doji', 'hammer', 'engulfing']
)

# Détection de patterns chartistes
chart_patterns = patterns.find_chart_patterns(
    data,
    pattern_types=['head_and_shoulders', 'double_top', 'triangle']
)

# Affichage des résultats
for pattern in doji_patterns:
    print(f"Pattern {pattern['type']} détecté à l'index {pattern['index']}")
```

## Backtesting

### Création d'une Stratégie Simple

```python
from sadie.analysis.backtest import Strategy, Backtest

# Définition d'une stratégie simple de croisement de moyennes mobiles
strategy = Strategy(
    name="MA Crossover",
    
    # Indicateurs à calculer
    indicators=[
        {'name': 'sma_fast', 'function': 'sma', 'params': {'price': 'close', 'period': 10}},
        {'name': 'sma_slow', 'function': 'sma', 'params': {'price': 'close', 'period': 30}}
    ],
    
    # Règle d'entrée en position (long uniquement)
    entry_conditions=[
        lambda data: data['sma_fast'][-1] > data['sma_slow'][-1],  # Fast MA au-dessus de Slow MA
        lambda data: data['sma_fast'][-2] <= data['sma_slow'][-2]  # Croisement récent
    ],
    
    # Règle de sortie
    exit_conditions=[
        lambda data: data['sma_fast'][-1] < data['sma_slow'][-1]   # Fast MA repasse sous Slow MA
    ],
    
    # Paramètres de gestion du risque
    risk_management={
        'stop_loss_pct': 2.0,       # Stop loss de 2%
        'take_profit_pct': 6.0,     # Take profit de 6%
        'position_size_pct': 10.0   # 10% du capital par position
    }
)

# Création et exécution du backtest
backtest = Backtest(
    strategy=strategy,
    symbol="BTC/USD",
    timeframe="1h",
    start_date="2023-01-01",
    end_date="2023-12-31",
    initial_capital=10000
)

# Exécution du backtest
results = backtest.run()

# Affichage des résultats
print(f"Rendement total: {results.total_return:.2f}%")
print(f"Drawdown maximal: {results.max_drawdown:.2f}%")
print(f"Nombre de trades: {results.total_trades}")
print(f"Pourcentage de trades gagnants: {results.win_rate:.2f}%")
```

### Visualisation des Résultats de Backtest

```python
from sadie.analysis.backtest import Visualizer

# Création d'un visualiseur
visualizer = Visualizer(results)

# Génération des graphiques
visualizer.plot_equity_curve(save_path="equity_curve.png")
visualizer.plot_drawdown(save_path="drawdown.png")
visualizer.plot_monthly_returns(save_path="monthly_returns.png")

# Création d'un rapport complet
visualizer.create_report(filename="backtest_report.pdf")
```

## Surveillance et Métriques

### Configuration des Métriques Prometheus

```python
from sadie.core.monitoring import metrics

# Initialisation de l'exportateur Prometheus
metrics.init_prometheus_exporter(port=9090)

# Création de métriques personnalisées
trade_counter = metrics.create_counter(
    name="trades_total",
    description="Nombre total de trades exécutés",
    labels=["symbol", "direction"]
)

execution_time = metrics.create_histogram(
    name="execution_time_seconds",
    description="Temps d'exécution des opérations",
    labels=["operation"]
)

# Utilisation des métriques
trade_counter.labels(symbol="BTCUSDT", direction="buy").inc()

with execution_time.labels(operation="data_processing").time():
    # Code à mesurer
    process_data()
```

## Alertes

### Création d'Alertes sur Indicateurs

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
        "cross_direction": "above"
    },
    notification_channels=["email", "app"]
)

# Alerte sur seuil de prix
create_alert(
    symbol="ETH/USD",
    alert_type="price_threshold",
    parameters={
        "price_target": 3000,
        "condition": "above"
    },
    notification_channels=["app"]
)
```

## Interface Web

L'interface web de sadie est accessible à l'adresse `http://localhost:3000` après démarrage et propose les fonctionnalités suivantes :

1. **Dashboard** - Vue d'ensemble des marchés et performances
2. **Chart** - Visualisation des graphiques avec indicateurs techniques
3. **Alerts** - Gestion des alertes
4. **Backtest** - Interface de backtesting
5. **Portfolio** - Suivi de portefeuille
6. **Metrics** - Surveillance des performances système

Chaque section dispose de sa propre documentation accessible via le menu d'aide de l'interface.

## Ressources Supplémentaires

- [Documentation complète](docs/)
- [Exemples d'utilisation](examples/)
- [Guide de sécurité](docs/security.md)
- [Documentation API](docs/api.md) 