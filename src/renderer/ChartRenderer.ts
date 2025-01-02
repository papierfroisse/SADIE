interface Viewport {
  xMin: number;
  xMax: number;
  yMin: number;
  yMax: number;
}

interface Point {
  x: number;
  y: number;
}

interface Dimensions {
  width: number;
  height: number;
}

export class ChartRenderer {
  protected canvas: HTMLCanvasElement;
  protected ctx: CanvasRenderingContext2D;
  private viewport: Viewport;
  private dimensions: Dimensions;
  private pixelRatio: number;
  private isDragging: boolean = false;
  private lastMousePosition: Point | null = null;

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas;
    const context = canvas.getContext('2d');
    if (!context) {
      throw new Error('Could not get canvas context');
    }
    this.ctx = context;

    // Initialisation des dimensions
    this.dimensions = {
      width: canvas.width,
      height: canvas.height
    };

    // Initialisation du viewport par défaut
    this.viewport = {
      xMin: 0,
      xMax: 100,
      yMin: 0,
      yMax: 100
    };

    // Gestion du pixel ratio pour les écrans haute résolution
    this.pixelRatio = window.devicePixelRatio || 1;
    this.setupCanvas();
    this.setupEventListeners();
  }

  private setupCanvas(): void {
    // Configuration du canvas pour les écrans haute résolution
    const { width, height } = this.dimensions;
    this.canvas.width = width * this.pixelRatio;
    this.canvas.height = height * this.pixelRatio;
    this.canvas.style.width = `${width}px`;
    this.canvas.style.height = `${height}px`;
    this.ctx.scale(this.pixelRatio, this.pixelRatio);
  }

  private setupEventListeners(): void {
    // Gestion du zoom avec la molette
    this.canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      const mousePos = this.getMousePosition(e);
      const zoomFactor = e.deltaY > 0 ? 1.1 : 0.9;
      this.zoom(mousePos, zoomFactor);
    });

    // Gestion du déplacement avec la souris
    this.canvas.addEventListener('mousedown', (e) => {
      this.isDragging = true;
      this.lastMousePosition = this.getMousePosition(e);
    });

    this.canvas.addEventListener('mousemove', (e) => {
      if (this.isDragging && this.lastMousePosition) {
        const currentPos = this.getMousePosition(e);
        const dx = currentPos.x - this.lastMousePosition.x;
        const dy = currentPos.y - this.lastMousePosition.y;
        this.pan(dx, dy);
        this.lastMousePosition = currentPos;
      }
    });

    this.canvas.addEventListener('mouseup', () => {
      this.isDragging = false;
      this.lastMousePosition = null;
    });

    this.canvas.addEventListener('mouseleave', () => {
      this.isDragging = false;
      this.lastMousePosition = null;
    });

    // Gestion du redimensionnement de la fenêtre
    window.addEventListener('resize', () => {
      this.resize();
    });
  }

  private getMousePosition(e: MouseEvent): Point {
    const rect = this.canvas.getBoundingClientRect();
    return {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    };
  }

  private zoom(center: Point, factor: number): void {
    // Calcul des nouvelles limites du viewport
    const dx = this.viewport.xMax - this.viewport.xMin;
    const dy = this.viewport.yMax - this.viewport.yMin;
    const centerXRatio = (center.x / this.dimensions.width);
    const centerYRatio = (center.y / this.dimensions.height);

    const newDx = dx * factor;
    const newDy = dy * factor;

    this.viewport = {
      xMin: this.viewport.xMin - (newDx - dx) * centerXRatio,
      xMax: this.viewport.xMax + (newDx - dx) * (1 - centerXRatio),
      yMin: this.viewport.yMin - (newDy - dy) * centerYRatio,
      yMax: this.viewport.yMax + (newDy - dy) * (1 - centerYRatio)
    };

    this.render();
  }

  private pan(dx: number, dy: number): void {
    // Conversion des pixels en unités du viewport
    const xScale = (this.viewport.xMax - this.viewport.xMin) / this.dimensions.width;
    const yScale = (this.viewport.yMax - this.viewport.yMin) / this.dimensions.height;

    const deltaX = dx * xScale;
    const deltaY = dy * yScale;

    this.viewport = {
      xMin: this.viewport.xMin - deltaX,
      xMax: this.viewport.xMax - deltaX,
      yMin: this.viewport.yMin - deltaY,
      yMax: this.viewport.yMax - deltaY
    };

    this.render();
  }

  private resize(): void {
    const parent = this.canvas.parentElement;
    if (!parent) return;

    // Mise à jour des dimensions
    this.dimensions = {
      width: parent.clientWidth,
      height: parent.clientHeight
    };

    // Mise à jour du canvas
    this.setupCanvas();
    this.render();
  }

  // Conversion des coordonnées du monde réel en pixels
  protected toCanvasX(x: number): number {
    return (
      ((x - this.viewport.xMin) / (this.viewport.xMax - this.viewport.xMin)) *
      this.dimensions.width
    );
  }

  protected toCanvasY(y: number): number {
    return (
      ((this.viewport.yMax - y) / (this.viewport.yMax - this.viewport.yMin)) *
      this.dimensions.height
    );
  }

  // Conversion des pixels en coordonnées du monde réel
  protected toWorldX(x: number): number {
    return (
      this.viewport.xMin +
      (x / this.dimensions.width) * (this.viewport.xMax - this.viewport.xMin)
    );
  }

  protected toWorldY(y: number): number {
    return (
      this.viewport.yMax -
      (y / this.dimensions.height) * (this.viewport.yMax - this.viewport.yMin)
    );
  }

  // Méthode de rendu principale (à surcharger dans les classes dérivées)
  protected render(): void {
    // Effacement du canvas
    this.ctx.clearRect(0, 0, this.dimensions.width, this.dimensions.height);

    // Rendu de la grille
    this.renderGrid();
  }

  private renderGrid(): void {
    const { width, height } = this.dimensions;
    
    // Configuration du style de la grille
    this.ctx.strokeStyle = '#2b2b43';
    this.ctx.lineWidth = 0.5;
    this.ctx.setLineDash([1, 3]);  // Pointillés

    // Calcul des intervalles de la grille
    const xRange = this.viewport.xMax - this.viewport.xMin;
    const yRange = this.viewport.yMax - this.viewport.yMin;
    
    const xStep = this.calculateGridStep(xRange);
    const yStep = this.calculateGridStep(yRange);

    // Lignes verticales
    const startX = Math.ceil(this.viewport.xMin / xStep) * xStep;
    for (let x = startX; x <= this.viewport.xMax; x += xStep) {
      const pixelX = this.toCanvasX(x);
      this.ctx.beginPath();
      this.ctx.moveTo(pixelX, 0);
      this.ctx.lineTo(pixelX, height);
      this.ctx.stroke();
    }

    // Lignes horizontales
    const startY = Math.ceil(this.viewport.yMin / yStep) * yStep;
    for (let y = startY; y <= this.viewport.yMax; y += yStep) {
      const pixelY = this.toCanvasY(y);
      this.ctx.beginPath();
      this.ctx.moveTo(0, pixelY);
      this.ctx.lineTo(width, pixelY);
      this.ctx.stroke();
    }

    // Réinitialisation du style de ligne
    this.ctx.setLineDash([]);

    // Rendu des labels
    this.ctx.fillStyle = '#787b86';
    this.ctx.font = '10px sans-serif';
    this.ctx.textAlign = 'right';
    this.ctx.textBaseline = 'middle';

    // Labels horizontaux (prix)
    for (let y = startY; y <= this.viewport.yMax; y += yStep) {
      const pixelY = this.toCanvasY(y);
      this.ctx.fillText(y.toFixed(2), width - 5, pixelY);
    }

    // Labels verticaux (temps)
    this.ctx.textAlign = 'center';
    this.ctx.textBaseline = 'top';
    for (let x = startX; x <= this.viewport.xMax; x += xStep) {
      const pixelX = this.toCanvasX(x);
      const date = new Date(x);
      const label = date.toLocaleDateString();
      this.ctx.fillText(label, pixelX, height - 15);
    }
  }

  private calculateGridStep(range: number): number {
    const minSteps = 4;
    const maxSteps = 8;
    const minStep = range / maxSteps;
    const magnitude = Math.pow(10, Math.floor(Math.log10(minStep)));
    const steps = [1, 2, 5, 10];
    
    for (const step of steps) {
      const currentStep = step * magnitude;
      const numSteps = range / currentStep;
      if (numSteps >= minSteps && numSteps <= maxSteps) {
        return currentStep;
      }
    }
    
    return steps[steps.length - 1] * magnitude;
  }

  // Méthodes publiques pour le contrôle externe
  public setViewport(viewport: Viewport): void {
    this.viewport = viewport;
    this.render();
  }

  public getViewport(): Viewport {
    return { ...this.viewport };
  }

  public getDimensions(): Dimensions {
    return { ...this.dimensions };
  }
} 