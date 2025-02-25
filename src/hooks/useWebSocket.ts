import { useState, useEffect, useCallback } from 'react';
import { MarketData, WebSocketMessage, CandleData } from '../types';

interface WebSocketState {
  marketData: { [key: string]: CandleData };
  connect: (symbol: string) => void;
  isConnected: boolean;
  error: string | null;
}

export const useWebSocket = (): WebSocketState => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [marketData, setMarketData] = useState<{ [key: string]: CandleData }>({});
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const connect = useCallback((symbol: string) => {
    if (socket) {
      socket.close();
    }

    const ws = new WebSocket(`ws://localhost:8000/ws/${symbol}`);

    ws.onopen = () => {
      setIsConnected(true);
      setError(null);
      console.log('WebSocket connection established');
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as WebSocketMessage;
        if (message.type === 'market_data') {
          const trade = message.data as MarketData;
          setMarketData(prev => {
            const current = prev[symbol] || {
              symbol: trade.symbol,
              timestamp: trade.timestamp,
              open: trade.price,
              high: trade.price,
              low: trade.price,
              close: trade.price,
              volume: trade.quantity,
              indicators: {}
            };

            return {
              ...prev,
              [symbol]: {
                ...current,
                timestamp: trade.timestamp,
                high: Math.max(current.high, trade.price),
                low: Math.min(current.low, trade.price),
                close: trade.price,
                volume: current.volume + trade.quantity
              }
            };
          });
        }
      } catch (err) {
        console.error('Error processing message:', err);
        setError('Error processing market data');
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('WebSocket connection error');
      setIsConnected(false);
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed');
      setIsConnected(false);
      setTimeout(() => connect(symbol), 5000); // Reconnexion après 5 secondes
    };

    setSocket(ws);
  }, [socket]);

  useEffect(() => {
    return () => {
      if (socket) {
        socket.close();
      }
    };
  }, [socket]);

  return { marketData, connect, isConnected, error };
}; 
