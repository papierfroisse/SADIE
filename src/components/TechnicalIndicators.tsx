import { useRef, useEffect } from 'react';
import { CandleData } from '../data/types';
import { calculateRSI, calculateMACD, MACDResult, calculateVolume } from '../utils/indicators';

interface TechnicalIndicatorsProps {
  data: CandleData[];
  width: number;
  height: number;
}

export function TechnicalIndicators({ data, width, height }: TechnicalIndicatorsProps) {
  const rsiCanvasRef = useRef<HTMLCanvasElement>(null);
  const macdCanvasRef = useRef<HTMLCanvasElement>(null);
  const volumeCanvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!data.length || !rsiCanvasRef.current || !macdCanvasRef.current || !volumeCanvasRef.current) return;

    // Calculer les indicateurs
    const rsiData = calculateRSI(data, 14);
    const macdData = calculateMACD(data);
    const volumeData = calculateVolume(data);

    // Configurer les canvas
    const rsiCtx = rsiCanvasRef.current.getContext('2d');
    const macdCtx = macdCanvasRef.current.getContext('2d');
    const volumeCtx = volumeCanvasRef.current.getContext('2d');

    if (!rsiCtx || !macdCtx || !volumeCtx) return;

    // Configuration commune
    const setupCanvas = (ctx: CanvasRenderingContext2D) => {
      ctx.canvas.style.width = `${width}px`;
      ctx.canvas.style.height = `${ctx.canvas.height}px`;
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    };

    setupCanvas(rsiCtx);
    setupCanvas(macdCtx);
    setupCanvas(volumeCtx);

    // Dessiner RSI
    const drawRSI = () => {
      rsiCtx.clearRect(0, 0, width, height);

      // Fond
      rsiCtx.fillStyle = '#131722';
      rsiCtx.fillRect(0, 0, width, height);

      // Grille
      rsiCtx.strokeStyle = '#2A2E39';
      rsiCtx.lineWidth = 1;

      // Lignes horizontales
      [0, 30, 50, 70, 100].forEach(level => {
        const y = height - (level / 100) * height;
        rsiCtx.beginPath();
        rsiCtx.moveTo(0, y);
        rsiCtx.lineTo(width, y);
        rsiCtx.stroke();

        // Labels
        rsiCtx.fillStyle = '#787B86';
        rsiCtx.font = '10px sans-serif';
        rsiCtx.textAlign = 'right';
        rsiCtx.fillText(level.toString(), width - 5, y - 3);
      });

      // Lignes de survente/surachat
      rsiCtx.strokeStyle = '#787B86';
      rsiCtx.setLineDash([2, 2]);
      
      [30, 70].forEach(level => {
        const y = height - (level / 100) * height;
        rsiCtx.beginPath();
        rsiCtx.moveTo(0, y);
        rsiCtx.lineTo(width, y);
        rsiCtx.stroke();
      });

      rsiCtx.setLineDash([]);

      // Dessiner la ligne RSI
      rsiCtx.strokeStyle = '#2196F3';
      rsiCtx.lineWidth = 1.5;
      rsiCtx.beginPath();

      rsiData.forEach((value: number, i: number) => {
        const x = (width * i) / rsiData.length;
        const y = height - (value / 100) * height;
        if (i === 0) rsiCtx.moveTo(x, y);
        else rsiCtx.lineTo(x, y);
      });

      rsiCtx.stroke();
    };

    // Dessiner MACD
    const drawMACD = () => {
      macdCtx.clearRect(0, 0, width, height);

      // Fond
      macdCtx.fillStyle = '#131722';
      macdCtx.fillRect(0, 0, width, height);

      // Grille
      macdCtx.strokeStyle = '#2A2E39';
      macdCtx.lineWidth = 1;

      // Ligne zéro
      const zeroY = height / 2;
      macdCtx.strokeStyle = '#787B86';
      macdCtx.setLineDash([2, 2]);
      macdCtx.beginPath();
      macdCtx.moveTo(0, zeroY);
      macdCtx.lineTo(width, zeroY);
      macdCtx.stroke();
      macdCtx.setLineDash([]);

      // Trouver les valeurs min/max pour l'échelle
      const allValues = [...macdData.macd, ...macdData.signal];
      const maxValue = Math.max(...allValues);
      const minValue = Math.min(...allValues);
      const valueRange = maxValue - minValue;

      // Dessiner l'histogramme
      const barWidth = Math.max(1, (width / macdData.histogram.length) - 1);
      macdData.histogram.forEach((value: number, i: number) => {
        const x = (width * i) / macdData.histogram.length;
        const barHeight = (value / valueRange) * (height / 4);
        
        macdCtx.fillStyle = value >= 0 ? '#26A69A' : '#EF5350';
        macdCtx.fillRect(x, zeroY, barWidth, -barHeight);
      });

      // Dessiner les lignes
      const drawLine = (data: number[], color: string) => {
        macdCtx.strokeStyle = color;
        macdCtx.lineWidth = 1.5;
        macdCtx.beginPath();
        data.forEach((value: number, i: number) => {
          const x = (width * i) / data.length;
          const y = height - ((value - minValue) / valueRange) * height;
          if (i === 0) macdCtx.moveTo(x, y);
          else macdCtx.lineTo(x, y);
        });
        macdCtx.stroke();
      };

      drawLine(macdData.macd, '#2196F3');
      drawLine(macdData.signal, '#FF9800');
    };

    // Dessiner Volume
    const drawVolume = () => {
      volumeCtx.clearRect(0, 0, width, height);

      // Fond
      volumeCtx.fillStyle = '#131722';
      volumeCtx.fillRect(0, 0, width, height);

      // Grille
      volumeCtx.strokeStyle = '#2A2E39';
      volumeCtx.lineWidth = 1;

      const maxVolume = Math.max(...volumeData);
      const barWidth = Math.max(1, (width / volumeData.length) - 1);

      // Dessiner les barres de volume
      volumeData.forEach((volume: number, i: number) => {
        const x = (width * i) / volumeData.length;
        const barHeight = (volume / maxVolume) * height;
        const y = height - barHeight;

        volumeCtx.fillStyle = data[i].close >= data[i].open ? '#26A69A' : '#EF5350';
        volumeCtx.fillRect(x, y, barWidth, barHeight);
      });

      // Labels de volume
      volumeCtx.fillStyle = '#787B86';
      volumeCtx.font = '10px sans-serif';
      volumeCtx.textAlign = 'right';
      volumeCtx.fillText(formatVolume(maxVolume), width - 5, 12);
      volumeCtx.fillText('0', width - 5, height - 3);
    };

    drawRSI();
    drawMACD();
    drawVolume();
  }, [data, width, height]);

  const formatVolume = (volume: number): string => {
    if (volume >= 1_000_000_000) return `${(volume / 1_000_000_000).toFixed(1)}B`;
    if (volume >= 1_000_000) return `${(volume / 1_000_000).toFixed(1)}M`;
    if (volume >= 1_000) return `${(volume / 1_000).toFixed(1)}K`;
    return volume.toString();
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '1px',
      background: '#131722',
      padding: '4px'
    }}>
      <div style={{ height: '150px', position: 'relative' }}>
        <div style={{
          position: 'absolute',
          left: '8px',
          top: '8px',
          color: '#787B86',
          fontSize: '12px'
        }}>
          RSI (14)
        </div>
        <canvas
          ref={rsiCanvasRef}
          width={width * window.devicePixelRatio}
          height={150 * window.devicePixelRatio}
          style={{ width: `${width}px`, height: '150px' }}
        />
      </div>
      <div style={{ height: '150px', position: 'relative' }}>
        <div style={{
          position: 'absolute',
          left: '8px',
          top: '8px',
          color: '#787B86',
          fontSize: '12px'
        }}>
          MACD (12, 26, 9)
        </div>
        <canvas
          ref={macdCanvasRef}
          width={width * window.devicePixelRatio}
          height={150 * window.devicePixelRatio}
          style={{ width: `${width}px`, height: '150px' }}
        />
      </div>
      <div style={{ height: '100px', position: 'relative' }}>
        <div style={{
          position: 'absolute',
          left: '8px',
          top: '8px',
          color: '#787B86',
          fontSize: '12px'
        }}>
          Volume
        </div>
        <canvas
          ref={volumeCanvasRef}
          width={width * window.devicePixelRatio}
          height={100 * window.devicePixelRatio}
          style={{ width: `${width}px`, height: '100px' }}
        />
      </div>
    </div>
  );
} 