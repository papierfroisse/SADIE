import { Candle } from '../data/types';

export interface CandlestickRendererOptions {
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
  private options: CandlestickRendererOptions;
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

  private calculateScales(data: Candle[]) {
    if (!data.length) return;

    // Calculer les prix min/max
    this.minPrice = Math.min(...data.map(d => d.low));
    this.maxPrice = Math.max(...data.map(d => d.high));
    this.priceRange = this.maxPrice - this.minPrice;

    // Ajouter une marge de 5%
    const margin = this.priceRange * 0.05;
    this.minPrice -= margin;
    this.maxPrice += margin;
    this.priceRange = this.maxPrice - this.minPrice;

    // Calculer l'échelle X
    const { width } = this.ctx.canvas;
    const totalWidth = (this.options.candleWidth + this.options.spacing) * data.length;
    this.scaleX = width / totalWidth;
    
    // Calculer le décalage X pour centrer les bougies
    this.offsetX = (width - totalWidth * this.scaleX) / 2;
  }

  public draw(data: Candle[]) {
    if (!data.length) return;

    this.calculateScales(data);

    const { width, height } = this.ctx.canvas;

    for (let i = 0; i < data.length; i++) {
      const candle = data[i];
      const x = this.offsetX + i * (this.options.candleWidth + this.options.spacing) * this.scaleX;
      
      // Convertir les prix en coordonnées Y
      const openY = height - ((candle.open - this.minPrice) / this.priceRange) * height;
      const closeY = height - ((candle.close - this.minPrice) / this.priceRange) * height;
      const highY = height - ((candle.high - this.minPrice) / this.priceRange) * height;
      const lowY = height - ((candle.low - this.minPrice) / this.priceRange) * height;

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