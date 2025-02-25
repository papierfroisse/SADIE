// Types pour les données de marché
export interface MarketData {
  symbol: string;
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  type?: string;
  indicators?: {
    rsi?: number;
    macd?: number;
    ema_20?: number;
    ema_50?: number;
    ema_200?: number;
  };
}

// Types pour les indicateurs techniques
export interface TechnicalIndicator {
  name: string;
  value: number;
  color?: string;
  signal?: 'buy' | 'sell' | 'neutral';
}

export interface IndicatorConfig {
  type: 'bollinger' | 'macd' | 'rsi' | 'stochastic';
  params: Record<string, number>;
  visible: boolean;
}

// Types pour les ordres
export interface Order {
  id: string;
  symbol: string;
  type: 'market' | 'limit' | 'stop' | 'stop_limit';
  side: 'buy' | 'sell';
  quantity: number;
  price?: number;
  stopPrice?: number;
  status: 'new' | 'filled' | 'cancelled' | 'rejected';
  timestamp: string;
}

// Types pour les alertes
export interface Alert {
  type: 'alert';
  id: string;
  symbol: string;
  alertType: 'price' | 'indicator';
  condition: 'above' | 'below';
  value: number;
  notification_type: 'browser' | 'email';
  created_at: number;
  triggered?: boolean;
  triggered_at?: number;
}

// Types pour l'analyse de sentiment
export interface SentimentData {
  symbol: string;
  timestamp: string;
  polarity: number;
  subjectivity: number;
  category: 'positive' | 'negative' | 'neutral';
  confidence: number;
  volume: number;
}

// Types pour les WebSocket
export type WebSocketMessage = MarketData | Alert | Trade;

// Types pour les réponses API
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

// Types pour la configuration utilisateur
export interface UserSettings {
  theme: 'light' | 'dark';
  chartType: 'candlestick' | 'line';
  defaultSymbol: string;
  indicators: IndicatorConfig[];
  notifications: {
    browser: boolean;
    email: boolean;
    sound: boolean;
  };
  layout: {
    showVolume: boolean;
    showOrderBook: boolean;
    showTrades: boolean;
  };
}

export interface Trade {
  type: 'trade';
  id: string;
  symbol: string;
  price: number;
  quantity: number;
  side: 'buy' | 'sell';
  timestamp: number;
}
