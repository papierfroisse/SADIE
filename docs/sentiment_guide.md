# Guide d'Utilisation : Analyse de Sentiment

Ce guide détaille l'utilisation du module d'analyse de sentiment de SADIE pour collecter et analyser les sentiments du marché à partir de multiples sources.

## Configuration Initiale

### 1. Installation des Dépendances
```bash
pip install -r requirements.txt
```

### 2. Configuration des APIs
Créez un fichier `.env` à la racine du projet avec vos clés API :

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

## Utilisation de Base

### 1. Initialisation du Collecteur
```python
from SADIE.data.sentiment import SentimentCollector, SentimentSource
from datetime import timedelta

# Configuration des clés API
api_keys = {
    "twitter_api_key": "votre_clé",
    "twitter_api_secret": "votre_secret",
    "twitter_bearer_token": "votre_token",
    "reddit_client_id": "votre_client_id",
    "reddit_client_secret": "votre_client_secret",
    "newsapi_key": "votre_clé"
}

# Création du collecteur
collector = SentimentCollector(
    name="crypto_sentiment",
    symbols=["BTC", "ETH"],
    sources=[
        SentimentSource.TWITTER,
        SentimentSource.REDDIT,
        SentimentSource.NEWS
    ],
    api_keys=api_keys,
    history_window=timedelta(hours=24),
    relevance_threshold=0.5,
    anomaly_threshold=2.0
)
```

### 2. Collecte Simple
```python
async def collect_sentiment():
    async with collector:
        sentiment_data = await collector.collect()
        print(sentiment_data)

# Exécution
import asyncio
asyncio.run(collect_sentiment())
```

### 3. Collecte Continue
```python
async def monitor_sentiment():
    async with collector:
        while True:
            sentiment_data = await collector.collect()
            process_sentiment(sentiment_data)
            await asyncio.sleep(60)  # Attendre 1 minute

def process_sentiment(data):
    for symbol, scores in data.items():
        print(f"Symbol: {symbol}")
        print(f"Score composite: {scores.composite_score}")
        print(f"Sources: {scores.source_scores}")
        if scores.is_anomaly:
            print("⚠️ Anomalie détectée!")
```

## Fonctionnalités Avancées

### 1. Filtrage par Pertinence
```python
collector = SentimentCollector(
    # ... autres paramètres ...
    relevance_threshold=0.7,  # Plus sélectif
    min_engagement=100,       # Engagement minimum
    trusted_sources=["Reuters", "Bloomberg"]
)
```

### 2. Détection d'Anomalies
```python
collector = SentimentCollector(
    # ... autres paramètres ...
    anomaly_threshold=1.5,     # Plus sensible
    anomaly_window=timedelta(hours=6)
)

async def monitor_anomalies():
    async with collector:
        while True:
            data = await collector.collect()
            for symbol, scores in data.items():
                if scores.is_anomaly:
                    alert_anomaly(symbol, scores)
            await asyncio.sleep(60)

def alert_anomaly(symbol, scores):
    print(f"⚠️ Anomalie détectée pour {symbol}")
    print(f"Score: {scores.composite_score}")
    print(f"Écart-type: {scores.std_dev}")
```

### 3. Gestion de la Mémoire
```python
collector = SentimentCollector(
    # ... autres paramètres ...
    history_window=timedelta(hours=12),  # Fenêtre plus courte
    cleanup_interval=300                 # Nettoyage toutes les 5 minutes
)
```

### 4. Pondération Personnalisée
```python
collector = SentimentCollector(
    # ... autres paramètres ...
    source_weights={
        SentimentSource.TWITTER: 0.3,
        SentimentSource.REDDIT: 0.3,
        SentimentSource.NEWS: 0.4
    }
)
```

## Exemples Pratiques

### 1. Surveillance Multi-Symboles
```python
async def monitor_portfolio():
    collector = SentimentCollector(
        name="portfolio_sentiment",
        symbols=["BTC", "ETH", "XRP", "ADA"],
        sources=[SentimentSource.ALL],
        api_keys=api_keys,
        update_interval=300  # 5 minutes
    )
    
    async with collector:
        while True:
            data = await collector.collect()
            update_dashboard(data)
            await asyncio.sleep(300)
```

### 2. Alertes en Temps Réel
```python
async def alert_system():
    collector = SentimentCollector(
        name="alert_system",
        symbols=["BTC"],
        sources=[SentimentSource.ALL],
        api_keys=api_keys,
        anomaly_threshold=1.8,
        relevance_threshold=0.6
    )
    
    async with collector:
        while True:
            data = await collector.collect()
            scores = data["BTC"]
            
            if scores.is_anomaly:
                if scores.composite_score < -0.5:
                    send_alert("Sentiment négatif anormal détecté pour BTC")
                elif scores.composite_score > 0.5:
                    send_alert("Sentiment positif anormal détecté pour BTC")
            
            await asyncio.sleep(60)
```

### 3. Analyse Historique
```python
async def analyze_history():
    collector = SentimentCollector(
        name="history_analyzer",
        symbols=["ETH"],
        sources=[SentimentSource.ALL],
        api_keys=api_keys,
        history_window=timedelta(days=7)
    )
    
    async with collector:
        # Collecter une semaine de données
        for _ in range(7 * 24):  # 7 jours * 24 heures
            data = await collector.collect()
            store_historical_data(data)
            await asyncio.sleep(3600)  # 1 heure
        
        # Analyser les tendances
        trends = analyze_trends(collector.get_history())
        generate_report(trends)
```

## Bonnes Pratiques

### 1. Gestion des Ressources
- Utilisez toujours le context manager (`async with`)
- Nettoyez régulièrement l'historique
- Surveillez l'utilisation mémoire

### 2. Traitement des Erreurs
```python
async def robust_collection():
    try:
        async with collector:
            data = await collector.collect()
    except ConnectionError:
        logger.error("Erreur de connexion API")
        await asyncio.sleep(60)  # Attendre avant de réessayer
    except Exception as e:
        logger.exception("Erreur inattendue")
        raise
```

### 3. Performance
- Ajustez `update_interval` selon vos besoins
- Utilisez `history_window` approprié
- Optimisez les seuils de pertinence

### 4. Monitoring
```python
from SADIE.core.monitoring import get_logger

logger = get_logger(__name__)

async def monitored_collection():
    async with collector:
        start_time = time.time()
        data = await collector.collect()
        duration = time.time() - start_time
        
        logger.info(
            "Collecte terminée",
            extra={
                "duration": duration,
                "symbols": len(data),
                "memory_usage": collector.get_memory_usage()
            }
        )
```

## Dépannage

### Problèmes Courants

1. Erreurs d'API
```python
# Vérifier les clés API
assert all(key in api_keys for key in [
    "twitter_bearer_token",
    "reddit_client_id",
    "newsapi_key"
])
```

2. Utilisation Mémoire
```python
# Surveiller l'utilisation mémoire
print(collector.get_memory_usage())
# Nettoyer si nécessaire
collector.clean_old_data()
```

3. Qualité des Données
```python
# Vérifier les scores
if not scores.is_valid():
    logger.warning(
        "Scores potentiellement invalides",
        extra={"scores": scores.source_scores}
    )
``` 