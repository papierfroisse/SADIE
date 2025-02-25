import { MarketData } from '../types';

interface ChartOptions {
  width: number;
  height: number;
  backgroundColor: string;
  textColor: string;
  gridColor: string;
  upColor: string;
  downColor: string;
}

export const drawChart = (
  ctx: CanvasRenderingContext2D,
  data: MarketData[],
  options: ChartOptions
) => {
  const { width, height, backgroundColor, textColor, gridColor } = options;

  // Effacer le canvas
  ctx.fillStyle = backgroundColor;
  ctx.fillRect(0, 0, width, height);

  if (data.length === 0) return;

  // Calculer les valeurs min/max pour l'échelle
  const prices = data.map(d => d.price);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const priceRange = maxPrice - minPrice;

  // Dessiner la grille
  ctx.strokeStyle = gridColor;
  ctx.lineWidth = 0.5;

  // Lignes horizontales
  const numHorizontalLines = 5;
  for (let i = 0; i <= numHorizontalLines; i++) {
    const y = (height * i) / numHorizontalLines;
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(width, y);
    ctx.stroke();

    // Prix sur l'axe Y
    const price = maxPrice - (priceRange * i) / numHorizontalLines;
    ctx.fillStyle = textColor;
    ctx.font = '12px Arial';
    ctx.textAlign = 'right';
    ctx.fillText(price.toFixed(2), width - 5, y - 5);
  }

  // Dessiner les points de données
  const pointWidth = width / Math.min(100, data.length);
  data.slice(-100).forEach((point, i) => {
    const x = i * pointWidth;
    const y = height - ((point.price - minPrice) / priceRange) * height;

    ctx.beginPath();
    ctx.arc(x, y, 2, 0, Math.PI * 2);
    ctx.fillStyle = point.price >= (data[i - 1]?.price ?? point.price) ? options.upColor : options.downColor;
    ctx.fill();

    // Relier les points
    if (i > 0) {
      const prevPoint = data[i - 1];
      const prevX = (i - 1) * pointWidth;
      const prevY = height - ((prevPoint.price - minPrice) / priceRange) * height;

      ctx.beginPath();
      ctx.moveTo(prevX, prevY);
      ctx.lineTo(x, y);
      ctx.strokeStyle = point.price >= prevPoint.price ? options.upColor : options.downColor;
      ctx.lineWidth = 1;
      ctx.stroke();
    }
  });
};

export const updateChart = (
  ctx: CanvasRenderingContext2D,
  newData: MarketData
) => {
  // Cette fonction sera appelée pour chaque nouvelle donnée
  // La mise à jour sera gérée par le composant parent via drawChart
  // car nous avons besoin du contexte complet des données pour dessiner correctement
}; 
