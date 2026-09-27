import { useState, useEffect, useCallback } from 'react';
import { Alert } from '../types';
import ApiService from '../services/api';

interface UseAlertsReturn {
  alerts: Alert[];
  loading: boolean;
  error: string | null;
  createAlert: (alert: Omit<Alert, 'id'>) => Promise<void>;
  deleteAlert: (id: string) => Promise<void>;
}

export const useAlerts = (): UseAlertsReturn => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
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

  useEffect(() => {
    fetchAlerts();
  }, [fetchAlerts]);

  // Le suivi temps réel des alertes n'est pas implémenté : le backend n'expose
  // aucune route WebSocket d'alerte (`sadie/web/app.py` ne déclare que
  // `@app.websocket("/ws/market")`). Le hook ouvrait une connexion par alerte
  // sur `.../ws/market/alert/<id>`, une URL inexistante, et ne traitait le
  // contenu que si `message.type === 'alert'` — une valeur que `Alert.type` ne
  // peut jamais prendre : la branche ne pouvait pas s'exécuter. Ces appels ont
  // été retirés au lieu d'être laissés en place en donnant l'illusion d'un flux
  // actif. Les alertes viennent de l'API REST ; le canal devra être écrit côté
  // serveur avant d'être rebranché ici (voir FRONT-A-FAIRE.md).

  return {
    alerts,
    loading,
    error,
    createAlert,
    deleteAlert,
  };
};
