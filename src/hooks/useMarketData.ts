import { useState, useEffect } from 'react';
import { TimeInterval, MarketData, CandleData } from '../data/types';
import { DataManager } from '../data/DataManager';

const dataManager = new DataManager({
  maxCacheSize: 10000,
  cleanupThreshold: 0.8,
  compressionEnabled: true,
  retryAttempts: 3,
  retryDelay: 1000
});

interface UseMarketDataProps {
  symbol: string;
  interval: TimeInterval;
}

interface UseMarketDataResult {
  data: MarketData | null;
  loading: boolean;
  error: Error | null;
  status: 'connected' | 'connecting' | 'disconnected' | 'error';
}

export function useMarketData({ symbol, interval }: UseMarketDataProps): UseMarketDataResult {
  const [data, setData] = useState<MarketData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [status, setStatus] = useState<'connected' | 'connecting' | 'disconnected' | 'error'>('connecting');

  useEffect(() => {
    setLoading(true);
    setError(null);

    // Récupérer les données historiques
    const endTime = Date.now();
    const startTime = endTime - 7 * 24 * 60 * 60 * 1000; // 7 jours

    const fetchData = async () => {
      try {
        const historicalData = await dataManager.fetchHistory(symbol, interval, startTime, endTime);
        setData(historicalData);
        setStatus('connected');
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch data'));
        setStatus('error');
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    // S'abonner aux mises à jour en temps réel
    const unsubscribe = dataManager.subscribe({
      symbol,
      interval,
      onUpdate: (candle: CandleData) => {
        setData(prevData => {
          if (!prevData) return null;
          
          const lastCandle = prevData.candles[prevData.candles.length - 1];
          if (lastCandle && lastCandle.time === candle.time) {
            // Mettre à jour la dernière bougie
            const updatedCandles = [...prevData.candles];
            updatedCandles[updatedCandles.length - 1] = candle;
            return {
              ...prevData,
              candles: updatedCandles,
              endTime: candle.time
            };
          } else {
            // Ajouter une nouvelle bougie
            return {
              ...prevData,
              candles: [...prevData.candles, candle],
              endTime: candle.time
            };
          }
        });
      },
      onError: (err: Error) => {
        setError(err);
        setStatus('error');
      }
    });

    // Mettre à jour le statut de connexion
    const statusInterval = setInterval(() => {
      setStatus(dataManager.getConnectionStatus());
    }, 1000);

    return () => {
      unsubscribe();
      clearInterval(statusInterval);
    };
  }, [symbol, interval]);

  return { data, loading, error, status };
} 