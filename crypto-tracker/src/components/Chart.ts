import { CandleData, Drawing, Point } from '../types/chart';

interface ChartOptions {
  width: number;
  height: number;
  padding: number;
  backgroundColor: string;
  textColor: string;
  gridColor: string;
  candleColors: {
    up: string;
    down: string;
  };
  volumeColors: {
    up: string;
    down: string;
  };
  isLogScale?: boolean;
}

export const initializeChart = (canvas: HTMLCanvasElement, options: ChartOptions) => {
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  ctx.canvas.width = options.width;
  ctx.canvas.height = options.height;
  ctx.fillStyle = options.backgroundColor;
  ctx.fillRect(0, 0, options.width, options.height);
};

export const drawChart = (
  canvas: HTMLCanvasElement,
  data: CandleData[],
  options: ChartOptions,
  drawings: Drawing[] = []
) => {
  const ctx = canvas.getContext('2d');
  if (!ctx || data.length === 0) return;

  // Clear canvas
  ctx.fillStyle = options.backgroundColor;
  ctx.fillRect(0, 0, options.width, options.height);

  // Calculate chart dimensions
  const chartHeight = options.height * 0.7;
  const volumeHeight = options.height * 0.2;
  const spacing = options.width / data.length;

  // Find price range
  const prices = data.flatMap(candle => [candle.high, candle.low]);
  const maxPrice = Math.max(...prices);
  const minPrice = Math.min(...prices);
  const priceRange = maxPrice - minPrice;

  // Find volume range
  const volumes = data.map(candle => candle.volume);
  const maxVolume = Math.max(...volumes);

  // Price to Y coordinate conversion
  const priceToY = (price: number): number => {
    if (options.isLogScale) {
      const logMin = Math.log(minPrice);
      const logMax = Math.log(maxPrice);
      const logPrice = Math.log(price);
      return options.padding + (logMax - logPrice) * (chartHeight - 2 * options.padding) / (logMax - logMin);
    }
    return options.padding + (maxPrice - price) * (chartHeight - 2 * options.padding) / priceRange;
  };

  // Draw grid
  ctx.strokeStyle = options.gridColor;
  ctx.lineWidth = 0.5;
  ctx.beginPath();

  // Vertical grid lines
  for (let i = 0; i < data.length; i += Math.ceil(data.length / 10)) {
    const x = i * spacing;
    ctx.moveTo(x, 0);
    ctx.lineTo(x, chartHeight);
  }

  // Horizontal grid lines
  const priceStep = priceRange / 10;
  for (let price = minPrice; price <= maxPrice; price += priceStep) {
    const y = priceToY(price);
    ctx.moveTo(0, y);
    ctx.lineTo(options.width, y);
    
    // Draw price labels
    ctx.fillStyle = options.textColor;
    ctx.textAlign = 'right';
    ctx.fillText(price.toFixed(2), options.width - 5, y - 5);
  }
  ctx.stroke();

  // Draw candles
  data.forEach((candle, i) => {
    const x = i * spacing;
    const candleWidth = Math.max(spacing * 0.8, 1);
    const isUp = candle.close > candle.open;
    
    // Draw candle body
    ctx.fillStyle = isUp ? options.candleColors.up : options.candleColors.down;
    const openY = priceToY(candle.open);
    const closeY = priceToY(candle.close);
    const candleHeight = Math.abs(closeY - openY);
    ctx.fillRect(x - candleWidth / 2, Math.min(openY, closeY), candleWidth, Math.max(candleHeight, 1));

    // Draw wicks
    ctx.beginPath();
    ctx.strokeStyle = isUp ? options.candleColors.up : options.candleColors.down;
    ctx.moveTo(x, priceToY(candle.high));
    ctx.lineTo(x, Math.min(openY, closeY));
    ctx.moveTo(x, Math.max(openY, closeY));
    ctx.lineTo(x, priceToY(candle.low));
    ctx.stroke();

    // Draw volume bars
    const volumeY = chartHeight + volumeHeight * (1 - candle.volume / maxVolume);
    ctx.fillStyle = isUp ? options.volumeColors.up : options.volumeColors.down;
    ctx.fillRect(x - candleWidth / 2, volumeY, candleWidth, chartHeight + volumeHeight - volumeY);
  });

  // Draw custom drawings
  drawings.forEach(drawing => {
    if (drawing.type === 'line' && drawing.points.length === 2) {
      ctx.beginPath();
      ctx.strokeStyle = drawing.color || '#ffffff';
      ctx.lineWidth = 1;
      ctx.moveTo(drawing.points[0].x, drawing.points[0].y);
      ctx.lineTo(drawing.points[1].x, drawing.points[1].y);
      ctx.stroke();
    } else if (drawing.type === 'rectangle' && drawing.points.length === 2) {
      ctx.beginPath();
      ctx.strokeStyle = drawing.color || '#ffffff';
      ctx.lineWidth = 1;
      const width = drawing.points[1].x - drawing.points[0].x;
      const height = drawing.points[1].y - drawing.points[0].y;
      ctx.strokeRect(drawing.points[0].x, drawing.points[0].y, width, height);
    }
  });
}; 