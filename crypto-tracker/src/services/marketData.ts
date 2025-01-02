import axios from 'axios';

export interface MarketData {
  id: string;
  symbol: string;
  name: string;
  image: string;
  current_price: number;
  market_cap: number;
  market_cap_rank: number;
  fully_diluted_valuation: number;
  total_volume: number;
  high_24h: number;
  low_24h: number;
  price_change_24h: number;
  price_change_percentage_24h: number;
  market_cap_change_24h: number;
  market_cap_change_percentage_24h: number;
  circulating_supply: number;
  total_supply: number;
  max_supply: number;
  ath: number;
  ath_change_percentage: number;
  ath_date: string;
  atl: number;
  atl_change_percentage: number;
  atl_date: string;
  last_updated: string;
}

const COINGECKO_API = 'https://api.coingecko.com/api/v3';

export const fetchMarketData = async (
  page: number = 1,
  perPage: number = 100,
  currency: string = 'usd'
): Promise<MarketData[]> => {
  try {
    const response = await axios.get(
      `${COINGECKO_API}/coins/markets`,
      {
        params: {
          vs_currency: currency,
          order: 'market_cap_desc',
          per_page: perPage,
          page,
          sparkline: false,
          locale: 'fr'
        }
      }
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching market data:', error);
    return [];
  }
};

// Cache pour les données de market cap
let marketDataCache: {
  data: MarketData[];
  timestamp: number;
} | null = null;

const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

export const getMarketData = async (
  page: number = 1,
  perPage: number = 100,
  currency: string = 'usd'
): Promise<MarketData[]> => {
  // Vérifier si les données en cache sont encore valides
  if (
    marketDataCache &&
    Date.now() - marketDataCache.timestamp < CACHE_DURATION
  ) {
    return marketDataCache.data;
  }

  // Sinon, récupérer les nouvelles données
  const data = await fetchMarketData(page, perPage, currency);
  
  // Mettre à jour le cache
  marketDataCache = {
    data,
    timestamp: Date.now()
  };

  return data;
}; 