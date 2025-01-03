import { Candle } from '../../data/types';
import { RSIIndicator } from './RSI';
import { MACDIndicator } from './MACD';
import { VolumeIndicator } from './Volume';

type IndicatorType = 'rsi' | 'macd' | 'volume';
type Indicator = RSIIndicator | MACDIndicator | VolumeIndicator;

interface IndicatorConfig {
  type: IndicatorType;
  options?: any;
}

export class IndicatorManager {
  private canvas: HTMLCanvasElement;
  private indicators = new Map<IndicatorType, Indicator>();

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas;
  }

  addIndicator(type: IndicatorType, options?: any) {
    let indicator: Indicator;

    switch (type) {
      case 'rsi':
        indicator = new RSIIndicator(this.canvas, options);
        break;
      case 'macd':
        indicator = new MACDIndicator(this.canvas, options);
        break;
      case 'volume':
        indicator = new VolumeIndicator(this.canvas, options);
        break;
      default:
        throw new Error(`Unsupported indicator type: ${type}`);
    }

    this.indicators.set(type, indicator);
  }

  removeIndicator(type: IndicatorType) {
    const indicator = this.indicators.get(type);
    if (indicator) {
      indicator.destroy();
      this.indicators.delete(type);
    }
  }

  draw(data: Candle[]) {
    this.indicators.forEach(indicator => {
      indicator.draw(data);
    });
  }

  resize() {
    this.indicators.forEach(indicator => {
      indicator.resize();
    });
  }

  destroy() {
    this.indicators.forEach(indicator => {
      indicator.destroy();
    });
    this.indicators.clear();
  }
} 