/**
 * Types du domaine SADIE.
 *
 * Ce fichier est le SEUL point de définition des types partagés.
 *
 * Il existait auparavant `src/types.ts` ET `src/types/index.ts`, qui
 * déclaraient les mêmes noms avec des formes différentes : `Alert` en
 * camelCase d'un côté, `Order` avec `timestamp` au lieu de
 * `createdAt`/`updatedAt` de l'autre, `TechnicalIndicator` sans `color` ni
 * `signal`. Comme TypeScript résout un fichier avant un dossier homonyme, tous
 * les imports `'../types'` tombaient sur `types.ts` et le second fichier
 * n'était jamais lu : deux contrats de données coexistaient, dont un fantôme.
 * Les deux ont été fusionnés ici (formes réellement utilisées par le code).
 */

// --- Données de marché -------------------------------------------------------

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

// --- Indicateurs techniques --------------------------------------------------

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

// --- Ordres ------------------------------------------------------------------

export interface Order {
  id: string;
  symbol: string;
  type: 'market' | 'limit' | 'stop' | 'stop_limit';
  side: 'buy' | 'sell';
  quantity: number;
  price?: number;
  stopPrice?: number;
  status: 'new' | 'open' | 'filled' | 'cancelled' | 'rejected';
  createdAt: number;
  updatedAt: number;
}

// --- Alertes -----------------------------------------------------------------

export interface Alert {
  id: string;
  symbol: string;
  type: 'price' | 'volume' | 'indicator';
  condition: string;
  value: number;
  notificationType: 'browser' | 'email';
  triggered: boolean;
  createdAt: number;
  triggeredAt?: number;
}

// --- Analyse de sentiment ----------------------------------------------------

export interface SentimentData {
  symbol: string;
  timestamp: string;
  polarity: number;
  subjectivity: number;
  category: 'positive' | 'negative' | 'neutral';
  confidence: number;
  volume: number;
}

// --- Transactions ------------------------------------------------------------

export interface Trade {
  type: 'trade';
  id: string;
  symbol: string;
  price: number;
  quantity: number;
  side: 'buy' | 'sell';
  timestamp: number;
}

// --- Enveloppe des messages WebSocket ---------------------------------------

export interface WebSocketMessage {
  type: 'market_data' | 'alert' | 'order' | 'trade';
  symbol: string;
  timeframe?: string;
  timestamp: number;
  open?: number;
  high?: number;
  low?: number;
  close?: number;
  volume?: number;
  /** Charge utile selon le type de message (forme variable par nature). */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  data?: any;
}

// --- Réponses de l'API ------------------------------------------------------

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

// --- Préférences utilisateur -------------------------------------------------

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