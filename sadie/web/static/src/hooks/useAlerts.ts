import { useState, useEffect, useCallback } from 'react';
import { Alert } from '../types';
import ApiService from '../services/api';
import { useWebSocket } from '../context/WebSocketContext';

interface UseAlertsProps {
  symbol?: string;
}

interface UseAlertsReturn {
  alerts: Alert[];
  loading: boolean;
  error: string | null;
  lastTriggered: Alert | null;
  createAlert: (alert: Omit<Alert, 'id'>) => Promise<void>;
  deleteAlert: (id: string) => Promise<void>;
}

export const useAlerts = ({ symbol }: UseAlertsProps = {}): UseAlertsReturn => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastTriggered, setLastTriggered] = useState<Alert | null>(null);
  const [notificationsEnabled, setNotificationsEnabled] = useState(false);
  const api = new ApiService();

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const response = await api.getAlerts();
      if (response.success && response.data) {
        setAlerts(response.data);
      } else {
        setError(response.error || 'Erreur lors de la récupération des alertes');
      }
    } catch (err) {
      setError('Erreur de connexion au serveur');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const createAlert = async (alert: Omit<Alert, 'id'>) => {
    try {
      const response = await api.createAlert(alert);
      if (response.success && response.data) {
        const newAlert = response.data as Alert;
        setAlerts(prev => [...prev, newAlert]);
        setError(null);
      } else {
        throw new Error(response.error || 'Failed to create alert');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  };

  const deleteAlert = async (id: string) => {
    try {
      const response = await api.deleteAlert(id);
      if (response.success) {
        setAlerts(prev => prev.filter(alert => alert.id !== id));
        setError(null);
      } else {
        throw new Error(response.error || 'Failed to delete alert');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  };

  const processWebSocketMessage = useCallback((message: WebSocketMessage) => {
    try {
      if (message.type === 'alert') {
        const alertData = message as Alert;
        setLastTriggered(alertData);
        setAlerts(prev => prev.map(a => (a.id === alertData.id ? alertData : a)));
      }
    } catch (err) {
      console.error('Error processing WebSocket message:', err);
      setError('Failed to process alert message');
    }
  }, []);

  useEffect(() => {
    fetchAlerts();
  }, [fetchAlerts]);

  useEffect(() => {
    if (!symbol) return;

    const connectAlertWebSocket = (alertId: string) => {
      const websocket = api.createWebSocket(`alert/${alertId}`);
      websocket.onmessage = (event: MessageEvent) => {
        const message = JSON.parse(event.data) as WebSocketMessage;
        processWebSocketMessage(message);
      };
      return websocket;
    };

    const activeAlerts = alerts.filter(alert => alert.triggered !== true);
    const websockets = activeAlerts.map(alert => connectAlertWebSocket(alert.id));

    return () => {
      websockets.forEach(ws => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.close();
        }
      });
    };
  }, [symbol, alerts, processWebSocketMessage]);

  return {
    alerts,
    loading,
    error,
    lastTriggered,
    createAlert,
    deleteAlert,
  };
};
