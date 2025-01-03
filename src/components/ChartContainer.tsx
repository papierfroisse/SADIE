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
  width = window.innerWidth - 300, // 300px pour le panneau droit
  height = window.innerHeight - 100 // 48px pour l'en-tête + marges
}: ChartContainerProps) {
  const mainCanvasRef = useRef<HTMLCanvasElement>(null);
  const [renderer, setRenderer] = useState<CandlestickRenderer | null>(null);
  const [drawingTools, setDrawingTools] = useState<DrawingTools | null>(null);
  const [interval, setInterval] = useState<TimeInterval>(initialInterval);
  
  const { data, loading, error } = useMarketData({
    symbol,
    interval
  });

  useEffect(() => {
    const canvas = mainCanvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

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

  useEffect(() => {
    if (!renderer || !data?.candles) return;
    renderer.setData(data.candles);
  }, [renderer, data]);

  useEffect(() => {
    if (!renderer) return;
    renderer.resize(width, height);
  }, [renderer, width, height]);

  const mainChartHeight = Math.floor(height * 0.7);
  const indicatorsHeight = height - mainChartHeight - 40;

  const handleIndicatorAdd = (type: string) => {
    console.log('Adding indicator:', type);
  };

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'minmax(0, 1fr) 300px',
      width: '100%',
      height: '100%',
      background: '#131722'
    }}>
      {/* Zone du graphique */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        minWidth: 0,
        height: '100%'
      }}>
        {/* Barre d'outils */}
        <ChartToolbar
          onIntervalChange={setInterval}
          onIndicatorAdd={handleIndicatorAdd}
          currentInterval={interval}
        />

        {/* Graphique */}
        <div style={{
          position: 'relative',
          flex: 1,
          minHeight: 0,
          background: '#131722'
        }}>
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

          <canvas
            ref={mainCanvasRef}
            style={{
              width: '100%',
              height: '100%',
              display: 'block'
            }}
          />

          {/* Overlay des prix */}
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
            color: '#787B86'
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

        {/* Indicateurs */}
        {data?.candles && (
          <div style={{ height: `${indicatorsHeight}px` }}>
            <TechnicalIndicators
              data={data.candles}
              width={width}
              height={indicatorsHeight}
            />
          </div>
        )}
      </div>

      {/* Panneau latéral */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        borderLeft: '1px solid #2A2E39',
        background: '#1E222D'
      }}>
        {/* Liste des tickers */}
        <TopTickers />

        {/* Statistiques */}
        <div style={{
          padding: '16px',
          borderBottom: '1px solid #2A2E39'
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
            <div style={{ color: '#D1D4DC', textAlign: 'right' }}>{data?.candles?.[data.candles.length - 1]?.volume.toLocaleString()}</div>
            <div style={{ color: '#787B86' }}>Plus haut 24h</div>
            <div style={{ color: '#D1D4DC', textAlign: 'right' }}>${data?.candles?.[data.candles.length - 1]?.high.toFixed(2)}</div>
            <div style={{ color: '#787B86' }}>Plus bas 24h</div>
            <div style={{ color: '#D1D4DC', textAlign: 'right' }}>${data?.candles?.[data.candles.length - 1]?.low.toFixed(2)}</div>
            <div style={{ color: '#787B86' }}>Cap. marché</div>
            <div style={{ color: '#D1D4DC', textAlign: 'right' }}>$890.00B</div>
            <div style={{ color: '#787B86' }}>Volume total</div>
            <div style={{ color: '#D1D4DC', textAlign: 'right' }}>$25.00B</div>
          </div>
        </div>

        {/* Volumes par exchange */}
        <div style={{
          padding: '16px',
          marginTop: 'auto',
          borderTop: '1px solid #2A2E39'
        }}>
          <div style={{
            fontSize: '14px',
            color: '#787B86',
            marginBottom: '12px'
          }}>
            Volumes par exchange
          </div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'auto 1fr auto',
            gap: '8px',
            fontSize: '14px'
          }}>
            <div style={{ color: '#D1D4DC' }}>Binance</div>
            <div style={{
              background: '#2962FF',
              height: '4px',
              alignSelf: 'center',
              borderRadius: '2px',
              width: '45%'
            }} />
            <div style={{ color: '#787B86' }}>45%</div>
            <div style={{ color: '#D1D4DC' }}>Coinbase</div>
            <div style={{
              background: '#2962FF',
              height: '4px',
              alignSelf: 'center',
              borderRadius: '2px',
              width: '25%'
            }} />
            <div style={{ color: '#787B86' }}>25%</div>
            <div style={{ color: '#D1D4DC' }}>FTX</div>
            <div style={{
              background: '#2962FF',
              height: '4px',
              alignSelf: 'center',
              borderRadius: '2px',
              width: '15%'
            }} />
            <div style={{ color: '#787B86' }}>15%</div>
            <div style={{ color: '#D1D4DC' }}>Kraken</div>
            <div style={{
              background: '#2962FF',
              height: '4px',
              alignSelf: 'center',
              borderRadius: '2px',
              width: '10%'
            }} />
            <div style={{ color: '#787B86' }}>10%</div>
            <div style={{ color: '#D1D4DC' }}>Autres</div>
            <div style={{
              background: '#2962FF',
              height: '4px',
              alignSelf: 'center',
              borderRadius: '2px',
              width: '5%'
            }} />
            <div style={{ color: '#787B86' }}>5%</div>
          </div>
        </div>
      </div>

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