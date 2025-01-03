import { Candle } from '../../data/types';

interface RSIOptions {
  period: number;
  overbought: number;
  oversold: number;
}

export class RSIIndicator {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private options: RSIOptions;
  private data: number[] = [];

  constructor(canvas: HTMLCanvasElement, options: RSIOptions = { period: 14, overbought: 70, oversold: 30 }) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d')!;
    this.options = options;
  }

  calculate(candles: Candle[]): number[] {
    if (candles.length < this.options.period + 1) {
      return [];
    }

    const changes = candles.map((candle, i) => {
      if (i === 0) return 0;
      return candle.close - candles[i - 1].close;
    }).slice(1);

    let gains = changes.map(change => change > 0 ? change : 0);
    let losses = changes.map(change => change < 0 ? -change : 0);

    // Calcul des moyennes initiales
    let avgGain = gains.slice(0, this.options.period).reduce((a, b) => a + b) / this.options.period;
    let avgLoss = losses.slice(0, this.options.period).reduce((a, b) => a + b) / this.options.period;

    const rsiValues: number[] = [];
    rsiValues.push(100 - (100 / (1 + avgGain / avgLoss)));

    // Calcul du RSI pour les périodes restantes
    for (let i = this.options.period + 1; i < changes.length; i++) {
      avgGain = ((avgGain * (this.options.period - 1)) + (gains[i] || 0)) / this.options.period;
      avgLoss = ((avgLoss * (this.options.period - 1)) + (losses[i] || 0)) / this.options.period;
      
      if (avgLoss === 0) {
        rsiValues.push(100);
      } else {
        rsiValues.push(100 - (100 / (1 + avgGain / avgLoss)));
      }
    }

    return rsiValues;
  }

  draw(data: Candle[]) {
    const rsiValues = this.calculate(data);
    if (rsiValues.length === 0) return;

    const { width, height } = this.canvas;
    const padding = { top: 10, right: 60, bottom: 20, left: 60 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;

    // Clear canvas
    this.ctx.clearRect(0, 0, width, height);

    // Draw background
    this.ctx.fillStyle = '#131722';
    this.ctx.fillRect(0, 0, width, height);

    // Draw overbought/oversold zones
    this.ctx.fillStyle = 'rgba(76, 175, 80, 0.1)';
    const oversoldY = chartHeight * (100 - this.options.oversold) / 100 + padding.top;
    this.ctx.fillRect(padding.left, oversoldY, chartWidth, chartHeight - oversoldY + padding.top);

    this.ctx.fillStyle = 'rgba(244, 67, 54, 0.1)';
    const overboughtY = chartHeight * (100 - this.options.overbought) / 100 + padding.top;
    this.ctx.fillRect(padding.left, padding.top, chartWidth, overboughtY - padding.top);

    // Draw RSI line
    this.ctx.beginPath();
    this.ctx.strokeStyle = '#2962FF';
    this.ctx.lineWidth = 1.5;

    const step = chartWidth / (rsiValues.length - 1);
    rsiValues.forEach((value, i) => {
      const x = padding.left + (i * step);
      const y = chartHeight * (100 - value) / 100 + padding.top;
      
      if (i === 0) {
        this.ctx.moveTo(x, y);
      } else {
        this.ctx.lineTo(x, y);
      }
    });

    this.ctx.stroke();

    // Draw levels
    this.ctx.strokeStyle = '#363A45';
    this.ctx.lineWidth = 1;
    [0, 20, 50, 80, 100].forEach(level => {
      const y = chartHeight * (100 - level) / 100 + padding.top;
      this.ctx.beginPath();
      this.ctx.moveTo(padding.left, y);
      this.ctx.lineTo(width - padding.right, y);
      this.ctx.stroke();

      // Draw level labels
      this.ctx.fillStyle = '#787B86';
      this.ctx.font = '11px sans-serif';
      this.ctx.textAlign = 'right';
      this.ctx.fillText(level.toString(), padding.left - 5, y + 4);
    });
  }

  resize() {
    if (this.canvas.parentElement) {
      this.canvas.width = this.canvas.parentElement.clientWidth;
      this.canvas.height = this.canvas.parentElement.clientHeight;
      if (this.data.length > 0) {
        // TODO: Stocker les données brutes pour le redimensionnement
        // this.draw(this.data);
      }
    }
  }

  destroy() {
    // Cleanup if needed
  }
} 