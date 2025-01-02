import React, { useEffect, useRef, useState } from 'react';
import { createChart, Time, IChartApi } from 'lightweight-charts';
import styled from 'styled-components';
import { exchangeDataService, Candle } from '../services/exchangeData';
import Indicators from './chart/Indicators';

const ChartContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  height: 800px;
  background: #1e222d;
  padding: 1rem;
`;

const MainChartContainer = styled.div`
  width: 100%;
  height: 400px;
  background: #1e222d;
`;

const SubChartContainer = styled.div`
  width: 100%;
  height: 150px;
  background: #1e222d;
`;

interface PriceChartProps {
  symbol: string;
  exchange: string;
  interval?: string;
}

const PriceChart: React.FC<PriceChartProps> = ({
  symbol,
  exchange,
  interval = '1h'
}) => {
  const mainChartRef = useRef<HTMLDivElement>(null);
  const rsiChartRef = useRef<HTMLDivElement>(null);
  const macdChartRef = useRef<HTMLDivElement>(null);
  const [data, setData] = useState<Candle[]>([]);
  const [charts, setCharts] = useState<{
    mainChart: IChartApi | null;
    rsiChart: IChartApi | null;
    macdChart: IChartApi | null;
  }>({
    mainChart: null,
    rsiChart: null,
    macdChart: null
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        let candles: Candle[];
        if (exchange === 'binance') {
          candles = await exchangeDataService.fetchBinanceHistory(symbol, interval);
        } else {
          candles = await exchangeDataService.fetchKrakenHistory(symbol, interval);
        }
        setData(candles);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, [symbol, exchange, interval]);

  useEffect(() => {
    if (!mainChartRef.current || !rsiChartRef.current || !macdChartRef.current || !data.length) return;

    // Création des graphiques
    const mainChart = createChart(mainChartRef.current, {
      width: mainChartRef.current.clientWidth,
      height: mainChartRef.current.clientHeight,
      layout: {
        background: { color: '#1e222d' },
        textColor: '#d1d4dc',
      },
      grid: {
        vertLines: { color: '#2b2b43' },
        horzLines: { color: '#2b2b43' },
      },
      crosshair: {
        mode: 0,
      },
      rightPriceScale: {
        borderColor: '#2b2b43',
      },
      timeScale: {
        borderColor: '#2b2b43',
        timeVisible: true,
        secondsVisible: false,
      },
    });

    const rsiChart = createChart(rsiChartRef.current, {
      width: rsiChartRef.current.clientWidth,
      height: rsiChartRef.current.clientHeight,
      layout: {
        background: { color: '#1e222d' },
        textColor: '#d1d4dc',
      },
      grid: {
        vertLines: { color: '#2b2b43' },
        horzLines: { color: '#2b2b43' },
      },
      rightPriceScale: {
        borderColor: '#2b2b43',
      },
      timeScale: {
        borderColor: '#2b2b43',
        visible: false,
      },
    });

    const macdChart = createChart(macdChartRef.current, {
      width: macdChartRef.current.clientWidth,
      height: macdChartRef.current.clientHeight,
      layout: {
        background: { color: '#1e222d' },
        textColor: '#d1d4dc',
      },
      grid: {
        vertLines: { color: '#2b2b43' },
        horzLines: { color: '#2b2b43' },
      },
      rightPriceScale: {
        borderColor: '#2b2b43',
      },
      timeScale: {
        borderColor: '#2b2b43',
        visible: false,
      },
    });

    // Création de la série de bougies
    const candlestickSeries = mainChart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    });

    // Ajout des données
    candlestickSeries.setData(
      data.map((candle) => ({
        time: (candle.timestamp / 1000) as Time,
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close,
      }))
    );

    // Synchronisation des échelles de temps
    mainChart.timeScale().subscribeVisibleTimeRangeChange((range) => {
      if (range) {
        rsiChart.timeScale().setVisibleRange(range);
        macdChart.timeScale().setVisibleRange(range);
      }
    });

    // Gestion du redimensionnement
    const handleResize = () => {
      if (mainChartRef.current && rsiChartRef.current && macdChartRef.current) {
        mainChart.applyOptions({
          width: mainChartRef.current.clientWidth,
          height: mainChartRef.current.clientHeight,
        });
        rsiChart.applyOptions({
          width: rsiChartRef.current.clientWidth,
          height: rsiChartRef.current.clientHeight,
        });
        macdChart.applyOptions({
          width: macdChartRef.current.clientWidth,
          height: macdChartRef.current.clientHeight,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    // Connexion au WebSocket pour les mises à jour en temps réel
    const handleUpdate = (candle: Candle) => {
      candlestickSeries.update({
        time: (candle.timestamp / 1000) as Time,
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close,
      });
    };

    if (exchange === 'binance') {
      exchangeDataService.connectBinanceWS(symbol, handleUpdate);
    } else {
      exchangeDataService.connectKrakenWS(symbol, handleUpdate);
    }

    setCharts({
      mainChart,
      rsiChart,
      macdChart
    });

    return () => {
      window.removeEventListener('resize', handleResize);
      mainChart.remove();
      rsiChart.remove();
      macdChart.remove();
      exchangeDataService.disconnect(exchange, symbol);
      setCharts({
        mainChart: null,
        rsiChart: null,
        macdChart: null
      });
    };
  }, [data, symbol, exchange]);

  return (
    <ChartContainer>
      <MainChartContainer ref={mainChartRef} />
      <SubChartContainer ref={rsiChartRef} />
      <SubChartContainer ref={macdChartRef} />
      {data.length > 0 && charts.mainChart && charts.rsiChart && charts.macdChart && (
        <Indicators
          data={data}
          mainChart={charts.mainChart}
          rsiChart={charts.rsiChart}
          macdChart={charts.macdChart}
        />
      )}
    </ChartContainer>
  );
};

export default PriceChart; 