export type TimeInterval = '1m' | '3m' | '5m' | '15m' | '30m' | '1h' | '2h' | '4h' | '6h' | '8h' | '12h' | '1d' | '3d' | '1w' | '1M';

export interface MarketData {
  symbol: string;
  interval: TimeInterval;
  startTime: number;
  endTime: number;
  candles: CandleData[];
}

export interface CandleData {
  time: number;    // Timestamp en millisecondes
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface DataManagerConfig {
  maxCacheSize: number;        // Nombre maximum de bougies en cache
  cleanupThreshold: number;    // Seuil de nettoyage (pourcentage)
  compressionEnabled: boolean; // Activation de la compression
  retryAttempts: number;      // Nombre de tentatives de reconnexion
  retryDelay: number;         // Délai entre les tentatives (ms)
}

export interface DataSubscription {
  symbol: string;
  interval: TimeInterval;
  onUpdate: (data: CandleData) => void;
  onError: (error: Error) => void;
}

export interface DataManager {
  // Gestion des données historiques
  fetchHistory(symbol: string, interval: TimeInterval, start: number, end: number): Promise<MarketData>;
  
  // Gestion du temps réel
  subscribe(subscription: DataSubscription): () => void;  // Retourne une fonction de désabonnement
  
  // Gestion du cache
  getCachedData(symbol: string, interval: TimeInterval): MarketData | null;
  clearCache(symbol?: string, interval?: TimeInterval): void;
  
  // Utilitaires
  mergeCandles(oldData: MarketData, newData: MarketData): MarketData;
  compressData(data: MarketData): MarketData;
  
  // Gestion des erreurs et état
  getConnectionStatus(): 'connected' | 'connecting' | 'disconnected' | 'error';
  getLastError(): Error | null;
} 