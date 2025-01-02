import { PrismaClient } from '@prisma/client';
import axios from 'axios';
import WebSocket from 'ws';

const prisma = new PrismaClient();

interface BinanceKline {
  t: number;  // Kline start time
  o: string;  // Open price
  h: string;  // High price
  l: string;  // Low price
  c: string;  // Close price
  v: string;  // Volume
}

interface KrakenOHLC {
  time: number;
  open: string;
  high: string;
  low: string;
  close: string;
  volume: string;
}

export class DataCollector {
  private binanceWs: WebSocket | null = null;
  private krakenWs: WebSocket | null = null;
  private symbols: string[] = [];
  private collectingActive = false;

  constructor(symbols: string[] = ['BTCUSDT', 'ETHUSDT']) {
    this.symbols = symbols;
  }

  async startCollecting() {
    if (this.collectingActive) return;
    this.collectingActive = true;

    // Démarrer la collecte en temps réel
    this.connectWebSockets();
    
    // Collecter l'historique initial
    await this.collectHistoricalData();
    
    // Planifier la collecte périodique
    setInterval(() => this.collectHistoricalData(), 60 * 60 * 1000); // Toutes les heures
  }

  private async collectHistoricalData() {
    for (const symbol of this.symbols) {
      // Collecter les données Binance
      try {
        const binanceData = await axios.get(
          `https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=1m&limit=1000`
        );
        
        for (const kline of binanceData.data) {
          await prisma.candle.upsert({
            where: {
              exchange_symbol_timestamp: {
                exchange: 'binance',
                symbol,
                timestamp: new Date(kline[0])
              }
            },
            update: {
              open: parseFloat(kline[1]),
              high: parseFloat(kline[2]),
              low: parseFloat(kline[3]),
              close: parseFloat(kline[4]),
              volume: parseFloat(kline[5])
            },
            create: {
              exchange: 'binance',
              symbol,
              timestamp: new Date(kline[0]),
              open: parseFloat(kline[1]),
              high: parseFloat(kline[2]),
              low: parseFloat(kline[3]),
              close: parseFloat(kline[4]),
              volume: parseFloat(kline[5])
            }
          });
        }
      } catch (error) {
        console.error(`Error collecting Binance data for ${symbol}:`, error);
      }

      // Collecter les données Kraken
      try {
        const krakenSymbol = symbol.replace('USDT', 'USD');
        const krakenData = await axios.get(
          `https://api.kraken.com/0/public/OHLC?pair=${krakenSymbol}&interval=1`
        );
        
        const data = krakenData.data.result[Object.keys(krakenData.data.result)[0]];
        for (const ohlc of data) {
          await prisma.candle.upsert({
            where: {
              exchange_symbol_timestamp: {
                exchange: 'kraken',
                symbol,
                timestamp: new Date(ohlc[0] * 1000)
              }
            },
            update: {
              open: parseFloat(ohlc[1]),
              high: parseFloat(ohlc[2]),
              low: parseFloat(ohlc[3]),
              close: parseFloat(ohlc[4]),
              volume: parseFloat(ohlc[6])
            },
            create: {
              exchange: 'kraken',
              symbol,
              timestamp: new Date(ohlc[0] * 1000),
              open: parseFloat(ohlc[1]),
              high: parseFloat(ohlc[2]),
              low: parseFloat(ohlc[3]),
              close: parseFloat(ohlc[4]),
              volume: parseFloat(ohlc[6])
            }
          });
        }
      } catch (error) {
        console.error(`Error collecting Kraken data for ${symbol}:`, error);
      }
    }
  }

  private connectWebSockets() {
    // Connexion WebSocket Binance
    this.binanceWs = new WebSocket('wss://stream.binance.com:9443/ws');
    
    this.binanceWs.on('open', () => {
      const subscribeMsg = {
        method: 'SUBSCRIBE',
        params: this.symbols.map(symbol => `${symbol.toLowerCase()}@kline_1m`),
        id: 1
      };
      this.binanceWs.send(JSON.stringify(subscribeMsg));
    });

    this.binanceWs.on('message', async (data: WebSocket.Data) => {
      try {
        const message = JSON.parse(data.toString());
        if (message.e === 'kline') {
          const kline = message.k;
          await this.updateMarketData('binance', {
            symbol: kline.s,
            lastPrice: parseFloat(kline.c),
            timestamp: new Date(kline.t)
          });
        }
      } catch (error) {
        console.error('Error processing Binance WebSocket message:', error);
      }
    });

    // Connexion WebSocket Kraken
    this.krakenWs = new WebSocket('wss://ws.kraken.com');

    this.krakenWs.on('open', () => {
      const subscribeMsg = {
        event: 'subscribe',
        pair: this.symbols.map(s => s.replace('USDT', 'USD')),
        subscription: { name: 'ohlc', interval: 1 }
      };
      this.krakenWs.send(JSON.stringify(subscribeMsg));
    });

    this.krakenWs.on('message', async (data: WebSocket.Data) => {
      try {
        const message = JSON.parse(data.toString());
        if (Array.isArray(message) && message[2] === 'ohlc-1') {
          const ohlc = message[1];
          await this.updateMarketData('kraken', {
            symbol: message[3].replace('USD', 'USDT'),
            lastPrice: parseFloat(ohlc[4]),
            timestamp: new Date(parseInt(ohlc[0]) * 1000)
          });
        }
      } catch (error) {
        console.error('Error processing Kraken WebSocket message:', error);
      }
    });
  }

  private async updateMarketData(
    exchange: string,
    data: { symbol: string; lastPrice: number; timestamp: Date }
  ) {
    try {
      await prisma.marketData.upsert({
        where: {
          exchange_symbol: {
            exchange,
            symbol: data.symbol
          }
        },
        update: {
          lastPrice: data.lastPrice,
          updatedAt: data.timestamp
        },
        create: {
          exchange,
          symbol: data.symbol,
          lastPrice: data.lastPrice,
          priceChange24h: 0,
          volume24h: 0,
          highPrice24h: data.lastPrice,
          lowPrice24h: data.lastPrice,
          updatedAt: data.timestamp
        }
      });
    } catch (error) {
      console.error('Error updating market data:', error);
    }
  }

  stop() {
    this.collectingActive = false;
    if (this.binanceWs) {
      this.binanceWs.close();
      this.binanceWs = null;
    }
    if (this.krakenWs) {
      this.krakenWs.close();
      this.krakenWs = null;
    }
  }
}

// Export une instance singleton
export const dataCollector = new DataCollector(); 