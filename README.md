# SADIE - Système Avancé de Distribution d'Information et d'Événements

## Description
SADIE est une plateforme avancée de distribution d'événements et d'informations en temps réel, conçue pour collecter, traiter et distribuer des données de manière efficace et fiable.

## Architecture
```
SADIE/
├── core/
│   ├── models/         # Modèles de données
│   ├── cache/          # Système de cache distribué
│   ├── streaming/      # Gestion des flux de données
│   └── monitoring/     # Surveillance et métriques
├── collectors/         # Collecteurs de données
├── api/               # API REST et WebSocket
└── utils/            # Utilitaires communs
```

## Fonctionnalités Principales
- Streaming de données en temps réel
- Cache distribué avec Redis
- Monitoring et logging avancés
- Tests automatisés
- Documentation complète

## Prérequis
- Python 3.8+
- PostgreSQL 14+
- Redis 6+

## Installation

### Base de données
1. Installer PostgreSQL :
   ```bash
   # Windows : Télécharger depuis postgresql.org
   # Linux :
   sudo apt install postgresql-14
   # macOS :
   brew install postgresql@14
   ```

2. Configurer la base de données :
   ```bash
   createdb sadie
   ```

### Redis
1. Installation :
   ```bash
   # Windows : Télécharger depuis redis.io
   # Linux :
   sudo apt install redis-server
   # macOS :
   brew install redis
   ```

### Application
1. Cloner le dépôt :
   ```bash
   git clone https://github.com/yourusername/SADIE.git
   cd SADIE
   ```

2. Créer un environnement virtuel :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   .\venv\Scripts\activate   # Windows
   ```

3. Installer les dépendances :
   ```bash
   pip install -e .
   ```

4. Configurer l'environnement :
   ```bash
   cp .env.example .env
   # Éditer .env avec vos paramètres
   ```

## Tests
```bash
pytest tests/
```

## Utilisation

### Streaming de Données
```python
from SADIE.core.streaming import StreamManager
from SADIE.core.streaming.handlers import LoggingHandler

async def main():
    manager = StreamManager()
    manager.subscribe("test_topic", LoggingHandler())
    
    async with manager:
        # Votre code ici
        pass
```

### Cache Distribué
```python
from SADIE.core.cache import Cache, RedisCache

async def main():
    cache = Cache(RedisCache(url="redis://localhost"))
    await cache.set("key", "value")
    value = await cache.get("key")
```

### Base de Données
```python
from SADIE.core.models.events import MarketEvent
from sqlalchemy.ext.asyncio import AsyncSession

async def save_event(session: AsyncSession, event: MarketEvent):
    session.add(event)
    await session.commit()
```

## Documentation
La documentation complète est disponible dans le dossier `docs/`.

## Contribution
Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour les détails.

## Licence
Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails. 