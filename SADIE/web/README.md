# Web SADIE

Interface web et API de SADIE.

## Structure

```
web/
├── app.py           # Application FastAPI principale
├── stream_manager.py # Gestionnaire de flux WebSocket
├── middleware/      # Middlewares (métriques, auth)
└── static/         # Assets statiques (JS, CSS)
```

## Fonctionnalités

### API REST
- Endpoints pour données historiques
- Gestion de la configuration
- Métriques et monitoring
- Documentation OpenAPI

### WebSocket
- Flux temps réel des trades
- État des connexions
- Gestion des souscriptions
- Reconnexion automatique

### Interface Web
- Design responsive avec Tailwind
- Graphiques temps réel avec Plotly
- Filtres par exchange/symbol
- Dark mode

## Configuration

```python
# Configuration de l'application
app = FastAPI(
    title="SADIE API",
    description="API temps réel pour données financières",
    version="1.0.0"
)

# Ajout des middlewares
app.add_middleware(MetricsMiddleware)
app.add_middleware(CORSMiddleware)

# Configuration WebSocket
app.mount("/ws", WebSocketApp())
```

## Endpoints

### REST API
- `GET /api/v1/trades` - Historique des trades
- `GET /api/v1/stats` - Statistiques
- `GET /metrics` - Métriques Prometheus

### WebSocket
- `ws://host/ws/trades` - Flux de trades
- `ws://host/ws/status` - État du système

## Développement

```bash
# Lancer le serveur de développement
uvicorn SADIE.web.app:app --reload

# Construire les assets
npm run build

# Lancer les tests
pytest tests/web/
``` 