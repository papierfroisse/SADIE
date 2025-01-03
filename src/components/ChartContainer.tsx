import React, { useRef, useEffect, useState } from 'react';
import { useMarketData } from '../hooks/useMarketData';
import { TimeInterval } from '../data/types';
import { CandlestickRenderer } from '../renderer/CandlestickRenderer';
import { DrawingTools } from '../renderer/DrawingTools';
import { TechnicalIndicators } from './TechnicalIndicators';
import { ChartToolbar } from './ChartToolbar';
import { TopTickers } from './TopTickers';

interface ChartContainerProps {
  symbol: string;
  interval: TimeInterval;
  width?: number;
  height?: number;
}

export function ChartContainer({
  symbol,
  interval: initialInterval,
  width = window.innerWidth - 300,
  height = window.innerHeight - 100
}: ChartContainerProps) {
  // Valider le symbole
  if (!symbol || typeof symbol !== 'string') {
    console.error('Invalid symbol provided to ChartContainer:', symbol);
    return <div>Invalid symbol</div>;
  }

  const mainCanvasRef = useRef<HTMLCanvasElement>(null);
  const gridCanvasRef = useRef<HTMLCanvasElement>(null);
  const [renderer, setRenderer] = useState<CandlestickRenderer | null>(null);
  const [drawingTools, setDrawingTools] = useState<DrawingTools | null>(null);
  const [interval, setInterval] = useState<TimeInterval>(initialInterval);
  
  const { data, loading, error } = useMarketData({
    symbol: symbol.toUpperCase(),
    interval
  });

  // Effet pour dessiner la grille
  useEffect(() => {
    const canvas = gridCanvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const scale = window.devicePixelRatio;
    canvas.width = canvas.clientWidth * scale;
    canvas.height = canvas.clientHeight * scale;
    ctx.scale(scale, scale);

    // Dessiner la grille
    const gridSize = 50; // Taille des cellules de la grille
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;

    ctx.strokeStyle = 'rgba(42, 46, 57, 0.5)';
    ctx.lineWidth = 1;

    // Lignes verticales
    for (let x = 0; x < width; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }

    // Lignes horizontales
    for (let y = 0; y < height; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }
  }, [width, height]);

  // Effet pour initialiser le canvas et les renderers
  useEffect(() => {
    const canvas = mainCanvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const scale = window.devicePixelRatio;
    const canvasWidth = canvas.clientWidth * scale;
    const canvasHeight = canvas.clientHeight * scale;
    
    canvas.width = canvasWidth;
    canvas.height = canvasHeight;
    ctx.scale(scale, scale);

    const newRenderer = new CandlestickRenderer(ctx, {
      upColor: '#26A69A',
      downColor: '#EF5350',
      wickColor: '#787B86',
      borderUpColor: '#26A69A',
      borderDownColor: '#EF5350',
      showWicks: true,
      candleWidth: 8,
      spacing: 2
    });
    
    const newDrawingTools = new DrawingTools(ctx);
    
    setRenderer(newRenderer);
    setDrawingTools(newDrawingTools);

    return () => {
      if (newRenderer && 'dispose' in newRenderer) {
        newRenderer.dispose();
      }
    };
  }, []);

  // Effet pour mettre à jour les données
  useEffect(() => {
    if (!renderer || !data?.candles) return;
    renderer.setData(data.candles);
  }, [renderer, data]);

  // Effet pour redimensionner le canvas
  useEffect(() => {
    if (!renderer || !mainCanvasRef.current) return;
    const canvas = mainCanvasRef.current;
    const scale = window.devicePixelRatio;
    const canvasWidth = canvas.clientWidth * scale;
    const canvasHeight = canvas.clientHeight * scale;
    
    canvas.width = canvasWidth;
    canvas.height = canvasHeight;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.scale(scale, scale);
    }
    
    renderer.resize(canvas.clientWidth, canvas.clientHeight);
  }, [renderer, width, height]);

  const handleIndicatorAdd = (type: string) => {
    console.log('Adding indicator:', type);
  };

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  return (
    <div className="chart-container">
      {/* Zone principale */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        overflow: 'hidden'
      }}>
        {/* Barre d'outils */}
        <ChartToolbar
          onIntervalChange={setInterval}
          onIndicatorAdd={handleIndicatorAdd}
          currentInterval={interval}
        />

        {/* Conteneur du graphique */}
        <div style={{
          position: 'relative',
          flex: '1 1 70%',
          minHeight: 0,
          background: '#131722'
        }}>
          {/* Grille */}
          <canvas
            ref={gridCanvasRef}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              zIndex: 1
            }}
          />

          {loading && (
            <div style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              zIndex: 10,
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              color: '#D1D4DC'
            }}>
              <div className="loading-spinner" />
              Loading...
            </div>
          )}

          <canvas
            ref={mainCanvasRef}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              zIndex: 2
            }}
          />

          {/* Échelle des prix */}
          <div style={{
            position: 'absolute',
            top: 0,
            right: 0,
            bottom: 0,
            width: '50px',
            background: 'rgba(19, 23, 34, 0.8)',
            borderLeft: '1px solid #2A2E39',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            padding: '8px 4px',
            fontSize: '12px',
            color: '#787B86',
            zIndex: 3
          }}>
            {data?.candles && Array.from({ length: 5 }).map((_, i) => {
              const price = data.candles[data.candles.length - 1].high -
                (i * (data.candles[data.candles.length - 1].high - data.candles[data.candles.length - 1].low) / 4);
              return (
                <div key={i} style={{ textAlign: 'right' }}>
                  {price.toFixed(2)}
                </div>
              );
            })}
          </div>
        </div>

        {/* Zone des indicateurs */}
        {data?.candles && (
          <div style={{
            flex: '1 1 30%',
            minHeight: 0,
            borderTop: '1px solid #2A2E39'
          }}>
            <TechnicalIndicators
              data={data.candles}
              width={width}
              height={height * 0.3}
            />
          </div>
        )}
      </div>

      {/* Panneau latéral */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        borderLeft: '1px solid #2A2E39',
        background: '#1E222D',
        overflow: 'hidden'
      }}>
        <TopTickers />
        
        {/* Statistiques */}
        <div style={{
          padding: '16px',
          borderTop: '1px solid #2A2E39'
        }}>
          <div style={{
            fontSize: '16px',
            fontWeight: 'bold',
            color: '#D1D4DC',
            marginBottom: '12px'
          }}>
            Statistiques
          </div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'auto 1fr',
            gap: '8px 16px',
            fontSize: '14px'
          }}>
            <div style={{ color: '#787B86' }}>Volume 24h</div>
            <div style={{ color: '#D1D4DC', textAlign: 'right' }}>
              {data?.candles?.[data.candles.length - 1]?.volume.toLocaleString()}
            </div>
            <div style={{ color: '#787B86' }}>Plus haut 24h</div>
            <div style={{ color: '#D1D4DC', textAlign: 'right' }}>
              ${data?.candles?.[data.candles.length - 1]?.high.toFixed(2)}
            </div>
            <div style={{ color: '#787B86' }}>Plus bas 24h</div>
            <div style={{ color: '#D1D4DC', textAlign: 'right' }}>
              ${data?.candles?.[data.candles.length - 1]?.low.toFixed(2)}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 