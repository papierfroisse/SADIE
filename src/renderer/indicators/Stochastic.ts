import { BaseIndicator } from './BaseIndicator';
import { IndicatorConfig, IndicatorValue, Viewport } from './types';
import { Candle } from '../CandlestickRenderer';

export class StochasticIndicator extends BaseIndicator {
  constructor(
    id: string,
    kPeriod: number = 14,
    dPeriod: number = 3,
    smoothK: number = 1
  ) {
    super({
      id,
      type: 'stoch',
      params: {
        kPeriod,
        dPeriod,
        smoothK,
        overBought: 80,
        overSold: 20
      },
      style: {
        color: '#2962FF',      // Ligne %K
        lineWidth: 1.5,
        opacity: 1
      },
      visible: true,
      overlay: false,
      height: 100
    });
  }

  calculate(candles: Candle[]): IndicatorValue[] {
    const {
      kPeriod = 14,
      dPeriod = 3,
      smoothK = 1,
      overBought = 80,
      overSold = 20
    } = this.config.params;

    if (candles.length < kPeriod) {
      return [];
    }

    // Calculer les valeurs %K brutes
    const rawK: number[] = [];
    for (let i = kPeriod - 1; i < candles.length; i++) {
      const periodCandles = candles.slice(i - kPeriod + 1, i + 1);
      const high = Math.max(...periodCandles.map(c => c.high));
      const low = Math.min(...periodCandles.map(c => c.low));
      const close = candles[i].close;

      const k = ((close - low) / (high - low)) * 100;
      rawK.push(k);
    }

    // Lisser les valeurs %K si nécessaire
    const smoothedK = this.smoothValues(rawK, smoothK);

    // Calculer les valeurs %D (moyenne mobile simple des valeurs %K)
    const values: IndicatorValue[] = [];
    for (let i = 0; i < smoothedK.length; i++) {
      const k = smoothedK[i];
      const time = candles[i + kPeriod - 1].time;

      // Calculer %D si nous avons assez de valeurs
      let d: number | undefined;
      if (i >= dPeriod - 1) {
        const dValues = smoothedK.slice(i - dPeriod + 1, i + 1);
        d = dValues.reduce((sum, val) => sum + val, 0) / dPeriod;
      }

      // Ajouter les valeurs %K et %D
      values.push(
        {
          time,
          value: k,
          color: this.getStochColor(k, overBought, overSold)
        }
      );

      if (d !== undefined) {
        values.push({
          time,
          value: d,
          color: '#FF6B6B'  // Rouge pour la ligne %D
        });
      }
    }

    return values;
  }

  private smoothValues(values: number[], period: number): number[] {
    if (period <= 1) return values;

    const result: number[] = [];
    for (let i = period - 1; i < values.length; i++) {
      let sum = 0;
      for (let j = 0; j < period; j++) {
        sum += values[i - j];
      }
      result.push(sum / period);
    }
    return result;
  }

  private getStochColor(value: number, overBought: number, overSold: number): string {
    if (value >= overBought) return '#EF5350';  // Rouge pour suracheté
    if (value <= overSold) return '#26A69A';    // Vert pour survendu
    return this.config.style.color;             // Couleur par défaut
  }

  render(ctx: CanvasRenderingContext2D, viewport: Viewport): void {
    if (!this.config.visible || this.values.length === 0) return;

    const { width, height } = ctx.canvas;
    const { xMin, xMax } = viewport;
    const { overBought = 80, overSold = 20 } = this.config.params;

    // Dessiner les lignes de surachat/survente
    ctx.strokeStyle = '#363A45';
    ctx.lineWidth = 1;
    ctx.setLineDash([5, 5]);

    const overBoughtY = height * (1 - overBought / 100);
    const overSoldY = height * (1 - overSold / 100);
    const middleY = height * 0.5;  // Ligne 50

    ctx.beginPath();
    ctx.moveTo(0, overBoughtY);
    ctx.lineTo(width, overBoughtY);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(0, overSoldY);
    ctx.lineTo(width, overSoldY);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(0, middleY);
    ctx.lineTo(width, middleY);
    ctx.stroke();

    ctx.setLineDash([]);

    // Dessiner les labels
    ctx.fillStyle = '#787B86';
    ctx.font = '12px Arial';
    ctx.textAlign = 'right';
    ctx.fillText(overBought.toString(), width - 5, overBoughtY - 5);
    ctx.fillText(overSold.toString(), width - 5, overSoldY + 15);
    ctx.fillText('50', width - 5, middleY + 5);

    // Séparer les valeurs %K et %D
    const kLine: IndicatorValue[] = [];
    const dLine: IndicatorValue[] = [];

    for (let i = 0; i < this.values.length; i += 2) {
      kLine.push(this.values[i]);
      if (this.values[i + 1]) {
        dLine.push(this.values[i + 1]);
      }
    }

    // Dessiner la ligne %K
    ctx.beginPath();
    ctx.strokeStyle = this.config.style.color;
    ctx.lineWidth = this.config.style.lineWidth;
    kLine.forEach((value, i) => {
      const x = ((value.time - xMin) / (xMax - xMin)) * width;
      const y = height * (1 - value.value / 100);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Dessiner la ligne %D
    if (dLine.length > 0) {
      ctx.beginPath();
      ctx.strokeStyle = '#FF6B6B';
      ctx.lineWidth = this.config.style.lineWidth;
      dLine.forEach((value, i) => {
        const x = ((value.time - xMin) / (xMax - xMin)) * width;
        const y = height * (1 - value.value / 100);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();
    }
  }

  onMouseMove(x: number, y: number): void {
    const value = this.getValueAtTime(x);
    if (value !== null) {
      const index = this.values.findIndex(v => v.time >= x);
      if (index >= 0 && index % 2 === 0) {
        const k = this.values[index].value;
        const d = this.values[index + 1]?.value;

        // TODO: Afficher une info-bulle avec les valeurs
        console.log(
          `Stochastic(${this.config.params.kPeriod},${this.config.params.dPeriod},${this.config.params.smoothK}):`,
          `\n%K: ${k.toFixed(2)}`,
          d !== undefined ? `\n%D: ${d.toFixed(2)}` : ''
        );
      }
    }
  }
} 