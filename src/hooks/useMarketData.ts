import { useState, useEffect } from 'react';
import { MarketData, TimeInterval } from '../data/types';
import { dataManager } from '../data/DataManager';

interface UseMarketDataProps {
  symbol: string;
  interval: TimeInterval;
}

interface UseMarketDataResult {
  data: MarketData | null;
  loading: boolean;
  error: Error | null;
}

export function useMarketData({ symbol, interval }: UseMarketDataProps): UseMarketDataResult {
  const [data, setData] = useState<MarketData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!symbol || typeof symbol !== 'string') {
      setError(new Error('Invalid symbol: must be a non-empty string'));
      setLoading(false);
      return;
    }

    const formattedSymbol = symbol.toUpperCase();

    async function fetchData() {
      try {
        setLoading(true);
        setError(null);
        const marketData = await dataManager.fetchHistory(formattedSymbol, interval);
        setData(marketData);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('An error occurred while fetching data'));
      } finally {
        setLoading(false);
      }
    }

    fetchData();

    // S'abonner aux mises à jour en temps réel
    dataManager.subscribe(formattedSymbol, interval);

    return () => {
      dataManager.unsubscribe(formattedSymbol, interval);
    };
  }, [symbol, interval]);

  return { data, loading, error };
} 