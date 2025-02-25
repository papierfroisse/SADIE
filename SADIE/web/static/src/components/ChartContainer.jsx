import React, { useEffect, useRef } from 'react';
import { useWebSocket } from '../context/WebSocketContext';
import { createChart } from 'lightweight-charts';
import './ChartContainer.css';

export function ChartContainer({ symbol }) {
  const chartContainerRef = useRef();
  const chartRef = useRef();
  const { marketData, connect } = useWebSocket();

  useEffect(() => {
    // Création du graphique
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 500,
      layout: {
        background: { color: '#1E222D' },
        textColor: '#DDD',
      },
      grid: {
        vertLines: { color: '#2B2B43' },
        horzLines: { color: '#2B2B43' },
      },
    });

    // Création de la série de prix
    const candleSeries = chart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    });

    // Ajout du volume
    const volumeSeries = chart.addHistogramSeries({
      color: '#385263',
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: '',
      scaleMargins: {
        top: 0.8,
        bottom: 0,
      },
    });

    chartRef.current = { chart, candleSeries, volumeSeries };

    // Connexion au WebSocket
    connect(symbol);

    // Nettoyage
    return () => {
      chart.remove();
    };
  }, [symbol]);

  useEffect(() => {
    if (marketData[symbol] && chartRef.current) {
      const { candleSeries, volumeSeries } = chartRef.current;
      const data = marketData[symbol];

      if (data.type === 'market_data') {
        candleSeries.update({
          time: data.timestamp / 1000,
          open: parseFloat(data.data.open),
          high: parseFloat(data.data.high),
          low: parseFloat(data.data.low),
          close: parseFloat(data.data.close),
        });

        volumeSeries.update({
          time: data.timestamp / 1000,
          value: parseFloat(data.data.volume),
          color: parseFloat(data.data.close) >= parseFloat(data.data.open) ? '#26a69a' : '#ef5350',
        });
      }
    }
  }, [marketData, symbol]);

  return <div className="chart-container" ref={chartContainerRef}></div>;
}
