# SADIE - Système d'Analyse de Données et d'Intelligence Économique

SADIE est un système d'analyse de données et d'intelligence économique développé par Radio France. Il permet de collecter, stocker et analyser des données financières et économiques en temps réel.

## Fonctionnalités

- Collecte de données en temps réel via REST API et WebSocket
- Stockage efficace des données en mémoire ou sur disque
- Analyse statistique et temporelle des données
- Visualisation des résultats
- Configuration flexible via fichiers YAML
- Logging complet des opérations

## Installation

### Depuis PyPI

```bash
pip install sadie
```

### Depuis les sources

```bash
git clone https://github.com/radiofrance/sadie.git
cd sadie
pip install -e ".[dev]"  # Installation en mode développement
```

## Structure du projet

```
sadie/
├── .github/            # Configuration GitHub (CI/CD, etc.)
├── config/            # Fichiers de configuration
├── data/             # Données (ignorées par Git)
├── docs/             # Documentation
├── examples/         # Exemples d'utilisation
├── models/           # Modèles entraînés
├── notebooks/        # Notebooks Jupyter
├── requirements/     # Fichiers de dépendances
├── scripts/          # Scripts utilitaires
├── src/             # Code source
│   └── sadie/
│       ├── analysis/    # Analyse des données
│       ├── data/        # Collecte des données
│       ├── storage/     # Stockage des données
│       └── utils/       # Utilitaires
└── tests/           # Tests
    ├── integration/  # Tests d'intégration
    ├── performance/  # Tests de performance
    └── unit/        # Tests unitaires
```

## Utilisation

### Configuration

Créez un fichier de configuration `config.yml` :

```yaml
logging:
  level: INFO
  format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  file: 'logs/sadie.log'

collectors:
  rest:
    base_url: 'https://api.example.com'
    timeout: 30
    symbols: ['AAPL', 'GOOGL', 'MSFT']
  websocket:
    url: 'wss://stream.example.com'
    symbols: ['BTC-USD', 'ETH-USD']

storage:
  type: 'memory'
  max_size: 1000000

analysis:
  window_size: 60
  metrics: ['mean', 'std', 'min', 'max']
```

### Exemple de code

```python
from sadie.data import RESTCollector, WebSocketCollector
from sadie.storage import MemoryStorage
from sadie.analysis import TimeSeriesAnalyzer
from sadie.utils import setup_logging

# Configuration du logging
setup_logging()

# Initialisation du stockage
storage = MemoryStorage()

# Création des collecteurs
rest_collector = RESTCollector(storage=storage)
ws_collector = WebSocketCollector(storage=storage)

# Démarrage de la collecte
rest_collector.start()
ws_collector.start()

# Analyse des données
analyzer = TimeSeriesAnalyzer(storage=storage)
results = analyzer.analyze()

# Arrêt des collecteurs
rest_collector.stop()
ws_collector.stop()
```

## Développement

### Installation des dépendances de développement

```bash
pip install -e ".[dev]"
```

### Exécution des tests

```bash
pytest                 # Tous les tests
pytest tests/unit      # Tests unitaires uniquement
pytest tests/integration  # Tests d'intégration uniquement
pytest tests/performance  # Tests de performance uniquement
```

### Vérification du style de code

```bash
black .               # Formatage du code
isort .              # Tri des imports
mypy src tests       # Vérification des types
```

## Documentation

La documentation complète est disponible sur [Read the Docs](https://sadie.readthedocs.io/).

## Contribution

Les contributions sont les bienvenues ! Consultez le fichier [CONTRIBUTING.md](CONTRIBUTING.md) pour plus d'informations.

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Contact

Pour toute question ou suggestion, n'hésitez pas à :
- Ouvrir une issue sur GitHub
- Nous contacter à opensource@radiofrance.com 