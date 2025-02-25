import React, { createContext, useContext, useEffect, useState } from 'react';

const WebSocketContext = createContext(null);

export function useWebSocket() {
  return useContext(WebSocketContext);
}

export function WebSocketProvider({ children }) {
  const [socket, setSocket] = useState(null);
  const [marketData, setMarketData] = useState({});

  const connect = symbol => {
    if (socket) {
      socket.close();
    }

    const ws = new WebSocket(`ws://localhost:8000/ws/${symbol}`);

    ws.onopen = () => {
      console.log('WebSocket Connected');
    };

    ws.onmessage = event => {
      const data = JSON.parse(event.data);
      setMarketData(prev => ({
        ...prev,
        [symbol]: data,
      }));
    };

    ws.onerror = error => {
      console.error('WebSocket Error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket Disconnected');
      // Tentative de reconnexion après 5 secondes
      setTimeout(() => connect(symbol), 5000);
    };

    setSocket(ws);
  };

  const disconnect = () => {
    if (socket) {
      socket.close();
      setSocket(null);
    }
  };

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, []);

  return (
    <WebSocketContext.Provider value={{ connect, disconnect, marketData }}>
      {children}
    </WebSocketContext.Provider>
  );
}
