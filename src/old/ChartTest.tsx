import React, { useEffect, useRef } from 'react';
import { ChartRenderer } from '../renderer/ChartRenderer';
import { Candle } from '../data/types';

// Fonction pour générer des données de test
const generateTestData = (count: number): Candle[] => {
  const now = Date.now();
  const oneHour = 60 * 60 * 1000;
  const data: Candle[] = [];

  let lastClose = 50000; // Prix de départ pour BTC/USD
  
  for (let i = 0; i < count; i++) {
    const timestamp = now - (count - i) * oneHour;
    const volatility = lastClose * 0.02; // 2% de volatilité
    const change = (Math.random() - 0.5) * volatility;
    
    const open = lastClose;
    const close = open + change;
    const high = Math.max(open, close) * (1 + Math.random() * 0.01);
    const low = Math.min(open, close) * (1 - Math.random() * 0.01);
    const volume = 100 + Math.random() * 900; // Volume entre 100 et 1000

    data.push({
      timestamp,
      open,
      high,
      low,
      close,
      volume
    });

    lastClose = close;
  }

  return data;
};

export function ChartTest() {
  const containerRef = useRef<HTMLDivElement>(null);
  const rendererRef = useRef<ChartRenderer | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Créer le renderer
    const renderer = new ChartRenderer(containerRef.current);
    rendererRef.current = renderer;

    // Générer et définir les données de test
    const testData = generateTestData(100); // 100 chandeliers
    renderer.setData(testData);

    return () => {
      renderer.destroy();
    };
  }, []);

  return (
    <div
      ref={containerRef}
      style={{
        width: '100%',
        height: '600px',
        background: '#131722'
      }}
    />
  );
} 