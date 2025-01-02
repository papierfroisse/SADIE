import React, { useRef, useEffect, useState } from 'react';
import { useMarketData } from '../hooks/useMarketData';
import { TimeInterval } from '../data/types';
import { CandlestickRenderer } from '../renderer/CandlestickRenderer';
import { DrawingTools } from '../renderer/DrawingTools';
import { TechnicalIndicators } from './TechnicalIndicators';

interface ChartContainerProps {
  symbol: string;
  interval: TimeInterval;
  width?: number;
  height?: number;
}

export function ChartContainer({
  symbol,
  interval,
  width = 800,
  height = 600
}: ChartContainerProps) {
  const mainCanvasRef = useRef<HTMLCanvasElement>(null);
  const [renderer, setRenderer] = useState<CandlestickRenderer | null>(null);
  const [drawingTools, setDrawingTools] = useState<DrawingTools | null>(null);
  
  const { data, loading, error, status } = useMarketData({
    symbol,
    interval
  });

  // Initialisation du renderer
  useEffect(() => {
    const canvas = mainCanvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Configuration du canvas pour la haute résolution
    const scale = window.devicePixelRatio;
    canvas.width = width * scale;
    canvas.height = height * scale;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    ctx.scale(scale, scale);

    const newRenderer = new CandlestickRenderer(ctx);
    const newDrawingTools = new DrawingTools(ctx);
    
    setRenderer(newRenderer);
    setDrawingTools(newDrawingTools);

    return () => {
      if (newRenderer && 'dispose' in newRenderer) {
        newRenderer.dispose();
      }
    };
  }, [width, height]);

  // Mise à jour des données
  useEffect(() => {
    if (!renderer || !data?.candles) return;
    renderer.setData(data.candles);
  }, [renderer, data]);

  // Gestion du redimensionnement
  useEffect(() => {
    if (!renderer) return;
    renderer.resize(width, height);
  }, [renderer, width, height]);

  const mainChartHeight = Math.floor(height * 0.6); // 60% pour le graphique principal
  const indicatorsHeight = height - mainChartHeight; // 40% pour les indicateurs

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      width: `${width}px`,
      height: `${height}px`,
      background: '#131722',
      borderRadius: '4px',
      overflow: 'hidden'
    }}>
      {/* Barre d'état */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '8px',
        borderBottom: '1px solid #2A2E39'
      }}>
        <span style={{
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          background: status === 'connected' ? '#4CAF50' 
            : status === 'connecting' ? '#FFC107'
            : '#F44336'
        }} />
        <span style={{
          color: '#D1D4DC',
          fontSize: '14px',
          fontWeight: 'bold'
        }}>
          {symbol}
        </span>
        <span style={{
          color: '#787B86',
          fontSize: '14px'
        }}>
          {interval}
        </span>
      </div>

      {/* Zone du graphique principal */}
      <div style={{
        position: 'relative',
        height: `${mainChartHeight}px`,
        background: '#131722'
      }}>
        {loading && (
          <div style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            color: '#D1D4DC',
            fontSize: '14px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <div style={{
              width: '16px',
              height: '16px',
              border: '2px solid #2196F3',
              borderTopColor: 'transparent',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }} />
            Loading...
          </div>
        )}

        {error && (
          <div style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            color: '#F44336',
            fontSize: '14px',
            textAlign: 'center',
            padding: '16px'
          }}>
            <div style={{ marginBottom: '8px' }}>
              Error loading data
            </div>
            <div style={{ 
              fontSize: '12px',
              color: '#787B86',
              maxWidth: '300px',
              wordBreak: 'break-word'
            }}>
              {error.message}
            </div>
          </div>
        )}

        <canvas
          ref={mainCanvasRef}
          style={{
            width: `${width}px`,
            height: `${mainChartHeight}px`
          }}
        />
      </div>

      {/* Zone des indicateurs techniques */}
      {data?.candles && (
        <TechnicalIndicators
          data={data.candles}
          width={width}
          height={indicatorsHeight}
        />
      )}

      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
} 