import { useState, useEffect, useCallback } from 'react';
import { WebSocketState } from '../types';

const RECONNECT_INTERVAL = 5000; // 5 secondes
const MAX_RETRIES = 5;

const useWebSocket = (symbol: string, timeframe: string = '1m') => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [state, setState] = useState<WebSocketState>({ marketData: {} });
  const [retryCount, setRetryCount] = useState(0);
  const [isConnected, setIsConnected] = useState(false);

  const connect = useCallback(() => {
    try {
      const wsUrl = `${process.env.REACT_APP_WS_URL}/market/${symbol}/${timeframe}`;
      console.log('Connecting to WebSocket:', wsUrl);
      const ws = new WebSocket(wsUrl);
      setSocket(ws);

      ws.onopen = () => {
        console.log('WebSocket Connected');
        setIsConnected(true);
        setRetryCount(0);
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('WebSocket message received:', data);
        
        if (data.type === 'market_data' && data.data) {
          const marketData = data.data;
          setState((prevState) => ({
            ...prevState,
            marketData: {
              ...prevState.marketData,
              [marketData.symbol]: marketData
            }
          }));
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };

      ws.onclose = () => {
        console.log('WebSocket Disconnected');
        setIsConnected(false);
        
        if (retryCount < MAX_RETRIES) {
          setTimeout(() => {
            setRetryCount(prev => prev + 1);
            connect();
          }, RECONNECT_INTERVAL);
        }
      };

      return ws;
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      return null;
    }
  }, [symbol, timeframe, retryCount]);

  useEffect(() => {
    const ws = connect();

    return () => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [connect]);

  return { state, isConnected, socket };
};

export default useWebSocket; 