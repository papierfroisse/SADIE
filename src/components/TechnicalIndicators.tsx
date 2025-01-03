import React from 'react';
import { Candle } from '../data/types';

interface TechnicalIndicatorsProps {
  data: Candle[];
  width: number;
  height: number;
}

export function TechnicalIndicators({ data, width, height }: TechnicalIndicatorsProps) {
  const rsiCanvasRef = React.useRef<HTMLCanvasElement>(null);
  const macdCanvasRef = React.useRef<HTMLCanvasElement>(null);

  React.useEffect(() => {
    const rsiCanvas = rsiCanvasRef.current;
    const macdCanvas = macdCanvasRef.current;
    if (!rsiCanvas || !macdCanvas || !data.length) return;

    const rsiCtx = rsiCanvas.getContext('2d');
    const macdCtx = macdCanvas.getContext('2d');
    if (!rsiCtx || !macdCtx) return;

    // Configuration des canvas pour les écrans HiDPI
    const scale = window.devicePixelRatio;
    const rsiHeight = height * 0.4;
    const macdHeight = height * 0.6;

    // RSI Canvas
    rsiCanvas.width = width * scale;
    rsiCanvas.height = rsiHeight * scale;
    rsiCanvas.style.width = `${width}px`;
    rsiCanvas.style.height = `${rsiHeight}px`;
    rsiCtx.scale(scale, scale);

    // MACD Canvas
    macdCanvas.width = width * scale;
    macdCanvas.height = macdHeight * scale;
    macdCanvas.style.width = `${width}px`;
    macdCanvas.style.height = `${macdHeight}px`;
    macdCtx.scale(scale, scale);

    // Calcul des indicateurs
    const rsiValues = calculateRSI(data, 14);
    const macdValues = calculateMACD(data);

    // Dessiner les indicateurs
    drawRSI(rsiCtx, width, rsiHeight, rsiValues);
    drawMACD(macdCtx, width, macdHeight, macdValues);
  }, [data, width, height]);

  return (
    <div className="indicators-container">
      {/* RSI */}
      <div className="indicator">
        <div className="indicator-header">
          <span>RSI (14)</span>
          <div style={{ display: 'flex', gap: '8px' }}>
            <span>70</span>
            <span>30</span>
          </div>
        </div>
        <div className="indicator-content">
          <canvas
            ref={rsiCanvasRef}
            style={{
              width: '100%',
              height: '100%'
            }}
          />
        </div>
      </div>

      {/* MACD */}
      <div className="indicator">
        <div className="indicator-header">
          <span>MACD (12, 26, 9)</span>
          <div style={{ display: 'flex', gap: '8px' }}>
            <span style={{ color: '#2962FF' }}>MACD</span>
            <span style={{ color: '#FF9800' }}>Signal</span>
            <span style={{ color: '#26A69A' }}>Histogramme</span>
          </div>
        </div>
        <div className="indicator-content">
          <canvas
            ref={macdCanvasRef}
            style={{
              width: '100%',
              height: '100%'
            }}
          />
        </div>
      </div>
    </div>
  );
}

// Fonction pour calculer le RSI
function calculateRSI(data: Candle[], period: number): number[] {
  const rsi: number[] = [];
  let gains = 0;
  let losses = 0;

  // Initialisation
  for (let i = 1; i < period + 1; i++) {
    const change = data[i].close - data[i - 1].close;
    if (change >= 0) {
      gains += change;
    } else {
      losses -= change;
    }
  }

  // Première valeur RSI
  let avgGain = gains / period;
  let avgLoss = losses / period;
  let rs = avgGain / avgLoss;
  rsi.push(100 - (100 / (1 + rs)));

  // Calcul des valeurs suivantes
  for (let i = period + 1; i < data.length; i++) {
    const change = data[i].close - data[i - 1].close;
    let currentGain = 0;
    let currentLoss = 0;

    if (change >= 0) {
      currentGain = change;
    } else {
      currentLoss = -change;
    }

    avgGain = ((avgGain * (period - 1)) + currentGain) / period;
    avgLoss = ((avgLoss * (period - 1)) + currentLoss) / period;

    rs = avgGain / avgLoss;
    rsi.push(100 - (100 / (1 + rs)));
  }

  return rsi;
}

// Fonction pour calculer le MACD
function calculateMACD(data: Candle[]): { macd: number[], signal: number[], histogram: number[] } {
  const closePrices = data.map(candle => candle.close);
  const ema12 = calculateEMA(closePrices, 12);
  const ema26 = calculateEMA(closePrices, 26);
  
  const macd = ema12.map((value, index) => value - ema26[index]);
  const signal = calculateEMA(macd, 9);
  const histogram = macd.map((value, index) => value - signal[index]);

  return { macd, signal, histogram };
}

// Fonction pour calculer l'EMA
function calculateEMA(data: number[], period: number): number[] {
  const k = 2 / (period + 1);
  const ema: number[] = [data[0]];

  for (let i = 1; i < data.length; i++) {
    ema.push(data[i] * k + ema[i - 1] * (1 - k));
  }

  return ema;
}

// Fonction pour dessiner le RSI
function drawRSI(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  rsiValues: number[]
) {
  // Effacer le canvas
  ctx.clearRect(0, 0, width, height);

  // Dessiner les lignes de niveau
  ctx.strokeStyle = '#2A2E39';
  ctx.setLineDash([5, 5]);
  
  // Ligne 70
  ctx.beginPath();
  ctx.moveTo(0, (30 / 100) * height);
  ctx.lineTo(width, (30 / 100) * height);
  ctx.stroke();
  
  // Ligne 30
  ctx.beginPath();
  ctx.moveTo(0, (70 / 100) * height);
  ctx.lineTo(width, (70 / 100) * height);
  ctx.stroke();
  
  ctx.setLineDash([]);

  // Dessiner le RSI
  ctx.strokeStyle = '#2962FF';
  ctx.lineWidth = 1;
  ctx.beginPath();
  
  for (let i = 0; i < rsiValues.length; i++) {
    const x = (i / rsiValues.length) * width;
    const y = ((100 - rsiValues[i]) / 100) * height;
    
    if (i === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  }
  
  ctx.stroke();
}

// Fonction pour dessiner le MACD
function drawMACD(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  macdValues: { macd: number[], signal: number[], histogram: number[] }
) {
  // Effacer le canvas
  ctx.clearRect(0, 0, width, height);
  
  // Trouver les valeurs min/max pour l'échelle
  const allValues = [
    ...macdValues.macd,
    ...macdValues.signal,
    ...macdValues.histogram
  ];
  const min = Math.min(...allValues);
  const max = Math.max(...allValues);
  const range = max - min;

  // Fonction pour convertir une valeur en coordonnée y
  const getY = (value: number) => {
    return ((max - value) / range) * height;
  };

  // Dessiner l'histogramme
  const barWidth = width / macdValues.histogram.length;
  
  for (let i = 0; i < macdValues.histogram.length; i++) {
    const value = macdValues.histogram[i];
    const x = i * barWidth;
    const y = getY(Math.max(0, value));
    const barHeight = Math.abs(getY(value) - getY(0));
    
    ctx.fillStyle = value >= 0 ? '#26A69A' : '#EF5350';
    ctx.fillRect(x, y, barWidth - 1, barHeight);
  }

  // Dessiner la ligne MACD
  ctx.strokeStyle = '#2962FF';
  ctx.beginPath();
  
  for (let i = 0; i < macdValues.macd.length; i++) {
    const x = i * barWidth + barWidth / 2;
    const y = getY(macdValues.macd[i]);
    
    if (i === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  }
  
  ctx.stroke();

  // Dessiner la ligne de signal
  ctx.strokeStyle = '#FF9800';
  ctx.beginPath();
  
  for (let i = 0; i < macdValues.signal.length; i++) {
    const x = i * barWidth + barWidth / 2;
    const y = getY(macdValues.signal[i]);
    
    if (i === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  }
  
  ctx.stroke();
} 