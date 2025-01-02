import { Indicator, IndicatorConfig, IndicatorParams, IndicatorStyle, IndicatorValue, Viewport } from './types';
import { Candle } from '../CandlestickRenderer';

export abstract class BaseIndicator implements Indicator {
  protected config: IndicatorConfig;
  protected values: IndicatorValue[] = [];

  constructor(config: IndicatorConfig) {
    this.config = config;
  }

  getConfig(): IndicatorConfig {
    return { ...this.config };
  }

  setParams(params: Partial<IndicatorParams>): void {
    this.config.params = { ...this.config.params, ...params };
  }

  setStyle(style: Partial<IndicatorStyle>): void {
    this.config.style = { ...this.config.style, ...style };
  }

  setVisible(visible: boolean): void {
    this.config.visible = visible;
  }

  abstract calculate(candles: Candle[]): IndicatorValue[];

  render(ctx: CanvasRenderingContext2D, viewport: Viewport): void {
    if (!this.config.visible || this.values.length === 0) return;

    const { width, height } = ctx.canvas;
    const { xMin, xMax, yMin, yMax } = viewport;

    // Convertir les coordonnées
    const toCanvasX = (time: number) => ((time - xMin) / (xMax - xMin)) * width;
    const toCanvasY = (value: number) => height - ((value - yMin) / (yMax - yMin)) * height;

    // Configuration du style
    const { color, lineWidth, opacity, dashArray, fillColor, fillOpacity } = this.config.style;
    ctx.strokeStyle = color;
    ctx.lineWidth = lineWidth;
    ctx.globalAlpha = opacity;
    if (dashArray) ctx.setLineDash(dashArray);

    // Dessiner la ligne
    ctx.beginPath();
    this.values.forEach((point, i) => {
      const x = toCanvasX(point.time);
      const y = toCanvasY(point.value);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Remplir la zone si nécessaire
    if (fillColor && fillOpacity) {
      ctx.globalAlpha = fillOpacity;
      ctx.fillStyle = fillColor;
      
      // Fermer le chemin pour le remplissage
      const lastPoint = this.values[this.values.length - 1];
      const firstPoint = this.values[0];
      ctx.lineTo(toCanvasX(lastPoint.time), height);
      ctx.lineTo(toCanvasX(firstPoint.time), height);
      ctx.closePath();
      ctx.fill();
    }

    // Réinitialiser les styles
    ctx.globalAlpha = 1;
    ctx.setLineDash([]);
  }

  protected getValueAtTime(time: number): number | null {
    // Trouver la valeur la plus proche dans le temps
    const index = this.values.findIndex(v => v.time >= time);
    if (index === -1) return null;
    if (index === 0) return this.values[0].value;

    // Interpolation linéaire entre les deux points
    const prev = this.values[index - 1];
    const next = this.values[index];
    const ratio = (time - prev.time) / (next.time - prev.time);
    return prev.value + (next.value - prev.value) * ratio;
  }

  onMouseMove?(x: number, y: number): void {
    // À implémenter dans les classes dérivées si nécessaire
  }

  onClick?(x: number, y: number): void {
    // À implémenter dans les classes dérivées si nécessaire
  }
} 