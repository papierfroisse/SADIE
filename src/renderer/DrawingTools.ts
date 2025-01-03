export class DrawingTools {
  private ctx: CanvasRenderingContext2D;
  private isDrawing = false;
  private startX = 0;
  private startY = 0;
  private currentTool: 'line' | 'rectangle' | 'circle' | null = null;

  constructor(ctx: CanvasRenderingContext2D) {
    this.ctx = ctx;
  }

  public startDrawing(x: number, y: number, tool: 'line' | 'rectangle' | 'circle') {
    this.isDrawing = true;
    this.startX = x;
    this.startY = y;
    this.currentTool = tool;
  }

  public draw(x: number, y: number) {
    if (!this.isDrawing || !this.currentTool) return;

    // Sauvegarder le contexte
    this.ctx.save();

    // Configuration du style
    this.ctx.strokeStyle = '#2962FF';
    this.ctx.lineWidth = 1;

    // Effacer le canvas
    this.ctx.clearRect(0, 0, this.ctx.canvas.width, this.ctx.canvas.height);

    // Dessiner selon l'outil sélectionné
    switch (this.currentTool) {
      case 'line':
        this.drawLine(x, y);
        break;
      case 'rectangle':
        this.drawRectangle(x, y);
        break;
      case 'circle':
        this.drawCircle(x, y);
        break;
    }

    // Restaurer le contexte
    this.ctx.restore();
  }

  public stopDrawing() {
    this.isDrawing = false;
    this.currentTool = null;
  }

  private drawLine(x: number, y: number) {
    this.ctx.beginPath();
    this.ctx.moveTo(this.startX, this.startY);
    this.ctx.lineTo(x, y);
    this.ctx.stroke();
  }

  private drawRectangle(x: number, y: number) {
    const width = x - this.startX;
    const height = y - this.startY;
    this.ctx.strokeRect(this.startX, this.startY, width, height);
  }

  private drawCircle(x: number, y: number) {
    const radius = Math.sqrt(
      Math.pow(x - this.startX, 2) + Math.pow(y - this.startY, 2)
    );
    this.ctx.beginPath();
    this.ctx.arc(this.startX, this.startY, radius, 0, Math.PI * 2);
    this.ctx.stroke();
  }

  public dispose() {
    // Nettoyer les ressources si nécessaire
  }
} 