import React, { useEffect, useRef, useState } from 'react';
import useWebSocket from '../../hooks/useWebSocket';
import { MarketData } from '../../types';
import { drawChart, updateChart } from '../../utils/chartUtils';

interface ChartContainerProps {
  symbol: string;
}

export const ChartContainer: React.FC<ChartContainerProps> = ({ symbol }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [chartData, setChartData] = useState<MarketData[]>([]);
  const { state } = useWebSocket(`ws://localhost:8000/api/ws/${symbol}`);

  useEffect(() => {
    if (!canvasRef.current) return;

    // Initialisation du graphique
    const ctx = canvasRef.current.getContext('2d');
    if (!ctx) return;

    // Configuration du canvas pour le retina display
    const dpr = window.devicePixelRatio || 1;
    const rect = canvasRef.current.getBoundingClientRect();
    canvasRef.current.width = rect.width * dpr;
    canvasRef.current.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    // Dessin initial du graphique
    drawChart(ctx, chartData, {
      width: rect.width,
      height: rect.height,
      backgroundColor: '#1E222D',
      textColor: '#DDD',
      gridColor: '#2B2B43',
      upColor: '#26a69a',
      downColor: '#ef5350'
    });

    // Gestion du redimensionnement
    const handleResize = () => {
      if (!canvasRef.current || !ctx) return;
      const rect = canvasRef.current.getBoundingClientRect();
      canvasRef.current.width = rect.width * dpr;
      canvasRef.current.height = rect.height * dpr;
      ctx.scale(dpr, dpr);
      drawChart(ctx, chartData, {
        width: rect.width,
        height: rect.height,
        backgroundColor: '#1E222D',
        textColor: '#DDD',
        gridColor: '#2B2B43',
        upColor: '#26a69a',
        downColor: '#ef5350'
      });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [chartData]);

  useEffect(() => {
    if (state?.marketData && state.marketData[symbol]) {
      const newData = state.marketData[symbol];
      setChartData(prevData => {
        const updatedData = [...prevData, newData];
        // Garder seulement les 1000 derniers points
        if (updatedData.length > 1000) {
          return updatedData.slice(-1000);
        }
        return updatedData;
      });

      // Mise à jour du graphique
      if (canvasRef.current) {
        const ctx = canvasRef.current.getContext('2d');
        if (ctx) {
          updateChart(ctx, newData);
        }
      }
    }
  }, [state, symbol]);

  return (
    <div className="chart-container" style={{ width: '100%', height: '100%', minHeight: '500px' }}>
      <canvas
        ref={canvasRef}
        style={{
          width: '100%',
          height: '100%'
        }}
      />
    </div>
  );
}; 