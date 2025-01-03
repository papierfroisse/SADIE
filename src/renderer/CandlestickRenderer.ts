import { Candle } from '../data/types';

export class CandlestickRenderer {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private data: Candle[] = [];
  private priceRange: { min: number; max: number } = { min: 0, max: 0 };
  private timeRange: { start: number; end: number } = { start: 0, end: 0 };

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d')!;
  }

  draw(data: Candle[]) {
    this.data = data;
    this.calculateRanges();
    this.render();
  }

  private calculateRanges() {
    if (this.data.length === 0) return;

    const prices = this.data.flatMap(c => [c.high, c.low]);
    const times = this.data.map(c => c.timestamp);

    this.priceRange = {
      min: Math.min(...prices),
      max: Math.max(...prices)
    };

    this.timeRange = {
      start: Math.min(...times),
      end: Math.max(...times)
    };
  }

  private render() {
    if (!this.ctx || this.data.length === 0) return;

    const { width, height } = this.canvas;
    const padding = { top: 10, right: 60, bottom: 20, left: 60 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;

    // Clear canvas
    this.ctx.clearRect(0, 0, width, height);

    // Calculate scaling factors
    const priceRange = this.priceRange.max - this.priceRange.min;
    const timeRange = this.timeRange.end - this.timeRange.start;
    const candleWidth = chartWidth / this.data.length;

    // Draw candles
    this.data.forEach((candle, i) => {
      const x = padding.left + (i * candleWidth);
      const open = chartHeight - ((candle.open - this.priceRange.min) / priceRange * chartHeight) + padding.top;
      const close = chartHeight - ((candle.close - this.priceRange.min) / priceRange * chartHeight) + padding.top;
      const high = chartHeight - ((candle.high - this.priceRange.min) / priceRange * chartHeight) + padding.top;
      const low = chartHeight - ((candle.low - this.priceRange.min) / priceRange * chartHeight) + padding.top;

      // Draw wick
      this.ctx.beginPath();
      this.ctx.moveTo(x + candleWidth / 2, high);
      this.ctx.lineTo(x + candleWidth / 2, low);
      this.ctx.strokeStyle = candle.close >= candle.open ? '#26A69A' : '#EF5350';
      this.ctx.stroke();

      // Draw body
      this.ctx.fillStyle = candle.close >= candle.open ? '#26A69A' : '#EF5350';
      this.ctx.fillRect(
        x,
        Math.min(open, close),
        candleWidth,
        Math.abs(close - open)
      );
    });
  }

  resize() {
    if (this.canvas.parentElement) {
      this.canvas.width = this.canvas.parentElement.clientWidth;
      this.canvas.height = this.canvas.parentElement.clientHeight;
      this.render();
    }
  }

  destroy() {
    // Cleanup if needed
  }
} 