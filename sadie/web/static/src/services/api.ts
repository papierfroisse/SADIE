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

/**
 * Payload d'alerte tel que l'API le renvoie (modèle `Alert` de
 * `sadie/web/app.py`) : en snake_case, avec des horodatages en millisecondes.
 *
 * Le domaine du front (`types.ts`) est en camelCase. La traduction se fait ici,
 * à la frontière, et nulle part ailleurs : sans elle, `alert.createdAt` restait
 * `undefined` et l'affichage plantait (`RangeError: Invalid time value`), tandis
 * qu'un envoi en camelCase vers un modèle snake_case était rejeté en 422.
 */
export interface AlerteApi {
  id?: string | null;
  symbol: string;
  type: string;
  condition: string;
  value: number;
  notification_type: string;
  triggered?: boolean;
  created_at?: number | null;
  triggered_at?: number | null;
}

/** Traduit une alerte de l'API vers le domaine du front. */
export const versAlerte = (donnees: AlerteApi): Alert => ({
  id: donnees.id ?? '',
  symbol: donnees.symbol,
  type: donnees.type as Alert['type'],
  condition: donnees.condition,
  value: donnees.value,
  notificationType: donnees.notification_type === 'email' ? 'email' : 'browser',
  triggered: donnees.triggered ?? false,
  createdAt: donnees.created_at ?? Date.now(),
  ...(donnees.triggered_at != null ? { triggeredAt: donnees.triggered_at } : {}),
});

/** Traduit une alerte du domaine du front vers le payload attendu par l'API. */
export const versAlerteApi = (alerte: Omit<Alert, 'id'> | Partial<Alert>) => ({
  symbol: alerte.symbol,
  type: alerte.type,
  condition: alerte.condition,
  value: alerte.value,
  notification_type: alerte.notificationType,
});

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
  /**
   * Ouvre le flux temps réel du marché.
   *
   * Le backend expose `@app.websocket("/ws/market")` avec deux paramètres de
   * requête obligatoires (`exchange`, `symbols` séparés par des virgules) :
   * l'ancienne URL `/ws/market/${symbol}` ne correspondait à aucune route, donc
   * aucun flux de marché ne s'ouvrait jamais.
   */
  createWebSocket(symbol: string, exchange: string = 'binance'): WebSocket {
    const parametres = new URLSearchParams({ exchange, symbols: symbol });
    const ws = new WebSocket(`${this.wsBaseUrl}/market?${parametres.toString()}`);

    ws.onerror = error => {
      console.error('WebSocket error:', error);
    };

    return ws;
  }

  // Méthodes pour les alertes
  async getAlerts(): Promise<ApiResponse<Alert[]>> {
    try {
      const response = await this.api.get<ApiResponse<AlerteApi[]>>('/alerts');
      const { success, data, error } = response.data;
      return { success, error, data: data?.map(versAlerte) };
    } catch (error) {
      return { success: false, error: this.handleError(error) };
    }
  }

  async createAlert(alert: Omit<Alert, 'id'>): Promise<ApiResponse<Alert>> {
    try {
      const response = await this.api.post<ApiResponse<AlerteApi>>(
        '/alerts',
        versAlerteApi(alert)
      );
      const { success, data, error } = response.data;
      return { success, error, data: data ? versAlerte(data) : undefined };
    } catch (error) {
      return { success: false, error: this.handleError(error) };
    }
  }

  /**
   * Note : l'API n'expose pas de route `PUT /api/alerts/{id}` (`sadie/web/app.py`
   * ne déclare que GET, POST et DELETE). Cet appel renverra donc 404 tant que la
   * route n'existe pas ; le payload est déjà traduit pour rester cohérent.
   */
  async updateAlert(id: string, alert: Partial<Alert>): Promise<ApiResponse<Alert>> {
    try {
      const response = await this.api.put<ApiResponse<AlerteApi>>(
        `/alerts/${id}`,
        versAlerteApi(alert)
      );
      const { success, data, error } = response.data;
      return { success, error, data: data ? versAlerte(data) : undefined };
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

/**
 * Interface pour les données d'inscription
 */
export interface RegisterData {
  username: string;
  password: string;
  email: string;
  full_name?: string;
}

/**
 * Interface pour la réponse d'inscription
 */
export interface RegisterResponse {
  success: boolean;
  message: string;
  user?: {
    username: string;
    email: string;
    full_name?: string;
    disabled?: boolean;
    scopes: string[];
  };
  error?: string;
}

/**
 * Fonction pour créer un nouvel utilisateur
 * @param userData Données de l'utilisateur
 * @returns Promesse avec le résultat de l'inscription
 */
export const registerUser = async (userData: RegisterData): Promise<RegisterResponse> => {
  const response = await fetch('/api/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  });

  const data = await response.json();
  
  if (!response.ok) {
    throw new Error(data.message || 'Erreur lors de l\'inscription');
  }

  return data;
};
