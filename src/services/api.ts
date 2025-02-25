import axios, { AxiosInstance } from 'axios';
import { MarketData, Alert, Trade, ApiResponse } from '../types';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async getAlerts(): Promise<ApiResponse<Alert[]>> {
    try {
      const response = await this.api.get<ApiResponse<Alert[]>>('/api/alerts');
      return response.data;
    } catch (error) {
      console.error('Error fetching alerts:', error);
      return { success: false, error: 'Failed to fetch alerts' };
    }
  }

  async createAlert(alert: Omit<Alert, 'id' | 'triggered' | 'createdAt' | 'triggeredAt'>): Promise<ApiResponse<Alert>> {
    try {
      const response = await this.api.post<ApiResponse<Alert>>('/api/alerts', alert);
      return response.data;
    } catch (error) {
      console.error('Error creating alert:', error);
      return { success: false, error: 'Failed to create alert' };
    }
  }

  async deleteAlert(id: string): Promise<ApiResponse<void>> {
    try {
      const response = await this.api.delete<ApiResponse<void>>(`/api/alerts/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting alert:', error);
      return { success: false, error: 'Failed to delete alert' };
    }
  }

  async getMarketData(symbol: string): Promise<ApiResponse<MarketData>> {
    try {
      const response = await this.api.get<ApiResponse<MarketData>>(`/api/market-data/${symbol}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching market data:', error);
      return { success: false, error: 'Failed to fetch market data' };
    }
  }

  async getTrades(symbol: string): Promise<ApiResponse<Trade[]>> {
    try {
      const response = await this.api.get<ApiResponse<Trade[]>>(`/api/trades/${symbol}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching trades:', error);
      return { success: false, error: 'Failed to fetch trades' };
    }
  }
}

export const apiService = new ApiService(); 