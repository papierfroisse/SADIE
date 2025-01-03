export interface Candle {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export type TimeInterval = '1m' | '5m' | '15m' | '30m' | '1h' | '4h' | '1d' | '1w' | '1M';

export interface MarketData {
  candles: Candle[];
  lastUpdate: number;
}

export interface MarketDataError {
  message: string;
  code?: string;
} 