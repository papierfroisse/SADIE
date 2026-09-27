# État technique — partie Python de SADIE

Relevé du 27/09/2026, après remise en état de l'environnement local.
Chiffres obtenus avec `pytest tests/unit`.

## Contexte

Le dépôt provient d'une autre machine (`C:\Users\radio\Document_Cursor\...`) :
l'environnement virtuel livré était **vide et pointait vers un interpréteur
inexistant**, et le projet n'était donc plus exécutable en local.

## Défauts corrigés

| # | Défaut | Symptôme | Correctif |
|---|---|---|---|
| 1 | Environnement virtuel mort (0 paquet, `python.exe` d'un autre utilisateur) | impossible de lancer le moindre script | `.venv` recréé (Python 3.14.6) + dépendances installées |
| 2 | Paquet nommé `SADIE/`, importé `sadie` par 173 références | `ModuleNotFoundError: No module named 'sadie'` — **le paquet entier était inimportable** | dossier renommé `sadie/`, 29 références en majuscules alignées |
| 3 | 4 fichiers sources en UTF-16 (BOM `FF FE`) | `SyntaxError: source code string cannot contain null bytes` | convertis en UTF-8 par `tools/normaliser_encodage.py` |
| 4 | `sadie/__init__.py` importe `sadie.web`, qui réclamait `global_metrics_manager` — absent de `metrics.py` | `ImportError` à l'import du paquet : **aucun module applicatif utilisable** | instance globale ajoutée dans `metrics.py` (le nom `PerformanceMetric` est réexposé en alias) |
| 5 | `bcrypt 5.0.0` avec `passlib 1.7.4` | `ValueError: password cannot be longer than 72 bytes` dans les tests d'authentification | `bcrypt==4.0.1` verrouillé dans `requirements/base.txt` |

## Ce qui fonctionne maintenant

```powershell
.venv\Scripts\python.exe tools\verifier_api.py     # application + API
.venv\Scripts\python.exe -m pytest tests/unit      # suite unitaire
```

- `import sadie` : OK (version 0.2.1) ;
- application FastAPI `sadie.web.app` : importable, titre « SADIE API », 17 routes montées ;
- `GET /api/healthcheck` : **HTTP 200** en mémoire (starlette TestClient) ;
- `sadie.core.collectors`, `sadie.analysis.indicators`, `sadie.storage` : importables ;
- suite unitaire : **31 tests passent** (11 avant l'intervention).

## Échecs restants : tests désynchronisés du code

La suite fait **19 échecs et 26 erreurs** : ils viennent de tests écrits contre
une arborescence qui a depuis été refactorée. Liste exacte :

| Test | Cause |
|---|---|
| `test_analysis.py` | `PatternType` n'existe plus dans `sadie.analysis.harmonic_patterns` (seule la classe `HarmonicAnalyzer` subsiste) |
| `test_backtester.py` | `sadie.analysis.backtesting` : déplacé vers `sadie/core/backtest/` |
| `test_statistics.py` | `sadie.analysis.statistics` : module absent |
| `test_collectors.py` | `sadie.data.collectors.rest` / `.websocket` : modules absents |
| `test_news_collector.py` | `sadie.data.sentiment` : module absent |
| `test_redis_cache.py` | `sadie.core.cache.redis` : module absent (`core/cache/` ne contient qu'un `__init__.py`) |
| `test_storage.py` | `BaseStorage` retiré de `sadie.storage` (seul `RedisStorage` est exporté) |
| `test_trade_collector.py` | classe renommée `BinanceTradeCollector` ; constructeur différent de celui attendu par le test |
| `test_kraken_collector.py` | `Exchange`, `Symbol`, `Timeframe` retirés de `sadie.core.models.events` |
| `test_timescale_storage.py` | `RedisStorage.__init__()` n'accepte plus les arguments utilisés par le test |
| `test_dashboards.py`, `test_metrics.py` | assertions sur la structure des métriques, différente de l'implémentation actuelle |

## Recommandation

Ne pas « réparer » ces tests à l'aveugle : chacun correspond à une décision de
conception (module supprimé, classe renommée). Deux pistes, au choix :

1. **Réécrire les tests** contre l'API actuelle, module par module, en
   commençant par `test_trade_collector.py` et `test_storage.py` (le code
   existe, seuls les noms et les signatures ont changé) ;
2. **Republier l'API attendue** dans le code applicatif (module `sadie.analysis.statistics`,
   `sadie.data.collectors.rest`, etc.) si ces fonctionnalités sont toujours
   prévues — auquel cas c'est du développement, pas de la maintenance.

En complément, plusieurs sous-dossiers n'ont pas de `__init__.py`
(`sadie/data/`, `sadie/data/collectors/`, `sadie/web/routes/`) : ils
fonctionnent comme paquets implicites, mais ne réexportent aucun nom — c'est la
cause des `ImportError: cannot import name ...` sur des paquets.

## Outils ajoutés

| Script | Rôle |
|---|---|
| `tools/verifier_api.py` | importe l'application et interroge les points d'entrée en mémoire |
| `tools/normaliser_encodage.py` | détecte et convertit les sources UTF-16 en UTF-8 (`--ecrire`) |
| `tools/verif_modules.py` | liste les modules disponibles dans l'environnement virtuel |

## Reproduction de l'environnement

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements\base.txt
.venv\Scripts\python.exe -m pip install -r requirements\tests.txt
.venv\Scripts\python.exe -m pytest tests/unit
```