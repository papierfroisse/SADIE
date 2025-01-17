# sadie

Système avancé de collecte et d'analyse de données de trading.

## Fonctionnalités

- Collecte de données en temps réel via WebSocket
- Support multi-exchanges (Binance, Kraken, Coinbase)
- Agrégation de données de marché
- Détection d'opportunités d'arbitrage
- Interface web avec visualisation
- Monitoring et métriques

## Installation

```bash
# Cloner le dépôt
git clone https://github.com/yourusername/sadie.git
cd sadie

# Installation en mode développement
pip install -e .
```

## Utilisation

### Collecte de trades

```python
from sadie.data.collectors import BinanceTradeCollector

# Création du collecteur
collector = BinanceTradeCollector(
    name="binance",
    symbols=["BTC-USD", "ETH-USD"]
)

# Démarrage de la collecte
await collector.start()

# Récupération des données
data = await collector.collect()

# Arrêt du collecteur
await collector.stop()
```

### Agrégation multi-exchanges

```python
from sadie.data.collectors import (
    BinanceTradeCollector,
    KrakenTradeCollector,
    CoinbaseTradeCollector
)

# Création des collecteurs
collectors = [
    BinanceTradeCollector(name="binance", symbols=symbols),
    KrakenTradeCollector(name="kraken", symbols=symbols),
    CoinbaseTradeCollector(name="coinbase", symbols=symbols)
]

# Démarrage des collecteurs
for collector in collectors:
    await collector.start()

# Collecte et agrégation des données
for collector in collectors:
    data = await collector.collect()
    # Traitement des données...

# Arrêt des collecteurs
for collector in collectors:
    await collector.stop()
```

## Exemples

Le dossier `examples/` contient plusieurs exemples d'utilisation :

- `trades_example.py` : Collecte simple de trades
- `market_aggregator.py` : Agrégation de données multi-exchanges
- `arbitrage_detector.py` : Détection d'opportunités d'arbitrage

## Documentation

La documentation complète est disponible sur [https://yourusername.github.io/sadie](https://yourusername.github.io/sadie).

## Tests

```bash
# Exécution des tests
pytest

# Avec couverture de code
pytest --cov=sadie
```

## Contribution

Les contributions sont les bienvenues ! Consultez [CONTRIBUTING.md](CONTRIBUTING.md) pour les détails.

## Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Changelog

Voir [CHANGELOG.md](CHANGELOG.md) pour l'historique des changements. 