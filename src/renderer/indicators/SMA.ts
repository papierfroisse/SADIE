import { BaseIndicator } from './BaseIndicator';
import { IndicatorConfig, IndicatorValue } from './types';
import { Candle } from '../CandlestickRenderer';

export class SMAIndicator extends BaseIndicator {
  constructor(id: string, period: number = 20) {
    super({
      id,
      type: 'sma',
      params: {
        period,
        source: 'close'
      },
      style: {
        color: '#2962FF',
        lineWidth: 1.5,
        opacity: 1
      },
      visible: true,
      overlay: true
    });
  }

  calculate(candles: Candle[]): IndicatorValue[] {
    const { period = 20, source = 'close' } = this.config.params;
    const values: IndicatorValue[] = [];

    if (candles.length < period) {
      return values;
    }

    let sum = 0;
    // Calculer la première moyenne
    for (let i = 0; i < period; i++) {
      sum += candles[i][source];
    }
    values.push({
      time: candles[period - 1].time,
      value: sum / period
    });

    // Calculer les moyennes suivantes
    for (let i = period; i < candles.length; i++) {
      sum = sum - candles[i - period][source] + candles[i][source];
      values.push({
        time: candles[i].time,
        value: sum / period
      });
    }

    return values;
  }

  // Surcharger la méthode onMouseMove pour afficher la valeur au survol
  onMouseMove(x: number, y: number): void {
    const value = this.getValueAtTime(x);
    if (value !== null) {
      // TODO: Afficher une info-bulle avec la valeur
      console.log(`SMA(${this.config.params.period}): ${value.toFixed(2)}`);
    }
  }
} 