import { BaseIndicator } from './BaseIndicator';
import { IndicatorConfig, IndicatorValue, Viewport } from './types';
import { Candle } from '../CandlestickRenderer';

type PriceSource = 'open' | 'high' | 'low' | 'close';

const isPriceSource = (source: string): source is PriceSource => {
  return ['open', 'high', 'low', 'close'].includes(source);
};

export class MACDIndicator extends BaseIndicator {
  constructor(
    id: string,
    fastPeriod: number = 12,
    slowPeriod: number = 26,
    signalPeriod: number = 9
  ) {
    super({
      id,
      type: 'macd',
      params: {
        fastPeriod,
        slowPeriod,
        signalPeriod,
        source: 'close' as PriceSource
      },
      style: {
        color: '#2962FF',      // Ligne MACD
        lineWidth: 1.5,
        opacity: 1,
        fillColor: '#787B86'   // Histogramme
      },
      visible: true,
      overlay: false,
      height: 150
    });
  }

  calculate(candles: Candle[]): IndicatorValue[] {
    const {
      fastPeriod = 12,
      slowPeriod = 26,
      signalPeriod = 9,
      source = 'close'
    } = this.config.params;

    if (candles.length < Math.max(fastPeriod, slowPeriod) + signalPeriod) {
      return [];
    }

    // Vérifier que la source est valide
    if (!isPriceSource(source)) {
      console.error(`Invalid price source: ${source}`);
      return [];
    }

    // Calculer les EMA
    const fastEMA = this.calculateEMA(candles, fastPeriod, source);
    const slowEMA = this.calculateEMA(candles, slowPeriod, source);

    // Calculer la ligne MACD
    const macdLine: number[] = [];
    const maxLength = Math.max(fastEMA.length, slowEMA.length);
    for (let i = 0; i < maxLength; i++) {
      if (fastEMA[i] !== undefined && slowEMA[i] !== undefined) {
        macdLine.push(fastEMA[i] - slowEMA[i]);
      }
    }

    // Calculer la ligne de signal (EMA du MACD)
    const signalLine = this.calculateEMAFromValues(macdLine, signalPeriod);

    // Calculer l'histogramme
    const values: IndicatorValue[] = [];
    const startIndex = slowPeriod - 1;
    for (let i = 0; i < macdLine.length; i++) {
      if (signalLine[i] !== undefined) {
        const time = candles[i + startIndex].time;
        const macd = macdLine[i];
        const signal = signalLine[i];
        const histogram = macd - signal;

        // Ajouter les trois composantes : MACD, Signal, Histogramme
        values.push(
          {
            time,
            value: macd,
            color: this.config.style.color
          },
          {
            time,
            value: signal,
            color: '#FF6B6B'  // Rouge pour la ligne de signal
          },
          {
            time,
            value: histogram,
            color: histogram >= 0 ? '#26A69A' : '#EF5350'  // Vert/Rouge pour l'histogramme
          }
        );
      }
    }

    return values;
  }

  private calculateEMA(candles: Candle[], period: number, source: PriceSource): number[] {
    const values: number[] = [];
    const multiplier = 2 / (period + 1);

    // Calculer la première moyenne simple
    let sum = 0;
    for (let i = 0; i < period; i++) {
      sum += candles[i][source];
    }
    let ema = sum / period;
    values.push(ema);

    // Calculer les EMA suivantes
    for (let i = period; i < candles.length; i++) {
      ema = (candles[i][source] - ema) * multiplier + ema;
      values.push(ema);
    }

    return values;
  }

  private calculateEMAFromValues(values: number[], period: number): number[] {
    const result: number[] = [];
    const multiplier = 2 / (period + 1);

    // Calculer la première moyenne simple
    let sum = 0;
    for (let i = 0; i < period; i++) {
      sum += values[i];
    }
    let ema = sum / period;
    result.push(ema);

    // Calculer les EMA suivantes
    for (let i = period; i < values.length; i++) {
      ema = (values[i] - ema) * multiplier + ema;
      result.push(ema);
    }

    return result;
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

    // Séparer les valeurs en composantes
    const macdLine: IndicatorValue[] = [];
    const signalLine: IndicatorValue[] = [];
    const histogram: IndicatorValue[] = [];

    for (let i = 0; i < this.values.length; i += 3) {
      macdLine.push(this.values[i]);
      signalLine.push(this.values[i + 1]);
      histogram.push(this.values[i + 2]);
    }

    // Dessiner l'histogramme
    const barWidth = Math.max(1, width / histogram.length * 0.8);
    histogram.forEach(value => {
      const x = ((value.time - xMin) / (xMax - xMin)) * width;
      const y = zero - value.value * scale;
      const barHeight = value.value * scale;

      ctx.fillStyle = value.color || this.config.style.fillColor || '#787B86';
      ctx.fillRect(
        x - barWidth / 2,
        y,
        barWidth,
        Math.max(1, Math.abs(barHeight))
      );
    });

    // Dessiner la ligne MACD
    ctx.beginPath();
    ctx.strokeStyle = this.config.style.color;
    ctx.lineWidth = this.config.style.lineWidth;
    macdLine.forEach((value, i) => {
      const x = ((value.time - xMin) / (xMax - xMin)) * width;
      const y = zero - value.value * scale;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Dessiner la ligne de signal
    ctx.beginPath();
    ctx.strokeStyle = '#FF6B6B';
    ctx.lineWidth = this.config.style.lineWidth;
    signalLine.forEach((value, i) => {
      const x = ((value.time - xMin) / (xMax - xMin)) * width;
      const y = zero - value.value * scale;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Dessiner les labels
    ctx.fillStyle = '#787B86';
    ctx.font = '12px Arial';
    ctx.textAlign = 'right';
    ctx.fillText(maxValue.toFixed(2), width - 5, 15);
    ctx.fillText('0', width - 5, zero + 5);
    ctx.fillText(minValue.toFixed(2), width - 5, height - 5);
  }

  onMouseMove(x: number, y: number): void {
    const value = this.getValueAtTime(x);
    if (value !== null) {
      const index = this.values.findIndex(v => v.time >= x);
      if (index >= 0 && index % 3 === 0) {
        const macd = this.values[index].value;
        const signal = this.values[index + 1].value;
        const histogram = this.values[index + 2].value;

        // TODO: Afficher une info-bulle avec les valeurs
        console.log(
          `MACD(${this.config.params.fastPeriod},${this.config.params.slowPeriod},${this.config.params.signalPeriod}):`,
          `\nMACD: ${macd.toFixed(2)}`,
          `\nSignal: ${signal.toFixed(2)}`,
          `\nHistogram: ${histogram.toFixed(2)}`
        );
      }
    }
  }
} 