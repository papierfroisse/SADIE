# Documentation Technique SADIE

## Architecture Générale

SADIE est organisé en plusieurs modules principaux :

```
SADIE/
├── core/                 # Composants fondamentaux
│   ├── cache/           # Système de cache
│   ├── monitoring/      # Surveillance et métriques
│   └── utils/           # Utilitaires communs
├── data/                # Gestion des données
│   ├── collectors/      # Collecteurs de données
│   └── sentiment/       # Analyse de sentiment
└── api/                 # Interfaces externes
```

## Modules Principaux

### Collecte de Données

#### OrderBookCollector
- Collecte en temps réel des carnets d'ordres
- Gestion des connexions WebSocket
- Normalisation des données
- Métriques de performance

#### TradeCollector
- Suivi des transactions en temps réel
- Agrégation par intervalles
- Calcul de statistiques
- Gestion de la mémoire

### Analyse de Sentiment

#### Architecture
L'analyse de sentiment est structurée en plusieurs composants :

```
sentiment/
├── collector.py         # Collecteur principal
├── twitter.py          # Collecteur Twitter
├── reddit.py           # Collecteur Reddit
└── news.py            # Collecteur NewsAPI
```

#### SentimentCollector
Classe principale gérant l'analyse de sentiment multi-source.

##### Initialisation
```python
collector = SentimentCollector(
    name="collector_name",
    symbols=["BTC", "ETH"],
    sources=[SentimentSource.TWITTER, SentimentSource.REDDIT],
    history_window=timedelta(hours=24),
    relevance_threshold=0.5,
    anomaly_threshold=2.0
)
```

##### Paramètres
- `name`: Identifiant unique du collecteur
- `symbols`: Liste des symboles à surveiller
- `sources`: Sources de données à utiliser
- `history_window`: Fenêtre de conservation des données
- `relevance_threshold`: Seuil minimal de pertinence
- `anomaly_threshold`: Seuil de détection d'anomalies

##### Fonctionnalités
1. Gestion de la Mémoire
   - Utilisation de `collections.deque` pour limiter l'historique
   - Nettoyage automatique des anciennes données
   - Optimisation de l'utilisation mémoire

2. Filtrage par Pertinence
   - Calcul du score de pertinence basé sur :
     * Fraîcheur des données
     * Fiabilité de la source
     * Engagement des utilisateurs
   - Filtrage des données non pertinentes

3. Détection d'Anomalies
   - Calcul des statistiques sur la fenêtre glissante
   - Détection des écarts significatifs
   - Alertes en temps réel

4. Pondération des Sources
   - Coefficients dynamiques par source
   - Ajustement basé sur la performance historique
   - Normalisation des scores

#### Collecteurs Spécifiques

##### TwitterCollector
- Connexion via l'API Twitter v2
- Recherche par mots-clés et cashtags
- Analyse des tweets et retweets
- Métriques d'engagement

##### RedditCollector
- Surveillance des subreddits financiers
- Analyse des posts et commentaires
- Score basé sur les votes et awards
- Filtrage du spam

##### NewsCollector
- Intégration avec NewsAPI
- Analyse des titres et contenus
- Pondération par source d'information
- Déduplication des articles

### Infrastructure

#### Cache Distribué
- Backend Redis pour les données fréquemment accédées
- Gestion des TTL par type de données
- Sérialisation optimisée
- Mécanismes de fallback

#### Monitoring
- Métriques de performance
- Logs structurés
- Alertes configurables
- Tableaux de bord en temps réel

## Performance

### Métriques Clés
- Latence de collecte : < 100ms
- Débit : > 1000 messages/seconde
- Utilisation mémoire : < 1GB
- CPU : < 50% sur un cœur

### Optimisations
1. Utilisation de pools de connexions
2. Mise en cache agressive
3. Traitement asynchrone
4. Compression des données

## Sécurité

### Authentification
- Gestion sécurisée des clés API
- Rotation automatique des tokens
- Validation des requêtes

### Protection des Données
- Chiffrement des données sensibles
- Nettoyage périodique
- Audit des accès

## Tests

### Types de Tests
1. Tests Unitaires
   - Couverture > 80%
   - Mock des APIs externes
   - Validation des transformations

2. Tests d'Intégration
   - Flux de données complets
   - Scénarios réels
   - Validation end-to-end

3. Tests de Performance
   - Benchmarks automatisés
   - Tests de charge
   - Profiling mémoire

## Déploiement

### Prérequis
- Python 3.8+
- Redis 6+
- Clés API configurées

### Configuration
1. Variables d'environnement
2. Fichiers de configuration
3. Paramètres runtime

### Monitoring
- Métriques système
- Logs applicatifs
- Alertes 