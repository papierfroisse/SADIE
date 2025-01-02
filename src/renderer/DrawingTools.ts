export type DrawingToolType = 'line' | 'horizontalLine' | 'verticalLine' | 'rectangle' | 'fibonacci' | 'text' | 'brush' | 'measure' | 'ray' | 'arrow' | null;

export interface Drawing {
  id: string;
  type: DrawingToolType;
  points: Point[];
  color: string;
  lineWidth: number;
  text?: string;
}

export interface Point {
  x: number;
  y: number;
}

export interface DrawingToolsConfig {
  color: string;
  lineWidth: number;
  font: string;
}

export class DrawingTools {
  private drawings: Drawing[] = [];
  private currentDrawing: Drawing | null = null;
  private currentTool: DrawingToolType = null;
  private config: DrawingToolsConfig = {
    color: '#2962FF',
    lineWidth: 1,
    font: '12px Arial'
  };

  constructor(private ctx: CanvasRenderingContext2D) {}

  setConfig(config: Partial<DrawingToolsConfig>) {
    this.config = { ...this.config, ...config };
  }

  setTool(tool: DrawingToolType) {
    this.currentTool = tool;
  }

  setColor(color: string) {
    this.config.color = color;
  }

  setLineWidth(width: number) {
    this.config.lineWidth = width;
  }

  startDrawing(point: Point) {
    if (!this.currentTool) return;

    this.currentDrawing = {
      id: Math.random().toString(36).substr(2, 9),
      type: this.currentTool,
      points: [point],
      color: this.config.color,
      lineWidth: this.config.lineWidth
    };
  }

  continueDrawing(point: Point) {
    if (!this.currentDrawing) return;

    this.currentDrawing.points.push(point);
    this.render();
  }

  endDrawing() {
    if (!this.currentDrawing) return;

    this.drawings.push(this.currentDrawing);
    this.currentDrawing = null;
    this.render();
  }

  render() {
    if (!this.ctx?.canvas) return;
    
    this.ctx.clearRect(0, 0, this.ctx.canvas.width, this.ctx.canvas.height);
    
    // Dessiner tous les dessins terminés
    this.drawings.forEach(drawing => this.drawShape(drawing));
    
    // Dessiner le dessin en cours
    if (this.currentDrawing) {
      this.drawShape(this.currentDrawing);
    }
  }

  private drawShape(drawing: Drawing) {
    if (!this.ctx?.canvas) return;
    
    const { type, points, color, lineWidth } = drawing;

    this.ctx.beginPath();
    this.ctx.strokeStyle = color;
    this.ctx.lineWidth = lineWidth;

    switch (type) {
      case 'line':
      case 'ray':
      case 'arrow':
        if (points.length >= 2) {
          this.ctx.moveTo(points[0].x, points[0].y);
          this.ctx.lineTo(points[1].x, points[1].y);
          if (type === 'arrow') {
            this.drawArrowhead(points[0], points[1]);
          }
        }
        break;

      case 'horizontalLine':
        if (points.length >= 1) {
          this.ctx.moveTo(0, points[0].y);
          this.ctx.lineTo(this.ctx.canvas.width, points[0].y);
        }
        break;

      case 'verticalLine':
        if (points.length >= 1) {
          this.ctx.moveTo(points[0].x, 0);
          this.ctx.lineTo(points[0].x, this.ctx.canvas.height);
        }
        break;

      case 'rectangle':
        if (points.length >= 2) {
          const width = points[1].x - points[0].x;
          const height = points[1].y - points[0].y;
          this.ctx.strokeRect(points[0].x, points[0].y, width, height);
        }
        break;

      case 'fibonacci':
        if (points.length >= 2) {
          this.drawFibonacciLevels(points[0], points[1]);
        }
        break;

      case 'text':
        if (points.length >= 1 && drawing.text) {
          this.ctx.font = this.config.font;
          this.ctx.fillStyle = color;
          this.ctx.fillText(drawing.text, points[0].x, points[0].y);
        }
        break;

      case 'brush':
        if (points.length >= 2) {
          this.ctx.moveTo(points[0].x, points[0].y);
          for (let i = 1; i < points.length; i++) {
            this.ctx.lineTo(points[i].x, points[i].y);
          }
        }
        break;

      case 'measure':
        if (points.length >= 2) {
          this.drawMeasurement(points[0], points[1]);
        }
        break;
    }

    this.ctx.stroke();
  }

  private drawArrowhead(start: Point, end: Point) {
    if (!this.ctx) return;
    
    const headLength = 10;
    const angle = Math.atan2(end.y - start.y, end.x - start.x);

    this.ctx.moveTo(end.x, end.y);
    this.ctx.lineTo(
      end.x - headLength * Math.cos(angle - Math.PI / 6),
      end.y - headLength * Math.sin(angle - Math.PI / 6)
    );
    this.ctx.moveTo(end.x, end.y);
    this.ctx.lineTo(
      end.x - headLength * Math.cos(angle + Math.PI / 6),
      end.y - headLength * Math.sin(angle + Math.PI / 6)
    );
  }

  private drawFibonacciLevels(start: Point, end: Point) {
    if (!this.ctx?.canvas) return;
    
    const levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1];
    const height = end.y - start.y;

    levels.forEach(level => {
      const y = start.y + height * level;
      this.ctx.moveTo(0, y);
      this.ctx.lineTo(this.ctx.canvas.width, y);
      
      // Ajouter le texte du niveau
      this.ctx.font = this.config.font;
      this.ctx.fillStyle = this.config.color;
      this.ctx.fillText(`${(level * 100).toFixed(1)}%`, 10, y - 5);
    });
  }

  private drawMeasurement(start: Point, end: Point) {
    if (!this.ctx) return;
    
    // Dessiner la ligne de mesure
    this.ctx.moveTo(start.x, start.y);
    this.ctx.lineTo(end.x, end.y);

    // Calculer la distance
    const dx = end.x - start.x;
    const dy = end.y - start.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    // Afficher la distance
    const midX = (start.x + end.x) / 2;
    const midY = (start.y + end.y) / 2;
    this.ctx.font = this.config.font;
    this.ctx.fillStyle = this.config.color;
    this.ctx.fillText(`${distance.toFixed(1)}px`, midX, midY - 5);
  }

  clear() {
    this.drawings = [];
    this.currentDrawing = null;
    this.render();
  }

  undo() {
    this.drawings.pop();
    this.render();
  }

  getDrawings(): Drawing[] {
    return this.drawings;
  }
} 