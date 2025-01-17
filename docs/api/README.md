# API Reference SADIE

## Vue d'ensemble

L'API SADIE expose les fonctionnalités suivantes :
- Collecte de données en temps réel via WebSocket
- Endpoints REST pour l'historique et les statistiques
- Gestion du cache et des configurations
- Monitoring et métriques

## Endpoints REST

### Données de Marché
- [Trades](trades.md) - Récupération des trades en temps réel et historiques
- [Statistics](statistics.md) - Statistiques de trading et performance
- [Health](health.md) - État du système et des connexions

### Administration
- [Configuration](configuration.md) - Gestion de la configuration
- [Cache](cache.md) - Gestion du cache Redis
- [Metrics](metrics.md) - Métriques Prometheus

## WebSocket API

### Flux de Données
- [Trade Stream](websocket/trades.md) - Flux temps réel des trades
- [Status Stream](websocket/status.md) - État des connexions et erreurs

### Exemples

```python
# Exemple de connexion WebSocket
import websockets
import json

async def subscribe_trades():
    uri = "ws://localhost:8000/ws/trades"
    async with websockets.connect(uri) as websocket:
        # Subscribe to BTC/USDT trades
        await websocket.send(json.dumps({
            "action": "subscribe",
            "symbol": "BTC/USDT"
        }))
        
        while True:
            trade = await websocket.recv()
            print(json.loads(trade))
```

## Authentification

L'API utilise des tokens JWT pour l'authentification. Voir [Authentication](authentication.md) pour plus de détails.

## Rate Limiting

- 100 requêtes/minute pour les endpoints REST
- Pas de limite pour les connexions WebSocket authentifiées

## Versions

- v1 (Current) - Base URL: `/api/v1`
- v0 (Deprecated) - Support jusqu'au 2024-12-31

## Support

Pour toute question sur l'API :
- Ouvrir une issue sur GitHub
- Consulter la [FAQ](faq.md)
- Contacter le support technique 