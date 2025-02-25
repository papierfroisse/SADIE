import axios, { AxiosInstance } from 'axios';
import { MarketData, Alert, ApiResponse, Trade } from '../types';

class ApiService {
  private api: AxiosInstance;
  private wsBaseUrl: string;

  constructor() {
    const baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.api = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true  // Ajouter cette option pour les requêtes CORS avec credentials
    });
    this.wsBaseUrl = baseURL.replace(/^http/, 'ws');
  }

  private handleError(error: any): string {
    if (error.response) {
      return error.response.data.message || 'Une erreur est survenue';
    }
    return error.message || 'Une erreur est survenue';
  }

  // Méthodes pour les WebSockets
  createWebSocket(symbol: string): WebSocket {
    const ws = new WebSocket(`${this.wsBaseUrl}/api/ws/${symbol}`);

    ws.onerror = error => {
      console.error('WebSocket error:', error);
    };

    return ws;
  }

  // Méthodes pour les alertes
  async getAlerts(): Promise<ApiResponse<Alert[]>> {
    try {
      const response = await this.api.get('/api/alerts');
      return response.data;
    } catch (error) {
      console.error('Error fetching alerts:', error);
      return { success: false, error: this.handleError(error) };
    }
  }

  async createAlert(alert: Omit<Alert, 'id'>): Promise<ApiResponse<Alert>> {
    try {
      const response = await this.api.post('/api/alerts', alert);
      return response.data;
    } catch (error) {
      return { success: false, error: this.handleError(error) };
    }
  }

  async updateAlert(id: string, alert: Partial<Alert>): Promise<ApiResponse<Alert>> {
    try {
      const response = await this.api.put(`/api/alerts/${id}`, alert);
      return response.data;
    } catch (error) {
      return { success: false, error: this.handleError(error) };
    }
  }

  async deleteAlert(id: string): Promise<ApiResponse<void>> {
    try {
      const response = await this.api.delete(`/api/alerts/${id}`);
      return response.data;
    } catch (error) {
      return { success: false, error: this.handleError(error) };
    }
  }

  // Market Data
  async getMarketData(symbol: string, timeframe: string): Promise<MarketData> {
    const response = await this.api.get(`/api/market-data/${symbol}/${timeframe}`);
    return response.data;
  }

  // Trading
  async getTrades(symbol: string): Promise<Trade[]> {
    const response = await this.api.get(`/api/trades/${symbol}`);
    return response.data;
  }
}

export const api = new ApiService(); 