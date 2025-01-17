# Modèles de Données SADIE

## Vue d'ensemble

Les modèles de données de SADIE sont conçus pour représenter et traiter efficacement les données de marché en temps réel. Ils sont définis dans le module `SADIE.core.models.events`.

## Enums

### Exchange

Définit les exchanges supportés par le système.

```python
class Exchange(str, Enum):
    BINANCE = "binance"
    BYBIT = "bybit"
    KUCOIN = "kucoin"
    BITGET = "bitget"
    OKEX = "okex"
```

### Symbol

Liste les paires de trading supportées.

```python
class Symbol(str, Enum):
    BTC_USDT = "BTC/USDT"
    ETH_USDT = "ETH/USDT"
    BNB_USDT = "BNB/USDT"
    # ...etc
```

### Timeframe

Définit les intervalles de temps supportés pour les données historiques.

```python
class Timeframe(str, Enum):
    M1 = "1m"    # 1 minute
    M3 = "3m"    # 3 minutes
    M5 = "5m"    # 5 minutes
    # ...etc
```

## Classes de Données

### MarketEvent

Classe de base pour tous les événements de marché.

**Attributs**:
- `exchange`: Exchange - L'exchange source de l'événement
- `symbol`: Symbol - La paire de trading
- `timestamp`: datetime - Horodatage de l'événement
- `price`: float - Prix de l'actif
- `volume`: float - Volume de la transaction
- `side`: str - Direction ("buy" ou "sell")
- `type`: str - Type d'événement (défaut: "market")
- `data`: Dict[str, Any] - Données additionnelles (optionnel)

### Trade

Représente une transaction exécutée. Hérite de MarketEvent.

**Attributs supplémentaires**:
- `trade_id`: str - Identifiant unique du trade (optionnel)
- `maker`: bool - True si le trade est maker (défaut: False)
- `liquidation`: bool - True si c'est une liquidation (défaut: False)

**Comportement**:
- Initialise automatiquement `type` à "trade"
- Convertit automatiquement `timestamp` en objet datetime si nécessaire

## Exemple d'utilisation

```python
from SADIE.core.models.events import Exchange, Symbol, Trade
from datetime import datetime

# Création d'un trade
trade = Trade(
    exchange=Exchange.BINANCE,
    symbol=Symbol.BTC_USDT,
    timestamp=datetime.now(),
    price=50000.0,
    volume=0.1,
    side="buy",
    trade_id="123456"
)
```

## Bonnes Pratiques

1. **Validation des Données**:
   - Utilisez toujours les enums pour `exchange` et `symbol`
   - Assurez-vous que `price` et `volume` sont positifs
   - Validez que `side` est soit "buy" soit "sell"

2. **Gestion des Timestamps**:
   - Préférez utiliser des objets `datetime` pour `timestamp`
   - Si vous passez un timestamp Unix, il sera automatiquement converti

3. **Données Additionnelles**:
   - Utilisez le champ `data` pour stocker des informations spécifiques à l'exchange
   - Documentez toujours la structure des données additionnelles

## Notes de Performance

- Les classes utilisent `@dataclass` pour une création efficace d'instances
- Les enums héritent de `str` pour une sérialisation facile
- Les champs optionnels utilisent `field()` pour éviter les problèmes de mutabilité 