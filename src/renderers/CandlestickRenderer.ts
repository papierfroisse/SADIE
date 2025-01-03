import { Candle } from '../data/types';

interface CandlestickRendererOptions {
  upColor: string;
  downColor: string;
  wickColor: string;
  borderUpColor: string;
  borderDownColor: string;
  showWicks: boolean;
  candleWidth: number;
  spacing: number;
}

const defaultOptions: CandlestickRendererOptions = {
  upColor: '#26A69A',
  downColor: '#EF5350',
  wickColor: '#787B86',
  borderUpColor: '#26A69A',
  borderDownColor: '#EF5350',
  showWicks: true,
  candleWidth: 8,
  spacing: 2
};

export class CandlestickRenderer {
  private ctx: CanvasRenderingContext2D;
  private data: Candle[] = [];
  private options: CandlestickRendererOptions;
  private width = 0;
  private height = 0;
  private scaleX = 1;
  private scaleY = 1;
  private offsetX = 0;
  private minPrice = 0;
  private maxPrice = 0;
  private priceRange = 0;

  constructor(ctx: CanvasRenderingContext2D, options: Partial<CandlestickRendererOptions> = {}) {
    this.ctx = ctx;
    this.options = { ...defaultOptions, ...options };
  }

  public setData(data: Candle[]) {
    this.data = data;
    this.calculateScales();
    this.render();
  }

  public resize(width: number, height: number) {
    this.width = width;
    this.height = height;
    this.calculateScales();
    this.render();
  }

  private calculateScales() {
    if (!this.data.length) return;

    // Calculer les prix min/max
    this.minPrice = Math.min(...this.data.map(d => d.low));
    this.maxPrice = Math.max(...this.data.map(d => d.high));
    this.priceRange = this.maxPrice - this.minPrice;

    // Ajouter une marge de 5% en haut et en bas
    const margin = this.priceRange * 0.05;
    this.minPrice -= margin;
    this.maxPrice += margin;
    this.priceRange = this.maxPrice - this.minPrice;

    // Calculer l'échelle X
    const totalWidth = (this.options.candleWidth + this.options.spacing) * this.data.length;
    this.scaleX = this.width / totalWidth;
    
    // Calculer l'échelle Y
    this.scaleY = this.height / this.priceRange;

    // Calculer le décalage X pour centrer les bougies
    this.offsetX = (this.width - totalWidth * this.scaleX) / 2;
  }

  private render() {
    if (!this.data.length) return;

    this.ctx.clearRect(0, 0, this.width, this.height);

    for (let i = 0; i < this.data.length; i++) {
      const candle = this.data[i];
      const x = this.offsetX + i * (this.options.candleWidth + this.options.spacing) * this.scaleX;
      
      // Convertir les prix en coordonnées Y
      const openY = this.height - (candle.open - this.minPrice) * this.scaleY;
      const closeY = this.height - (candle.close - this.minPrice) * this.scaleY;
      const highY = this.height - (candle.high - this.minPrice) * this.scaleY;
      const lowY = this.height - (candle.low - this.minPrice) * this.scaleY;

      const isUp = candle.close >= candle.open;
      const candleHeight = Math.abs(closeY - openY);

      // Dessiner la mèche
      if (this.options.showWicks) {
        this.ctx.beginPath();
        this.ctx.strokeStyle = this.options.wickColor;
        this.ctx.lineWidth = 1;
        this.ctx.moveTo(x + this.options.candleWidth * this.scaleX / 2, highY);
        this.ctx.lineTo(x + this.options.candleWidth * this.scaleX / 2, lowY);
        this.ctx.stroke();
      }

      // Dessiner le corps de la bougie
      this.ctx.fillStyle = isUp ? this.options.upColor : this.options.downColor;
      this.ctx.strokeStyle = isUp ? this.options.borderUpColor : this.options.borderDownColor;
      this.ctx.lineWidth = 1;

      const bodyY = Math.min(openY, closeY);
      this.ctx.fillRect(
        x,
        bodyY,
        this.options.candleWidth * this.scaleX,
        candleHeight
      );
      this.ctx.strokeRect(
        x,
        bodyY,
        this.options.candleWidth * this.scaleX,
        candleHeight
      );
    }
  }

  public dispose() {
    // Nettoyer les ressources si nécessaire
  }
} 