# Documentation du Système de Backtesting

## Introduction

Le système de backtesting de sadie permet de tester des stratégies de trading sur des données historiques pour évaluer leur performance avant de les utiliser en conditions réelles. Ce module fournit des outils puissants et flexibles pour définir, tester et optimiser des stratégies d'investissement.

## Fonctionnalités Principales

- **Test sur données historiques** : Testez vos stratégies sur des données historiques de différentes périodes et timeframes
- **Métriques de performance** : Évaluez vos stratégies avec des métriques complètes (rendement, drawdown, Sharpe ratio, etc.)
- **Optimisation de paramètres** : Trouvez les meilleurs paramètres pour vos stratégies via des méthodes d'optimisation avancées
- **Visualisations claires** : Analysez les résultats via des graphiques détaillés et personnalisables
- **Comparaison de stratégies** : Comparez plusieurs stratégies sur les mêmes données historiques
- **Exportation des résultats** : Exportez vos résultats au format CSV, JSON ou PDF

## Architecture du Système

Le système de backtesting est composé de plusieurs modules :

```
sadie/analysis/backtest/
├── engine.py         # Moteur de backtesting principal
├── strategy.py       # Classes de définition des stratégies
├── metrics.py        # Calcul des métriques de performance
├── optimization.py   # Outils d'optimisation de paramètres
├── risk.py           # Gestion des risques et du capital
├── visualization.py  # Création de graphiques et visualisations
└── utils.py          # Utilitaires divers
```

## Définition d'une Stratégie

### Stratégie Simple

Une stratégie de base peut être définie comme suit :

```python
from sadie.analysis.backtest import Strategy

# Définition d'une stratégie de croisement de moyennes mobiles
ma_cross_strategy = Strategy(
    name="MA Crossover",
    
    # Règle d'entrée en position
    entry_conditions=[
        lambda data: data['ema_fast'][-1] > data['ema_slow'][-1],  # Fast MA au-dessus de Slow MA
        lambda data: data['ema_fast'][-2] <= data['ema_slow'][-2]  # Croisement à la hausse
    ],
    
    # Règle de sortie
    exit_conditions=[
        lambda data: data['ema_fast'][-1] < data['ema_slow'][-1],  # Fast MA en-dessous de Slow MA
        lambda data: data['ema_fast'][-2] >= data['ema_slow'][-2]  # Croisement à la baisse
    ],
    
    # Indicateurs à calculer
    indicators=[
        {'name': 'ema_fast', 'function': 'ema', 'params': {'price': 'close', 'period': 9}},
        {'name': 'ema_slow', 'function': 'ema', 'params': {'price': 'close', 'period': 21}}
    ],
    
    # Paramètres de gestion du risque
    risk_management={
        'stop_loss_pct': 2.0,       # Stop loss en pourcentage du prix d'entrée
        'take_profit_pct': 6.0,     # Take profit en pourcentage du prix d'entrée
        'max_position_size_pct': 20.0,  # Taille maximale de position en % du capital
        'trailing_stop_pct': 1.5    # Stop loss suiveur (optionnel)
    }
)
```

### Stratégie Avancée

Les stratégies avancées peuvent utiliser des conditions plus complexes et des mécanismes de gestion des risques personnalisés :

```python
from sadie.analysis.backtest import AdvancedStrategy, Position

class RSI_MA_Strategy(AdvancedStrategy):
    def init(self):
        # Configuration des indicateurs
        self.add_indicator('rsi', 'rsi', {'period': 14})
        self.add_indicator('ema50', 'ema', {'period': 50})
        self.add_indicator('ema200', 'ema', {'period': 200})
        self.add_indicator('atr', 'atr', {'period': 14})
        
        # Paramètres de la stratégie
        self.rsi_oversold = 30
        self.rsi_overbought = 70
        self.risk_per_trade = 0.02  # 2% du capital par trade
    
    def should_long(self, data):
        # Condition d'entrée long : RSI survendu + EMA50 > EMA200
        if (data['rsi'][-1] < self.rsi_oversold and 
            data['ema50'][-1] > data['ema200'][-1] and
            data['close'][-1] > data['ema50'][-1]):
            return True
        return False
    
    def should_short(self, data):
        # Condition d'entrée short : RSI suracheté + EMA50 < EMA200
        if (data['rsi'][-1] > self.rsi_overbought and 
            data['ema50'][-1] < data['ema200'][-1] and
            data['close'][-1] < data['ema50'][-1]):
            return True
        return False
    
    def position_size(self, data, direction):
        # Calcul de la taille de position basée sur l'ATR
        atr = data['atr'][-1]
        stop_distance = atr * 2  # Stop loss à 2 ATR
        
        if direction == 'long':
            stop_price = data['close'][-1] - stop_distance
        else:  # short
            stop_price = data['close'][-1] + stop_distance
        
        risk_amount = self.portfolio.equity * self.risk_per_trade
        position_size = risk_amount / abs(data['close'][-1] - stop_price)
        
        return position_size, stop_price
    
    def should_exit_long(self, position, data):
        # Sortie de position longue
        if data['rsi'][-1] > self.rsi_overbought:
            return True
        if data['close'][-1] < data['ema50'][-1]:
            return True
        return False
    
    def should_exit_short(self, position, data):
        # Sortie de position courte
        if data['rsi'][-1] < self.rsi_oversold:
            return True
        if data['close'][-1] > data['ema50'][-1]:
            return True
        return False
```

## Exécution d'un Backtest

### Backtest Simple

```python
from sadie.analysis.backtest import Backtest

# Création d'une instance de backtest
backtest = Backtest(
    strategy=ma_cross_strategy,
    symbol="BTC/USD",
    timeframe="1h",
    start_date="2023-01-01",
    end_date="2023-12-31",
    initial_capital=10000,
    commission=0.001,  # 0.1%
    slippage=0.0005    # 0.05%
)

# Exécution du backtest
results = backtest.run()

# Affichage des résultats
print(f"Rendement total: {results.total_return:.2f}%")
print(f"Rendement annualisé: {results.annual_return:.2f}%")
print(f"Sharpe ratio: {results.sharpe_ratio:.2f}")
print(f"Drawdown maximal: {results.max_drawdown:.2f}%")
print(f"Ratio de profit: {results.profit_ratio:.2f}")
print(f"Nombre de trades: {results.total_trades}")
print(f"Pourcentage de trades gagnants: {results.win_rate:.2f}%")
```

### Visualisation des Résultats

```python
from sadie.analysis.backtest import Visualizer

# Création d'un visualiseur
visualizer = Visualizer(results)

# Génération des graphiques
visualizer.plot_equity_curve()
visualizer.plot_underwater_curve()  # Drawdown au fil du temps
visualizer.plot_monthly_returns()
visualizer.plot_trades_on_chart()
visualizer.plot_return_distribution()

# Création d'un dashboard complet
visualizer.create_report(
    filename="ma_cross_strategy_report.pdf",
    include_trade_list=True,
    include_metrics=True
)
```

## Optimisation des Paramètres

Le module d'optimisation permet de trouver les meilleurs paramètres pour une stratégie donnée :

```python
from sadie.analysis.backtest import Optimizer

# Définition des paramètres à optimiser
param_space = {
    'ema_fast': range(5, 21, 1),     # Périodes de 5 à 20 par pas de 1
    'ema_slow': range(20, 101, 5),   # Périodes de 20 à 100 par pas de 5
    'stop_loss_pct': [1.0, 1.5, 2.0, 2.5, 3.0],
    'take_profit_pct': [3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
}

# Création d'une instance d'optimisateur
optimizer = Optimizer(
    strategy=ma_cross_strategy,
    param_space=param_space,
    symbol="BTC/USD",
    timeframe="1h",
    start_date="2023-01-01",
    end_date="2023-12-31",
    initial_capital=10000,
    optimization_metric='sharpe_ratio',  # Métrique à optimiser
    max_threads=4  # Nombre de threads pour le parallélisme
)

# Exécution de l'optimisation
optimization_results = optimizer.run()

# Affichage des meilleurs paramètres
best_params = optimization_results.best_params
print(f"Meilleurs paramètres: {best_params}")
print(f"Sharpe ratio: {optimization_results.best_score:.2f}")

# Visualisation des résultats d'optimisation
optimization_results.plot_param_importance()
optimization_results.plot_param_vs_metric('ema_fast', 'sharpe_ratio')
optimization_results.plot_param_vs_metric('ema_slow', 'sharpe_ratio')
optimization_results.plot_heatmap('ema_fast', 'ema_slow', 'sharpe_ratio')
```

## Walk-Forward Analysis

Le walk-forward testing permet de vérifier la robustesse d'une stratégie en évitant le surapprentissage :

```python
from sadie.analysis.backtest import WalkForwardAnalysis

# Création d'une analyse walk-forward
wfa = WalkForwardAnalysis(
    strategy=ma_cross_strategy,
    param_space=param_space,
    symbol="BTC/USD",
    timeframe="1h",
    start_date="2023-01-01",
    end_date="2023-12-31",
    initial_capital=10000,
    train_size=180,  # Jours d'entraînement
    test_size=30,    # Jours de test
    step_size=30,    # Avancer de 30 jours à chaque itération
    optimization_metric='sharpe_ratio'
)

# Exécution de l'analyse
wfa_results = wfa.run()

# Affichage des résultats
print(f"Performance moyenne sur les périodes de test: {wfa_results.mean_test_return:.2f}%")
print(f"Stabilité des paramètres: {wfa_results.parameter_stability:.2f}")

# Visualisation des résultats
wfa_results.plot_test_periods_performance()
wfa_results.plot_parameter_stability()
```

## Comparaison de Stratégies

Comparez plusieurs stratégies sur les mêmes données historiques :

```python
from sadie.analysis.backtest import StrategyComparison

# Définition des stratégies à comparer
strategies = [
    ma_cross_strategy,
    rsi_strategy,
    bollinger_strategy
]

# Création d'une comparaison
comparison = StrategyComparison(
    strategies=strategies,
    symbol="BTC/USD",
    timeframe="1h",
    start_date="2023-01-01",
    end_date="2023-12-31",
    initial_capital=10000
)

# Exécution de la comparaison
comparison_results = comparison.run()

# Visualisation des résultats
comparison_results.plot_equity_curves()
comparison_results.plot_drawdowns()
comparison_results.plot_metrics_comparison()
comparison_results.create_comparison_report("strategy_comparison.pdf")
```

## Gestion du Risque Avancée

Le module de gestion du risque permet de définir des règles de gestion du capital sophistiquées :

```python
from sadie.analysis.backtest import RiskManager

# Définition d'un gestionnaire de risque personnalisé
class AdaptiveRiskManager(RiskManager):
    def __init__(self, initial_risk=0.02, max_risk=0.05, min_risk=0.01):
        self.initial_risk = initial_risk  # Risque initial par trade (2%)
        self.max_risk = max_risk          # Risque maximal (5%)
        self.min_risk = min_risk          # Risque minimal (1%)
        self.consecutive_wins = 0
        self.consecutive_losses = 0
    
    def calculate_position_size(self, portfolio, price, stop_price):
        # Ajuster le risque en fonction des résultats récents
        if self.consecutive_wins >= 3:
            risk = min(self.initial_risk * 1.5, self.max_risk)
        elif self.consecutive_losses >= 2:
            risk = max(self.initial_risk * 0.5, self.min_risk)
        else:
            risk = self.initial_risk
        
        # Calculer la taille de la position
        risk_amount = portfolio.equity * risk
        position_size = risk_amount / abs(price - stop_price)
        
        return position_size
    
    def update_stats(self, trade_result):
        # Mettre à jour les statistiques après un trade
        if trade_result.profit > 0:
            self.consecutive_wins += 1
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1
            self.consecutive_wins = 0
```

## Interface Utilisateur

L'interface web permet d'interagir facilement avec le système de backtesting :

1. **Création de Stratégies** : Interface visuelle pour définir des stratégies sans coder
2. **Exécution de Backtests** : Paramétrage et lancement des backtests avec quelques clics
3. **Visualisation des Résultats** : Tableaux de bord interactifs pour analyser les performances
4. **Optimisation de Paramètres** : Interface pour définir et exécuter des optimisations
5. **Exportation** : Export des résultats et rapports dans différents formats

## Bonnes Pratiques

### Éviter le Surapprentissage

1. **Division des données** : Utiliser des périodes distinctes pour le développement de la stratégie, l'optimisation et la validation
2. **Walk-forward analysis** : Tester la stratégie sur des périodes glissantes
3. **Validation sur plusieurs actifs** : Vérifier que la stratégie fonctionne sur différents instruments

### Modélisation Réaliste

1. **Frais de transaction** : Inclure les commissions et le slippage
2. **Liquidité** : Prendre en compte les contraintes de volume et de liquidité
3. **Latence** : Modéliser les délais d'exécution des ordres

### Analyse des Résultats

1. **Au-delà du rendement** : Examiner toutes les métriques (drawdown, Sharpe, etc.)
2. **Robustesse** : Analyser la sensibilité de la stratégie aux changements de paramètres
3. **Analyse par périodes** : Examiner les performances dans différentes conditions de marché 