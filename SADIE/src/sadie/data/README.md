# Module de Gestion des Données

## Vue d'ensemble

Ce module gère la collecte, le stockage et le prétraitement des données pour SADIE.

## Structure

### 📡 Connecteurs (`connectors/`)
- `binance.py` : API Binance (données de marché en temps réel)
- `alpha_vantage.py` : API Alpha Vantage (données historiques)
- `twitter.py` : API Twitter (analyse de sentiment)
- `reddit.py` : API Reddit (sentiment communautaire)
- `blockchain.py` : Données on-chain (ETH, BTC)

### 💾 Stockage (`storage/`)
- `timescale.py` : Gestion TimescaleDB
- `cache.py` : Système de cache multi-niveaux
- `compression.py` : Compression des données historiques

### 🔄 Prétraitement (`preprocessing/`)
- `normalizer.py` : Normalisation des données
- `cleaner.py` : Nettoyage et correction des anomalies
- `aggregator.py` : Agrégation multi-timeframes

## Utilisation

```python
from sadie.data import MarketManager

# Configuration du manager
manager = MarketManager(
    db_url="postgresql://localhost:5432/sadie",
    cache_dir="/path/to/cache",
    max_cache_age=3600
)

# Démarrage
await manager.start()

# Collecte de données
data = await manager.get_market_data(
    symbol="BTC/USDT",
    timeframe="1m",
    limit=1000
)

# Nettoyage des anciennes données
manager.clean_old_data(
    before="2024-01-01",
    source="binance"
)
```

## Configuration

### Base de données
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sadie
DB_USER=user
DB_PASS=password
```

### Cache
- L1 (Mémoire) : 1 heure
- L2 (Redis) : 24 heures
- L3 (Disque) : 7 jours

### TimescaleDB
- Compression après 7 jours
- Rétention : 5 ans
- Chunks adaptatifs selon volatilité

## Gestion des erreurs

```python
from sadie.exceptions import SADIEDataError

try:
    data = await manager.get_market_data(...)
except SADIEDataError as e:
    logger.error(f"Erreur de données: {e}")
```

## Tests

```bash
# Tests des connecteurs
pytest tests/data/test_connectors.py

# Tests du stockage
pytest tests/data/test_storage.py

# Tests de prétraitement
pytest tests/data/test_preprocessing.py
```

## Métriques de performance

- Latence maximale : 100ms
- Taux de compression : ~70%
- Hit ratio cache : >95%
- Débit : 1000 requêtes/s
``` 