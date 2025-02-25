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
  side: 'buy' | 'sell';
}

export interface WebSocketState {
  marketData: {
    [symbol: string]: MarketData;
  };
}

export interface KrakenWebSocketMessage {
  type: 'subscribe' | 'unsubscribe' | 'error' | 'data';
  channel: 'ohlc' | 'ticker';
  symbol: string;
  data?: any;
  error?: string;
}

export interface KrakenOHLCData {
  time: number;
  etime: number;
  open: string;
  high: string;
  low: string;
  close: string;
  vwap: string;
  volume: string;
  count: number;
}

export interface KrakenTickerData {
  p: [string, string];  // price array [today's first trade price, last trade price]
  v: [string, string];  // volume array [today, last 24 hours]
  t: [number, number];  // number of trades array [today, last 24 hours]
  l: [string, string];  // low array [today, last 24 hours]
  h: [string, string];  // high array [today, last 24 hours]
  o: [string, string];  // open array [today, last 24 hours]
}

export interface Alert {
  id: string;
  symbol: string;
  type: 'price' | 'indicator';
  condition: 'above' | 'below';
  value: number;
  notification_type: 'browser' | 'email';
  triggered: boolean;
  created_at: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface Trade {
  id: string;
  symbol: string;
  side: 'buy' | 'sell';
  price: number;
  quantity: number;
  timestamp: number;
  status: 'open' | 'closed' | 'cancelled';
}

export interface OrderBook {
  symbol: string;
  timestamp: number;
  bids: [number, number][]; // [price, quantity][]
  asks: [number, number][]; // [price, quantity][]
}

export interface ChartTimeframe {
  label: string;
  value: string;
  interval: number; // in minutes
}

// Pour éviter l'erreur TS1208
export {}; 