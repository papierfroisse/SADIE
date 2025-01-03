import React, { useEffect, useRef } from 'react';
import { ChartRenderer } from '../renderer/ChartRenderer';
import { Candle, TimeInterval } from '../data/types';

interface ChartProps {
  symbol: string;
  interval: TimeInterval;
  data: Candle[];
}

export function Chart({ symbol, interval, data }: ChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const rendererRef = useRef<ChartRenderer | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const renderer = new ChartRenderer(containerRef.current);
    rendererRef.current = renderer;

    return () => {
      renderer.destroy();
    };
  }, []);

  useEffect(() => {
    if (rendererRef.current) {
      rendererRef.current.setSymbol(symbol);
      rendererRef.current.setInterval(interval);
    }
  }, [symbol, interval]);

  useEffect(() => {
    if (rendererRef.current && data) {
      rendererRef.current.setData(data);
    }
  }, [data]);

  return (
    <div
      ref={containerRef}
      style={{
        width: '100%',
        height: '100%',
        background: '#131722'
      }}
    />
  );
} 