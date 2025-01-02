import { BaseIndicator } from './BaseIndicator';
import { IndicatorConfig, IndicatorValue, Viewport } from './types';
import { Candle } from '../CandlestickRenderer';

export class RSIIndicator extends BaseIndicator {
  constructor(id: string, period: number = 14) {
    super({
      id,
      type: 'rsi',
      params: {
        period,
        source: 'close',
        overBought: 70,
        overSold: 30
      },
      style: {
        color: '#2962FF',
        lineWidth: 1.5,
        opacity: 1
      },
      visible: true,
      overlay: false,
      height: 100
    });
  }

  calculate(candles: Candle[]): IndicatorValue[] {
    const { period = 14, source = 'close' } = this.config.params;
    const values: IndicatorValue[] = [];

    if (candles.length < period + 1) {
      return values;
    }

    // Calculer les variations de prix
    const changes: number[] = [];
    for (let i = 1; i < candles.length; i++) {
      changes.push(candles[i][source] - candles[i - 1][source]);
    }

    // Calculer les premiers gains et pertes moyens
    let sumGains = 0;
    let sumLosses = 0;
    for (let i = 0; i < period; i++) {
      const change = changes[i];
      if (change > 0) sumGains += change;
      else sumLosses -= change;
    }

    let avgGain = sumGains / period;
    let avgLoss = sumLosses / period;

    // Calculer le premier RSI
    let rsi = 100 - (100 / (1 + avgGain / avgLoss));
    values.push({
      time: candles[period].time,
      value: rsi
    });

    // Calculer les RSI suivants avec la méthode de lissage
    for (let i = period; i < changes.length; i++) {
      const change = changes[i];
      const gain = change > 0 ? change : 0;
      const loss = change < 0 ? -change : 0;

      avgGain = (avgGain * (period - 1) + gain) / period;
      avgLoss = (avgLoss * (period - 1) + loss) / period;

      rsi = 100 - (100 / (1 + avgGain / avgLoss));
      values.push({
        time: candles[i + 1].time,
        value: rsi,
        color: this.getRSIColor(rsi)
      });
    }

    return values;
  }

  private getRSIColor(rsi: number): string {
    const { overBought = 70, overSold = 30 } = this.config.params;
    if (rsi >= overBought) return '#EF5350';  // Rouge pour suracheté
    if (rsi <= overSold) return '#26A69A';    // Vert pour survendu
    return this.config.style.color;           // Couleur par défaut
  }

  render(ctx: CanvasRenderingContext2D, viewport: Viewport): void {
    if (!this.config.visible || this.values.length === 0) return;

    const { width, height } = ctx.canvas;
    const { xMin, xMax } = viewport;
    const { overBought = 70, overSold = 30 } = this.config.params;

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
    ctx.fillText('70', width - 5, overBoughtY - 5);
    ctx.fillText('30', width - 5, overSoldY + 15);
    ctx.fillText('50', width - 5, middleY + 5);

    // Dessiner la ligne du RSI
    ctx.beginPath();
    ctx.strokeStyle = this.config.style.color;
    ctx.lineWidth = this.config.style.lineWidth;

    this.values.forEach((value, i) => {
      const x = ((value.time - xMin) / (xMax - xMin)) * width;
      const y = height * (1 - value.value / 100);

      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });

    ctx.stroke();
  }

  onMouseMove(x: number, y: number): void {
    const value = this.getValueAtTime(x);
    if (value !== null) {
      // TODO: Afficher une info-bulle avec la valeur du RSI
      console.log(`RSI(${this.config.params.period}): ${value.toFixed(2)}`);
    }
  }
} 