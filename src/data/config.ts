import { DataManagerConfig } from './types';

export const defaultConfig: DataManagerConfig = {
  maxCacheSize: 10000,        // Maximum de 10000 bougies en cache
  cleanupThreshold: 0.8,      // Nettoie quand 80% du cache est utilisé
  compressionEnabled: true,   // Active la compression des données
  retryAttempts: 5,          // 5 tentatives de reconnexion
  retryDelay: 5000,          // 5 secondes entre chaque tentative
}; 