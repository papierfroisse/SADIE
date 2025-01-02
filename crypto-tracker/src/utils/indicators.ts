import { CandleData } from '../types/chart';

export const calculateSMA = (data: CandleData[], period: number): number[] => {
  const sma: number[] = [];
  for (let i = period - 1; i < data.length; i++) {
    const sum = data.slice(i - period + 1, i + 1).reduce((acc, candle) => acc + candle.close, 0);
    sma.push(sum / period);
  }
  return sma;
};

export const calculateBollingerBands = (data: CandleData[], period: number = 20, multiplier: number = 2): {
  upper: number[];
  middle: number[];
  lower: number[];
} => {
  const sma = calculateSMA(data, period);
  const upper: number[] = [];
  const lower: number[] = [];

  for (let i = period - 1; i < data.length; i++) {
    const slice = data.slice(i - period + 1, i + 1);
    const mean = sma[i - (period - 1)];
    const squaredDiffs = slice.map(candle => Math.pow(candle.close - mean, 2));
    const standardDeviation = Math.sqrt(squaredDiffs.reduce((acc, val) => acc + val, 0) / period);
    
    upper.push(mean + multiplier * standardDeviation);
    lower.push(mean - multiplier * standardDeviation);
  }

  return { upper, middle: sma, lower };
}; 