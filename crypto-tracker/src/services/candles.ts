import axios from 'axios';

export interface CandleData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

const formatTimestamp = (timestamp: number): string => {
  return new Date(timestamp).toISOString();
};

const formatBinanceCandles = (data: any[]): CandleData[] => {
  const uniqueMap = new Map();
  
  data.forEach(([time, open, high, low, close]) => {
    const timestamp = Math.floor(time / 1000) * 1000;
    if (!uniqueMap.has(timestamp)) {
      uniqueMap.set(timestamp, {
        time: formatTimestamp(timestamp),
        open: parseFloat(open),
        high: parseFloat(high),
        low: parseFloat(low),
        close: parseFloat(close),
        volume: 0,
      });
    }
  });

  return Array.from(uniqueMap.values())
    .sort((a, b) => new Date(a.time).getTime() - new Date(b.time).getTime());
};

const formatKrakenCandles = (data: any): CandleData[] => {
  const uniqueMap = new Map();
  
  Object.entries(data.result).forEach(([_, candles]: [string, any]) => {
    candles.forEach(([time, open, high, low, close]: any) => {
      const timestamp = Math.floor(time) * 1000;
      if (!uniqueMap.has(timestamp)) {
        uniqueMap.set(timestamp, {
          time: formatTimestamp(timestamp),
          open: parseFloat(open),
          high: parseFloat(high),
          low: parseFloat(low),
          close: parseFloat(close),
          volume: 0,
        });
      }
    });
  });

  return Array.from(uniqueMap.values())
    .sort((a, b) => new Date(a.time).getTime() - new Date(b.time).getTime());
};

const timeframeMap = {
  '1m': { binance: '1m', kraken: '1' },
  '15m': { binance: '15m', kraken: '15' },
  '1h': { binance: '1h', kraken: '60' },
  '4h': { binance: '4h', kraken: '240' },
  '1d': { binance: '1d', kraken: '1440' },
};

export const fetchCandleData = async (
  exchange: 'binance' | 'kraken',
  symbol: string,
  timeframe: '1m' | '15m' | '1h' | '4h' | '1d'
): Promise<CandleData[]> => {
  try {
    if (exchange === 'binance') {
      const response = await axios.get(
        `https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=${
          timeframeMap[timeframe].binance
        }&limit=100`
      );
      return formatBinanceCandles(response.data);
    } else {
      const krakenSymbol = symbol
        .replace('USDT', 'USD')
        .replace(/([A-Z]{3,})([A-Z]{3,})/, '$1/$2');
      const response = await axios.get(
        `https://api.kraken.com/0/public/OHLC?pair=${krakenSymbol}&interval=${
          timeframeMap[timeframe].kraken
        }`
      );
      return formatKrakenCandles(response.data);
    }
  } catch (error) {
    console.error('Error fetching candle data:', error);
    return [];
  }
}; 