import { useState, useEffect, useCallback } from 'react';
import { MarketData, WebSocketMessage } from '../types';
import { api } from '../services/api';

interface UseMarketDataProps {
  symbol: string;
  interval?: string;
  limit?: number;
}

interface UseMarketDataReturn {
  data: MarketData[];
  loading: boolean;
  error: string | null;
  lastUpdate: MarketData | null;
}

export const useMarketData = ({
  symbol,
  interval = '1m',
  limit = 1000,
}: UseMarketDataProps): UseMarketDataReturn => {
  const [data, setData] = useState<MarketData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<MarketData | null>(null);

  // Chargement des données historiques
  const loadHistoricalData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await api.getHistoricalData(symbol, interval, limit);
      if (response.success && response.data) {
        setData(response.data);
        setError(null);
      } else {
        setError(response.error || 'Failed to load historical data');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, [symbol, interval, limit]);

  // Gestion des mises à jour WebSocket
  const handleWebSocketMessage = useCallback(
    (event: MessageEvent) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        if (message.type === 'market_data') {
          const marketData = message as MarketData;
          setLastUpdate(marketData);
          setData(prevData => {
            const newData = [...prevData];
            const lastIndex = newData.findIndex(d => d.timestamp === marketData.timestamp);
            if (lastIndex >= 0) {
              newData[lastIndex] = marketData;
            } else {
              newData.push(marketData);
              if (newData.length > limit) {
                newData.shift();
              }
            }
            return newData;
          });
        }
      } catch (err) {
        console.error('Error processing WebSocket message:', err);
      }
    },
    [limit]
  );

  // Configuration du WebSocket
  useEffect(() => {
    let reconnectTimeout: NodeJS.Timeout;
    const connectWebSocket = () => {
      const websocket = api.createWebSocket(symbol);

      websocket.onopen = () => {
        console.log(`WebSocket connected for ${symbol}`);
        setError(null);
      };

      websocket.onmessage = handleWebSocketMessage;

      websocket.onerror = error => {
        console.error('WebSocket error:', error);
        setError('WebSocket connection error - Attempting to reconnect...');
      };

      websocket.onclose = () => {
        console.log(`WebSocket disconnected for ${symbol} - Attempting to reconnect...`);
        reconnectTimeout = setTimeout(connectWebSocket, 5000);
      };
    };

    connectWebSocket();

    return () => {
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
    };
  }, [symbol, handleWebSocketMessage]);

  // Chargement initial des données
  useEffect(() => {
    loadHistoricalData();
  }, [loadHistoricalData]);

  return {
    data,
    loading,
    error,
    lastUpdate,
  };
};
