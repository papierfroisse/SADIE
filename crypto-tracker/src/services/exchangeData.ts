import axios from 'axios';

export interface Candle {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface ExchangeData {
  exchange: string;
  symbol: string;
  interval: string;
  candles: Candle[];
}

class ExchangeDataService {
  private static instance: ExchangeDataService;
  private cache: Map<string, ExchangeData>;
  private wsConnections: Map<string, WebSocket>;

  private constructor() {
    this.cache = new Map();
    this.wsConnections = new Map();
  }

  public static getInstance(): ExchangeDataService {
    if (!ExchangeDataService.instance) {
      ExchangeDataService.instance = new ExchangeDataService();
    }
    return ExchangeDataService.instance;
  }

  private getCacheKey(exchange: string, symbol: string, interval: string): string {
    return `${exchange}-${symbol}-${interval}`;
  }

  // Récupère les données historiques de Binance
  async fetchBinanceHistory(symbol: string, interval: string = '1h'): Promise<Candle[]> {
    try {
      const response = await axios.get(
        `https://api.binance.com/api/v3/klines`,
        {
          params: {
            symbol: symbol.toUpperCase(),
            interval,
            limit: 1000
          }
        }
      );

      const candles: Candle[] = response.data.map((d: any) => ({
        timestamp: d[0],
        open: parseFloat(d[1]),
        high: parseFloat(d[2]),
        low: parseFloat(d[3]),
        close: parseFloat(d[4]),
        volume: parseFloat(d[5])
      }));

      const cacheKey = this.getCacheKey('binance', symbol, interval);
      this.cache.set(cacheKey, {
        exchange: 'binance',
        symbol,
        interval,
        candles
      });

      return candles;
    } catch (error) {
      console.error('Error fetching Binance history:', error);
      throw error;
    }
  }

  // Récupère les données historiques de Kraken
  async fetchKrakenHistory(symbol: string, interval: string = '1h'): Promise<Candle[]> {
    try {
      const response = await axios.get(
        `https://api.kraken.com/0/public/OHLC`,
        {
          params: {
            pair: symbol,
            interval: parseInt(interval) * 60
          }
        }
      );

      const data = response.data.result[Object.keys(response.data.result)[0]];
      const candles: Candle[] = data.map((d: any) => ({
        timestamp: d[0] * 1000,
        open: parseFloat(d[1]),
        high: parseFloat(d[2]),
        low: parseFloat(d[3]),
        close: parseFloat(d[4]),
        volume: parseFloat(d[6])
      }));

      const cacheKey = this.getCacheKey('kraken', symbol, interval);
      this.cache.set(cacheKey, {
        exchange: 'kraken',
        symbol,
        interval,
        candles
      });

      return candles;
    } catch (error) {
      console.error('Error fetching Kraken history:', error);
      throw error;
    }
  }

  // Connexion WebSocket à Binance pour les mises à jour en temps réel
  connectBinanceWS(symbol: string, onUpdate: (candle: Candle) => void): void {
    const wsSymbol = symbol.toLowerCase();
    const wsUrl = `wss://stream.binance.com:9443/ws/${wsSymbol}@kline_1m`;
    
    const ws = new WebSocket(wsUrl);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const k = data.k;
      
      const candle: Candle = {
        timestamp: k.t,
        open: parseFloat(k.o),
        high: parseFloat(k.h),
        low: parseFloat(k.l),
        close: parseFloat(k.c),
        volume: parseFloat(k.v)
      };
      
      onUpdate(candle);
    };

    this.wsConnections.set(`binance-${symbol}`, ws);
  }

  // Connexion WebSocket à Kraken pour les mises à jour en temps réel
  connectKrakenWS(symbol: string, onUpdate: (candle: Candle) => void): void {
    const wsUrl = 'wss://ws.kraken.com';
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      ws.send(JSON.stringify({
        event: 'subscribe',
        pair: [symbol],
        subscription: {
          name: 'ohlc',
          interval: 1
        }
      }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (Array.isArray(data) && data[2] === 'ohlc-1') {
        const ohlc = data[1];
        const candle: Candle = {
          timestamp: parseInt(ohlc[0]) * 1000,
          open: parseFloat(ohlc[2]),
          high: parseFloat(ohlc[3]),
          low: parseFloat(ohlc[4]),
          close: parseFloat(ohlc[5]),
          volume: parseFloat(ohlc[7])
        };
        onUpdate(candle);
      }
    };

    this.wsConnections.set(`kraken-${symbol}`, ws);
  }

  // Déconnexion des WebSockets
  disconnect(exchange: string, symbol: string): void {
    const ws = this.wsConnections.get(`${exchange}-${symbol}`);
    if (ws) {
      ws.close();
      this.wsConnections.delete(`${exchange}-${symbol}`);
    }
  }

  // Récupère les données en cache
  getCachedData(exchange: string, symbol: string, interval: string): ExchangeData | undefined {
    const cacheKey = this.getCacheKey(exchange, symbol, interval);
    return this.cache.get(cacheKey);
  }

  // Met à jour les données en cache
  updateCache(exchange: string, symbol: string, interval: string, candle: Candle): void {
    const cacheKey = this.getCacheKey(exchange, symbol, interval);
    const data = this.cache.get(cacheKey);
    
    if (data) {
      const lastCandle = data.candles[data.candles.length - 1];
      
      if (lastCandle.timestamp === candle.timestamp) {
        // Mise à jour de la dernière bougie
        data.candles[data.candles.length - 1] = candle;
      } else {
        // Ajout d'une nouvelle bougie
        data.candles.push(candle);
      }
      
      this.cache.set(cacheKey, data);
    }
  }
}

export const exchangeDataService = ExchangeDataService.getInstance(); 