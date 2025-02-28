import axios, { AxiosInstance } from 'axios';
import { MarketData, Alert, ApiResponse } from '../types';
// Ajouté par le script de correction
export interface Trade {
  type: 'trade';
  id: string;
  symbol: string;
  price: number;
  quantity: number;
  side: 'buy' | 'sell';
  timestamp: number;
};

export default class ApiService {
  private api: AxiosInstance;
  private wsBaseUrl: string;

  constructor() {
    this.api = axios.create({
      baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    this.wsBaseUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';
  }

  // Méthodes pour les trades
  async getTrades(symbol: string, startTime?: Date, endTime?: Date): Promise<ApiResponse<Trade[]>> {
    try {
      const params = {
        start_time: startTime?.toISOString(),
        end_time: endTime?.toISOString(),
      };
      const response = await this.api.get(`/trades/${symbol}`, { params });
      return response.data;
    } catch (error) {
      return { success: false, error: this.handleError(error) };
    }
  }

  // Méthodes pour les données de marché
  async getMarketData(symbol: string): Promise<ApiResponse<MarketData>> {
    try {
      const response = await this.api.get(`/market/${symbol}`);
      return response.data;
    } catch (error) {
      return { success: false, error: this.handleError(error) };
    }
  }

  async getHistoricalData(
    symbol: string,
    interval: string = '1m',
    limit: number = 1000
  ): Promise<ApiResponse<MarketData[]>> {
    try {
      const params = {
        interval,
        limit,
      };
      const response = await this.api.get(`/market/${symbol}/history`, { params });
      return response.data;
    } catch (error) {
      return { success: false, error: this.handleError(error) };
    }
  }

  // Méthodes pour les WebSockets
  createWebSocket(symbol: string): WebSocket {
    const ws = new WebSocket(`${this.wsBaseUrl}/market/${symbol}`);

    ws.onerror = error => {
      console.error('WebSocket error:', error);
    };

    return ws;
  }

  // Méthodes pour les alertes
  async getAlerts(): Promise<ApiResponse<Alert[]>> {
    try {
      const response = await this.api.get('/alerts');
      return response.data;
    } catch (error) {
      return { success: false, error: this.handleError(error) };
    }
  }

  async createAlert(alert: Omit<Alert, 'id'>): Promise<ApiResponse<Alert>> {
    try {
      const response = await this.api.post('/alerts', alert);
      return response.data;
    } catch (error) {
      return { success: false, error: this.handleError(error) };
    }
  }

  async updateAlert(id: string, alert: Partial<Alert>): Promise<ApiResponse<Alert>> {
    try {
      const response = await this.api.put(`/alerts/${id}`, alert);
      return response.data;
    } catch (error) {
      return { success: false, error: this.handleError(error) };
    }
  }

  async deleteAlert(id: string): Promise<ApiResponse<void>> {
    try {
      const response = await this.api.delete(`/alerts/${id}`);
      return response.data;
    } catch (error) {
      return { success: false, error: this.handleError(error) };
    }
  }

  private handleError(error: unknown): string {
    if (axios.isAxiosError(error)) {
      return error.response?.data?.error || error.message;
    }
    return 'Une erreur inattendue est survenue';
  }
}

export const api = new ApiService();

/**
 * Interface pour la réponse d'authentification
 */
export interface AuthResponse {
  access_token: string;
  token_type: string;
}

/**
 * Fonction pour authentifier un utilisateur
 * @param username Nom d'utilisateur
 * @param password Mot de passe
 * @returns Promesse avec le token d'accès
 */
export const loginUser = async (username: string, password: string): Promise<AuthResponse> => {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  const response = await fetch('/api/token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Authentification échouée');
  }

  return response.json();
};

/**
 * Vérifie si l'utilisateur est authentifié
 * @returns true si l'utilisateur est connecté
 */
export const isAuthenticated = (): boolean => {
  return !!localStorage.getItem('auth_token');
};

/**
 * Déconnecte l'utilisateur
 */
export const logoutUser = (): void => {
  localStorage.removeItem('auth_token');
  localStorage.removeItem('username');
};
