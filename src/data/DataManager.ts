import { Candle, TimeInterval, MarketData } from './types';

export class DataManager {
  private static instance: DataManager;
  private ws: WebSocket | null = null;
  private subscriptions: Map<string, Set<TimeInterval>> = new Map();
  private data: Map<string, Map<TimeInterval, MarketData>> = new Map();
  private callbacks: Map<string, Set<(data: MarketData) => void>> = new Map();

  private constructor() {
    this.connectWebSocket();
  }

  public static getInstance(): DataManager {
    if (!DataManager.instance) {
      DataManager.instance = new DataManager();
    }
    return DataManager.instance;
  }

  private connectWebSocket() {
    this.ws = new WebSocket('wss://stream.binance.com:9443/ws');

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      // Réabonner aux paires existantes
      this.subscriptions.forEach((intervals, symbol) => {
        intervals.forEach(interval => {
          this.subscribe(symbol, interval);
        });
      });
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.e === 'kline') {
        const symbol = data.s;
        const interval = data.k.i as TimeInterval;
        const candle: Candle = {
          timestamp: data.k.t,
          open: parseFloat(data.k.o),
          high: parseFloat(data.k.h),
          low: parseFloat(data.k.l),
          close: parseFloat(data.k.c),
          volume: parseFloat(data.k.v)
        };

        // Mettre à jour les données
        if (!this.data.has(symbol)) {
          this.data.set(symbol, new Map());
        }
        const symbolData = this.data.get(symbol)!;
        if (!symbolData.has(interval)) {
          symbolData.set(interval, { candles: [], lastUpdate: 0 });
        }
        const intervalData = symbolData.get(interval)!;

        // Mettre à jour ou ajouter la bougie
        const index = intervalData.candles.findIndex(c => c.timestamp === candle.timestamp);
        if (index !== -1) {
          intervalData.candles[index] = candle;
        } else {
          intervalData.candles.push(candle);
          // Trier par timestamp
          intervalData.candles.sort((a, b) => a.timestamp - b.timestamp);
        }
        intervalData.lastUpdate = Date.now();

        // Notifier les callbacks
        const key = `${symbol}-${interval}`;
        if (this.callbacks.has(key)) {
          this.callbacks.get(key)!.forEach(callback => callback(intervalData));
        }
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      // Reconnecter après un délai
      setTimeout(() => this.connectWebSocket(), 5000);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  private subscribe(symbol: string, interval: TimeInterval) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket not connected');
      return;
    }

    const subscriptionMsg = {
      method: 'SUBSCRIBE',
      params: [`${symbol.toLowerCase()}@kline_${interval}`],
      id: Date.now()
    };

    this.ws.send(JSON.stringify(subscriptionMsg));
  }

  private unsubscribe(symbol: string, interval: TimeInterval) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket not connected');
      return;
    }

    const unsubscriptionMsg = {
      method: 'UNSUBSCRIBE',
      params: [`${symbol.toLowerCase()}@kline_${interval}`],
      id: Date.now()
    };

    this.ws.send(JSON.stringify(unsubscriptionMsg));
  }

  public addSubscription(symbol: string, interval: TimeInterval) {
    if (!symbol || typeof symbol !== 'string') {
      console.error('Invalid symbol:', symbol);
      return;
    }

    // Ajouter à la map des abonnements
    if (!this.subscriptions.has(symbol)) {
      this.subscriptions.set(symbol, new Set());
    }
    this.subscriptions.get(symbol)!.add(interval);

    // S'abonner au flux WebSocket
    this.subscribe(symbol, interval);
  }

  public removeSubscription(symbol: string, interval: TimeInterval) {
    if (!this.subscriptions.has(symbol)) return;

    const intervals = this.subscriptions.get(symbol)!;
    intervals.delete(interval);

    if (intervals.size === 0) {
      this.subscriptions.delete(symbol);
    }

    this.unsubscribe(symbol, interval);
  }

  public addCallback(symbol: string, interval: TimeInterval, callback: (data: MarketData) => void) {
    const key = `${symbol}-${interval}`;
    if (!this.callbacks.has(key)) {
      this.callbacks.set(key, new Set());
    }
    this.callbacks.get(key)!.add(callback);

    // Envoyer les données existantes immédiatement si disponibles
    const symbolData = this.data.get(symbol);
    if (symbolData) {
      const intervalData = symbolData.get(interval);
      if (intervalData) {
        callback(intervalData);
      }
    }
  }

  public removeCallback(symbol: string, interval: TimeInterval, callback: (data: MarketData) => void) {
    const key = `${symbol}-${interval}`;
    if (!this.callbacks.has(key)) return;

    this.callbacks.get(key)!.delete(callback);

    if (this.callbacks.get(key)!.size === 0) {
      this.callbacks.delete(key);
    }
  }

  public getData(symbol: string, interval: TimeInterval): MarketData | undefined {
    return this.data.get(symbol)?.get(interval);
  }

  public destroy() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.subscriptions.clear();
    this.data.clear();
    this.callbacks.clear();
  }
} 