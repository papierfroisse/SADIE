import { CandleData } from '../types/chart';

export interface IndicatorValue {
  timestamp: number;
  value: number;
}

export interface BollingerBands {
  upper: IndicatorValue[];
  middle: IndicatorValue[];
  lower: IndicatorValue[];
}

/**
 * Calcule la Moyenne Mobile Simple (SMA)
 */
export const calculateSMA = (data: CandleData[], period: number): IndicatorValue[] => {
  const sma: IndicatorValue[] = [];
  
  for (let i = period - 1; i < data.length; i++) {
    const slice = data.slice(i - period + 1, i + 1);
    const sum = slice.reduce((acc, candle) => acc + candle.close, 0);
    sma.push({
      timestamp: data[i].timestamp,
      value: sum / period
    });
  }
  
  return sma;
};

/**
 * Calcule la Moyenne Mobile Exponentielle (EMA)
 */
export const calculateEMA = (data: CandleData[], period: number): IndicatorValue[] => {
  const ema: IndicatorValue[] = [];
  const multiplier = 2 / (period + 1);

  // Première valeur = SMA
  const firstSlice = data.slice(0, period);
  const firstSum = firstSlice.reduce((acc, candle) => acc + candle.close, 0);
  let prevEMA = firstSum / period;

  ema.push({
    timestamp: data[period - 1].timestamp,
    value: prevEMA
  });

  // Calcul EMA pour les valeurs suivantes
  for (let i = period; i < data.length; i++) {
    const currentClose = data[i].close;
    const currentEMA = (currentClose - prevEMA) * multiplier + prevEMA;
    
    ema.push({
      timestamp: data[i].timestamp,
      value: currentEMA
    });
    
    prevEMA = currentEMA;
  }

  return ema;
};

/**
 * Calcule l'Indice de Force Relative (RSI)
 */
export const calculateRSI = (data: CandleData[], period: number = 14): IndicatorValue[] => {
  const rsi: IndicatorValue[] = [];
  const changes: { gain: number; loss: number }[] = [];

  // Calculer les variations
  for (let i = 1; i < data.length; i++) {
    const change = data[i].close - data[i - 1].close;
    changes.push({
      gain: change > 0 ? change : 0,
      loss: change < 0 ? -change : 0
    });
  }

  // Première moyenne
  let avgGain = changes.slice(0, period).reduce((sum, curr) => sum + curr.gain, 0) / period;
  let avgLoss = changes.slice(0, period).reduce((sum, curr) => sum + curr.loss, 0) / period;

  // Première valeur RSI
  rsi.push({
    timestamp: data[period].timestamp,
    value: 100 - (100 / (1 + avgGain / avgLoss))
  });

  // Calcul RSI pour les valeurs suivantes
  for (let i = period; i < changes.length; i++) {
    avgGain = ((avgGain * (period - 1)) + changes[i].gain) / period;
    avgLoss = ((avgLoss * (period - 1)) + changes[i].loss) / period;

    rsi.push({
      timestamp: data[i + 1].timestamp,
      value: 100 - (100 / (1 + avgGain / avgLoss))
    });
  }

  return rsi;
};

/**
 * Calcule les Bandes de Bollinger
 */
export const calculateBollingerBands = (
  data: CandleData[],
  period: number = 20,
  stdDev: number = 2
): BollingerBands => {
  const sma = calculateSMA(data, period);
  const upper: IndicatorValue[] = [];
  const lower: IndicatorValue[] = [];

  for (let i = period - 1; i < data.length; i++) {
    const slice = data.slice(i - period + 1, i + 1);
    const mean = sma[i - (period - 1)].value;
    
    // Calcul de l'écart-type
    const squaredDiffs = slice.map(candle => Math.pow(candle.close - mean, 2));
    const variance = squaredDiffs.reduce((acc, val) => acc + val, 0) / period;
    const standardDeviation = Math.sqrt(variance);

    upper.push({
      timestamp: data[i].timestamp,
      value: mean + (standardDeviation * stdDev)
    });

    lower.push({
      timestamp: data[i].timestamp,
      value: mean - (standardDeviation * stdDev)
    });
  }

  return { upper, middle: sma, lower };
};

/**
 * Calcule le MACD (Moving Average Convergence Divergence)
 */
export const calculateMACD = (
  data: CandleData[],
  fastPeriod: number = 12,
  slowPeriod: number = 26,
  signalPeriod: number = 9
): {
  macd: IndicatorValue[];
  signal: IndicatorValue[];
  histogram: IndicatorValue[];
} => {
  const fastEMA = calculateEMA(data, fastPeriod);
  const slowEMA = calculateEMA(data, slowPeriod);
  
  // Calculer la ligne MACD (Fast EMA - Slow EMA)
  const macdLine: IndicatorValue[] = [];
  for (let i = slowPeriod - 1; i < data.length; i++) {
    const fastIndex = i - (slowPeriod - fastPeriod);
    if (fastIndex >= 0) {
      macdLine.push({
        timestamp: data[i].timestamp,
        value: fastEMA[fastIndex].value - slowEMA[i - (slowPeriod - 1)].value
      });
    }
  }

  // Calculer la ligne de signal (EMA du MACD)
  const signalLine: IndicatorValue[] = [];
  const multiplier = 2 / (signalPeriod + 1);
  
  // Première valeur = SMA du MACD
  const firstSlice = macdLine.slice(0, signalPeriod);
  let prevSignal = firstSlice.reduce((sum, curr) => sum + curr.value, 0) / signalPeriod;
  
  signalLine.push({
    timestamp: macdLine[signalPeriod - 1].timestamp,
    value: prevSignal
  });

  // Calcul des valeurs suivantes
  for (let i = signalPeriod; i < macdLine.length; i++) {
    const currentMACD = macdLine[i].value;
    const currentSignal = (currentMACD - prevSignal) * multiplier + prevSignal;
    
    signalLine.push({
      timestamp: macdLine[i].timestamp,
      value: currentSignal
    });
    
    prevSignal = currentSignal;
  }

  // Calculer l'histogramme (MACD - Signal)
  const histogram = macdLine.slice(signalPeriod - 1).map((macd, i) => ({
    timestamp: macd.timestamp,
    value: macd.value - signalLine[i].value
  }));

  return {
    macd: macdLine,
    signal: signalLine,
    histogram
  };
}; 