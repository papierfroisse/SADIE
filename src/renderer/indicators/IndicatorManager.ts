import { Indicator, IndicatorManager as IIndicatorManager, Viewport } from './types';
import { Candle } from '../CandlestickRenderer';

export class IndicatorManager implements IIndicatorManager {
  private indicators: Map<string, Indicator> = new Map();
  private overlayCanvas: HTMLCanvasElement;
  private overlayCtx: CanvasRenderingContext2D;
  private panelCanvas: HTMLCanvasElement;
  private panelCtx: CanvasRenderingContext2D;

  constructor(container: HTMLElement, width: number, height: number) {
    // Créer le canvas pour les indicateurs en superposition
    this.overlayCanvas = document.createElement('canvas');
    this.overlayCanvas.width = width;
    this.overlayCanvas.height = height;
    this.overlayCanvas.style.position = 'absolute';
    this.overlayCanvas.style.top = '0';
    this.overlayCanvas.style.left = '0';
    this.overlayCanvas.style.pointerEvents = 'none';
    container.appendChild(this.overlayCanvas);

    const overlayCtx = this.overlayCanvas.getContext('2d');
    if (!overlayCtx) throw new Error('Could not get overlay canvas context');
    this.overlayCtx = overlayCtx;

    // Créer le canvas pour les indicateurs en panneau
    this.panelCanvas = document.createElement('canvas');
    this.panelCanvas.width = width;
    this.panelCanvas.height = height * 0.2; // 20% de la hauteur totale
    this.panelCanvas.style.position = 'absolute';
    this.panelCanvas.style.bottom = '0';
    this.panelCanvas.style.left = '0';
    this.panelCanvas.style.pointerEvents = 'none';
    container.appendChild(this.panelCanvas);

    const panelCtx = this.panelCanvas.getContext('2d');
    if (!panelCtx) throw new Error('Could not get panel canvas context');
    this.panelCtx = panelCtx;
  }

  addIndicator(indicator: Indicator): void {
    const config = indicator.getConfig();
    this.indicators.set(config.id, indicator);
  }

  removeIndicator(id: string): void {
    this.indicators.delete(id);
  }

  getIndicator(id: string): Indicator | null {
    return this.indicators.get(id) || null;
  }

  getAllIndicators(): Indicator[] {
    return Array.from(this.indicators.values());
  }

  calculateAll(candles: Candle[]): void {
    this.indicators.forEach(indicator => {
      const values = indicator.calculate(candles);
      // Les valeurs sont stockées dans l'indicateur lui-même
    });
  }

  clearCache(): void {
    // Pas de cache à nettoyer pour le moment
  }

  render(viewport: Viewport): void {
    // Nettoyer les canvas
    this.overlayCtx.clearRect(0, 0, this.overlayCanvas.width, this.overlayCanvas.height);
    this.panelCtx.clearRect(0, 0, this.panelCanvas.width, this.panelCanvas.height);

    // Trier les indicateurs par type (overlay ou panneau)
    const overlayIndicators: Indicator[] = [];
    const panelIndicators: Indicator[] = [];

    this.indicators.forEach(indicator => {
      const config = indicator.getConfig();
      if (config.visible) {
        if (config.overlay) {
          overlayIndicators.push(indicator);
        } else {
          panelIndicators.push(indicator);
        }
      }
    });

    // Rendre les indicateurs en superposition
    overlayIndicators.forEach(indicator => {
      indicator.render(this.overlayCtx, viewport);
    });

    // Rendre les indicateurs en panneau
    if (panelIndicators.length > 0) {
      const panelHeight = this.panelCanvas.height / panelIndicators.length;
      panelIndicators.forEach((indicator, index) => {
        // Créer un viewport spécifique pour chaque panneau
        const panelViewport: Viewport = {
          ...viewport,
          yMin: 0,
          yMax: 100 // Utiliser une échelle de 0 à 100 pour les panneaux
        };

        // Sauvegarder et configurer le contexte pour ce panneau
        this.panelCtx.save();
        this.panelCtx.beginPath();
        this.panelCtx.rect(0, index * panelHeight, this.panelCanvas.width, panelHeight);
        this.panelCtx.clip();

        // Rendre l'indicateur
        indicator.render(this.panelCtx, panelViewport);

        // Restaurer le contexte
        this.panelCtx.restore();

        // Dessiner une ligne de séparation
        if (index > 0) {
          this.panelCtx.beginPath();
          this.panelCtx.strokeStyle = '#363A45';
          this.panelCtx.moveTo(0, index * panelHeight);
          this.panelCtx.lineTo(this.panelCanvas.width, index * panelHeight);
          this.panelCtx.stroke();
        }
      });
    }
  }

  resize(width: number, height: number): void {
    // Redimensionner le canvas de superposition
    this.overlayCanvas.width = width;
    this.overlayCanvas.height = height;

    // Redimensionner le canvas des panneaux
    this.panelCanvas.width = width;
    this.panelCanvas.height = height * 0.2;
  }

  dispose(): void {
    // Nettoyer les ressources
    this.overlayCanvas.remove();
    this.panelCanvas.remove();
    this.indicators.clear();
  }
} 