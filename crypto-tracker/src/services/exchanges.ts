import axios from 'axios';

export interface ExchangeData {
  symbol: string;
  baseAsset: string;
  price: number;
  priceChangePercent: number;
}

const formatBinanceData = (data: any[]): ExchangeData[] => {
  return data
    .filter(ticker => ticker.symbol.endsWith('USDT'))
    .map(ticker => ({
      symbol: ticker.symbol,
      baseAsset: ticker.symbol.replace('USDT', ''),
      price: parseFloat(ticker.lastPrice),
      priceChangePercent: parseFloat(ticker.priceChangePercent),
    }))
    .sort((a, b) => b.price * b.priceChangePercent - a.price * a.priceChangePercent);
};

const formatKrakenData = (data: any): ExchangeData[] => {
  return Object.entries(data.result)
    .filter(([symbol]) => symbol.endsWith('USD'))
    .map(([symbol, ticker]: [string, any]) => ({
      symbol: symbol,
      baseAsset: symbol.replace('USD', '').replace('XBT', 'BTC'),
      price: parseFloat(ticker.c[0]),
      priceChangePercent: ((parseFloat(ticker.c[0]) - parseFloat(ticker.o)) / parseFloat(ticker.o)) * 100,
    }))
    .sort((a, b) => b.price * b.priceChangePercent - a.price * a.priceChangePercent);
};

export const fetchExchangeData = async (exchange: 'binance' | 'kraken'): Promise<ExchangeData[]> => {
  try {
    if (exchange === 'binance') {
      const response = await axios.get('https://api.binance.com/api/v3/ticker/24hr');
      return formatBinanceData(response.data);
    } else {
      const response = await axios.get('https://api.kraken.com/0/public/Ticker');
      return formatKrakenData(response.data);
    }
  } catch (error) {
    console.error('Error fetching exchange data:', error);
    return [];
  }
}; 