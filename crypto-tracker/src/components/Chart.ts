import { ChartOptions, CandleData } from '../types/chart';

export function initializeChart(canvas: HTMLCanvasElement, options: ChartOptions) {
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  // Effacer le canvas
  ctx.fillStyle = options.backgroundColor;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
}

export function drawChart(ctx: CanvasRenderingContext2D, data: CandleData[], options: ChartOptions) {
  const { width, height, padding, backgroundColor, candleColors, gridColor, textColor } = options;
  const chartWidth = width - 2 * padding;
  const chartHeight = height - 2 * padding;

  // Effacer le canvas
  ctx.fillStyle = backgroundColor;
  ctx.fillRect(0, 0, width, height);

  if (data.length === 0) return;

  // Calculer les valeurs min/max
  let minPrice = Math.min(...data.map(d => d.low));
  let maxPrice = Math.max(...data.map(d => d.high));
  const maxVolume = Math.max(...data.map(d => d.volume));

  // Ajouter une marge de 5% au-dessus et en-dessous
  const priceMargin = (maxPrice - minPrice) * 0.05;
  minPrice -= priceMargin;
  maxPrice += priceMargin;

  // Fonction de conversion prix -> coordonnée Y
  const priceToY = (price: number) => {
    if (options.isLogScale) {
      const logMin = Math.log(minPrice);
      const logMax = Math.log(maxPrice);
      const logPrice = Math.log(price);
      return height - padding - ((logPrice - logMin) / (logMax - logMin)) * chartHeight;
    }
    return height - padding - ((price - minPrice) / (maxPrice - minPrice)) * chartHeight;
  };

  // Fonction de conversion volume -> hauteur
  const volumeToHeight = (volume: number) => {
    return (volume / maxVolume) * (chartHeight * 0.2);
  };

  // Fonction de conversion timestamp -> coordonnée X
  const timestampToX = (timestamp: number) => {
    const minTimestamp = data[0].timestamp;
    const maxTimestamp = data[data.length - 1].timestamp;
    return padding + ((timestamp - minTimestamp) / (maxTimestamp - minTimestamp)) * chartWidth;
  };

  // Dessiner la grille
  ctx.strokeStyle = gridColor;
  ctx.lineWidth = 0.5;
  ctx.beginPath();

  // Lignes horizontales
  const priceStep = (maxPrice - minPrice) / 8;
  for (let price = minPrice; price <= maxPrice; price += priceStep) {
    const y = priceToY(price);
    ctx.moveTo(padding, y);
    ctx.lineTo(width - padding, y);
    
    // Prix sur l'axe Y
    ctx.fillStyle = textColor;
    ctx.textAlign = 'right';
    ctx.fillText(price.toFixed(2), padding - 5, y + 4);
  }

  // Lignes verticales
  const timeStep = Math.floor(data.length / 8);
  for (let index = 0; index < data.length; index += timeStep) {
    const x = timestampToX(data[index].timestamp);
    ctx.moveTo(x, padding);
    ctx.lineTo(x, height - padding);
    
    // Date sur l'axe X
    const date = new Date(data[index].timestamp);
    ctx.fillStyle = textColor;
    ctx.textAlign = 'center';
    ctx.fillText(date.toLocaleDateString(), x, height - padding + 15);
  }

  ctx.stroke();

  // Dessiner les volumes
  const candleWidth = (chartWidth / data.length) * 0.8;
  data.forEach((candle) => {
    const x = timestampToX(candle.timestamp);
    const volHeight = volumeToHeight(candle.volume);
    const y = height - padding - volHeight;
    
    ctx.fillStyle = candle.close >= candle.open ? candleColors.up : candleColors.down;
    ctx.fillRect(x - candleWidth / 2, y, candleWidth, volHeight);
  });

  // Dessiner les bougies
  data.forEach((candle) => {
    const x = timestampToX(candle.timestamp);
    const open = priceToY(candle.open);
    const close = priceToY(candle.close);
    const high = priceToY(candle.high);
    const low = priceToY(candle.low);
    
    // Corps de la bougie
    ctx.fillStyle = candle.close >= candle.open ? candleColors.up : candleColors.down;
    ctx.fillRect(x - candleWidth / 2, Math.min(open, close), candleWidth, Math.abs(close - open));
    
    // Mèches
    ctx.beginPath();
    ctx.strokeStyle = candle.close >= candle.open ? candleColors.up : candleColors.down;
    ctx.moveTo(x, high);
    ctx.lineTo(x, Math.min(open, close));
    ctx.moveTo(x, Math.max(open, close));
    ctx.lineTo(x, low);
    ctx.stroke();
  });

  // Dessiner les indicateurs
  if (options.indicators) {
    options.indicators.forEach(indicator => {
      ctx.beginPath();
      ctx.strokeStyle = indicator.color;
      ctx.lineWidth = 1;

      indicator.data.forEach((value, index) => {
        if (isNaN(value)) return;
        const x = timestampToX(data[index].timestamp);
        const y = priceToY(value);
        if (index === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });

      ctx.stroke();
    });
  }

  // Dessiner les dessins
  if (options.drawings) {
    options.drawings.forEach(drawing => {
      ctx.beginPath();
      ctx.strokeStyle = drawing.color;
      ctx.lineWidth = 1;

      switch (drawing.type) {
        case 'line':
        case 'horizontalLine':
        case 'verticalLine':
          if (drawing.points.length >= 2) {
            const start = drawing.points[0];
            const end = drawing.points[1];
            const x1 = timestampToX(start.timestamp);
            const y1 = priceToY(start.price);
            const x2 = timestampToX(end.timestamp);
            const y2 = priceToY(end.price);

            if (drawing.type === 'horizontalLine') {
              ctx.moveTo(padding, y1);
              ctx.lineTo(width - padding, y1);
            } else if (drawing.type === 'verticalLine') {
              ctx.moveTo(x1, padding);
              ctx.lineTo(x1, height - padding);
            } else {
              ctx.moveTo(x1, y1);
              ctx.lineTo(x2, y2);
            }
          }
          break;

        case 'rectangle':
          if (drawing.points.length >= 2) {
            const start = drawing.points[0];
            const end = drawing.points[1];
            const x1 = timestampToX(start.timestamp);
            const y1 = priceToY(start.price);
            const x2 = timestampToX(end.timestamp);
            const y2 = priceToY(end.price);

            ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
          }
          break;

        case 'fibonacci':
          if (drawing.points.length >= 2) {
            const start = drawing.points[0];
            const end = drawing.points[1];
            const x1 = timestampToX(start.timestamp);
            const y1 = priceToY(start.price);
            const x2 = timestampToX(end.timestamp);
            const y2 = priceToY(end.price);

            const levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1];
            levels.forEach(level => {
              const y = y1 + (y2 - y1) * level;
              ctx.moveTo(x1, y);
              ctx.lineTo(x2, y);
              
              ctx.fillStyle = drawing.color;
              ctx.textAlign = 'left';
              ctx.fillText(`${(level * 100).toFixed(1)}%`, x2 + 5, y + 4);
            });
          }
          break;
      }

      ctx.stroke();
    });
  }

  // Dessiner les annotations
  if (options.annotations) {
    ctx.font = '12px Arial';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';

    options.annotations.forEach(annotation => {
      const x = timestampToX(annotation.timestamp);
      const y = priceToY(annotation.price);

      // Point
      ctx.beginPath();
      ctx.fillStyle = annotation.color;
      ctx.arc(x, y, 3, 0, Math.PI * 2);
      ctx.fill();

      // Texte
      ctx.fillStyle = textColor;
      ctx.fillText(annotation.text, x + 5, y);
    });
  }
} 