# SADIE Core Package

## Structure

Le package SADIE est organisé en plusieurs modules principaux :

### 📊 data/
Gestion des données et connecteurs API
- `market.py` : Gestionnaire de données de marché
- `connectors/` : Connecteurs pour différentes sources (Binance, Alpha Vantage, etc.)
- `storage/` : Gestion du stockage (TimescaleDB, cache)

### 🧠 models/
Modèles prédictifs et d'optimisation
- `lstm.py` : Modèles LSTM spécialisés
- `attention.py` : Mécanismes d'attention
- `gan.py` : Modèles génératifs
- `portfolio.py` : Optimisation de portefeuille

### 📈 analysis/
Indicateurs et analyses
- `technical.py` : Indicateurs techniques
- `sentiment.py` : Analyse de sentiment
- `risk.py` : Mesures de risque

## Utilisation

```python
from sadie import SADIE

# Initialisation
sadie = SADIE(
    db_url="postgresql://user:pass@localhost:5432/sadie",
    cache_dir="/path/to/cache"
)

# Démarrage
await sadie.start()

# Utilisation
# ... code ...

# Arrêt
await sadie.stop()
```

## Configuration

Le système peut être configuré via :
- Variables d'environnement
- Fichier .env
- Arguments du constructeur

## Gestion des erreurs

Le package utilise des exceptions personnalisées :
- `SADIEConfigError` : Erreurs de configuration
- `SADIEInitError` : Erreurs d'initialisation
- `SADIEDataError` : Erreurs de données
- etc.

## Logging

Système de logging avancé :
```python
from sadie import setup_logging

setup_logging(
    log_level="DEBUG",
    log_file="sadie.log"
)
```

## Tests

Les tests unitaires sont dans le répertoire `tests/` :
```bash
pytest tests/
```

## Documentation

La documentation complète est disponible dans `docs/` :
```bash
cd docs/
make html
``` 