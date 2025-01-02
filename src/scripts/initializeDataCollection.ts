import { dataCollector } from '../services/market-data/DataCollector';

const SYMBOLS = [
  'BTCUSDT',
  'ETHUSDT',
  'BNBUSDT',
  'ADAUSDT',
  'DOGEUSDT',
  'XRPUSDT',
  'DOTUSDT',
  'UNIUSDT'
];

const INTERVALS = ['1m', '5m', '15m', '30m', '1h', '4h', '1d'];

async function initializeCollection() {
  try {
    // Initialisation des exchanges
    console.log('Initializing exchanges...');
    await dataCollector.initializeExchange('binance');
    await dataCollector.initializeExchange('kraken');

    // Collecte des données historiques
    console.log('Starting historical data collection...');
    for (const symbol of SYMBOLS) {
      for (const interval of INTERVALS) {
        console.log(`Collecting historical data for ${symbol} - ${interval}`);
        
        // Binance
        try {
          await dataCollector.startHistoricalCollection('binance', symbol, interval);
          console.log(`✓ Binance - ${symbol} - ${interval}`);
        } catch (error) {
          console.error(`✗ Error collecting Binance data for ${symbol} - ${interval}:`, error);
        }

        // Kraken
        try {
          await dataCollector.startHistoricalCollection('kraken', symbol, interval);
          console.log(`✓ Kraken - ${symbol} - ${interval}`);
        } catch (error) {
          console.error(`✗ Error collecting Kraken data for ${symbol} - ${interval}:`, error);
        }

        // Petite pause pour éviter de surcharger les APIs
        await new Promise(resolve => setTimeout(resolve, 1000));
      }

      // Démarrage de la collecte en temps réel
      console.log(`Starting realtime collection for ${symbol}`);
      try {
        await dataCollector.startRealtimeCollection('binance', symbol);
        console.log(`✓ Binance realtime - ${symbol}`);
      } catch (error) {
        console.error(`✗ Error starting Binance realtime collection for ${symbol}:`, error);
      }

      try {
        await dataCollector.startRealtimeCollection('kraken', symbol);
        console.log(`✓ Kraken realtime - ${symbol}`);
      } catch (error) {
        console.error(`✗ Error starting Kraken realtime collection for ${symbol}:`, error);
      }
    }

    console.log('Data collection initialized successfully!');
  } catch (error) {
    console.error('Error initializing data collection:', error);
  }
}

// Gestion des erreurs non capturées
process.on('unhandledRejection', (error) => {
  console.error('Unhandled rejection:', error);
});

process.on('uncaughtException', (error) => {
  console.error('Uncaught exception:', error);
});

// Démarrage de la collecte
initializeCollection(); 