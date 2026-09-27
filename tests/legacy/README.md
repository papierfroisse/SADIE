# Tests de l'architecture héritée

Ces tests ne sont **plus exécutés** par défaut (`pytest.ini` ignore ce dossier) :
ils visent une API qui n'existe plus dans `sadie/`. Ils sont conservés ici plutôt
que supprimés, parce qu'ils décrivent des comportements voulus — mais les
remettre en état demande une décision de conception, pas un simple renommage.

Contexte établi le 27/09/2026 : ni `sadie/` (code actuel) ni `old/SADIE_backup/`
(l'ancienne implémentation conservée) ne contiennent les noms attendus par ces
tests. Ils ont été écrits contre un état antérieur du dépôt qui n'y est plus.

## Pourquoi chaque fichier est ici

| Fichier | Ce qui n'existe plus |
|---|---|
| `test_analysis.py` | `PatternType` et `TrendType` dans `sadie.analysis.harmonic_patterns` (seule la classe `HarmonicAnalyzer` subsiste) |
| `test_backtester.py` | `sadie.analysis.backtesting` : le module a été remplacé par `sadie/core/backtest/` (`BacktestEngine`, `Strategy`, `Position`) — les noms et la structure diffèrent |
| `test_statistics.py` | `sadie.analysis.statistics` : module absent, aucune classe `StatisticalAnalyzer` |
| `test_collectors.py` | `sadie.data.collectors.rest` et `.websocket` : modules absents |
| `test_data_collectors.py` | `BaseCollector`, `RESTCollector`, `WebSocketCollector` ne sont pas réexportés par `sadie.data.collectors` |
| `test_news_collector.py` | `sadie.data.sentiment` : module absent |
| `test_redis_cache.py` | `sadie.core.cache.redis` : module absent (`core/cache/` ne contient qu'un `__init__.py` vide) |
| `test_storage.py` | `MemoryStorage` : inexistant ; `BaseStorage` n'était pas réexporté par `sadie.storage` (corrigé depuis) |
| `test_trade_collector.py` | `TradeCollector` : la classe s'appelle désormais `BinanceTradeCollector`, construite sur un seul `symbol` |
| `test_kraken_collector.py` | `Exchange` et `Symbol` dans `sadie.core.models.events` (seul `Trade` subsiste) |
| `test_binance_collector.py` | `BinanceTradeCollector(name=…, symbols=[…])` et l'injection d'un stockage : le constructeur prend `symbol` et ne reçoit plus de stockage |
| `test_redis_storage.py` | `RedisStorage(name=…, max_trades=…)`, l'attribut privé `_redis` (devenu `client`) et l'envoi d'objets `Trade` (l'API attend des dictionnaires) |
| `test_timescale_storage.py` | Même désynchronisation ; nécessite en plus un PostgreSQL/TimescaleDB actif |
| `test_dashboards.py` | `sadie.web.routes.dashboards` : le module de routes n'existe plus (`sadie/web/routes/` contient alerts, export, metrics, prometheus, technical) |

## Les dossiers d'intégration, de charge, de performance et de résistance

Ces 23 fichiers (`legacy/integration/`, `legacy/load/`, `legacy/performance/`,
`legacy/resilience/`, `legacy/stress/`, plus trois tests de collecteurs à la
racine de `tests/`) présentent tous la même désynchronisation : ils importent des
modules et des classes de collecteurs qui n'existent plus.

| Attendu par les tests | État dans `sadie/` |
|---|---|
| `sadie.data.collectors.trades`, `.binance`, `.orderbook`, `.sentiment`, `.rest`, `.websocket` | modules absents (`sadie/data/collectors/` ne contient `base.py` vide de contenu) |
| `OrderBookCollector`, `WebSocketCollector`, `RESTCollector`, `BaseCollector` réexportés par `sadie.data.collectors` | non réexportés (pas de `__init__.py`) |
| `TradeCollector` | renommé `BinanceTradeCollector`, construite sur un seul `symbol` |
| `AlertManager` dans `sadie.core.monitoring.alerts` | renommé `PerformanceAlertManager` |
| `sadie.storage.database`, `src.sadie` | modules absents |
| `RedisStorage(socket_timeout=…, ` puis `flush_db()`) | ni le paramètre ni la méthode n'existent |
| `sadie.analysis.statistics`, `.backtesting` | remplacés par `sadie/core/backtest/` |

Deux dépendances externes s'y ajoutent : ces tests réclament un **Redis** (port
6379) et un **PostgreSQL/TimescaleDB** (5432) actifs, et plusieurs durent
plusieurs minutes par construction (dossiers `load`, `stress`, `performance`).

## Ce qui a été corrigé côté code (et non contourné)

Trois défauts réels ont été trouvés grâce à ces tests et corrigés dans `sadie/` :

1. `sadie/core/monitoring/metrics.py` — `UnboundLocalError` sur `throughput` et
   `avg_latency` : ces variables n'étaient définies que dans une branche
   conditionnelle, mais utilisées inconditionnellement dans le journal. Toute
   collecte s'arrêtait donc (`test_base_collector.py` passe désormais).
2. `sadie/storage/base.py` — `BaseStorage` n'avait pas d'`__init__` alors que
   `TimescaleStorage` appelle `super().__init__(name, logger)` :
   `TypeError: object.__init__() takes exactly one argument`. Le stockage
   TimescaleDB était **impossible à instancier**.
3. `sadie/storage/__init__.py` — `BaseStorage` et `TimescaleStorage` ne sont plus
   exportés par le paquet, ce qui obligeait à importer les sous-modules.

## Comment les relancer

```powershell
# ils échouent à la collecte tant que l'API attendue n'est pas rétablie
.venv\Scripts\python.exe -m pytest tests/legacy
```

Deux pistes, au choix, pour chacun :

1. **réécrire le test** contre l'API actuelle (à faire pour les cas proches :
   `test_binance_collector.py`, `test_redis_storage.py`, `test_timescale_storage.py`
   — les classes existent, seuls les noms et les signatures ont changé) ;
2. **rétablir la fonctionnalité** dans `sadie/` (comptabilité statistique,
   collecteur REST/WebSocket, cache Redis, collecteur d'actualités, routes de
   tableaux de bord) si elle reste au programme : c'est alors du développement.

Les tests de stockage exigent en outre un Redis (6379) et un PostgreSQL/TimeScaleDB
(5432) joints ; aucun des deux n'était actif lors du relevé.