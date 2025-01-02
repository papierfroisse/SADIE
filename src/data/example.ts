import { DataManager } from './DataManager';
import { defaultConfig } from './config';
import { CandleData } from './types';

// Création d'une instance du gestionnaire
const dataManager = new DataManager(defaultConfig);

// Exemple de récupération de données historiques
async function fetchHistoricalData() {
  try {
    const endTime = Date.now();
    const startTime = endTime - 7 * 24 * 60 * 60 * 1000; // 7 jours

    const data = await dataManager.fetchHistory(
      'BTCUSDT',
      '1h',
      startTime,
      endTime
    );

    console.log(`Récupéré ${data.candles.length} bougies`);
  } catch (error) {
    console.error('Erreur lors de la récupération des données:', error);
  }
}

// Exemple d'abonnement aux données en temps réel
function subscribeToRealtime() {
  const unsubscribe = dataManager.subscribe({
    symbol: 'BTCUSDT',
    interval: '1m',
    onUpdate: (candle: CandleData) => {
      console.log('Nouvelle bougie:', candle);
    },
    onError: (error: Error) => {
      console.error('Erreur de streaming:', error);
    }
  });

  // Pour se désabonner plus tard :
  // unsubscribe();
}

// Exemple d'utilisation du cache
function checkCache() {
  const cachedData = dataManager.getCachedData('BTCUSDT', '1h');
  if (cachedData) {
    console.log('Données en cache:', {
      symbol: cachedData.symbol,
      interval: cachedData.interval,
      numberOfCandles: cachedData.candles.length,
      fromDate: new Date(cachedData.startTime),
      toDate: new Date(cachedData.endTime)
    });
  }
}

// Exemple de compression des données
function compressHistoricalData() {
  const cachedData = dataManager.getCachedData('BTCUSDT', '1h');
  if (cachedData) {
    const compressed = dataManager.compressData(cachedData);
    console.log('Taux de compression:', 
      (1 - compressed.candles.length / cachedData.candles.length) * 100,
      '%'
    );
  }
}

// Export des fonctions d'exemple
export const examples = {
  fetchHistoricalData,
  subscribeToRealtime,
  checkCache,
  compressHistoricalData
}; 