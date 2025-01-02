export interface Candle {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface Viewport {
  xMin: number;
  xMax: number;
  yMin: number;
  yMax: number;
}

export class CandlestickRenderer {
  private candles: Candle[] = [];
  private viewport: Viewport = {
    xMin: 0,
    xMax: 0,
    yMin: 0,
    yMax: 0
  };
  private options = {
    backgroundColor: '#131722',
    gridColor: '#1f2937',
    upColor: '#26a69a',
    downColor: '#ef5350',
    textColor: '#787B86',
    padding: 60,
    candleWidth: 8,
    wickWidth: 1,
    fontSize: 11,
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
  };

  constructor(private ctx: CanvasRenderingContext2D) {}

  setData(candles: Candle[]) {
    this.candles = candles;
    this.updateViewport();
    this.render();
  }

  private updateViewport() {
    if (this.candles.length === 0) return;

    let minPrice = Infinity;
    let maxPrice = -Infinity;
    let minTime = this.candles[0].time;
    let maxTime = this.candles[this.candles.length - 1].time;

    this.candles.forEach(candle => {
      minPrice = Math.min(minPrice, candle.low);
      maxPrice = Math.max(maxPrice, candle.high);
    });

    const priceMargin = (maxPrice - minPrice) * 0.1;
    const timeMargin = (maxTime - minTime) * 0.05; // Réduit pour avoir plus de bougies visibles

    this.viewport = {
      xMin: minTime - timeMargin,
      xMax: maxTime + timeMargin,
      yMin: minPrice - priceMargin,
      yMax: maxPrice + priceMargin
    };
  }

  private toCanvasX(time: number): number {
    const { width } = this.ctx.canvas;
    const { xMin, xMax } = this.viewport;
    const usableWidth = width - this.options.padding;
    return this.options.padding + ((time - xMin) / (xMax - xMin)) * usableWidth;
  }

  private toCanvasY(price: number): number {
    const { height } = this.ctx.canvas;
    const { yMin, yMax } = this.viewport;
    return height - ((price - yMin) / (yMax - yMin)) * height;
  }

  render() {
    const { width, height } = this.ctx.canvas;
    
    // Fond
    this.ctx.fillStyle = this.options.backgroundColor;
    this.ctx.fillRect(0, 0, width, height);

    // Grille
    this.drawGrid();

    // Bougies
    this.candles.forEach(candle => {
      this.drawCandle(candle);
    });

    // Axes
    this.drawPriceAxis();
    this.drawTimeAxis();
  }

  private drawGrid() {
    const { width, height } = this.ctx.canvas;
    const gridCount = {
      x: Math.floor((width - this.options.padding) / 100),
      y: Math.floor(height / 60)
    };

    this.ctx.strokeStyle = this.options.gridColor;
    this.ctx.lineWidth = 1;

    // Lignes horizontales
    for (let i = 0; i <= gridCount.y; i++) {
      const y = (height * i) / gridCount.y;
      this.ctx.beginPath();
      this.ctx.moveTo(this.options.padding, y);
      this.ctx.lineTo(width, y);
      this.ctx.stroke();
    }

    // Lignes verticales
    for (let i = 0; i <= gridCount.x; i++) {
      const x = this.options.padding + ((width - this.options.padding) * i) / gridCount.x;
      this.ctx.beginPath();
      this.ctx.moveTo(x, 0);
      this.ctx.lineTo(x, height);
      this.ctx.stroke();
    }
  }

  private drawCandle(candle: Candle) {
    const x = this.toCanvasX(candle.time);
    const openY = this.toCanvasY(candle.open);
    const highY = this.toCanvasY(candle.high);
    const lowY = this.toCanvasY(candle.low);
    const closeY = this.toCanvasY(candle.close);

    const isGreen = candle.close >= candle.open;
    const color = isGreen ? this.options.upColor : this.options.downColor;

    // Mèche
    this.ctx.strokeStyle = color;
    this.ctx.lineWidth = this.options.wickWidth;
    this.ctx.beginPath();
    this.ctx.moveTo(x, highY);
    this.ctx.lineTo(x, lowY);
    this.ctx.stroke();

    // Corps
    this.ctx.fillStyle = color;
    const candleHeight = Math.max(Math.abs(closeY - openY), 1);
    this.ctx.fillRect(
      x - this.options.candleWidth / 2,
      isGreen ? closeY : openY,
      this.options.candleWidth,
      candleHeight
    );
  }

  private drawPriceAxis() {
    const { height } = this.ctx.canvas;
    const priceCount = 8;

    this.ctx.font = `${this.options.fontSize}px ${this.options.fontFamily}`;
    this.ctx.fillStyle = this.options.textColor;
    this.ctx.textAlign = 'right';

    for (let i = 0; i <= priceCount; i++) {
      const price = this.viewport.yMin + ((this.viewport.yMax - this.viewport.yMin) * i) / priceCount;
      const y = this.toCanvasY(price);

      this.ctx.fillText(
        price.toLocaleString(undefined, {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        }),
        this.ctx.canvas.width - 10,
        y + this.options.fontSize / 3
      );
    }
  }

  private drawTimeAxis() {
    const { width } = this.ctx.canvas;
    const timeCount = 8;

    this.ctx.font = `${this.options.fontSize}px ${this.options.fontFamily}`;
    this.ctx.fillStyle = this.options.textColor;
    this.ctx.textAlign = 'center';

    for (let i = 0; i <= timeCount; i++) {
      const time = this.viewport.xMin + ((this.viewport.xMax - this.viewport.xMin) * i) / timeCount;
      const x = this.toCanvasX(time);
      const date = new Date(time);
      
      this.ctx.fillText(
        date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        x,
        this.ctx.canvas.height - 5
      );
    }
  }

  resize(width: number, height: number) {
    this.ctx.canvas.width = width;
    this.ctx.canvas.height = height;
    this.render();
  }

  dispose() {
    this.candles = [];
    if (this.ctx.canvas) {
      this.ctx.clearRect(0, 0, this.ctx.canvas.width, this.ctx.canvas.height);
    }
  }
} 