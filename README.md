# SADIE - Système d'Analyse et de Décision pour l'Investissement en cryptomonnaies

SADIE est un système avancé d'analyse et de trading de cryptomonnaies qui utilise l'apprentissage automatique et l'analyse technique pour prendre des décisions d'investissement éclairées.

## Fonctionnalités

- Collecte et prétraitement de données de marché en temps réel
- Analyse technique avec plus de 100 indicateurs
- Modèles d'apprentissage automatique pour la prédiction des prix
- Backtesting et optimisation de stratégies
- Interface web interactive pour le suivi des performances
- Notifications en temps réel via Telegram
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
│   ├── raw/
│   └── processed/
├── docs/              # Documentation
├── models/            # Modèles entraînés
├── notebooks/         # Notebooks Jupyter
├── scripts/           # Scripts utilitaires
├── src/              # Code source
│   └── sadie/
├── tests/            # Tests
│   ├── unit/
│   ├── integration/
│   └── performance/
└── requirements.txt   # Dépendances
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

La documentation complète est disponible sur [GitHub Pages](https://papierfroisse.github.io/SADIE/).

Pour générer la documentation localement :
```bash
mkdocs serve
```

## Contribution

Les contributions sont les bienvenues ! Consultez [CONTRIBUTING.md](CONTRIBUTING.md) pour les directives.

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Contact

- GitHub : [@papierfroisse](https://github.com/papierfroisse)
- Email : papierfroisse@example.com 