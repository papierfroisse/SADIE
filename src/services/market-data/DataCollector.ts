import { PrismaClient } from '@prisma/client';
import axios from 'axios';
import WebSocket from 'ws';
import { RateLimiter } from './RateLimiter';

const prisma = new PrismaClient();

interface CandleData {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export class DataCollector {
  private static instance: DataCollector;
  private wsConnections: Map<string, WebSocket>;
  private rateLimiter: RateLimiter;

  private constructor() {
    this.wsConnections = new Map();
    this.rateLimiter = new RateLimiter({
      binance: { maxRequests: 1200, perMinute: true },
      kraken: { maxRequests: 60, perMinute: true }
    });
  }

  public static getInstance(): DataCollector {
    if (!DataCollector.instance) {
      DataCollector.instance = new DataCollector();
    }
    return DataCollector.instance;
  }

  // Initialise la collecte de données pour un exchange
  public async initializeExchange(exchangeName: string): Promise<void> {
    try {
      // Vérifie si l'exchange existe déjà
      let exchange = await prisma.exchange.findUnique({
        where: { name: exchangeName }
      });

      // Crée l'exchange s'il n'existe pas
      if (!exchange) {
        exchange = await prisma.exchange.create({
          data: { name: exchangeName }
        });
      }

      // Récupère les paires disponibles
      const pairs = await this.fetchAvailablePairs(exchangeName);

      // Crée ou met à jour les paires dans la base de données
      for (const pair of pairs) {
        await prisma.pair.upsert({
          where: {
            symbol_exchangeId: {
              symbol: pair.symbol,
              exchangeId: exchange.id
            }
          },
          create: {
            symbol: pair.symbol,
            baseAsset: pair.baseAsset,
            quoteAsset: pair.quoteAsset,
            exchangeId: exchange.id
          },
          update: {
            baseAsset: pair.baseAsset,
            quoteAsset: pair.quoteAsset
          }
        });
      }
    } catch (error) {
      console.error(`Error initializing exchange ${exchangeName}:`, error);
      throw error;
    }
  }

  // Récupère les paires disponibles sur un exchange
  private async fetchAvailablePairs(exchange: string): Promise<Array<{
    symbol: string;
    baseAsset: string;
    quoteAsset: string;
  }>> {
    try {
      await this.rateLimiter.waitForToken(exchange);

      if (exchange === 'binance') {
        const response = await axios.get('https://api.binance.com/api/v3/exchangeInfo');
        return response.data.symbols
          .filter((s: any) => s.status === 'TRADING')
          .map((s: any) => ({
            symbol: s.symbol,
            baseAsset: s.baseAsset,
            quoteAsset: s.quoteAsset
          }));
      } else if (exchange === 'kraken') {
        const response = await axios.get('https://api.kraken.com/0/public/AssetPairs');
        return Object.entries(response.data.result)
          .map(([symbol, info]: [string, any]) => ({
            symbol,
            baseAsset: info.base,
            quoteAsset: info.quote
          }));
      }

      throw new Error(`Unsupported exchange: ${exchange}`);
    } catch (error) {
      console.error(`Error fetching pairs for ${exchange}:`, error);
      throw error;
    }
  }

  // Démarre la collecte de données historiques
  public async startHistoricalCollection(
    exchange: string,
    symbol: string,
    interval: string,
    startTime?: number
  ): Promise<void> {
    try {
      const pair = await prisma.pair.findFirst({
        where: {
          symbol,
          exchange: { name: exchange }
        }
      });

      if (!pair) {
        throw new Error(`Pair ${symbol} not found for exchange ${exchange}`);
      }

      // Récupère la dernière mise à jour
      const lastUpdate = await prisma.lastUpdate.findUnique({
        where: {
          pairId_interval: {
            pairId: pair.id,
            interval
          }
        }
      });

      const fromTime = startTime || lastUpdate?.timestamp.getTime() || Date.now() - 30 * 24 * 60 * 60 * 1000;

      // Récupère les données historiques
      const candles = await this.fetchHistoricalData(exchange, symbol, interval, fromTime);

      // Enregistre les données dans la base de données
      await this.saveCandles(pair.id, interval, candles);

      // Met à jour le timestamp de dernière mise à jour
      await prisma.lastUpdate.upsert({
        where: {
          pairId_interval: {
            pairId: pair.id,
            interval
          }
        },
        create: {
          pairId: pair.id,
          interval,
          timestamp: new Date(Math.max(...candles.map(c => c.timestamp)))
        },
        update: {
          timestamp: new Date(Math.max(...candles.map(c => c.timestamp)))
        }
      });
    } catch (error) {
      console.error(`Error collecting historical data for ${symbol} on ${exchange}:`, error);
      throw error;
    }
  }

  // Récupère les données historiques d'un exchange
  private async fetchHistoricalData(
    exchange: string,
    symbol: string,
    interval: string,
    fromTime: number
  ): Promise<CandleData[]> {
    try {
      await this.rateLimiter.waitForToken(exchange);

      if (exchange === 'binance') {
        const response = await axios.get('https://api.binance.com/api/v3/klines', {
          params: {
            symbol,
            interval,
            startTime: fromTime,
            limit: 1000
          }
        });

        return response.data.map((d: any) => ({
          timestamp: d[0],
          open: parseFloat(d[1]),
          high: parseFloat(d[2]),
          low: parseFloat(d[3]),
          close: parseFloat(d[4]),
          volume: parseFloat(d[5])
        }));
      } else if (exchange === 'kraken') {
        const response = await axios.get('https://api.kraken.com/0/public/OHLC', {
          params: {
            pair: symbol,
            interval: this.convertInterval(interval),
            since: Math.floor(fromTime / 1000)
          }
        });

        const data = response.data.result[Object.keys(response.data.result)[0]];
        return data.map((d: any) => ({
          timestamp: d[0] * 1000,
          open: parseFloat(d[1]),
          high: parseFloat(d[2]),
          low: parseFloat(d[3]),
          close: parseFloat(d[4]),
          volume: parseFloat(d[6])
        }));
      }

      throw new Error(`Unsupported exchange: ${exchange}`);
    } catch (error) {
      console.error(`Error fetching historical data for ${symbol} on ${exchange}:`, error);
      throw error;
    }
  }

  // Enregistre les bougies dans la base de données
  private async saveCandles(pairId: string, interval: string, candles: CandleData[]): Promise<void> {
    try {
      // Utilise une transaction pour garantir l'atomicité
      await prisma.$transaction(async (tx) => {
        for (const candle of candles) {
          await tx.candle.upsert({
            where: {
              pairId_timestamp_interval: {
                pairId,
                timestamp: new Date(candle.timestamp),
                interval
              }
            },
            create: {
              pairId,
              interval,
              timestamp: new Date(candle.timestamp),
              open: candle.open,
              high: candle.high,
              low: candle.low,
              close: candle.close,
              volume: candle.volume
            },
            update: {
              open: candle.open,
              high: candle.high,
              low: candle.low,
              close: candle.close,
              volume: candle.volume
            }
          });
        }
      });
    } catch (error) {
      console.error('Error saving candles:', error);
      throw error;
    }
  }

  // Convertit les intervalles entre les formats des différents exchanges
  private convertInterval(interval: string): number {
    const value = parseInt(interval.slice(0, -1));
    const unit = interval.slice(-1);

    switch (unit) {
      case 'm':
        return value;
      case 'h':
        return value * 60;
      case 'd':
        return value * 1440;
      case 'w':
        return value * 10080;
      default:
        throw new Error(`Unsupported interval unit: ${unit}`);
    }
  }

  // Démarre la collecte en temps réel
  public async startRealtimeCollection(exchange: string, symbol: string): Promise<void> {
    const wsKey = `${exchange}-${symbol}`;

    if (this.wsConnections.has(wsKey)) {
      return;
    }

    if (exchange === 'binance') {
      const ws = new WebSocket(`wss://stream.binance.com:9443/ws/${symbol.toLowerCase()}@kline_1m`);
      
      ws.on('message', async (data: string) => {
        const msg = JSON.parse(data);
        if (msg.e === 'kline') {
          const candle: CandleData = {
            timestamp: msg.k.t,
            open: parseFloat(msg.k.o),
            high: parseFloat(msg.k.h),
            low: parseFloat(msg.k.l),
            close: parseFloat(msg.k.c),
            volume: parseFloat(msg.k.v)
          };

          const pair = await prisma.pair.findFirst({
            where: {
              symbol,
              exchange: { name: exchange }
            }
          });

          if (pair) {
            await this.saveCandles(pair.id, '1m', [candle]);
          }
        }
      });

      this.wsConnections.set(wsKey, ws);
    } else if (exchange === 'kraken') {
      const ws = new WebSocket('wss://ws.kraken.com');

      ws.on('open', () => {
        ws.send(JSON.stringify({
          event: 'subscribe',
          pair: [symbol],
          subscription: {
            name: 'ohlc',
            interval: 1
          }
        }));
      });

      ws.on('message', async (data: string) => {
        const msg = JSON.parse(data);
        if (Array.isArray(msg) && msg[2] === 'ohlc-1') {
          const ohlc = msg[1];
          const candle: CandleData = {
            timestamp: parseInt(ohlc[0]) * 1000,
            open: parseFloat(ohlc[2]),
            high: parseFloat(ohlc[3]),
            low: parseFloat(ohlc[4]),
            close: parseFloat(ohlc[5]),
            volume: parseFloat(ohlc[7])
          };

          const pair = await prisma.pair.findFirst({
            where: {
              symbol,
              exchange: { name: exchange }
            }
          });

          if (pair) {
            await this.saveCandles(pair.id, '1m', [candle]);
          }
        }
      });

      this.wsConnections.set(wsKey, ws);
    }
  }

  // Arrête la collecte en temps réel
  public stopRealtimeCollection(exchange: string, symbol: string): void {
    const wsKey = `${exchange}-${symbol}`;
    const ws = this.wsConnections.get(wsKey);
    
    if (ws) {
      ws.close();
      this.wsConnections.delete(wsKey);
    }
  }
}

export const dataCollector = DataCollector.getInstance(); 