import { MarketData, TimeInterval, Candle } from './types';

const BINANCE_WS_URL = 'wss://stream.binance.com/ws';
const RECONNECT_DELAY = 5000;
const MAX_RETRY_ATTEMPTS = 5;

interface WebSocketState {
  instance: WebSocket | null;
  isConnecting: boolean;
  retryCount: number;
  subscriptions: Set<string>;
}

export class DataManager {
  private wsState: WebSocketState = {
    instance: null,
    isConnecting: false,
    retryCount: 0,
    subscriptions: new Set()
  };

  private cache: Map<string, MarketData> = new Map();

  constructor() {
    this.setupWebSocket();
  }

  private setupWebSocket() {
    if (this.wsState.instance?.readyState === WebSocket.OPEN || this.wsState.isConnecting) {
      return;
    }

    this.wsState.isConnecting = true;

    try {
      const ws = new WebSocket(BINANCE_WS_URL);

      ws.onopen = () => {
        console.log('WebSocket connected');
        this.wsState.instance = ws;
        this.wsState.isConnecting = false;
        this.wsState.retryCount = 0;

        // Réabonner aux flux précédents
        if (this.wsState.subscriptions.size > 0) {
          const subscribeMsg = {
            method: 'SUBSCRIBE',
            params: Array.from(this.wsState.subscriptions),
            id: Date.now()
          };
          ws.send(JSON.stringify(subscribeMsg));
        }
      };

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        this.wsState.instance = null;
        this.wsState.isConnecting = false;

        // Tentative de reconnexion avec backoff exponentiel
        if (this.wsState.retryCount < MAX_RETRY_ATTEMPTS) {
          const delay = RECONNECT_DELAY * Math.pow(2, this.wsState.retryCount);
          this.wsState.retryCount++;
          console.log(`Tentative de reconnexion dans ${delay}ms...`);
          setTimeout(() => this.setupWebSocket(), delay);
        } else {
          console.error('Nombre maximum de tentatives de reconnexion atteint');
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleWebSocketMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

    } catch (error) {
      console.error('Error creating WebSocket:', error);
      this.wsState.isConnecting = false;
    }
  }

  private handleWebSocketMessage(data: any) {
    // Gérer les différents types de messages
    if (data.e === 'kline') {
      const candle: Candle = {
        timestamp: data.k.t,
        open: parseFloat(data.k.o),
        high: parseFloat(data.k.h),
        low: parseFloat(data.k.l),
        close: parseFloat(data.k.c),
        volume: parseFloat(data.k.v)
      };

      const symbol = data.s.toLowerCase();
      const interval = data.k.i;
      const cacheKey = `${symbol}-${interval}`;

      // Mettre à jour le cache
      const cachedData = this.cache.get(cacheKey);
      if (cachedData) {
        const lastCandle = cachedData.candles[cachedData.candles.length - 1];
        if (lastCandle.timestamp === candle.timestamp) {
          cachedData.candles[cachedData.candles.length - 1] = candle;
        } else {
          cachedData.candles.push(candle);
        }
        cachedData.lastUpdate = Date.now();
      }
    }
  }

  public subscribe(symbol: string, interval: TimeInterval): void {
    if (!symbol || typeof symbol !== 'string') {
      throw new Error('Invalid symbol: must be a non-empty string');
    }

    const stream = `${symbol.toLowerCase()}@kline_${interval}`;
    
    if (this.wsState.subscriptions.has(stream)) {
      return;
    }

    this.wsState.subscriptions.add(stream);

    if (this.wsState.instance?.readyState === WebSocket.OPEN) {
      const subscribeMsg = {
        method: 'SUBSCRIBE',
        params: [stream],
        id: Date.now()
      };
      this.wsState.instance.send(JSON.stringify(subscribeMsg));
    } else {
      this.setupWebSocket();
    }
  }

  public unsubscribe(symbol: string, interval: TimeInterval): void {
    if (!symbol || typeof symbol !== 'string') {
      throw new Error('Invalid symbol: must be a non-empty string');
    }

    const stream = `${symbol.toLowerCase()}@kline_${interval}`;
    
    if (!this.wsState.subscriptions.has(stream)) {
      return;
    }

    this.wsState.subscriptions.delete(stream);

    if (this.wsState.instance?.readyState === WebSocket.OPEN) {
      const unsubscribeMsg = {
        method: 'UNSUBSCRIBE',
        params: [stream],
        id: Date.now()
      };
      this.wsState.instance.send(JSON.stringify(unsubscribeMsg));
    }
  }

  public async fetchHistory(symbol: string, interval: TimeInterval, limit: number = 1000): Promise<MarketData> {
    if (!symbol || typeof symbol !== 'string') {
      throw new Error('Invalid symbol: must be a non-empty string');
    }

    try {
      const response = await fetch(
        `https://api.binance.com/api/v3/klines?symbol=${symbol.toUpperCase()}&interval=${interval}&limit=${limit}`
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const candles: Candle[] = data.map((item: any) => ({
        timestamp: item[0],
        open: parseFloat(item[1]),
        high: parseFloat(item[2]),
        low: parseFloat(item[3]),
        close: parseFloat(item[4]),
        volume: parseFloat(item[5])
      }));

      const marketData: MarketData = {
        candles,
        lastUpdate: Date.now()
      };

      // Mettre en cache
      const cacheKey = `${symbol.toLowerCase()}-${interval}`;
      this.cache.set(cacheKey, marketData);

      // S'abonner aux mises à jour en temps réel
      this.subscribe(symbol, interval);

      return marketData;
    } catch (error) {
      console.error('Error fetching history:', error);
      throw error;
    }
  }

  public dispose() {
    if (this.wsState.instance) {
      this.wsState.instance.close();
      this.wsState.instance = null;
    }
    this.wsState.subscriptions.clear();
    this.cache.clear();
  }
}

// Créer une instance singleton
export const dataManager = new DataManager(); 