import React, { useRef, useEffect } from 'react';
import { createChart, IChartApi, ColorType } from 'lightweight-charts';
import { formatDateForChart } from '../utils/dateUtils';
import { removeDuplicatesAndSort } from '../utils/arrayUtils';
import { ChartContainer } from './ChartContainer';

interface PriceChartProps {
  data: Array<{ time: string; open: number; high: number; low: number; close: number }>;
  isDarkMode: boolean;
}

const PriceChart: React.FC<PriceChartProps> = ({ data, isDarkMode }) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const resizeObserverRef = useRef<ResizeObserver | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current || !data.length) return;

    try {
      chartRef.current = createChart(chartContainerRef.current, {
        width: chartContainerRef.current.clientWidth,
        height: chartContainerRef.current.clientHeight,
        layout: {
          background: { type: ColorType.Solid, color: isDarkMode ? '#1a1a1a' : '#ffffff' },
          textColor: isDarkMode ? '#ffffff' : '#1a1a1a',
        },
        grid: {
          vertLines: { color: isDarkMode ? '#333333' : '#e6e6e6' },
          horzLines: { color: isDarkMode ? '#333333' : '#e6e6e6' },
        },
        timeScale: {
          timeVisible: true,
          secondsVisible: false,
        },
      });

      const candlestickSeries = chartRef.current.addCandlestickSeries({
        upColor: '#4caf50',
        downColor: '#f44336',
        borderVisible: false,
        wickUpColor: '#4caf50',
        wickDownColor: '#f44336',
      });

      const uniqueData = removeDuplicatesAndSort(data);
      const formattedData = uniqueData.map(candle => ({
        time: formatDateForChart(candle.time),
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close,
      }));

      if (formattedData.length > 0) {
        candlestickSeries.setData(formattedData);
        chartRef.current.timeScale().fitContent();
      }

      // Use ResizeObserver instead of window event listener
      resizeObserverRef.current = new ResizeObserver(entries => {
        if (chartRef.current && entries[0]) {
          const { width, height } = entries[0].contentRect;
          chartRef.current.applyOptions({ width, height });
        }
      });

      resizeObserverRef.current.observe(chartContainerRef.current);

      return () => {
        if (resizeObserverRef.current) {
          resizeObserverRef.current.disconnect();
        }
        if (chartRef.current) {
          chartRef.current.remove();
          chartRef.current = null;
        }
      };
    } catch (error) {
      console.error('Error initializing chart:', error);
      // You could add a proper error UI here
      return;
    }
  }, [data, isDarkMode]);

  return <ChartContainer ref={chartContainerRef} />;
};

export default PriceChart; 