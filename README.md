# SADIE - Système d'Analyse de Données et d'Intelligence Économique

## Description
SADIE est une plateforme avancée d'analyse de données financières qui combine des données de marché en temps réel avec des analyses de sentiment et des indicateurs techniques.

## Fonctionnalités Principales

### Données de Marché
- Collecte en temps réel des carnets d'ordres
- Suivi des transactions tick par tick
- Agrégation et normalisation des données

### Analyse de Sentiment
- Collecte multi-source (Twitter, Reddit, News)
- Détection d'anomalies en temps réel
- Pondération intelligente des sources
- Gestion optimisée de la mémoire
- Filtrage par pertinence

### Infrastructure
- Cache distribué haute performance
- Tests de charge et de résilience
- Monitoring et logging avancés

## Installation

```bash
# Cloner le repository
git clone https://github.com/votre-username/SADIE.git
cd SADIE

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

## Configuration

### Configuration des APIs
Créez un fichier `.env` à la racine du projet :
```env
# Twitter API
TWITTER_API_KEY=votre_clé
TWITTER_API_SECRET=votre_secret
TWITTER_BEARER_TOKEN=votre_token

# Reddit API
REDDIT_CLIENT_ID=votre_client_id
REDDIT_CLIENT_SECRET=votre_client_secret
REDDIT_USERNAME=votre_username

# NewsAPI
NEWSAPI_KEY=votre_clé
```

### Configuration du Cache
```python
from SADIE.core.cache import Cache, RedisBackend

cache = Cache(
    backend=RedisBackend(
        host="localhost",
        port=6379
    )
)
```

## Utilisation

### Collecte de Données de Marché
```python
from SADIE.data.collectors import OrderBookCollector

collector = OrderBookCollector(
    symbols=["BTC-USD", "ETH-USD"],
    update_interval=1.0
)

async with collector:
    data = await collector.collect()
```

### Analyse de Sentiment
```python
from SADIE.data.sentiment import SentimentCollector, SentimentSource

collector = SentimentCollector(
    name="crypto_sentiment",
    symbols=["BTC", "ETH"],
    sources=[
        SentimentSource.TWITTER,
        SentimentSource.REDDIT,
        SentimentSource.NEWS
    ],
    api_keys=api_keys
)

async with collector:
    sentiment_data = await collector.collect()
```

## Tests
```bash
# Exécuter tous les tests
pytest

# Tests spécifiques
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/
```

## Documentation
La documentation complète est disponible dans le dossier `docs/` et inclut :
- Guide d'utilisation détaillé
- Documentation technique
- Exemples d'intégration
- Guide de contribution

## Contribution
Les contributions sont les bienvenues ! Consultez `CONTRIBUTING.md` pour les directives.

## Licence
Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails. 