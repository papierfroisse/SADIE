import { BaseIndicator } from './BaseIndicator';
import { IndicatorConfig, IndicatorValue, Viewport } from './types';
import { Candle } from '../CandlestickRenderer';

export class ForceIndexIndicator extends BaseIndicator {
  constructor(id: string, period: number = 13) {
    super({
      id,
      type: 'fi',
      params: {
        period
      },
      style: {
        color: '#2962FF',
        lineWidth: 1.5,
        opacity: 1,
        fillColor: '#2962FF',
        fillOpacity: 0.1
      },
      visible: true,
      overlay: false,
      height: 100
    });
  }

  calculate(candles: Candle[]): IndicatorValue[] {
    const { period = 13 } = this.config.params;

    if (candles.length < period + 1) {
      return [];
    }

    // Calculer les valeurs brutes du Force Index
    const rawForce: number[] = [];
    for (let i = 1; i < candles.length; i++) {
      const priceDiff = candles[i].close - candles[i - 1].close;
      const force = priceDiff * candles[i].volume;
      rawForce.push(force);
    }

    // Calculer l'EMA du Force Index
    const values: IndicatorValue[] = [];
    const multiplier = 2 / (period + 1);

    // Calculer la première moyenne simple
    let sum = 0;
    for (let i = 0; i < period; i++) {
      sum += rawForce[i];
    }
    let ema = sum / period;

    // Ajouter la première valeur
    values.push({
      time: candles[period].time,
      value: ema,
      color: this.getForceColor(ema)
    });

    // Calculer les EMA suivantes
    for (let i = period; i < rawForce.length; i++) {
      ema = (rawForce[i] - ema) * multiplier + ema;
      values.push({
        time: candles[i + 1].time,
        value: ema,
        color: this.getForceColor(ema)
      });
    }

    return values;
  }

  private getForceColor(force: number): string {
    return force >= 0 ? '#26A69A' : '#EF5350';
  }

  render(ctx: CanvasRenderingContext2D, viewport: Viewport): void {
    if (!this.config.visible || this.values.length === 0) return;

    const { width, height } = ctx.canvas;
    const { xMin, xMax } = viewport;

    // Trouver les valeurs min/max pour l'échelle
    let minValue = Infinity;
    let maxValue = -Infinity;
    this.values.forEach(value => {
      minValue = Math.min(minValue, value.value);
      maxValue = Math.max(maxValue, value.value);
    });

    const range = maxValue - minValue;
    const padding = range * 0.1;
    const scale = height / (range + 2 * padding);
    const zero = height * (maxValue + padding) / (range + 2 * padding);

    // Dessiner la ligne zéro
    ctx.strokeStyle = '#363A45';
    ctx.lineWidth = 1;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(0, zero);
    ctx.lineTo(width, zero);
    ctx.stroke();
    ctx.setLineDash([]);

    // Dessiner les barres du Force Index
    const barWidth = Math.max(1, width / this.values.length * 0.8);
    this.values.forEach(value => {
      const x = ((value.time - xMin) / (xMax - xMin)) * width;
      const y = zero - value.value * scale;
      const barHeight = value.value * scale;

      ctx.fillStyle = value.color || this.config.style.color;
      ctx.fillRect(
        x - barWidth / 2,
        y,
        barWidth,
        Math.max(1, Math.abs(barHeight))
      );
    });

    // Dessiner les labels
    ctx.fillStyle = '#787B86';
    ctx.font = '12px Arial';
    ctx.textAlign = 'right';

    const formatValue = (value: number): string => {
      if (Math.abs(value) >= 1_000_000_000) {
        return `${(value / 1_000_000_000).toFixed(2)}B`;
      }
      if (Math.abs(value) >= 1_000_000) {
        return `${(value / 1_000_000).toFixed(2)}M`;
      }
      if (Math.abs(value) >= 1_000) {
        return `${(value / 1_000).toFixed(2)}K`;
      }
      return value.toFixed(2);
    };

    ctx.fillText(formatValue(maxValue), width - 5, 15);
    ctx.fillText('0', width - 5, zero + 5);
    ctx.fillText(formatValue(minValue), width - 5, height - 5);
  }

  onMouseMove(x: number, y: number): void {
    const value = this.getValueAtTime(x);
    if (value !== null) {
      // TODO: Afficher une info-bulle avec la valeur
      console.log(
        `Force Index(${this.config.params.period}):`,
        `\nValue: ${this.formatValue(value)}`
      );
    }
  }

  private formatValue(value: number): string {
    if (Math.abs(value) >= 1_000_000_000) {
      return `${(value / 1_000_000_000).toFixed(2)}B`;
    }
    if (Math.abs(value) >= 1_000_000) {
      return `${(value / 1_000_000).toFixed(2)}M`;
    }
    if (Math.abs(value) >= 1_000) {
      return `${(value / 1_000).toFixed(2)}K`;
    }
    return value.toFixed(2);
  }
} 