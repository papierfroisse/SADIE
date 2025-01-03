export type DrawingToolType = 
  | 'cursor' 
  | 'crosshair'
  | 'line'
  | 'horizontalLine'
  | 'verticalLine'
  | 'rectangle'
  | 'fibonacci'
  | 'measure'
  | 'text'
  | null;

export interface DrawingTool {
  type: DrawingToolType;
  draw: (ctx: CanvasRenderingContext2D) => void;
  onMouseDown: (x: number, y: number) => void;
  onMouseMove: (x: number, y: number) => void;
  onMouseUp: (x: number, y: number) => void;
  destroy: () => void;
}

export class DrawingTools {
  private ctx: CanvasRenderingContext2D;
  private currentTool: DrawingToolType = null;
  private isDrawing = false;
  private startPoint: { x: number; y: number } | null = null;
  private currentPoint: { x: number; y: number } | null = null;

  constructor(ctx: CanvasRenderingContext2D) {
    this.ctx = ctx;
    this.setupEventListeners();
  }

  private setupEventListeners() {
    const canvas = this.ctx.canvas;

    canvas.addEventListener('mousedown', this.handleMouseDown);
    canvas.addEventListener('mousemove', this.handleMouseMove);
    canvas.addEventListener('mouseup', this.handleMouseUp);
    canvas.addEventListener('mouseleave', this.handleMouseLeave);
  }

  private handleMouseDown = (e: MouseEvent) => {
    if (!this.currentTool) return;

    this.isDrawing = true;
    const rect = this.ctx.canvas.getBoundingClientRect();
    this.startPoint = {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    };
  };

  private handleMouseMove = (e: MouseEvent) => {
    if (!this.isDrawing || !this.startPoint || !this.currentTool) return;

    const rect = this.ctx.canvas.getBoundingClientRect();
    this.currentPoint = {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    };

    this.draw();
  };

  private handleMouseUp = () => {
    this.isDrawing = false;
    this.startPoint = null;
    this.currentPoint = null;
  };

  private handleMouseLeave = () => {
    this.isDrawing = false;
    this.startPoint = null;
    this.currentPoint = null;
  };

  public draw() {
    if (!this.startPoint || !this.currentPoint || !this.currentTool) return;

    const { width, height } = this.ctx.canvas;
    
    // Effacer le canvas temporaire
    this.ctx.clearRect(0, 0, width, height);

    // Style de base pour le dessin
    this.ctx.strokeStyle = '#2962FF';
    this.ctx.lineWidth = 1;
    this.ctx.setLineDash([]);

    switch (this.currentTool) {
      case 'line':
        this.drawLine();
        break;
      case 'horizontalLine':
        this.drawHorizontalLine();
        break;
      case 'verticalLine':
        this.drawVerticalLine();
        break;
      case 'rectangle':
        this.drawRectangle();
        break;
      // Autres outils à implémenter...
    }
  }

  private drawLine() {
    if (!this.startPoint || !this.currentPoint) return;

    this.ctx.beginPath();
    this.ctx.moveTo(this.startPoint.x, this.startPoint.y);
    this.ctx.lineTo(this.currentPoint.x, this.currentPoint.y);
    this.ctx.stroke();
  }

  private drawHorizontalLine() {
    if (!this.startPoint || !this.currentPoint) return;

    this.ctx.beginPath();
    this.ctx.moveTo(0, this.startPoint.y);
    this.ctx.lineTo(this.ctx.canvas.width, this.startPoint.y);
    this.ctx.stroke();
  }

  private drawVerticalLine() {
    if (!this.startPoint || !this.currentPoint) return;

    this.ctx.beginPath();
    this.ctx.moveTo(this.startPoint.x, 0);
    this.ctx.lineTo(this.startPoint.x, this.ctx.canvas.height);
    this.ctx.stroke();
  }

  private drawRectangle() {
    if (!this.startPoint || !this.currentPoint) return;

    const width = this.currentPoint.x - this.startPoint.x;
    const height = this.currentPoint.y - this.startPoint.y;
    this.ctx.strokeRect(this.startPoint.x, this.startPoint.y, width, height);
  }

  public setTool(tool: DrawingToolType) {
    this.currentTool = tool;
  }

  public destroy() {
    const canvas = this.ctx.canvas;
    canvas.removeEventListener('mousedown', this.handleMouseDown);
    canvas.removeEventListener('mousemove', this.handleMouseMove);
    canvas.removeEventListener('mouseup', this.handleMouseUp);
    canvas.removeEventListener('mouseleave', this.handleMouseLeave);
  }
} 