import { DataManager as IDataManager, DataManagerConfig, DataSubscription, MarketData, CandleData, TimeInterval } from './types';

export class DataManager implements IDataManager {
  private config: DataManagerConfig;
  private cache: Map<string, MarketData> = new Map();
  private subscriptions: Map<string, Set<DataSubscription>> = new Map();
  private status: 'connected' | 'connecting' | 'disconnected' | 'error' = 'disconnected';
  private lastError: Error | null = null;
  private ws: WebSocket | null = null;

  constructor(config: DataManagerConfig) {
    this.config = config;
  }

  // Génère une clé unique pour le cache
  private getCacheKey(symbol: string, interval: TimeInterval): string {
    return `${symbol}-${interval}`;
  }

  // Gestion des données historiques
  async fetchHistory(
    symbol: string,
    interval: TimeInterval,
    start: number,
    end: number
  ): Promise<MarketData> {
    try {
      // Vérifier d'abord le cache
      const cachedData = this.getCachedData(symbol, interval);
      if (cachedData) {
        const isWithinRange = 
          cachedData.startTime <= start && cachedData.endTime >= end;
        if (isWithinRange) {
          return this.filterDataByTimeRange(cachedData, start, end);
        }
      }

      // Récupérer les données depuis l'API
      const response = await fetch(
        `https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=${interval}&startTime=${start}&endTime=${end}&limit=1000`
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const marketData: MarketData = {
        symbol,
        interval,
        startTime: start,
        endTime: end,
        candles: data.map((item: any) => ({
          time: item[0],
          open: parseFloat(item[1]),
          high: parseFloat(item[2]),
          low: parseFloat(item[3]),
          close: parseFloat(item[4]),
          volume: parseFloat(item[5])
        }))
      };

      // Mettre en cache
      this.updateCache(marketData);

      return marketData;
    } catch (error) {
      this.lastError = error as Error;
      throw error;
    }
  }

  // Gestion du temps réel
  subscribe(subscription: DataSubscription): () => void {
    const key = this.getCacheKey(subscription.symbol, subscription.interval);
    
    if (!this.subscriptions.has(key)) {
      this.subscriptions.set(key, new Set());
    }
    
    this.subscriptions.get(key)!.add(subscription);
    this.ensureWebSocketConnection();

    return () => {
      const subs = this.subscriptions.get(key);
      if (subs) {
        subs.delete(subscription);
        if (subs.size === 0) {
          this.subscriptions.delete(key);
          this.cleanupWebSocket();
        }
      }
    };
  }

  // Gestion du cache
  getCachedData(symbol: string, interval: TimeInterval): MarketData | null {
    const key = this.getCacheKey(symbol, interval);
    return this.cache.get(key) || null;
  }

  clearCache(symbol?: string, interval?: TimeInterval): void {
    if (symbol && interval) {
      this.cache.delete(this.getCacheKey(symbol, interval));
    } else {
      this.cache.clear();
    }
  }

  // Utilitaires
  mergeCandles(oldData: MarketData, newData: MarketData): MarketData {
    if (oldData.symbol !== newData.symbol || oldData.interval !== newData.interval) {
      throw new Error('Cannot merge data from different symbols or intervals');
    }

    const mergedCandles = [...oldData.candles];
    const timeMap = new Map(mergedCandles.map(c => [c.time, c]));

    for (const candle of newData.candles) {
      timeMap.set(candle.time, candle);
    }

    const sortedCandles = Array.from(timeMap.values())
      .sort((a, b) => a.time - b.time);

    return {
      symbol: oldData.symbol,
      interval: oldData.interval,
      startTime: Math.min(oldData.startTime, newData.startTime),
      endTime: Math.max(oldData.endTime, newData.endTime),
      candles: sortedCandles
    };
  }

  compressData(data: MarketData): MarketData {
    if (!this.config.compressionEnabled) return data;

    // Implémentation basique : ne garde que les points importants
    const compressed = data.candles.filter((candle, index) => {
      if (index === 0 || index === data.candles.length - 1) return true;
      
      const prev = data.candles[index - 1];
      const next = data.candles[index + 1];
      
      // Garde les points avec changement significatif
      const priceChange = Math.abs(candle.close - prev.close) / prev.close;
      const volumeChange = Math.abs(candle.volume - prev.volume) / prev.volume;
      
      return priceChange > 0.001 || volumeChange > 0.1;
    });

    return {
      ...data,
      candles: compressed
    };
  }

  // Gestion des erreurs et état
  getConnectionStatus(): 'connected' | 'connecting' | 'disconnected' | 'error' {
    return this.status;
  }

  getLastError(): Error | null {
    return this.lastError;
  }

  // Méthodes privées
  private filterDataByTimeRange(data: MarketData, start: number, end: number): MarketData {
    return {
      ...data,
      startTime: start,
      endTime: end,
      candles: data.candles.filter(c => c.time >= start && c.time <= end)
    };
  }

  private updateCache(data: MarketData): void {
    const key = this.getCacheKey(data.symbol, data.interval);
    const existing = this.cache.get(key);

    if (existing) {
      this.cache.set(key, this.mergeCandles(existing, data));
    } else {
      this.cache.set(key, data);
    }

    this.cleanupCacheIfNeeded();
  }

  private cleanupCacheIfNeeded(): void {
    const totalCandles = Array.from(this.cache.values())
      .reduce((sum, data) => sum + data.candles.length, 0);

    if (totalCandles > this.config.maxCacheSize) {
      // Supprimer les données les plus anciennes
      const entries = Array.from(this.cache.entries())
        .sort(([, a], [, b]) => a.endTime - b.endTime);

      let candlesToRemove = totalCandles - this.config.maxCacheSize;
      for (const [key, data] of entries) {
        if (candlesToRemove <= 0) break;
        this.cache.delete(key);
        candlesToRemove -= data.candles.length;
      }
    }
  }

  private ensureWebSocketConnection(): void {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this.status = 'connecting';
    this.ws = new WebSocket('wss://stream.binance.com:9443/ws');

    this.ws.onopen = () => {
      this.status = 'connected';
      this.subscribeToStreams();
    };

    this.ws.onclose = () => {
      this.status = 'disconnected';
      this.reconnect();
    };

    this.ws.onerror = (error) => {
      this.status = 'error';
      this.lastError = new Error('WebSocket connection error');
      this.reconnect();
    };

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        this.handleWebSocketMessage(message);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
  }

  private subscribeToStreams(): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;

    const streams = Array.from(this.subscriptions.keys())
      .map(key => {
        const [symbol, interval] = key.split('-');
        return `${symbol.toLowerCase()}@kline_${interval}`;
      });

    if (streams.length > 0) {
      this.ws.send(JSON.stringify({
        method: 'SUBSCRIBE',
        params: streams,
        id: Date.now()
      }));
    }
  }

  private handleWebSocketMessage(message: any): void {
    if (!message.k) return; // Ignore les messages non-kline

    const candle: CandleData = {
      time: message.k.t,
      open: parseFloat(message.k.o),
      high: parseFloat(message.k.h),
      low: parseFloat(message.k.l),
      close: parseFloat(message.k.c),
      volume: parseFloat(message.k.v)
    };

    const key = this.getCacheKey(message.s, message.k.i);
    const subscribers = this.subscriptions.get(key);

    if (subscribers) {
      for (const subscription of subscribers) {
        try {
          subscription.onUpdate(candle);
        } catch (error) {
          subscription.onError(error as Error);
        }
      }
    }

    // Mise à jour du cache
    const cachedData = this.getCachedData(message.s, message.k.i);
    if (cachedData) {
      this.updateCache({
        ...cachedData,
        endTime: Math.max(cachedData.endTime, candle.time),
        candles: [...cachedData.candles, candle]
      });
    }
  }

  private async reconnect(): Promise<void> {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    let attempts = 0;
    const tryReconnect = async () => {
      if (attempts >= this.config.retryAttempts) {
        this.status = 'error';
        this.lastError = new Error('Max retry attempts reached');
        return;
      }

      attempts++;
      await new Promise(resolve => setTimeout(resolve, this.config.retryDelay));
      this.ensureWebSocketConnection();
    };

    await tryReconnect();
  }

  private cleanupWebSocket(): void {
    if (this.subscriptions.size === 0 && this.ws) {
      this.ws.close();
      this.ws = null;
      this.status = 'disconnected';
    }
  }
} 