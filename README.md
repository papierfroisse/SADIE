# sadie

Système avancé de collecte et d'analyse de données de trading.

## Fonctionnalités

- Collecte en temps réel des trades sur plusieurs exchanges (Binance, Kraken, Coinbase)
- Stockage hybride des données :
  - Redis pour les données en temps réel
  - TimescaleDB pour l'historique
- Calcul de statistiques en temps réel (VWAP, volume, etc.)
- API REST et WebSocket pour l'accès aux données
- Interface web de visualisation

## Installation

### Prérequis

- Python 3.9+
- Redis 6.0+
- TimescaleDB 2.0+
- Docker (optionnel)

### Installation des dépendances

```bash
# Installation basique
pip install -e .

# Installation avec toutes les fonctionnalités
pip install -e .[analysis,database,test,dev,docs]
```

### Configuration de la base de données

1. Redis :
```bash
# Installation
sudo apt install redis-server

# Démarrage
sudo systemctl start redis
```

2. TimescaleDB :
```bash
# Installation via Docker
docker run -d \
    --name timescaledb \
    -p 5432:5432 \
    -e POSTGRES_PASSWORD=postgres \
    timescale/timescaledb:latest-pg14

# Création de la base de données
psql -h localhost -U postgres -c "CREATE DATABASE sadie;"
```

## Utilisation

### Collecte des données

```python
from sadie.data.collectors import BinanceTradeCollector
from sadie.storage import RedisStorage, TimescaleStorage

# Configuration du stockage
redis = RedisStorage(
    name="redis",
    host="localhost",
    port=6379
)

timescale = TimescaleStorage(
    name="timescale",
    dsn="postgresql://postgres:postgres@localhost:5432/sadie"
)

# Création du collecteur
collector = BinanceTradeCollector(
    name="binance",
    symbols=["BTC/USDT", "ETH/USDT"],
    storage=redis  # Stockage en temps réel
)

# Démarrage de la collecte
await collector.start()

# Récupération des données
trades = await redis.get_trades("BTC/USDT")
stats = await redis.get_statistics("BTC/USDT")

# Arrêt de la collecte
await collector.stop()
```

### API Web

```bash
# Démarrage du serveur
uvicorn sadie.web.app:app --reload
```

L'API est ensuite accessible sur http://localhost:8000

## Architecture

### Stockage des données

Le système utilise une architecture de stockage hybride :

1. Redis (temps réel) :
   - Stockage des derniers trades (limité en nombre)
   - Statistiques en temps réel
   - Faible latence pour les requêtes fréquentes

2. TimescaleDB (historique) :
   - Stockage permanent de tous les trades
   - Agrégation temporelle des données
   - Requêtes analytiques complexes

### Collecteurs

Les collecteurs de données peuvent être configurés pour utiliser l'un ou l'autre des systèmes de stockage, ou les deux en même temps.

La classe `BaseCollector` fournit :
- Gestion du stockage
- Calcul des statistiques
- Gestion de la mémoire

Les implémentations spécifiques (`BinanceTradeCollector`, `KrakenTradeCollector`, `CoinbaseTradeCollector`) ajoutent :
- Connexion aux APIs
- Normalisation des données
- Gestion des reconnexions

## Tests

```bash
# Tests unitaires
pytest tests/unit

# Tests d'intégration
pytest tests/integration

# Tests de performance
pytest tests/performance

# Tous les tests avec couverture
pytest --cov=sadie
```

## Contribution

1. Fork du projet
2. Création d'une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit des changements (`git commit -am 'Ajout de la fonctionnalité'`)
4. Push de la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Création d'une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails. 