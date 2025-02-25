import axios, { AxiosInstance } from 'axios';
import { MarketData, Alert, Trade, ApiResponse } from '../types';

class ApiService {
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
