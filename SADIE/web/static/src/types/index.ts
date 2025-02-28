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
  timeframe?: string;
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
  id: string;
  symbol: string;
  type: 'price' | 'volume' | 'indicator';
  condition: string;
  value: number;
  notificationType: 'browser' | 'email';
  createdAt?: number;
  triggered?: boolean;
  triggeredAt?: number;
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
export interface Trade {
  type: 'trade';
  id: string;
  symbol: string;
  price: number;
  quantity: number;
  side: 'buy' | 'sell';
  timestamp: number;
}

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
