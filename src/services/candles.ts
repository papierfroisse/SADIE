import axios, { AxiosError } from 'axios';

export interface CandleData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

class CandleDataError extends Error {
  constructor(message: string, public readonly code: string) {
    super(message);
    this.name = 'CandleDataError';
  }
}

const validateCandleData = (data: any): boolean => {
  if (!Array.isArray(data)) return false;
  return data.every(candle => 
    Array.isArray(candle) && 
    candle.length >= 5 &&
    !isNaN(Number(candle[1])) && // open
    !isNaN(Number(candle[2])) && // high
    !isNaN(Number(candle[3])) && // low
    !isNaN(Number(candle[4]))    // close
  );
};

const formatTimestamp = (timestamp: number): string => {
  return new Date(timestamp).toISOString();
};

const formatBinanceCandles = (data: any[]): CandleData[] => {
  if (!validateCandleData(data)) {
    throw new CandleDataError('Invalid Binance candle data format', 'INVALID_DATA');
  }

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
  if (!data?.result || typeof data.result !== 'object') {
    throw new CandleDataError('Invalid Kraken response format', 'INVALID_RESPONSE');
  }

  const uniqueMap = new Map();
  
  Object.entries(data.result).forEach(([_, candles]: [string, any]) => {
    if (!Array.isArray(candles)) {
      throw new CandleDataError('Invalid Kraken candle data format', 'INVALID_DATA');
    }

    candles.forEach(([time, open, high, low, close]: any) => {
      if (!time || !open || !high || !low || !close) {
        throw new CandleDataError('Missing required candle data', 'MISSING_DATA');
      }

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
} as const;

export const fetchCandleData = async (
  exchange: 'binance' | 'kraken',
  symbol: string,
  timeframe: keyof typeof timeframeMap
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
    if (error instanceof CandleDataError) {
      console.error(`Candle data error: ${error.message} (${error.code})`);
      return [];
    }
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      console.error('API request failed:', {
        status: axiosError.response?.status,
        statusText: axiosError.response?.statusText,
        data: axiosError.response?.data,
      });
      return [];
    }
    console.error('Unexpected error:', error);
    return [];
  }
}; 