# Documentation SADIE

## Introduction
SADIE (Système d'Analyse de Données et d'Intelligence Économique) est une plateforme de collecte, stockage et analyse de données financières et économiques en temps réel.

## Architecture

### Collecteurs de Données
SADIE utilise deux types principaux de collecteurs :

1. **REST Collectors**
   - `AsyncRESTCollector` : Collecteur asynchrone pour les APIs REST
   - Gestion automatique des sessions et des timeouts
   - Système de retry intelligent
   - Support des requêtes batch

2. **WebSocket Collectors**
   - `AsyncWebSocketCollector` : Collecteur asynchrone pour les WebSockets
   - Reconnexion automatique avec backoff exponentiel
   - Gestion des souscriptions aux canaux
   - Support des handlers de messages personnalisés

### Stockage
Le système de stockage est conçu pour être :
- Performant avec TimescaleDB
- Flexible avec différents backends
- Optimisé pour les séries temporelles
- Cache multi-niveaux

### Analyse
Les composants d'analyse incluent :
- Analyse statistique
- Analyse de séries temporelles
- Détection d'anomalies
- Prédiction de tendances

## Installation

### Prérequis
- Python 3.9+
- PostgreSQL 13+
- TimescaleDB 2.0+

### Installation depuis PyPI
```bash
pip install sadie
```

### Installation depuis les sources
```bash
git clone https://github.com/radiofrance/sadie.git
cd sadie
pip install -e ".[dev]"
```

## Configuration

### Configuration de base
```python
from sadie.utils import setup_logging
from sadie.data import AsyncRESTCollector
from sadie.storage import MemoryStorage

# Configuration du logging
setup_logging()

# Configuration du stockage
storage = MemoryStorage()

# Configuration du collecteur
collector = AsyncRESTCollector(
    base_url="https://api.example.com",
    timeout=30,
    storage=storage
)
```

### Configuration WebSocket
```python
from sadie.data import AsyncWebSocketCollector

# Configuration du collecteur WebSocket
ws_collector = AsyncWebSocketCollector(
    url="wss://ws.example.com",
    ping_interval=20.0,
    storage=storage
)

# Ajout d'un handler de messages
async def handle_message(data):
    print(f"Message reçu: {data}")

ws_collector.add_message_handler("channel_name", handle_message)
```

## Utilisation

### Collecte de données REST
```python
async def collect_data():
    # Démarrage du collecteur
    await collector.start()
    
    try:
        # Collecte des données
        data = await collector.fetch("endpoint")
        print(f"Données collectées: {data}")
        
        # Collecte batch
        endpoints = ["endpoint1", "endpoint2"]
        batch_data = await collector.fetch_batch(endpoints)
        print(f"Données batch: {batch_data}")
    
    finally:
        # Arrêt du collecteur
        await collector.stop()
```

### Collecte de données WebSocket
```python
async def collect_ws_data():
    # Démarrage du collecteur
    await ws_collector.start()
    
    try:
        # Souscription aux canaux
        await ws_collector.subscribe("market_data")
        await ws_collector.subscribe("trades")
        
        # Attente des données
        await asyncio.sleep(60)  # Collecte pendant 1 minute
    
    finally:
        # Désinscription et arrêt
        await ws_collector.unsubscribe("market_data")
        await ws_collector.unsubscribe("trades")
        await ws_collector.stop()
```

## Tests

### Exécution des tests
```bash
# Tous les tests
pytest

# Tests spécifiques
pytest tests/unit
pytest tests/integration
pytest tests/performance
```

### Coverage
```bash
pytest --cov=sadie
```

## Contribution

### Setup développement
1. Fork le repository
2. Créer une branche
3. Installer les dépendances de développement
4. Implémenter les changements
5. Ajouter des tests
6. Créer une Pull Request

### Standards de code
- Black pour le formatage
- isort pour les imports
- mypy pour le typage
- flake8 pour le linting

## Support

### Ressources
- [Documentation complète](https://sadie.readthedocs.io/)
- [GitHub Issues](https://github.com/radiofrance/sadie/issues)
- [Exemples](https://github.com/radiofrance/sadie/tree/main/examples)

### Contact
- Email: opensource@radiofrance.com
- GitHub: [radiofrance/sadie](https://github.com/radiofrance/sadie)
