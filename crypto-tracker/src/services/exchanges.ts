import axios from 'axios';

export interface ExchangeData {
  symbol: string;
  baseAsset: string;
  price: number;
  priceChangePercent: number;
  volume: number;
  quoteVolume: number;
  high24h: number;
  low24h: number;
  priceChange24h: number;
}

export async function fetchExchangeData(exchange: 'binance' | 'kraken'): Promise<ExchangeData[]> {
  try {
    if (exchange === 'binance') {
      const response = await axios.get('https://api.binance.com/api/v3/ticker/24hr');
      return response.data.map((item: any) => ({
        symbol: item.symbol,
        baseAsset: item.symbol.replace('USDT', ''),
        price: parseFloat(item.lastPrice),
        priceChangePercent: parseFloat(item.priceChangePercent),
        volume: parseFloat(item.volume),
        quoteVolume: parseFloat(item.quoteVolume),
        high24h: parseFloat(item.highPrice),
        low24h: parseFloat(item.lowPrice),
        priceChange24h: parseFloat(item.priceChange)
      }));
    } else if (exchange === 'kraken') {
      const [pairsResponse, tickerResponse] = await Promise.all([
        axios.get('https://api.kraken.com/0/public/AssetPairs'),
        axios.get('https://api.kraken.com/0/public/Ticker')
      ]);

      const pairs = pairsResponse.data.result;
      const tickers = tickerResponse.data.result;

      return Object.entries(pairs)
        .filter(([pair]) => pair.includes('USDT'))
        .map(([pair, info]: [string, any]) => {
          const ticker = tickers[pair];
          if (!ticker) return null;

          const baseAsset = info.base.replace('XBT', 'BTC');
          const symbol = pair.replace('/', '');

          return {
            symbol,
            baseAsset,
            price: parseFloat(ticker.c[0]),
            priceChangePercent: ((parseFloat(ticker.c[0]) - parseFloat(ticker.o)) / parseFloat(ticker.o)) * 100,
            volume: parseFloat(ticker.v[1]),
            quoteVolume: parseFloat(ticker.v[1]) * parseFloat(ticker.c[0]),
            high24h: parseFloat(ticker.h[1]),
            low24h: parseFloat(ticker.l[1]),
            priceChange24h: parseFloat(ticker.c[0]) - parseFloat(ticker.o)
          };
        })
        .filter((item): item is ExchangeData => item !== null);
    }
    return [];
  } catch (error) {
    console.error(`Error fetching ${exchange} data:`, error);
    return [];
  }
}

export function normalizePairSymbol(symbol: string, exchange: string): string {
  switch (exchange) {
    case 'binance':
      return symbol;
    case 'kraken':
      return symbol.replace('XBT', 'BTC');
    default:
      return symbol;
  }
} 