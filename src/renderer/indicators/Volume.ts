import { BaseIndicator } from './BaseIndicator';
import { IndicatorConfig, IndicatorValue, Viewport } from './types';
import { Candle } from '../CandlestickRenderer';

export class VolumeIndicator extends BaseIndicator {
  constructor(id: string) {
    super({
      id,
      type: 'volume',
      params: {},
      style: {
        color: '#787B86',
        lineWidth: 1,
        opacity: 0.8
      },
      visible: true,
      overlay: false,
      height: 100
    });
  }

  calculate(candles: Candle[]): IndicatorValue[] {
    return candles.map(candle => ({
      time: candle.time,
      value: candle.volume,
      color: candle.close >= candle.open ? '#26A69A' : '#EF5350'
    }));
  }

  render(ctx: CanvasRenderingContext2D, viewport: Viewport): void {
    if (!this.config.visible || this.values.length === 0) return;

    const { width, height } = ctx.canvas;
    const { xMin, xMax } = viewport;

    // Trouver le volume maximum pour l'échelle
    const maxVolume = Math.max(...this.values.map(v => v.value));
    const scale = height / maxVolume;

    // Calculer la largeur des barres
    const barWidth = Math.max(1, width / this.values.length * 0.8);
    const barGap = barWidth * 0.2;

    // Dessiner les barres de volume
    this.values.forEach(value => {
      const x = ((value.time - xMin) / (xMax - xMin)) * width;
      const barHeight = value.value * scale;

      ctx.fillStyle = value.color || this.config.style.color;
      ctx.globalAlpha = this.config.style.opacity;

      ctx.fillRect(
        x - barWidth / 2,
        height - barHeight,
        barWidth,
        barHeight
      );
    });

    // Dessiner l'échelle des volumes
    ctx.fillStyle = '#787B86';
    ctx.font = '12px Arial';
    ctx.textAlign = 'right';

    const volumeLevels = [
      maxVolume,
      maxVolume * 0.75,
      maxVolume * 0.5,
      maxVolume * 0.25
    ];

    volumeLevels.forEach(volume => {
      const y = height - (volume * scale);
      ctx.fillText(this.formatVolume(volume), width - 10, y);
    });

    // Réinitialiser l'opacité
    ctx.globalAlpha = 1;
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
    return volume.toFixed(2);
  }

  // Surcharger la méthode onMouseMove pour afficher le volume au survol
  onMouseMove(x: number, y: number): void {
    const value = this.getValueAtTime(x);
    if (value !== null) {
      // TODO: Afficher une info-bulle avec le volume
      console.log(`Volume: ${this.formatVolume(value)}`);
    }
  }
} 