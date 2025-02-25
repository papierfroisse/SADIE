import React, { useEffect, useRef } from 'react';
import { Grid, Paper } from '@mui/material';
import {
  createChart,
  IChartApi,
  CandlestickSeriesApi,
  HistogramSeriesApi,
  Time,
  ChartOptions,
  CandlestickSeriesOptions,
  HistogramSeriesOptions,
} from 'lightweight-charts';
import OrderPanel from '../components/trading/OrderPanel';
import AlertPanel from '../components/trading/AlertPanel';
import { useMarketData } from '../hooks/useMarketData';
import { MarketData } from '../types';

interface TradingViewProps {
  symbol: string;
}

export const TradingView: React.FC<TradingViewProps> = ({ symbol }) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<CandlestickSeriesApi | null>(null);
  const volumeSeriesRef = useRef<HistogramSeriesApi | null>(null);
  const { data: marketData, lastUpdate } = useMarketData({ symbol });

  useEffect(() => {
    if (chartContainerRef.current) {
      const chartOptions: ChartOptions = {
        width: chartContainerRef.current.clientWidth,
        height: 600,
        layout: {
          background: {
            color: '#1E222D',
            type: 'solid',
          },
          textColor: '#DDD',
          fontSize: 12,
        },
        grid: {
          vertLines: {
            color: '#2B2B43',
            style: 1,
            visible: true,
          },
          horzLines: {
            color: '#2B2B43',
            style: 1,
            visible: true,
          },
        },
        crosshair: {
          mode: 0,
          vertLine: {
            color: '#2B2B43',
            width: 1,
            style: 1,
            visible: true,
            labelVisible: true,
          },
          horzLine: {
            color: '#2B2B43',
            width: 1,
            style: 1,
            visible: true,
            labelVisible: true,
          },
        },
        rightPriceScale: {
          borderColor: '#2B2B43',
          borderVisible: true,
          visible: true,
          alignLabels: true,
        },
        timeScale: {
          borderColor: '#2B2B43',
          timeVisible: true,
          secondsVisible: false,
          borderVisible: true,
          visible: true,
        },
        handleScale: {
          mouseWheel: true,
          pinch: true,
        },
        handleScroll: {
          mouseWheel: true,
          pressedMouseMove: true,
        },
      };

      const chart = createChart(chartContainerRef.current, chartOptions);

      const candlestickSeriesOptions: CandlestickSeriesOptions = {
        upColor: '#26a69a',
        downColor: '#ef5350',
        borderVisible: false,
        wickUpColor: '#26a69a',
        wickDownColor: '#ef5350',
      };

      const volumeSeriesOptions: HistogramSeriesOptions = {
        color: '#26a69a',
        priceFormat: {
          type: 'volume',
        },
        priceScaleId: '',
      };

      const candlestickSeries = chart.addCandlestickSeries(candlestickSeriesOptions);
      const volumeSeries = chart.addHistogramSeries(volumeSeriesOptions);

      volumeSeries.priceScale().applyOptions({
        scaleMargins: {
          top: 0.8,
          bottom: 0,
        },
      });

      chartRef.current = chart;
      candlestickSeriesRef.current = candlestickSeries;
      volumeSeriesRef.current = volumeSeries;

      const handleResize = () => {
        if (chartContainerRef.current && chartRef.current) {
          chartRef.current.applyOptions({
            width: chartContainerRef.current.clientWidth,
          });
        }
      };

      window.addEventListener('resize', handleResize);

      return () => {
        window.removeEventListener('resize', handleResize);
        chart.remove();
      };
    }
  }, []);

  useEffect(() => {
    if (marketData && candlestickSeriesRef.current && volumeSeriesRef.current) {
      const formattedData = marketData.map((candle: MarketData) => ({
        time: candle.timestamp as Time,
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close,
      }));

      const volumeData = marketData.map((candle: MarketData) => ({
        time: candle.timestamp as Time,
        value: candle.volume,
        color: candle.close >= candle.open ? '#26a69a' : '#ef5350',
      }));

      candlestickSeriesRef.current.setData(formattedData);
      volumeSeriesRef.current.setData(volumeData);
    }
  }, [marketData]);

  useEffect(() => {
    if (lastUpdate && candlestickSeriesRef.current && volumeSeriesRef.current) {
      const candleData = {
        time: lastUpdate.timestamp as Time,
        open: lastUpdate.open,
        high: lastUpdate.high,
        low: lastUpdate.low,
        close: lastUpdate.close,
      };

      candlestickSeriesRef.current.update(candleData);
      volumeSeriesRef.current.update({
        time: lastUpdate.timestamp as Time,
        value: lastUpdate.volume,
        color: lastUpdate.close >= lastUpdate.open ? '#26a69a' : '#ef5350',
      });
    }
  }, [lastUpdate]);

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} md={9}>
        <Paper sx={{ p: 2 }}>
          <div ref={chartContainerRef} style={{ width: '100%', height: 600 }} />
        </Paper>
      </Grid>
      <Grid item xs={12} md={3}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <OrderPanel
              symbol={symbol}
              currentPrice={lastUpdate?.close || 0}
              onSubmitOrder={async () => {}}
            />
          </Grid>
          <Grid item xs={12}>
            <AlertPanel
              symbol={symbol}
              currentPrice={lastUpdate?.close || 0}
              onCreateAlert={async () => {}}
            />
          </Grid>
        </Grid>
      </Grid>
    </Grid>
  );
};
