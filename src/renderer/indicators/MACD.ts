import { Candle } from '../../data/types';

interface MACDOptions {
  fastPeriod: number;
  slowPeriod: number;
  signalPeriod: number;
}

interface MACDResult {
  macd: number[];
  signal: number[];
  histogram: number[];
}

export class MACDIndicator {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private options: MACDOptions;
  private rawData: Candle[] = [];

  constructor(
    canvas: HTMLCanvasElement,
    options: MACDOptions = { fastPeriod: 12, slowPeriod: 26, signalPeriod: 9 }
  ) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d')!;
    this.options = options;
  }

  private calculateEMA(prices: number[], period: number): number[] {
    const multiplier = 2 / (period + 1);
    const ema: number[] = [];
    
    // Initialiser avec la moyenne simple
    let sum = 0;
    for (let i = 0; i < period; i++) {
      sum += prices[i];
    }
    ema.push(sum / period);
    
    // Calculer l'EMA pour les périodes restantes
    for (let i = period; i < prices.length; i++) {
      const value = (prices[i] - ema[ema.length - 1]) * multiplier + ema[ema.length - 1];
      ema.push(value);
    }
    
    return ema;
  }

  calculate(candles: Candle[]): MACDResult {
    if (candles.length < this.options.slowPeriod) {
      return { macd: [], signal: [], histogram: [] };
    }

    const prices = candles.map(c => c.close);
    const fastEMA = this.calculateEMA(prices, this.options.fastPeriod);
    const slowEMA = this.calculateEMA(prices, this.options.slowPeriod);

    // Calculer la ligne MACD
    const macdLine: number[] = [];
    const startIndex = this.options.slowPeriod - 1;
    for (let i = 0; i < fastEMA.length; i++) {
      if (i >= startIndex) {
        macdLine.push(fastEMA[i] - slowEMA[i - (this.options.slowPeriod - this.options.fastPeriod)]);
      }
    }

    // Calculer la ligne de signal
    const signalLine = this.calculateEMA(macdLine, this.options.signalPeriod);

    // Calculer l'histogramme
    const histogram = macdLine.slice(this.options.signalPeriod - 1).map(
      (macd, i) => macd - signalLine[i]
    );

    return {
      macd: macdLine.slice(this.options.signalPeriod - 1),
      signal: signalLine,
      histogram
    };
  }

  draw(data: Candle[]) {
    this.rawData = data;
    const result = this.calculate(data);
    if (result.macd.length === 0) return;

    const { width, height } = this.canvas;
    const padding = { top: 10, right: 60, bottom: 20, left: 60 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;

    // Clear canvas
    this.ctx.clearRect(0, 0, width, height);

    // Draw background
    this.ctx.fillStyle = '#131722';
    this.ctx.fillRect(0, 0, width, height);

    // Trouver les valeurs min/max pour l'échelle
    const allValues = [...result.macd, ...result.signal, ...result.histogram];
    const minValue = Math.min(...allValues);
    const maxValue = Math.max(...allValues);
    const valueRange = maxValue - minValue;

    // Fonction pour convertir une valeur en coordonnée Y
    const toY = (value: number) => (
      chartHeight * (1 - (value - minValue) / valueRange) + padding.top
    );

    // Draw zero line
    this.ctx.strokeStyle = '#363A45';
    this.ctx.lineWidth = 1;
    const zeroY = toY(0);
    this.ctx.beginPath();
    this.ctx.moveTo(padding.left, zeroY);
    this.ctx.lineTo(width - padding.right, zeroY);
    this.ctx.stroke();

    // Draw histogram
    const barWidth = chartWidth / result.histogram.length;
    result.histogram.forEach((value, i) => {
      const x = padding.left + (i * barWidth);
      const y = toY(Math.max(0, value));
      const barHeight = Math.abs(toY(value) - toY(0));

      this.ctx.fillStyle = value >= 0 ? '#26A69A' : '#EF5350';
      this.ctx.fillRect(x, y, barWidth - 1, barHeight);
    });

    // Draw MACD line
    this.ctx.beginPath();
    this.ctx.strokeStyle = '#2962FF';
    this.ctx.lineWidth = 1.5;
    result.macd.forEach((value, i) => {
      const x = padding.left + (i * barWidth) + barWidth / 2;
      const y = toY(value);
      
      if (i === 0) {
        this.ctx.moveTo(x, y);
      } else {
        this.ctx.lineTo(x, y);
      }
    });
    this.ctx.stroke();

    // Draw signal line
    this.ctx.beginPath();
    this.ctx.strokeStyle = '#FF6B6B';
    this.ctx.lineWidth = 1.5;
    result.signal.forEach((value, i) => {
      const x = padding.left + (i * barWidth) + barWidth / 2;
      const y = toY(value);
      
      if (i === 0) {
        this.ctx.moveTo(x, y);
      } else {
        this.ctx.lineTo(x, y);
      }
    });
    this.ctx.stroke();

    // Draw labels
    this.ctx.fillStyle = '#787B86';
    this.ctx.font = '11px sans-serif';
    this.ctx.textAlign = 'right';
    
    // Min/Max labels
    this.ctx.fillText(maxValue.toFixed(2), padding.left - 5, padding.top + 15);
    this.ctx.fillText(minValue.toFixed(2), padding.left - 5, height - padding.bottom - 5);
    
    // Zero label
    this.ctx.fillText('0', padding.left - 5, zeroY + 4);
  }

  resize() {
    if (this.canvas.parentElement) {
      this.canvas.width = this.canvas.parentElement.clientWidth;
      this.canvas.height = this.canvas.parentElement.clientHeight;
      if (this.rawData.length > 0) {
        this.draw(this.rawData);
      }
    }
  }

  destroy() {
    // Cleanup if needed
  }
} 