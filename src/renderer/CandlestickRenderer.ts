import { ChartRenderer } from './ChartRenderer';

export interface Candle {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface CandlestickStyle {
  upColor: string;
  downColor: string;
  wickColor: string;
  borderUpColor: string;
  borderDownColor: string;
  wickWidth: number;
  bodyWidth: number;
}

interface CursorPosition {
  x: number;
  y: number;
}

export interface CandlestickOptions {
  symbol: string;
  interval: string;
  style?: Partial<CandlestickStyle>;
}

export class CandlestickRenderer extends ChartRenderer {
  private candles: Candle[] = [];
  private style: CandlestickStyle;
  private cursorPosition: CursorPosition | null = null;
  private hoveredCandle: Candle | null = null;
  private volumeHeight: number = 100;  // Hauteur de la zone de volume en pixels
  private symbol: string;
  private interval: string;
  private legendHeight: number = 40;  // Hauteur de la légende en pixels

  constructor(
    canvas: HTMLCanvasElement,
    options: CandlestickOptions
  ) {
    super(canvas);
    
    // Style par défaut
    this.style = {
      upColor: '#26a69a',
      downColor: '#ef5350',
      wickColor: '#737375',
      borderUpColor: '#26a69a',
      borderDownColor: '#ef5350',
      wickWidth: 1,
      bodyWidth: 8,
      ...options.style
    };

    this.symbol = options.symbol;
    this.interval = options.interval;

    // Ajout des écouteurs d'événements pour le curseur
    this.canvas.addEventListener('mousemove', this.handleMouseMove.bind(this));
    this.canvas.addEventListener('mouseleave', this.handleMouseLeave.bind(this));
  }

  public setCandles(candles: Candle[]): void {
    this.candles = candles;
    
    // Ajuster le viewport pour afficher tous les chandeliers
    if (candles.length > 0) {
      const times = candles.map(c => c.time);
      const prices = candles.flatMap(c => [c.high, c.low]);
      
      const padding = {
        x: (Math.max(...times) - Math.min(...times)) * 0.1,
        y: (Math.max(...prices) - Math.min(...prices)) * 0.1
      };

      this.setViewport({
        xMin: Math.min(...times) - padding.x,
        xMax: Math.max(...times) + padding.x,
        yMin: Math.min(...prices) - padding.y,
        yMax: Math.max(...prices) + padding.y
      });
    }
  }

  private handleMouseMove(e: MouseEvent): void {
    const rect = this.canvas.getBoundingClientRect();
    this.cursorPosition = {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    };

    // Trouver le chandelier le plus proche
    const worldX = this.toWorldX(this.cursorPosition.x);
    this.hoveredCandle = this.findNearestCandle(worldX);

    this.render();
  }

  private handleMouseLeave(): void {
    this.cursorPosition = null;
    this.hoveredCandle = null;
    this.render();
  }

  private findNearestCandle(x: number): Candle | null {
    if (this.candles.length === 0) return null;

    let nearest = this.candles[0];
    let minDistance = Math.abs(nearest.time - x);

    for (const candle of this.candles) {
      const distance = Math.abs(candle.time - x);
      if (distance < minDistance) {
        minDistance = distance;
        nearest = candle;
      }
    }

    return nearest;
  }

  protected override render(): void {
    super.render();  // Appel du rendu de base (grille)

    const { height } = this.getDimensions();
    const priceChartHeight = height - this.volumeHeight - this.legendHeight;
    const chartTop = this.legendHeight;

    // Rendu de la légende
    this.renderLegend();

    // Sauvegarde du contexte
    this.ctx.save();

    // Rendu de la zone des prix
    this.ctx.beginPath();
    this.ctx.rect(0, chartTop, this.getDimensions().width, priceChartHeight);
    this.ctx.clip();
    
    // Rendu des chandeliers
    for (const candle of this.candles) {
      this.renderCandle(candle);
    }

    this.ctx.restore();

    // Rendu des volumes
    this.ctx.save();
    this.ctx.beginPath();
    this.ctx.rect(0, chartTop + priceChartHeight, this.getDimensions().width, this.volumeHeight);
    this.ctx.clip();
    
    this.renderVolumes(chartTop + priceChartHeight);
    
    this.ctx.restore();

    // Rendu du curseur et des infos
    if (this.cursorPosition && this.hoveredCandle) {
      this.renderCursor();
      this.renderHoverInfo();
    }
  }

  private renderLegend(): void {
    if (this.candles.length === 0) return;

    const lastCandle = this.candles[this.candles.length - 1];
    const change = ((lastCandle.close - lastCandle.open) / lastCandle.open) * 100;
    const isUp = lastCandle.close >= lastCandle.open;

    // Style du texte
    this.ctx.font = 'bold 14px sans-serif';
    this.ctx.textBaseline = 'middle';
    this.ctx.textAlign = 'left';

    // Symbole et intervalle
    this.ctx.fillStyle = '#d1d4dc';
    this.ctx.fillText(`${this.symbol} • ${this.interval}`, 10, this.legendHeight / 2);

    // Prix de clôture et variation
    this.ctx.textAlign = 'right';
    const { width } = this.getDimensions();
    
    // Prix de clôture
    this.ctx.fillStyle = '#d1d4dc';
    this.ctx.fillText(
      `$${lastCandle.close.toFixed(2)}`,
      width - 120,
      this.legendHeight / 2
    );

    // Variation
    this.ctx.fillStyle = isUp ? this.style.upColor : this.style.downColor;
    this.ctx.fillText(
      `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`,
      width - 10,
      this.legendHeight / 2
    );
  }

  private renderVolumes(yOffset: number): void {
    if (this.candles.length === 0) return;

    // Calcul de l'échelle pour les volumes
    const maxVolume = Math.max(...this.candles.map(c => c.volume));
    const volumeScale = this.volumeHeight / maxVolume;

    // Rendu des barres de volume
    for (const candle of this.candles) {
      const x = this.toCanvasX(candle.time);
      const volumeHeight = candle.volume * volumeScale;
      const isUp = candle.close >= candle.open;

      this.ctx.fillStyle = isUp 
        ? this.style.upColor + '40'  // 40 = 25% d'opacité
        : this.style.downColor + '40';

      const halfWidth = this.style.bodyWidth / 2;
      this.ctx.fillRect(
        x - halfWidth,
        yOffset + this.volumeHeight - volumeHeight,
        this.style.bodyWidth,
        volumeHeight
      );
    }

    // Ajout des graduations de volume
    this.ctx.fillStyle = '#787b86';
    this.ctx.font = '10px sans-serif';
    this.ctx.textAlign = 'right';
    this.ctx.textBaseline = 'middle';

    const volumeSteps = [0, maxVolume / 2, maxVolume];
    volumeSteps.forEach(volume => {
      const y = yOffset + this.volumeHeight - (volume * volumeScale);
      this.ctx.fillText(
        volume.toLocaleString(undefined, { maximumFractionDigits: 0 }),
        this.getDimensions().width - 5,
        y
      );
    });
  }

  private renderCursor(): void {
    if (!this.cursorPosition) return;

    const { x, y } = this.cursorPosition;
    const { width, height } = this.getDimensions();

    // Lignes du curseur
    this.ctx.beginPath();
    this.ctx.strokeStyle = 'rgba(150, 150, 150, 0.5)';
    this.ctx.lineWidth = 1;
    this.ctx.setLineDash([5, 5]);

    // Ligne verticale
    this.ctx.moveTo(x, 0);
    this.ctx.lineTo(x, height);

    // Ligne horizontale
    this.ctx.moveTo(0, y);
    this.ctx.lineTo(width, y);

    this.ctx.stroke();
    this.ctx.setLineDash([]);
  }

  private renderHoverInfo(): void {
    if (!this.cursorPosition || !this.hoveredCandle) return;

    const { x, y } = this.cursorPosition;
    const candle = this.hoveredCandle;
    const { width, height } = this.getDimensions();

    // Style du texte
    this.ctx.font = '12px sans-serif';
    this.ctx.fillStyle = '#d1d4dc';
    this.ctx.textBaseline = 'middle';

    // Prix au survol
    const price = this.toWorldY(y).toFixed(2);
    this.ctx.textAlign = 'left';
    this.ctx.fillText(`$${price}`, width - 100, y);

    // Informations du chandelier
    const date = new Date(candle.time).toLocaleString();
    const info = [
      `Date: ${date}`,
      `O: ${candle.open.toFixed(2)}`,
      `H: ${candle.high.toFixed(2)}`,
      `L: ${candle.low.toFixed(2)}`,
      `C: ${candle.close.toFixed(2)}`,
      `V: ${candle.volume.toFixed(0)}`
    ];

    // Fond de l'info-bulle
    const padding = 10;
    const lineHeight = 20;
    const boxWidth = 150;
    const boxHeight = info.length * lineHeight + padding * 2;
    let boxX = x + 20;
    let boxY = y - boxHeight / 2;

    // Ajustement si l'info-bulle dépasse les bords
    if (boxX + boxWidth > width) boxX = x - boxWidth - 20;
    if (boxY < 0) boxY = 0;
    if (boxY + boxHeight > height) boxY = height - boxHeight;

    // Rendu du fond
    this.ctx.fillStyle = 'rgba(32, 35, 43, 0.9)';
    this.ctx.strokeStyle = '#363a45';
    this.ctx.lineWidth = 1;
    this.ctx.beginPath();
    this.ctx.roundRect(boxX, boxY, boxWidth, boxHeight, 4);
    this.ctx.fill();
    this.ctx.stroke();

    // Rendu du texte
    this.ctx.fillStyle = '#d1d4dc';
    this.ctx.textAlign = 'left';
    info.forEach((text, i) => {
      this.ctx.fillText(text, boxX + padding, boxY + padding + i * lineHeight + lineHeight / 2);
    });
  }

  private renderCandle(candle: Candle): void {
    const isUp = candle.close >= candle.open;
    
    // Coordonnées en pixels
    const x = this.toCanvasX(candle.time);
    const open = this.toCanvasY(candle.open);
    const close = this.toCanvasY(candle.close);
    const high = this.toCanvasY(candle.high);
    const low = this.toCanvasY(candle.low);

    // Rendu de la mèche
    this.ctx.beginPath();
    this.ctx.strokeStyle = this.style.wickColor;
    this.ctx.lineWidth = this.style.wickWidth;
    this.ctx.moveTo(x, high);
    this.ctx.lineTo(x, low);
    this.ctx.stroke();

    // Rendu du corps
    const bodyTop = Math.min(open, close);
    const bodyBottom = Math.max(open, close);
    const bodyHeight = Math.max(bodyBottom - bodyTop, 1);  // Hauteur minimale de 1px

    this.ctx.fillStyle = isUp ? this.style.upColor : this.style.downColor;
    this.ctx.strokeStyle = isUp ? this.style.borderUpColor : this.style.borderDownColor;
    this.ctx.lineWidth = 1;

    const halfWidth = this.style.bodyWidth / 2;
    this.ctx.fillRect(x - halfWidth, bodyTop, this.style.bodyWidth, bodyHeight);
    this.ctx.strokeRect(x - halfWidth, bodyTop, this.style.bodyWidth, bodyHeight);
  }

  public setStyle(style: Partial<CandlestickStyle>): void {
    this.style = { ...this.style, ...style };
    this.render();
  }

  public getStyle(): CandlestickStyle {
    return { ...this.style };
  }
} 