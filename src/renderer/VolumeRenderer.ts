import { CandleData } from '../data/types';

export class VolumeRenderer {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private data: CandleData[] = [];
  private width: number;
  private height: number;
  private startIndex: number = 0;
  private visibleCount: number = 100;
  private maxVolume: number = 0;

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas;
    const ctx = canvas.getContext('2d');
    if (!ctx) throw new Error('Could not get canvas context');
    this.ctx = ctx;
    
    this.width = canvas.width;
    this.height = canvas.height;
  }

  public setData(data: CandleData[], startIndex: number, visibleCount: number): void {
    this.data = data;
    this.startIndex = startIndex;
    this.visibleCount = visibleCount;
    this.updateMaxVolume();
    this.render();
  }

  public resize(width: number, height: number): void {
    this.width = width;
    this.height = height;
    this.canvas.width = width;
    this.canvas.height = height;
    this.render();
  }

  private updateMaxVolume(): void {
    const visibleData = this.data.slice(
      this.startIndex,
      this.startIndex + this.visibleCount
    );
    this.maxVolume = Math.max(...visibleData.map(d => d.volume));
  }

  private formatVolume(volume: number): string {
    if (volume >= 1_000_000_000) {
      return `${(volume / 1_000_000_000).toFixed(2)}B`;
    }
    if (volume >= 1_000_000) {
      return `${(volume / 1_000_000).toFixed(2)}M`;
    }
    if (volume >= 1_000) {
      return `${(volume / 1_000).toFixed(2)}K`;
    }
    return volume.toString();
  }

  public render(): void {
    if (this.data.length === 0) return;

    this.ctx.clearRect(0, 0, this.width, this.height);

    // Grille et axe Y
    this.renderGrid();

    const visibleData = this.data.slice(
      this.startIndex,
      this.startIndex + this.visibleCount
    );

    const barWidth = (this.width - 60) / this.visibleCount;

    visibleData.forEach((candle, i) => {
      const x = i * barWidth;
      const height = (candle.volume / this.maxVolume) * (this.height - 20);
      const y = this.height - height;

      // Couleur selon la direction
      const isUp = candle.close >= candle.open;
      this.ctx.fillStyle = isUp ? 'rgba(38, 166, 154, 0.5)' : 'rgba(239, 83, 80, 0.5)';
      
      this.ctx.fillRect(x, y, Math.max(barWidth * 0.8, 1), height);
    });

    // Axe des volumes à droite
    this.ctx.fillStyle = '#787B86';
    this.ctx.font = '10px sans-serif';
    this.ctx.textAlign = 'right';
    this.ctx.textBaseline = 'middle';

    const volumeLevels = [
      this.maxVolume,
      this.maxVolume * 0.75,
      this.maxVolume * 0.5,
      this.maxVolume * 0.25,
      0
    ];

    volumeLevels.forEach(volume => {
      const y = this.height - (volume / this.maxVolume) * (this.height - 20);
      this.ctx.fillText(this.formatVolume(volume), this.width - 5, y);
    });
  }

  private renderGrid(): void {
    this.ctx.strokeStyle = '#363A45';
    this.ctx.lineWidth = 1;

    // Lignes horizontales
    const steps = 4;
    for (let i = 0; i <= steps; i++) {
      const y = (this.height - 20) * (i / steps);
      
      this.ctx.beginPath();
      this.ctx.moveTo(0, y);
      this.ctx.lineTo(this.width - 60, y);
      this.ctx.stroke();
    }
  }
} 