// Calcul de la Moyenne Mobile Simple (SMA)
export function calculateSMA(prices: number[], period: number): number[] {
  const sma: number[] = [];
  
  for (let i = 0; i < prices.length; i++) {
    if (i < period - 1) {
      sma.push(NaN);
      continue;
    }
    
    let sum = 0;
    for (let j = 0; j < period; j++) {
      sum += prices[i - j];
    }
    sma.push(sum / period);
  }
  
  return sma;
}

// Calcul de la Moyenne Mobile Exponentielle (EMA)
export function calculateEMA(data: number[], period: number): number[] {
  const ema: number[] = [];
  const multiplier = 2 / (period + 1);
  
  // Première valeur EMA est la même que SMA
  let initialSMA = 0;
  for (let i = 0; i < period; i++) {
    initialSMA += data[i];
  }
  initialSMA /= period;
  
  ema.push(initialSMA);
  
  for (let i = 1; i < data.length; i++) {
    if (i < period - 1) {
      ema.push(NaN);
      continue;
    }
    const currentEMA = (data[i] - ema[i - 1]) * multiplier + ema[i - 1];
    ema.push(currentEMA);
  }
  
  return ema;
}

// Calcul du RSI (Relative Strength Index)
export function calculateRSI(data: number[], period: number = 14): number[] {
  const rsi: number[] = [];
  const gains: number[] = [];
  const losses: number[] = [];
  
  // Calculer les gains et pertes
  for (let i = 1; i < data.length; i++) {
    const difference = data[i] - data[i - 1];
    gains.push(Math.max(difference, 0));
    losses.push(Math.max(-difference, 0));
  }
  
  // Calculer les moyennes initiales
  let avgGain = gains.slice(0, period).reduce((a, b) => a + b, 0) / period;
  let avgLoss = losses.slice(0, period).reduce((a, b) => a + b, 0) / period;
  
  // Première valeur RSI
  rsi.push(100 - (100 / (1 + avgGain / avgLoss)));
  
  // Calculer le reste des valeurs RSI
  for (let i = period; i < data.length - 1; i++) {
    avgGain = (avgGain * (period - 1) + gains[i]) / period;
    avgLoss = (avgLoss * (period - 1) + losses[i]) / period;
    
    if (avgLoss === 0) {
      rsi.push(100);
    } else {
      rsi.push(100 - (100 / (1 + avgGain / avgLoss)));
    }
  }
  
  // Ajouter NaN pour les premières périodes
  return Array(period).fill(NaN).concat(rsi);
}

// Calcul des Bandes de Bollinger
export function calculateBollingerBands(prices: number[], period: number = 20, multiplier: number = 2): {
  upper: number[];
  middle: number[];
  lower: number[];
} {
  const sma = calculateSMA(prices, period);
  const upper: number[] = [];
  const lower: number[] = [];
  
  for (let i = 0; i < prices.length; i++) {
    if (i < period - 1) {
      upper.push(NaN);
      lower.push(NaN);
      continue;
    }
    
    let sumSquaredDiff = 0;
    for (let j = 0; j < period; j++) {
      sumSquaredDiff += Math.pow(prices[i - j] - sma[i], 2);
    }
    
    const standardDeviation = Math.sqrt(sumSquaredDiff / period);
    upper.push(sma[i] + multiplier * standardDeviation);
    lower.push(sma[i] - multiplier * standardDeviation);
  }
  
  return {
    upper,
    middle: sma,
    lower
  };
}

// Calcul du MACD (Moving Average Convergence Divergence)
export function calculateMACD(data: number[], fastPeriod: number = 12, slowPeriod: number = 26, signalPeriod: number = 9): {
  macd: number[];
  signal: number[];
  histogram: number[];
} {
  const fastEMA = calculateEMA(data, fastPeriod);
  const slowEMA = calculateEMA(data, slowPeriod);
  
  // Calculer la ligne MACD
  const macd = fastEMA.map((fast, i) => fast - slowEMA[i]);
  
  // Calculer la ligne de signal
  const signal = calculateEMA(macd, signalPeriod);
  
  // Calculer l'histogramme
  const histogram = macd.map((value, i) => value - signal[i]);
  
  return { macd, signal, histogram };
} 