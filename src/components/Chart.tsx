import React, { useEffect, useRef } from 'react';
import styled from 'styled-components';
import { CandlestickRenderer, Candle, CandlestickOptions } from '../renderer/CandlestickRenderer';

const ChartContainer = styled.div`
  width: 100%;
  height: 100%;
  background-color: #131722;
  position: relative;
`;

const Canvas = styled.canvas`
  width: 100%;
  height: 100%;
  display: block;
`;

interface ChartProps {
  symbol: string;
  interval: string;
  candles: Candle[];
  style?: React.CSSProperties;
}

export const Chart: React.FC<ChartProps> = ({ symbol, interval, candles, style }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rendererRef = useRef<CandlestickRenderer | null>(null);

  // Fonction pour mettre à jour les dimensions du canvas
  const updateCanvasDimensions = () => {
    if (!containerRef.current || !canvasRef.current) return;

    const container = containerRef.current;
    const canvas = canvasRef.current;
    
    // Mise à jour des dimensions physiques du canvas
    canvas.width = container.clientWidth;
    canvas.height = container.clientHeight;

    // Si le renderer existe déjà, on force un re-rendu
    if (rendererRef.current) {
      rendererRef.current.setCandles(candles);
    }
  };

  useEffect(() => {
    if (!containerRef.current || !canvasRef.current) return;

    // Initialisation du canvas avec les dimensions du conteneur
    updateCanvasDimensions();

    // Options pour le renderer
    const options: CandlestickOptions = {
      symbol,
      interval,
      style: {
        upColor: '#26a69a',
        downColor: '#ef5350',
        wickColor: '#737375',
        borderUpColor: '#26a69a',
        borderDownColor: '#ef5350',
        wickWidth: 1,
        bodyWidth: 8
      }
    };

    // Création du renderer
    rendererRef.current = new CandlestickRenderer(canvasRef.current, options);
    rendererRef.current.setCandles(candles);

    // Gestion du redimensionnement
    const resizeObserver = new ResizeObserver(updateCanvasDimensions);
    resizeObserver.observe(containerRef.current);

    // Nettoyage
    return () => {
      resizeObserver.disconnect();
    };
  }, [symbol, interval]);  // Re-initialisation si le symbole ou l'intervalle change

  // Mise à jour des chandeliers quand ils changent
  useEffect(() => {
    if (rendererRef.current) {
      rendererRef.current.setCandles(candles);
    }
  }, [candles]);

  return (
    <ChartContainer ref={containerRef} style={style}>
      <Canvas ref={canvasRef} />
    </ChartContainer>
  );
}; 