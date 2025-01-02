import { BaseIndicator } from './BaseIndicator';
import { IndicatorConfig, IndicatorValue, Viewport } from './types';
import { Candle } from '../CandlestickRenderer';

export class BollingerBandsIndicator extends BaseIndicator {
  constructor(id: string, period: number = 20, standardDeviations: number = 2) {
    super({
      id,
      type: 'bb',
      params: {
        period,
        standardDeviations,
        source: 'close'
      },
      style: {
        color: '#2962FF',
        lineWidth: 1.5,
        opacity: 0.8,
        fillColor: '#2962FF',
        fillOpacity: 0.1
      },
      visible: true,
      overlay: true
    });
  }

  calculate(candles: Candle[]): IndicatorValue[] {
    const { period = 20, standardDeviations = 2, source = 'close' } = this.config.params;
    const values: IndicatorValue[] = [];

    if (candles.length < period) {
      return values;
    }

    // Calculer la SMA et les bandes pour chaque point
    for (let i = period - 1; i < candles.length; i++) {
      // Calculer la moyenne
      let sum = 0;
      for (let j = 0; j < period; j++) {
        sum += candles[i - j][source];
      }
      const sma = sum / period;

      // Calculer l'écart-type
      let squaredSum = 0;
      for (let j = 0; j < period; j++) {
        const diff = candles[i - j][source] - sma;
        squaredSum += diff * diff;
      }
      const standardDeviation = Math.sqrt(squaredSum / period);
      const deviation = standardDeviation * standardDeviations;

      // Ajouter les trois valeurs (bande supérieure, moyenne, bande inférieure)
      const time = candles[i].time;
      values.push(
        {
          time,
          value: sma + deviation,
          color: this.config.style.color
        },
        {
          time,
          value: sma,
          color: this.config.style.color
        },
        {
          time,
          value: sma - deviation,
          color: this.config.style.color
        }
      );
    }

    return values;
  }

  render(ctx: CanvasRenderingContext2D, viewport: Viewport): void {
    if (!this.config.visible || this.values.length === 0) return;

    const { width, height } = ctx.canvas;
    const { xMin, xMax, yMin, yMax } = viewport;

    // Convertir les coordonnées
    const toCanvasX = (time: number) => ((time - xMin) / (xMax - xMin)) * width;
    const toCanvasY = (value: number) => height - ((value - yMin) / (yMax - yMin)) * height;

    // Configuration du style
    const { color, lineWidth, opacity, fillColor, fillOpacity } = this.config.style;
    ctx.strokeStyle = color;
    ctx.lineWidth = lineWidth;
    ctx.globalAlpha = opacity;

    // Dessiner les bandes
    const upperBand: Point[] = [];
    const middleBand: Point[] = [];
    const lowerBand: Point[] = [];

    // Séparer les valeurs en trois bandes
    for (let i = 0; i < this.values.length; i += 3) {
      const time = this.values[i].time;
      upperBand.push({ x: toCanvasX(time), y: toCanvasY(this.values[i].value) });
      middleBand.push({ x: toCanvasX(time), y: toCanvasY(this.values[i + 1].value) });
      lowerBand.push({ x: toCanvasX(time), y: toCanvasY(this.values[i + 2].value) });
    }

    // Dessiner la zone de remplissage
    if (fillColor && fillOpacity) {
      ctx.globalAlpha = fillOpacity;
      ctx.fillStyle = fillColor;
      ctx.beginPath();
      
      // Tracer le chemin supérieur
      upperBand.forEach((point, i) => {
        if (i === 0) ctx.moveTo(point.x, point.y);
        else ctx.lineTo(point.x, point.y);
      });

      // Tracer le chemin inférieur en sens inverse
      for (let i = lowerBand.length - 1; i >= 0; i--) {
        ctx.lineTo(lowerBand[i].x, lowerBand[i].y);
      }

      ctx.closePath();
      ctx.fill();
    }

    // Dessiner les lignes
    ctx.globalAlpha = opacity;
    
    // Bande supérieure
    ctx.beginPath();
    upperBand.forEach((point, i) => {
      if (i === 0) ctx.moveTo(point.x, point.y);
      else ctx.lineTo(point.x, point.y);
    });
    ctx.stroke();

    // Ligne moyenne
    ctx.beginPath();
    middleBand.forEach((point, i) => {
      if (i === 0) ctx.moveTo(point.x, point.y);
      else ctx.lineTo(point.x, point.y);
    });
    ctx.stroke();

    // Bande inférieure
    ctx.beginPath();
    lowerBand.forEach((point, i) => {
      if (i === 0) ctx.moveTo(point.x, point.y);
      else ctx.lineTo(point.x, point.y);
    });
    ctx.stroke();

    // Réinitialiser l'opacité
    ctx.globalAlpha = 1;
  }

  // Surcharger la méthode onMouseMove pour afficher les valeurs au survol
  onMouseMove(x: number, y: number): void {
    const value = this.getValueAtTime(x);
    if (value !== null) {
      const index = this.values.findIndex(v => v.time >= x);
      if (index >= 0 && index % 3 === 0) {
        const upper = this.values[index].value;
        const middle = this.values[index + 1].value;
        const lower = this.values[index + 2].value;
        
        // TODO: Afficher une info-bulle avec les valeurs
        console.log(`BB(${this.config.params.period}, ${this.config.params.standardDeviations}):`,
          `\nUpper: ${upper.toFixed(2)}`,
          `\nMiddle: ${middle.toFixed(2)}`,
          `\nLower: ${lower.toFixed(2)}`
        );
      }
    }
  }
}

interface Point {
  x: number;
  y: number;
} 