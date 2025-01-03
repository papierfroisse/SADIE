import { Candle } from '../data/types';

export interface Viewport {
  xMin: number;
  xMax: number;
  yMin: number;
  yMax: number;
}

export interface IndicatorConfig {
  type: string;
  name: string;
  params: Record<string, any>;
}

export interface IndicatorRenderer {
  update(data: Candle[]): void;
  draw(ctx: CanvasRenderingContext2D, data: Candle[], viewport: Viewport): void;
  destroy(): void;
} 