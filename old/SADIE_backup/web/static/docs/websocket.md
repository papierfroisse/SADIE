# Documentation WebSocket SADIE

## Vue d'ensemble

L'API WebSocket de SADIE permet une communication en temps réel entre le client et le serveur. Elle est utilisée pour :
- Recevoir les mises à jour du marché en temps réel
- Recevoir les notifications d'alertes déclenchées
- Maintenir une connexion active avec le serveur

## Points d'entrée WebSocket

### Données de marché
```
ws://localhost:8000/ws/{symbol}
```

Ce point d'entrée permet de recevoir les mises à jour en temps réel pour un symbole spécifique.

#### Messages reçus

##### Type "market_data"
```typescript
{
  type: "market_data",
  data: {
    symbol: string;
    timestamp: number;
    data: {
      open: number;
      high: number;
      low: number;
      close: number;
      volume: number;
      indicators?: {
        rsi?: number;
        macd?: number;
        ema_20?: number;
        ema_50?: number;
        ema_200?: number;
      };
    };
  }
}
```

##### Type "statistics"
```typescript
{
  type: "statistics",
  data: {
    symbol: string;
    timestamp: number;
    trades_24h: number;
    volume_24h: number;
    price_change_24h: number;
    price_change_percent_24h: number;
  }
}
```

### Alertes
```
ws://localhost:8000/ws/alert/{alertId}
```

Ce point d'entrée permet de recevoir les notifications en temps réel pour une alerte spécifique.

#### Messages reçus

##### Type "alert"
```typescript
{
  type: "alert",
  data: {
    id: string;
    symbol: string;
    type: "price" | "indicator";
    condition: "above" | "below";
    value: number;
    notification_type: "browser" | "email";
    created_at: number;
    triggered: boolean;
    triggered_at?: number;
  }
}
```

## Gestion de la connexion

### Établissement de la connexion

```typescript
const ws = new WebSocket(`ws://localhost:8000/ws/${symbol}`);

ws.onopen = () => {
  console.log('Connexion WebSocket établie');
};

ws.onclose = () => {
  console.log('Connexion WebSocket fermée');
};

ws.onerror = (error) => {
  console.error('Erreur WebSocket:', error);
};
```

### Réception des messages

```typescript
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch (message.type) {
    case 'market_data':
      // Traitement des données de marché
      handleMarketData(message.data);
      break;
      
    case 'statistics':
      // Traitement des statistiques
      handleStatistics(message.data);
      break;
      
    case 'alert':
      // Traitement des alertes
      handleAlert(message.data);
      break;
  }
};
```

## Reconnexion automatique

Le système gère automatiquement :
- Les tentatives de reconnexion en cas de perte de connexion
- Un nombre maximum de tentatives configurable
- L'intervalle entre les tentatives

### Exemple d'implémentation

```typescript
class WebSocketClient {
  private ws: WebSocket | null = null;
  private retries = 0;
  private maxRetries = 5;
  private retryInterval = 5000;

  constructor(private url: string) {}

  connect() {
    this.ws = new WebSocket(this.url);
    
    this.ws.onopen = () => {
      console.log('Connexion établie');
      this.retries = 0;
    };
    
    this.ws.onclose = () => {
      console.log('Connexion fermée');
      this.reconnect();
    };
    
    this.ws.onerror = (error) => {
      console.error('Erreur:', error);
    };
  }

  private reconnect() {
    if (this.retries >= this.maxRetries) {
      console.error('Nombre maximum de tentatives atteint');
      return;
    }
    
    this.retries++;
    console.log(`Tentative de reconnexion ${this.retries}/${this.maxRetries}`);
    
    setTimeout(() => {
      this.connect();
    }, this.retryInterval);
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
```

## Bonnes pratiques

1. **Gestion des erreurs**
   - Toujours implémenter un gestionnaire d'erreurs
   - Logger les erreurs pour le débogage
   - Informer l'utilisateur des problèmes de connexion

2. **Reconnexion**
   - Implémenter une stratégie de reconnexion automatique
   - Utiliser un délai exponentiel entre les tentatives
   - Limiter le nombre de tentatives

3. **Performance**
   - Ne pas maintenir plus de connexions que nécessaire
   - Fermer les connexions inutilisées
   - Gérer correctement la mémoire en nettoyant les listeners

4. **Sécurité**
   - Valider les données reçues avant traitement
   - Ne pas exposer d'informations sensibles
   - Utiliser HTTPS/WSS en production

## Exemples d'utilisation

### React Hook

```typescript
import { useState, useEffect, useCallback } from 'react';
import { MarketData, WebSocketMessage } from '../types';

export const useWebSocket = (symbol: string) => {
  const [data, setData] = useState<MarketData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  const connect = useCallback(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${symbol}`);

    ws.onopen = () => {
      setIsConnected(true);
      setError(null);
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        if (message.type === 'market_data') {
          setData(message.data);
        }
      } catch (err) {
        console.error('Error processing message:', err);
      }
    };

    ws.onerror = (error) => {
      setError('WebSocket error');
      setIsConnected(false);
    };

    ws.onclose = () => {
      setIsConnected(false);
    };

    return ws;
  }, [symbol]);

  useEffect(() => {
    const ws = connect();
    return () => {
      ws.close();
    };
  }, [connect]);

  return { data, error, isConnected };
};
```

### Utilisation dans un composant

```typescript
const MarketDataComponent = ({ symbol }: { symbol: string }) => {
  const { data, error, isConnected } = useWebSocket(symbol);

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!isConnected) {
    return <div>Connecting...</div>;
  }

  return (
    <div>
      <h2>{symbol} Market Data</h2>
      {data && (
        <div>
          <p>Price: {data.data.close}</p>
          <p>Volume: {data.data.volume}</p>
          {data.data.indicators && (
            <div>
              <p>RSI: {data.data.indicators.rsi}</p>
              <p>MACD: {data.data.indicators.macd}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
```

## Notifications

### Vue d'ensemble
Le système de notifications permet d'alerter l'utilisateur même lorsque l'application n'est pas au premier plan.

### Types de notifications
1. Notifications du navigateur
   - Nécessite une permission de l'utilisateur
   - Fonctionne même lorsque l'application est en arrière-plan
   - Configuration via le composant AlertList

2. Notifications in-app
   - Snackbar pour les messages système
   - Indicateurs visuels dans l'interface

### Utilisation des notifications du navigateur

```typescript
// Vérification et demande de permission
const checkNotificationPermission = async () => {
  if ('Notification' in window) {
    const permission = await Notification.requestPermission();
    return permission === 'granted';
  }
  return false;
};

// Envoi d'une notification
const sendNotification = (title: string, body: string) => {
  if (Notification.permission === 'granted') {
    new Notification(title, { body });
  }
};
```

### Bonnes pratiques
1. Toujours vérifier la permission avant d'envoyer une notification
2. Fournir une alternative lorsque les notifications ne sont pas disponibles
3. Permettre à l'utilisateur de configurer ses préférences de notification
4. Limiter le nombre de notifications pour éviter la fatigue de l'utilisateur

## Tests

### Tests WebSocket
Les tests couvrent :
- La connexion/déconnexion
- La réception des messages
- La gestion des erreurs
- La reconnexion automatique
- Le maintien de l'état

### Tests Notifications
Les tests vérifient :
- La demande de permission
- L'affichage des notifications
- La gestion des permissions refusées
- Le toggle des notifications

## Dépannage

### Problèmes courants WebSocket
1. Échec de connexion
   - Vérifier que le serveur est accessible
   - Vérifier le format de l'URL WebSocket

2. Perte de connexion fréquente
   - Vérifier la qualité du réseau
   - Augmenter l'intervalle de reconnexion

### Problèmes courants Notifications
1. Notifications non reçues
   - Vérifier les permissions du navigateur
   - Vérifier que les notifications sont activées dans l'OS

2. Notifications en double
   - Vérifier la logique de dédoublonnage
   - Vérifier la gestion d'état des alertes 