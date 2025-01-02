import { CandleData } from '../data/types';

export function calculateRSI(data: CandleData[], period: number = 14): number[] {
  if (data.length < period + 1) {
    return Array(data.length).fill(0);
  }

  const changes = data.map((candle, i) => {
    if (i === 0) return 0;
    return candle.close - data[i - 1].close;
  });

  const gains = changes.map(change => change > 0 ? change : 0);
  const losses = changes.map(change => change < 0 ? -change : 0);

  const avgGain = gains.slice(1, period + 1).reduce((sum, gain) => sum + gain, 0) / period;
  const avgLoss = losses.slice(1, period + 1).reduce((sum, loss) => sum + loss, 0) / period;

  const rsi: number[] = Array(period).fill(0);
  let prevAvgGain = avgGain;
  let prevAvgLoss = avgLoss;

  for (let i = period; i < data.length; i++) {
    const gain = gains[i];
    const loss = losses[i];

    const newAvgGain = (prevAvgGain * (period - 1) + gain) / period;
    const newAvgLoss = (prevAvgLoss * (period - 1) + loss) / period;

    prevAvgGain = newAvgGain;
    prevAvgLoss = newAvgLoss;

    const rs = newAvgGain / (newAvgLoss === 0 ? 1 : newAvgLoss);
    const rsiValue = 100 - (100 / (1 + rs));
    rsi.push(rsiValue);
  }

  return rsi;
}

export interface MACDResult {
  macd: number[];
  signal: number[];
  histogram: number[];
}

export function calculateMACD(
  data: CandleData[],
  fastPeriod: number = 12,
  slowPeriod: number = 26,
  signalPeriod: number = 9
): MACDResult {
  if (data.length < Math.max(fastPeriod, slowPeriod) + signalPeriod) {
    return {
      macd: Array(data.length).fill(0),
      signal: Array(data.length).fill(0),
      histogram: Array(data.length).fill(0)
    };
  }

  // Calculer les EMA
  const calculateEMA = (prices: number[], period: number): number[] => {
    const k = 2 / (period + 1);
    const ema: number[] = [];
    let prevEMA = prices.slice(0, period).reduce((sum, price) => sum + price, 0) / period;

    prices.forEach((price, i) => {
      if (i < period) {
        ema.push(prevEMA);
        return;
      }

      prevEMA = price * k + prevEMA * (1 - k);
      ema.push(prevEMA);
    });

    return ema;
  };

  const prices = data.map(candle => candle.close);
  const fastEMA = calculateEMA(prices, fastPeriod);
  const slowEMA = calculateEMA(prices, slowPeriod);

  // Calculer MACD
  const macd = fastEMA.map((fast, i) => fast - slowEMA[i]);

  // Calculer la ligne de signal (EMA du MACD)
  const signal = calculateEMA(macd, signalPeriod);

  // Calculer l'histogramme
  const histogram = macd.map((value, i) => value - signal[i]);

  return { macd, signal, histogram };
}

export function calculateVolume(data: CandleData[]): number[] {
  return data.map(candle => candle.volume);
} 