import React, { createContext, useContext, useEffect, useState, useCallback, useRef } from 'react';
import { MarketData, WebSocketMessage, Alert } from '../types';

interface WebSocketContextType {
  connect: (symbol: string, timeframe: string) => void;
  disconnect: () => void;
  marketData: { [key: string]: MarketData };
  isConnected: boolean;
  error: string | null;
  lastAlert: Alert | null;
  lastUpdate: MarketData | null;
}

const WebSocketContext = createContext<WebSocketContextType | null>(null);

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

interface WebSocketProviderProps {
  children: React.ReactNode;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

// Interface pour les messages WebSocket entrants
interface MarketDataMessage {
  type: 'market_data';
  symbol: string;
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  timeframe: string;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [marketData, setMarketData] = useState<{ [key: string]: MarketData }>({});
  const [lastAlert, setLastAlert] = useState<Alert | null>(null);
  const [lastUpdate, setLastUpdate] = useState<MarketData | null>(null);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;
  const reconnectInterval = 5000;
  const [error, setError] = useState<string | null>(null);
  const [currentSymbol, setCurrentSymbol] = useState<string>('');
  const [currentTimeframe, setCurrentTimeframe] = useState<string>('');

  const cleanup = useCallback(() => {
    if (ws) {
      ws.onopen = null;
      ws.onclose = null;
      ws.onmessage = null;
      ws.onerror = null;
      ws.close();
      setWs(null);
      setIsConnected(false);
      setError(null);
      setCurrentSymbol('');
      setCurrentTimeframe('');
    }
  }, [ws]);

  const connect = useCallback((symbol: string, timeframe: string) => {
    cleanup();
    setError(null);
    reconnectAttemptsRef.current = 0;

    try {
      console.log('Tentative de connexion WebSocket pour', symbol, timeframe);
      const newWs = new WebSocket(`ws://localhost:8000/ws/${symbol}?timeframe=${timeframe}`);
      setWs(newWs);

      newWs.onopen = () => {
        console.log('WebSocket Connecté');
        setIsConnected(true);
        setError(null);
        setCurrentSymbol(symbol);
        setCurrentTimeframe(timeframe);
        reconnectAttemptsRef.current = 0; // Réinitialiser le compteur après une connexion réussie
      };

      newWs.onmessage = event => {
        try {
          const message = JSON.parse(event.data) as MarketDataMessage | Alert;
          console.log('Message reçu:', message);

          if ('type' in message) {
            if (message.type === 'market_data' && message.symbol === symbol) {
              const newData: MarketData = {
                symbol: message.symbol,
                timestamp: message.timestamp,
                open: message.open,
                high: message.high,
                low: message.low,
                close: message.close,
                volume: message.volume,
                type: message.type,
                timeframe: message.timeframe
              };
              
              setMarketData(prev => ({
                ...prev,
                [symbol]: newData
              }));
              
              setLastUpdate(newData);
            } else if (message.type === 'price' || message.type === 'volume' || message.type === 'indicator') {
              // C'est une alerte
              setLastAlert(message as Alert);
            }
          }
        } catch (error) {
          console.error('Erreur lors du parsing du message WebSocket:', error);
          setError('Erreur lors du traitement des données');
        }
      };

      newWs.onerror = error => {
        console.error('Erreur WebSocket:', error);
        setIsConnected(false);
        setError('Erreur de connexion WebSocket');
      };

      newWs.onclose = event => {
        console.log('WebSocket Déconnecté, code:', event.code, 'raison:', event.reason);
        setIsConnected(false);

        // Gérer les différents codes de fermeture
        if (event.code === 1000) {
          // Fermeture normale
          setError(null);
        } else {
          setError(`Connexion perdue (${event.code})`);
          
          if (reconnectAttemptsRef.current < maxReconnectAttempts) {
            const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 10000);
            console.log(
              `Reconnexion dans ${delay}ms... Tentative ${reconnectAttemptsRef.current + 1} sur ${maxReconnectAttempts}`
            );
            reconnectAttemptsRef.current += 1;
            setTimeout(() => connect(symbol, timeframe), delay);
          } else {
            setError('Nombre maximum de tentatives de reconnexion atteint');
          }
        }
      };
    } catch (err) {
      console.error('Erreur lors de la création du WebSocket:', err);
      setError('Impossible de créer la connexion WebSocket');
    }
  }, [cleanup, maxReconnectAttempts]);

  const disconnect = useCallback(() => {
    cleanup();
  }, [cleanup]);

  useEffect(() => {
    return () => {
      cleanup();
    };
  }, [cleanup]);

  return (
    <WebSocketContext.Provider
      value={{
        connect,
        disconnect,
        isConnected,
        marketData,
        lastAlert,
        error,
        lastUpdate: lastUpdate,
      }}
    >
      {children}
    </WebSocketContext.Provider>
  );
};
