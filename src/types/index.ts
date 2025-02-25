export interface MarketData {
  symbol: string;
  timestamp: number;
  price: number;
  quantity: number;
  trade_id: string;
  buyer_order_id: string;
  seller_order_id: string;
  buyer_is_maker: boolean;
  is_best_match: boolean;
}

export interface Alert {
  id: string;
  symbol: string;
  type: 'price' | 'indicator';
  condition: 'above' | 'below';
  value: number;
  notification_type: 'browser' | 'email';
  created_at: number;
  triggered: boolean;
  triggered_at?: number;
}

export interface WebSocketMessage {
  type: 'market_data' | 'alert';
  data: MarketData | Alert;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface CandleData {
  symbol: string;
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  indicators?: {
    rsi?: number;
    macd?: number;
    ema20?: number;
    ema50?: number;
    ema200?: number;
  };
} 