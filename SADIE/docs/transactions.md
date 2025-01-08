# Flux de Transactions en Temps Réel

## Vue d'ensemble

Le module de flux de transactions fournit une implémentation robuste pour la collecte et l'analyse des transactions en temps réel sur les marchés financiers. Il permet de suivre les transactions individuelles, de calculer des métriques agrégées et d'analyser les tendances du marché.

## Fonctionnalités Principales

### Collecte de Données
- Connexion WebSocket pour les transactions en temps réel
- Support multi-symboles
- Gestion efficace des reconnexions
- Cache circulaire optimisé

### Métriques en Temps Réel
- Prix moyen pondéré par volume (VWAP)
- Ratio achat/vente
- Statistiques de trading (taille moyenne, volume total)
- Callbacks personnalisables pour les métriques

### Performance
- Utilisation de `deque` pour une gestion efficace de la mémoire
- Traitement asynchrone des données
- Cache optimisé pour les accès fréquents
- Gestion configurable de la fenêtre de données

## Installation

```bash
pip install sadie
```

## Utilisation

### Initialisation Simple

```python
from sadie.data.collectors.transactions import TransactionCollector

collector = TransactionCollector(
    symbols=["BTCUSDT"],
    window_size=1000,
    update_interval=0.1
)

await collector.start()
```

### Accès aux Données

```python
# Obtenir les transactions récentes
transactions = await collector.get_transactions("BTCUSDT", limit=100)

# Obtenir les métriques actuelles
metrics = await collector.get_metrics("BTCUSDT", window=500)
```

### Utilisation des Callbacks

```python
def on_metrics_update(symbol: str, metrics: Dict[str, Any]):
    print(f"Nouvelles métriques pour {symbol}:")
    print(f"VWAP: {metrics['vwap']}")
    print(f"Ratio achat/vente: {metrics['buy_sell_ratio']}")
    print(f"Volume total: {metrics['total_volume']}")

collector = TransactionCollector(
    symbols=["BTCUSDT"],
    metrics_callback=on_metrics_update
)
```

## Architecture

### Classes Principales

#### Transaction
Représentation d'une transaction individuelle.

```python
class Transaction:
    def __init__(
        self,
        price: Decimal,
        quantity: Decimal,
        timestamp: datetime,
        is_buyer_maker: bool,
        trade_id: int
    ):
        ...
```

#### TransactionMetrics
Classe utilitaire pour le calcul des métriques de trading.

```python
class TransactionMetrics:
    @staticmethod
    def compute_vwap(transactions: List[Transaction]) -> Decimal:
        ...
    
    @staticmethod
    def compute_buy_sell_ratio(transactions: List[Transaction]) -> Decimal:
        ...
```

#### TransactionCollector
Collecteur principal pour les données de transactions.

```python
class TransactionCollector(BaseCollector):
    def __init__(
        self,
        symbols: List[str],
        window_size: int = 1000,
        update_interval: float = 0.1,
        rate_limit: int = 20,
        metrics_callback: Optional[Callable] = None
    ):
        ...
```

## Métriques Disponibles

### VWAP (Volume-Weighted Average Price)
Prix moyen pondéré par le volume des transactions.

```python
vwap = metrics["vwap"]  # Decimal
```

### Ratio Achat/Vente
Ratio entre le volume d'achat et le volume de vente.

```python
ratio = metrics["buy_sell_ratio"]  # > 1 : plus d'achats, < 1 : plus de ventes
```

### Statistiques de Trading
Métriques générales sur l'activité de trading.

```python
avg_size = metrics["avg_trade_size"]  # Taille moyenne des trades
volume = metrics["total_volume"]      # Volume total
count = metrics["trade_count"]        # Nombre de transactions
```

## Gestion des Erreurs

Le collecteur inclut une gestion robuste des erreurs avec :
- Reconnexion automatique en cas de perte de connexion
- Validation des données entrantes
- Gestion des timeouts
- Logging détaillé

```python
try:
    await collector.start()
except CollectorError as e:
    logger.error(f"Erreur du collecteur: {e}")
```

## Performance et Optimisation

### Gestion de la Mémoire
- Fenêtre glissante avec taille configurable
- Nettoyage automatique des anciennes données
- Structures de données optimisées

### Traitement des Données
- Traitement asynchrone
- Mise en cache intelligente
- Optimisation des calculs de métriques

## Tests

Le module inclut une suite de tests complète :

```bash
pytest tests/unit/test_transactions.py -v
```

Les tests couvrent :
- Initialisation et configuration
- Traitement des messages WebSocket
- Calcul des métriques
- Gestion des erreurs
- Performance

## Exemples Avancés

### Analyse de Tendance

```python
async def analyze_market_trend(collector: TransactionCollector):
    while True:
        metrics = await collector.get_metrics("BTCUSDT")
        ratio = metrics["buy_sell_ratio"]
        
        if ratio > 1.5:
            print("Forte pression acheteuse détectée")
        elif ratio < 0.67:
            print("Forte pression vendeuse détectée")
            
        await asyncio.sleep(1)
```

### Surveillance Multi-Marchés

```python
symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
collector = TransactionCollector(symbols=symbols)

async def monitor_volumes():
    while True:
        for symbol in symbols:
            metrics = await collector.get_metrics(symbol)
            print(f"{symbol} volume: {metrics['total_volume']}")
        await asyncio.sleep(1)
```

## Limitations Connues

- Latence minimale de 100ms pour les mises à jour WebSocket
- Utilisation mémoire proportionnelle à window_size * nombre de symboles
- Pas de persistance des données historiques

## Prochaines Évolutions

- Support pour d'autres exchanges
- Métriques additionnelles (volatilité, liquidité)
- Persistance des données
- Interface graphique pour la visualisation
- Analyse technique en temps réel 