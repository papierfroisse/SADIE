# SADIE (Smart AI-Driven Investment Engine)

## Description
SADIE est un système avancé d'intelligence artificielle conçu pour l'optimisation de portefeuille et la prédiction des marchés financiers. Le projet combine des modèles LSTM (Long Short-Term Memory) avec des techniques d'apprentissage avancées pour fournir des prédictions fiables et une gestion de portefeuille optimisée.

## Fonctionnalités principales
- Collecte et prétraitement de données de marché en temps réel
- Analyse technique avec plus de 100 indicateurs
- Modèles d'apprentissage automatique avancés (LSTM, Transformers, Hybrides)
- Analyse de sentiment et données alternatives
- Backtesting et optimisation de stratégies
- Interface web interactive pour le suivi des performances
- Notifications en temps réel
- Documentation complète et tests automatisés

## Installation

1. Cloner le dépôt :
```bash
git clone https://github.com/papierfroisse/SADIE.git
cd SADIE
```

2. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Pour le développement, installer les dépendances supplémentaires :
```bash
pip install -r requirements-dev.txt
```

5. Configurer les variables d'environnement :
```bash
cp .env.example .env
# Éditer .env avec vos clés API et configurations
```

## Structure du Projet

```
SADIE/
├── .github/            # Configuration GitHub Actions
├── config/            # Configuration du projet
├── data/              # Données
│   ├── raw/          # Données brutes
│   └── processed/    # Données prétraitées
├── docs/              # Documentation
├── examples/          # Exemples d'utilisation
├── models/            # Modèles entraînés
├── notebooks/         # Notebooks Jupyter
├── scripts/           # Scripts utilitaires
├── src/              # Code source
│   └── sadie/        # Package principal
├── tests/            # Tests
│   ├── unit/        # Tests unitaires
│   ├── integration/ # Tests d'intégration
│   └── performance/ # Tests de performance
├── .env.example      # Template de configuration
├── .gitignore        # Fichiers ignorés par Git
├── .pre-commit-config.yaml # Configuration pre-commit
├── LICENSE           # Licence MIT
├── README.md         # Ce fichier
├── requirements.txt  # Dépendances principales
├── requirements-dev.txt # Dépendances de développement
└── setup.py         # Configuration du package
```

## Utilisation

1. Démarrer la collecte de données :
```bash
python -m sadie.data_collection
```

2. Entraîner un modèle :
```bash
python -m sadie.train
```

3. Lancer le backtesting :
```bash
python -m sadie.backtest
```

4. Démarrer l'interface web :
```bash
python -m sadie.web
```

## Tests

Exécuter les tests :
```bash
pytest
```

Avec la couverture de code :
```bash
pytest --cov=sadie tests/
```

## Documentation
La documentation complète est disponible dans le dossier `docs/` et peut être consultée en ligne à [URL_A_DEFINIR].

## Contribution
Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour les guidelines de contribution.

## Licence
Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails. 