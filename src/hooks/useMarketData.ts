import { useState, useEffect } from 'react';
import { Candle, TimeInterval } from '../data/types';

interface MarketDataParams {
  symbol: string;
  interval: TimeInterval;
}

interface MarketData {
  candles: Candle[];
}

// Fonction pour générer des données de test
const generateTestData = (count: number): Candle[] => {
  const now = Date.now();
  const oneHour = 60 * 60 * 1000;
  const data: Candle[] = [];

  let lastClose = 50000; // Prix de départ pour BTC/USD
  
  for (let i = 0; i < count; i++) {
    const timestamp = now - (count - i) * oneHour;
    const volatility = lastClose * 0.02; // 2% de volatilité
    const change = (Math.random() - 0.5) * volatility;
    
    const open = lastClose;
    const close = open + change;
    const high = Math.max(open, close) * (1 + Math.random() * 0.01);
    const low = Math.min(open, close) * (1 - Math.random() * 0.01);
    const volume = 100 + Math.random() * 900; // Volume entre 100 et 1000

    data.push({
      timestamp,
      open,
      high,
      low,
      close,
      volume
    });

    lastClose = close;
  }

  return data;
};

export function useMarketData({ symbol, interval }: MarketDataParams) {
  const [data, setData] = useState<MarketData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    // Simuler un appel API avec un délai
    const timer = setTimeout(() => {
      try {
        const testData = generateTestData(100);
        setData({ candles: testData });
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Unknown error'));
        setLoading(false);
      }
    }, 500);

    return () => {
      clearTimeout(timer);
    };
  }, [symbol, interval]);

  return { data, loading, error };
} 