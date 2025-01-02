import React, { useEffect, useMemo } from 'react';
import { IChartApi, LineStyle, Time, createChart } from 'lightweight-charts';
import { CandleData } from '../../types/chart';
import {
  calculateSMA,
  calculateRSI,
  calculateBollingerBands,
  calculateMACD
} from '../../services/indicators';

interface IndicatorsProps {
  data: CandleData[];
  mainChart: ReturnType<typeof createChart>;
  rsiChart: ReturnType<typeof createChart>;
  macdChart: ReturnType<typeof createChart>;
}

const convertToTime = (timestamp: number): Time => {
  return (timestamp / 1000) as Time;
};

export const Indicators: React.FC<IndicatorsProps> = ({
  data,
  mainChart,
  rsiChart,
  macdChart
}) => {
  // Calcul des indicateurs
  const indicators = useMemo(() => ({
    sma20: calculateSMA(data, 20),
    sma50: calculateSMA(data, 50),
    sma200: calculateSMA(data, 200),
    bb: calculateBollingerBands(data),
    rsi: calculateRSI(data),
    macd: calculateMACD(data)
  }), [data]);

  useEffect(() => {
    if (!data.length) return;

    // Moyennes mobiles sur le graphique principal
    const sma20Series = mainChart.addLineSeries({
      color: '#2196f3',
      lineWidth: 1,
      title: 'SMA 20',
      priceScaleId: 'right',
    });
    sma20Series.setData(indicators.sma20.map(d => ({
      time: convertToTime(d.timestamp),
      value: d.value
    })));

    const sma50Series = mainChart.addLineSeries({
      color: '#9c27b0',
      lineWidth: 1,
      title: 'SMA 50',
      priceScaleId: 'right',
    });
    sma50Series.setData(indicators.sma50.map(d => ({
      time: convertToTime(d.timestamp),
      value: d.value
    })));

    const sma200Series = mainChart.addLineSeries({
      color: '#ff9800',
      lineWidth: 1,
      title: 'SMA 200',
      priceScaleId: 'right',
    });
    sma200Series.setData(indicators.sma200.map(d => ({
      time: convertToTime(d.timestamp),
      value: d.value
    })));

    // Bandes de Bollinger
    const bbUpper = mainChart.addLineSeries({
      color: '#4caf50',
      lineWidth: 1,
      lineStyle: LineStyle.Dotted,
      title: 'BB Upper',
      priceScaleId: 'right',
    });
    bbUpper.setData(indicators.bb.upper.map(d => ({
      time: convertToTime(d.timestamp),
      value: d.value
    })));

    const bbLower = mainChart.addLineSeries({
      color: '#4caf50',
      lineWidth: 1,
      lineStyle: LineStyle.Dotted,
      title: 'BB Lower',
      priceScaleId: 'right',
    });
    bbLower.setData(indicators.bb.lower.map(d => ({
      time: convertToTime(d.timestamp),
      value: d.value
    })));

    // RSI
    const rsiSeries = rsiChart.addLineSeries({
      color: '#e91e63',
      lineWidth: 1,
      title: 'RSI (14)',
      priceScaleId: 'right',
    });
    rsiSeries.setData(indicators.rsi.map(d => ({
      time: convertToTime(d.timestamp),
      value: d.value
    })));

    // Niveaux de survente/surachat du RSI
    const rsiOverSold = rsiChart.addLineSeries({
      color: '#666666',
      lineWidth: 1,
      lineStyle: LineStyle.Dotted,
      priceScaleId: 'right',
    });
    rsiOverSold.setData([
      { time: convertToTime(data[0].timestamp), value: 30 },
      { time: convertToTime(data[data.length - 1].timestamp), value: 30 }
    ]);

    const rsiOverBought = rsiChart.addLineSeries({
      color: '#666666',
      lineWidth: 1,
      lineStyle: LineStyle.Dotted,
      priceScaleId: 'right',
    });
    rsiOverBought.setData([
      { time: convertToTime(data[0].timestamp), value: 70 },
      { time: convertToTime(data[data.length - 1].timestamp), value: 70 }
    ]);

    // MACD
    const macdSeries = macdChart.addLineSeries({
      color: '#2196f3',
      lineWidth: 1,
      title: 'MACD',
      priceScaleId: 'right',
    });
    macdSeries.setData(indicators.macd.macd.map(d => ({
      time: convertToTime(d.timestamp),
      value: d.value
    })));

    const signalSeries = macdChart.addLineSeries({
      color: '#ff9800',
      lineWidth: 1,
      title: 'Signal',
      priceScaleId: 'right',
    });
    signalSeries.setData(indicators.macd.signal.map(d => ({
      time: convertToTime(d.timestamp),
      value: d.value
    })));

    const histogramSeries = macdChart.addHistogramSeries({
      color: '#4caf50',
      title: 'Histogram',
      priceScaleId: 'right',
    });
    histogramSeries.setData(indicators.macd.histogram.map(d => ({
      time: convertToTime(d.timestamp),
      value: d.value,
      color: d.value >= 0 ? '#4caf50' : '#f44336'
    })));

    return () => {
      mainChart.removeSeries(sma20Series);
      mainChart.removeSeries(sma50Series);
      mainChart.removeSeries(sma200Series);
      mainChart.removeSeries(bbUpper);
      mainChart.removeSeries(bbLower);
      rsiChart.removeSeries(rsiSeries);
      rsiChart.removeSeries(rsiOverSold);
      rsiChart.removeSeries(rsiOverBought);
      macdChart.removeSeries(macdSeries);
      macdChart.removeSeries(signalSeries);
      macdChart.removeSeries(histogramSeries);
    };
  }, [data, indicators, mainChart, rsiChart, macdChart]);

  return null;
};

export default Indicators; 