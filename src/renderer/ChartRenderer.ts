import { DrawingToolType } from './DrawingTools';
import { CandlestickRenderer } from './CandlestickRenderer';
import { Candle } from '../data/types';
import { IndicatorManager } from './indicators/IndicatorManager';

type IndicatorType = 'rsi' | 'macd' | 'volume';

interface AnimationState {
  startTime: number;
  startValue: number;
  endValue: number;
  duration: number;
  onUpdate: (value: number) => void;
}

export class ChartRenderer {
  private canvas: HTMLCanvasElement;
  private candlestickRenderer: CandlestickRenderer;
  private indicatorManager: IndicatorManager;
  private symbol: string = '';
  private interval: string = '';
  private visibleRange: { start: number; end: number } = { start: 0, end: 0 };
  private zoomLevel: number = 1;
  private data: Candle[] = [];
  private animationFrame: number | null = null;
  private animationState: AnimationState | null = null;

  constructor(container: HTMLDivElement) {
    this.canvas = document.createElement('canvas');
    this.canvas.style.width = '100%';
    this.canvas.style.height = '100%';
    container.appendChild(this.canvas);

    this.candlestickRenderer = new CandlestickRenderer(this.canvas);
    this.indicatorManager = new IndicatorManager(this.canvas);

    // Gérer le redimensionnement
    const resizeObserver = new ResizeObserver(() => {
      this.resize();
    });
    resizeObserver.observe(container);
  }

  setSymbol(symbol: string) {
    this.symbol = symbol;
  }

  setInterval(interval: string) {
    this.interval = interval;
  }

  setData(data: Candle[]) {
    this.data = data;
    this.render();
  }

  setDrawingTool(tool: DrawingToolType) {
    // TODO: Implémenter les outils de dessin
    console.log('Setting drawing tool:', tool);
  }

  addIndicator(type: IndicatorType) {
    this.indicatorManager.addIndicator(type);
    this.render();
  }

  removeIndicator(type: IndicatorType) {
    this.indicatorManager.removeIndicator(type);
    this.render();
  }

  setVisibleRange(start: number, end: number) {
    this.animate(
      this.visibleRange.start,
      start,
      this.visibleRange.end,
      end,
      300,
      (newStart, newEnd) => {
        this.visibleRange = { start: newStart, end: newEnd };
        this.render();
      }
    );
  }

  zoom(factor: number, center: number) {
    const range = this.visibleRange.end - this.visibleRange.start;
    const midPoint = this.visibleRange.start + range * center;
    const newRange = range / factor;
    
    const newStart = midPoint - newRange * center;
    const newEnd = midPoint + newRange * (1 - center);
    
    this.animate(
      this.visibleRange.start,
      newStart,
      this.visibleRange.end,
      newEnd,
      300,
      (newStart, newEnd) => {
        this.visibleRange = { start: newStart, end: newEnd };
        this.zoomLevel *= factor;
        this.render();
      }
    );
  }

  pan(delta: number) {
    const range = this.visibleRange.end - this.visibleRange.start;
    const shift = range * (delta / this.canvas.width);
    
    const newStart = this.visibleRange.start - shift;
    const newEnd = this.visibleRange.end - shift;
    
    this.animate(
      this.visibleRange.start,
      newStart,
      this.visibleRange.end,
      newEnd,
      150,
      (newStart, newEnd) => {
        this.visibleRange = { start: newStart, end: newEnd };
        this.render();
      }
    );
  }

  private animate(
    startValue1: number,
    endValue1: number,
    startValue2: number,
    endValue2: number,
    duration: number,
    onUpdate: (value1: number, value2: number) => void
  ) {
    // Annuler l'animation précédente si elle existe
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
    }

    const startTime = performance.now();

    const animate = (currentTime: number) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);

      // Fonction d'easing
      const easeOutCubic = (t: number) => 1 - Math.pow(1 - t, 3);
      const easedProgress = easeOutCubic(progress);

      // Calculer les valeurs courantes
      const currentValue1 = startValue1 + (endValue1 - startValue1) * easedProgress;
      const currentValue2 = startValue2 + (endValue2 - startValue2) * easedProgress;

      onUpdate(currentValue1, currentValue2);

      if (progress < 1) {
        this.animationFrame = requestAnimationFrame(animate);
      } else {
        this.animationFrame = null;
      }
    };

    this.animationFrame = requestAnimationFrame(animate);
  }

  private render() {
    if (!this.data.length) return;

    // Filtrer les données selon la plage visible
    const visibleData = this.data.filter(
      candle => candle.timestamp >= this.visibleRange.start && 
                candle.timestamp <= this.visibleRange.end
    );

    // Effacer le canvas
    const ctx = this.canvas.getContext('2d')!;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // Dessiner les chandelles
    this.candlestickRenderer.draw(visibleData);

    // Dessiner les indicateurs
    this.indicatorManager.draw(visibleData);
  }

  private resize() {
    if (this.canvas.parentElement) {
      const { width, height } = this.canvas.parentElement.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      
      // Mettre à jour la taille du canvas en tenant compte du DPR
      this.canvas.width = width * dpr;
      this.canvas.height = height * dpr;
      this.canvas.style.width = `${width}px`;
      this.canvas.style.height = `${height}px`;

      // Mettre à l'échelle le contexte
      const ctx = this.canvas.getContext('2d')!;
      ctx.scale(dpr, dpr);

      this.render();
    }
  }

  destroy() {
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
    }
    this.candlestickRenderer.destroy();
    this.indicatorManager.destroy();
    this.canvas.remove();
  }
} 