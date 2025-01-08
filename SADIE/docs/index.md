# SADIE - Documentation

Bienvenue dans la documentation de SADIE (Système d'Analyse et de Décision pour l'Investissement en cryptomonnaies).

## Vue d'ensemble

SADIE est un système avancé d'analyse et de trading de cryptomonnaies qui combine :
- L'apprentissage automatique pour la prédiction des prix
- L'analyse technique pour l'identification des opportunités
- L'automatisation des décisions de trading
- Le backtesting et l'optimisation des stratégies

## Démarrage rapide

1. Installation :
```bash
git clone https://github.com/papierfroisse/SADIE.git
cd SADIE
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

2. Configuration :
```bash
cp .env.example .env
# Éditer .env avec vos clés API et configurations
```

3. Utilisation :
```bash
python -m sadie.data_collection  # Collecter les données
python -m sadie.train           # Entraîner un modèle
python -m sadie.backtest        # Tester une stratégie
python -m sadie.web             # Lancer l'interface web
```

## Structure du projet

```
SADIE/
├── .github/            # Configuration GitHub Actions
├── config/            # Configuration du projet
├── data/              # Données
│   ├── raw/          # Données brutes
│   └── processed/    # Données prétraitées
├── docs/              # Documentation
├── models/            # Modèles entraînés
├── notebooks/         # Notebooks Jupyter
├── scripts/           # Scripts utilitaires
├── src/              # Code source
│   └── sadie/        # Package principal
└── tests/            # Tests
    ├── unit/
    ├── integration/
    └── performance/
```

## Fonctionnalités principales

- **Collecte de données** : Intégration avec plusieurs sources (Binance, Alpha Vantage)
- **Prétraitement** : Nettoyage, normalisation et calcul d'indicateurs techniques
- **Modélisation** : LSTM, analyse de sentiments et indicateurs techniques avancés
- **Backtesting** : Framework complet pour tester et optimiser les stratégies
- **Interface web** : Dashboard en temps réel et configuration des stratégies
- **Notifications** : Alertes Telegram et rapports de performance

## État du projet

Consultez notre [feuille de route](ROADMAP.md) pour voir l'état d'avancement du projet et les fonctionnalités à venir.

## Contribution

Les contributions sont les bienvenues ! Consultez notre [guide de contribution](CONTRIBUTING.md) pour commencer.
