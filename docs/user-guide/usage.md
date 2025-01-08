# Guide d'Utilisation

Ce guide explique comment utiliser SADIE pour l'analyse et l'optimisation de portefeuille.

## Démarrage rapide

### Lancement de l'application

```bash
# Démarrer l'API
python -m src.main

# Accéder au dashboard
http://localhost:8000/dashboard
```

## Fonctionnalités principales

### 1. Analyse de marché

#### Prédictions de prix
```python
from sadie.models import PricePredictor

# Créer une instance du prédicteur
predictor = PricePredictor()

# Obtenir des prédictions
predictions = predictor.predict("BTC-USD", horizon="7d")
```

#### Analyse de sentiment
```python
from sadie.analysis import SentimentAnalyzer

# Analyser le sentiment du marché
sentiment = SentimentAnalyzer.analyze("BTC-USD")
```

### 2. Gestion de portefeuille

#### Création d'un portefeuille
```python
from sadie.portfolio import Portfolio

# Créer un nouveau portefeuille
portfolio = Portfolio(
    initial_capital=100000,
    risk_tolerance="moderate"
)

# Ajouter des actifs
portfolio.add_asset("BTC-USD", weight=0.3)
portfolio.add_asset("ETH-USD", weight=0.3)
portfolio.add_asset("SPY", weight=0.4)
```

#### Optimisation automatique
```python
# Optimiser le portefeuille
portfolio.optimize(
    objective="sharpe_ratio",
    constraints={
        "max_position": 0.4,
        "min_position": 0.1
    }
)
```

### 3. Surveillance et alertes

#### Configuration des alertes
```python
from sadie.monitoring import AlertManager

# Configurer des alertes
alerts = AlertManager()
alerts.add_price_alert("BTC-USD", threshold=50000, condition="above")
alerts.add_volatility_alert("market", threshold=0.2, condition="above")
```

#### Suivi des performances
```python
# Obtenir les métriques de performance
performance = portfolio.get_performance_metrics()
print(f"Rendement total : {performance['total_return']}%")
print(f"Ratio Sharpe : {performance['sharpe_ratio']}")
```

## Utilisation avancée

### 1. Personnalisation des modèles

#### Ajustement des paramètres
```python
from sadie.models import LSTMModel

# Créer un modèle personnalisé
model = LSTMModel(
    layers=[128, 64, 32],
    dropout=0.3,
    learning_rate=0.001
)

# Entraîner le modèle
model.train(
    data=historical_data,
    epochs=200,
    batch_size=32
)
```

### 2. Backtesting

#### Test de stratégie
```python
from sadie.backtest import Backtester

# Créer un backtest
backtest = Backtester(
    strategy=portfolio.strategy,
    period="1y",
    initial_capital=100000
)

# Exécuter le backtest
results = backtest.run()
```

### 3. Reporting

#### Génération de rapports
```python
from sadie.reporting import ReportGenerator

# Générer un rapport
report = ReportGenerator(portfolio)
report.generate_pdf("rapport_mensuel.pdf")
```

## Bonnes pratiques

### Gestion des risques
- Diversifiez votre portefeuille
- Utilisez des stop-loss
- Surveillez la volatilité du marché

### Optimisation des performances
- Réentraînez régulièrement les modèles
- Ajustez les paramètres selon les conditions du marché
- Validez les prédictions avec plusieurs indicateurs

## Dépannage

### Problèmes courants

1. **Erreur de prédiction**
   - Vérifiez la qualité des données
   - Ajustez les paramètres du modèle
   - Augmentez la taille des données d'entraînement

2. **Performance du portefeuille**
   - Vérifiez les contraintes d'optimisation
   - Ajustez la fréquence de rééquilibrage
   - Revoyez les paramètres de gestion des risques

## Ressources supplémentaires

- [Documentation API](../dev-guide/api-reference.md)
- [Guide des modèles](../models/lstm.md)
- [Architecture](../dev-guide/architecture.md) 