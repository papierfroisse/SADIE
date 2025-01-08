# Carnet d'Ordres Avancé

## Vue d'ensemble

Le module de carnet d'ordres avancé fournit une implémentation robuste et performante pour la collecte et l'analyse des données de carnet d'ordres en temps réel. Il supporte les carnets d'ordres de niveau 2 (L2) et niveau 3 (L3), avec des fonctionnalités avancées pour le calcul de métriques et l'analyse en temps réel.

## Fonctionnalités Principales

### Collecte de Données
- Support complet des carnets d'ordres L2/L3
- Connexion WebSocket pour les mises à jour en temps réel
- Gestion efficace des reconnexions et des erreurs
- Support multi-symboles

### Métriques en Temps Réel
- Spread bid-ask
- Profondeur du marché
- Déséquilibre du carnet d'ordres
- Callbacks personnalisables pour les métriques

### Performance
- Utilisation de `SortedDict` pour une gestion efficace des prix
- Mise à jour incrémentale des données
- Cache optimisé pour les accès fréquents
- Gestion de la mémoire avec limite de profondeur configurable

## Installation

```bash
pip install sadie
```

## Utilisation

### Initialisation Simple

```python
from sadie.data.collectors.orderbook import OrderBookCollector

collector = OrderBookCollector(
    symbols=["BTCUSDT"],
    depth=1000,
    update_interval=0.1
)

await collector.start()
```

### Accès aux Données

```python
# Obtenir un snapshot du carnet d'ordres
bids, asks = await collector.get_order_book("BTCUSDT")

# Obtenir les métriques actuelles
metrics = await collector.get_metrics(
    "BTCUSDT",
    price_range=Decimal("100"),
    levels=10
)
```

### Utilisation des Callbacks

```python
def on_metrics_update(symbol: str, metrics: Dict[str, Decimal]):
    print(f"Nouvelles métriques pour {symbol}:")
    print(f"Spread: {metrics['spread']}")
    print(f"Déséquilibre: {metrics['imbalance']}")

collector = OrderBookCollector(
    symbols=["BTCUSDT"],
    metrics_callback=on_metrics_update
)
```

## Architecture

### Classes Principales

#### OrderBookCollector
La classe principale qui gère la collecte et la distribution des données.

```python
class OrderBookCollector(BaseCollector):
    def __init__(
        self,
        symbols: List[str],
        depth: int = 1000,
        update_interval: float = 0.1,
        rate_limit: int = 20,
        metrics_callback: Optional[Callable] = None
    ):
        ...
```

#### OrderBook
Représentation interne du carnet d'ordres avec gestion efficace des mises à jour.

```python
class OrderBook:
    def __init__(self, depth: int = 1000):
        self.bids = SortedDict()
        self.asks = SortedDict()
        ...
```

#### OrderBookMetrics
Classe utilitaire pour le calcul des métriques du carnet d'ordres.

```python
class OrderBookMetrics:
    @staticmethod
    def compute_spread(bids, asks) -> Decimal:
        ...
    
    @staticmethod
    def compute_depth(bids, asks, price_range) -> Tuple[Decimal, Decimal]:
        ...
```

## Métriques Disponibles

### Spread
Le spread bid-ask représente la différence entre le meilleur prix d'achat et le meilleur prix de vente.

```python
spread = metrics["spread"]  # Decimal
```

### Profondeur
La profondeur du marché indique le volume disponible dans une plage de prix donnée.

```python
bid_depth = metrics["bid_depth"]  # Volume côté achat
ask_depth = metrics["ask_depth"]  # Volume côté vente
```

### Déséquilibre
Le déséquilibre du carnet d'ordres mesure la différence relative entre le volume d'achat et de vente.

```python
imbalance = metrics["imbalance"]  # Entre -1 et 1
```

## Gestion des Erreurs

Le collecteur inclut une gestion robuste des erreurs avec :
- Reconnexion automatique en cas de perte de connexion WebSocket
- Validation des données entrantes
- Gestion des timeouts et des erreurs réseau
- Logging détaillé des erreurs et des événements

```python
try:
    await collector.start()
except CollectorError as e:
    logger.error(f"Erreur du collecteur: {e}")
```

## Performance et Optimisation

### Gestion de la Mémoire
- Limite de profondeur configurable
- Nettoyage automatique des niveaux de prix obsolètes
- Utilisation efficace des structures de données

### Optimisation des Mises à Jour
- Mises à jour incrémentales
- Validation des séquences de mise à jour
- Cache des snapshots fréquemment accédés

## Tests

Le module inclut une suite de tests complète :

```bash
pytest tests/unit/test_orderbook.py -v
```

Les tests couvrent :
- Initialisation et configuration
- Gestion des mises à jour
- Calcul des métriques
- Gestion des erreurs
- Performance et charge

## Exemples Avancés

### Analyse en Temps Réel

```python
async def analyze_market_depth(collector: OrderBookCollector):
    while True:
        metrics = await collector.get_metrics("BTCUSDT")
        if metrics["imbalance"] > 0.5:
            print("Fort déséquilibre acheteur détecté")
        await asyncio.sleep(1)
```

### Surveillance Multi-Symboles

```python
symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
collector = OrderBookCollector(symbols=symbols)

async def monitor_spreads():
    while True:
        for symbol in symbols:
            metrics = await collector.get_metrics(symbol)
            print(f"{symbol} spread: {metrics['spread']}")
        await asyncio.sleep(1)
```

## Limitations Connues

- Profondeur maximale de 5000 niveaux de prix
- Latence minimale de 100ms pour les mises à jour WebSocket
- Utilisation mémoire proportionnelle au nombre de symboles suivis

## Prochaines Évolutions

- Support pour d'autres exchanges
- Métriques additionnelles (volatilité, liquidité)
- Optimisation pour les systèmes à haute fréquence
- Interface graphique pour la visualisation 