import { Candle } from '../../data/types';

interface VolumeOptions {
  movingAveragePeriod: number;
}

export class VolumeIndicator {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private options: VolumeOptions;
  private rawData: Candle[] = [];

  constructor(
    canvas: HTMLCanvasElement,
    options: VolumeOptions = { movingAveragePeriod: 20 }
  ) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d')!;
    this.options = options;
  }

  private calculateSMA(values: number[], period: number): number[] {
    const sma: number[] = [];
    let sum = 0;
    
    // Calculer la première moyenne
    for (let i = 0; i < period; i++) {
      sum += values[i];
      if (i === period - 1) {
        sma.push(sum / period);
      }
    }
    
    // Calculer les moyennes suivantes
    for (let i = period; i < values.length; i++) {
      sum = sum - values[i - period] + values[i];
      sma.push(sum / period);
    }
    
    return sma;
  }

  draw(data: Candle[]) {
    this.rawData = data;
    if (data.length === 0) return;

    const { width, height } = this.canvas;
    const padding = { top: 10, right: 60, bottom: 20, left: 60 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;

    // Clear canvas
    this.ctx.clearRect(0, 0, width, height);

    // Draw background
    this.ctx.fillStyle = '#131722';
    this.ctx.fillRect(0, 0, width, height);

    // Calculer la moyenne mobile
    const volumes = data.map(c => c.volume);
    const sma = this.calculateSMA(volumes, this.options.movingAveragePeriod);

    // Trouver le volume maximum pour l'échelle
    const maxVolume = Math.max(...volumes);
    const scale = chartHeight / maxVolume;

    // Dessiner les volumes
    const barWidth = chartWidth / data.length;
    data.forEach((candle, i) => {
      const x = padding.left + (i * barWidth);
      const barHeight = candle.volume * scale;
      const y = height - padding.bottom - barHeight;

      // Couleur basée sur la direction du prix
      this.ctx.fillStyle = candle.close >= candle.open 
        ? 'rgba(38, 166, 154, 0.3)'  // Vert transparent
        : 'rgba(239, 83, 80, 0.3)';  // Rouge transparent

      this.ctx.fillRect(x, y, barWidth - 1, barHeight);
    });

    // Dessiner la moyenne mobile
    this.ctx.beginPath();
    this.ctx.strokeStyle = '#2962FF';
    this.ctx.lineWidth = 1.5;

    const offset = this.options.movingAveragePeriod - 1;
    sma.forEach((value, i) => {
      const x = padding.left + ((i + offset) * barWidth) + barWidth / 2;
      const y = height - padding.bottom - (value * scale);
      
      if (i === 0) {
        this.ctx.moveTo(x, y);
      } else {
        this.ctx.lineTo(x, y);
      }
    });
    this.ctx.stroke();

    // Draw volume labels
    this.ctx.fillStyle = '#787B86';
    this.ctx.font = '11px sans-serif';
    this.ctx.textAlign = 'right';

    const volumeLevels = [maxVolume, maxVolume / 2, 0];
    volumeLevels.forEach(level => {
      const y = height - padding.bottom - (level * scale);
      this.ctx.fillText(
        level.toLocaleString(undefined, { maximumFractionDigits: 0 }),
        padding.left - 5,
        y + 4
      );
    });
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