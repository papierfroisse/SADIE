# Core SADIE

Ce dossier contient les composants principaux de SADIE.

## Structure

```
core/
├── collectors/     # Collecteurs de données temps réel
│   └── trade_collector.py  # Collecteur de trades (4800+ trades/sec)
├── models/         # Modèles de données et événements
│   └── events.py   # Classes Event, Trade, etc.
├── cache/          # Système de cache distribué
│   └── redis_cache.py  # Implémentation Redis
└── metrics.py      # Métriques Prometheus
```

## Composants

### Collectors
- Collecte haute performance de trades
- Gestion des reconnexions
- Buffer circulaire pour la gestion de charge
- Validation des données

### Models
- Modèles de données standardisés
- Validation et normalisation
- Support de sérialisation

### Cache
- Cache distribué avec Redis
- Gestion de la mémoire
- Statistiques de performance

### Metrics
- Métriques Prometheus
- Monitoring des performances
- Alertes configurables

## Performance

- **Collecte** : 4800+ trades/seconde
- **Latence** : P95 < 100ms
- **Mémoire** : ~500MB pour 10 symbols

## Utilisation

```python
from SADIE.core.collectors import TradeCollector
from SADIE.core.models import Symbol, Exchange

collector = TradeCollector(
    symbols=[Symbol.BTC_USDT],
    exchange=Exchange.BINANCE
)

await collector.start()
``` 