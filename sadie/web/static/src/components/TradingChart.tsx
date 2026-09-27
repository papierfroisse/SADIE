import React, { useEffect, useRef, useState, useCallback } from 'react';
import { MarketData } from '../types';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Chip,
  IconButton,
  Tooltip,
  useTheme,
  Divider,
  Stack,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  Fullscreen,
  FullscreenExit,
  Settings,
  Timeline,
  ShowChart as ChartIcon,
} from '@mui/icons-material';
import {
  createChart,
  IChartApi,
  CandlestickSeriesApi,
  HistogramSeriesApi,
  Time,
  CandlestickData,
  HistogramData,
} from 'lightweight-charts';
import { useWebSocket } from '../context/WebSocketContext';

interface TradingChartProps {
  symbol: string;
}

const TIMEFRAMES = {
  "1m": "1 minute",
  "5m": "5 minutes",
  "15m": "15 minutes",
  "30m": "30 minutes",
  "1h": "1 heure",
  "4h": "4 heures",
  "1d": "1 jour",
  "1w": "1 semaine"
};

export const TradingChart: React.FC<TradingChartProps> = ({ symbol }) => {
  const theme = useTheme();
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<CandlestickSeriesApi | null>(null);
  const volumeSeriesRef = useRef<HistogramSeriesApi | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [lastPrice, setLastPrice] = useState<number | null>(null);
  const [priceChange, setPriceChange] = useState<number>(0);
  const [selectedTimeframe, setSelectedTimeframe] = useState<string>("1m");

  const { connect, disconnect, marketData, isConnected } = useWebSocket();

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: chartContainerRef.current.clientHeight,
      layout: {
        background: { color: theme.palette.background.paper },
        textColor: theme.palette.text.primary,
      },
      grid: {
        vertLines: { color: theme.palette.divider },
        horzLines: { color: theme.palette.divider },
      },
    });

    const candlestickSeries = chart.addCandlestickSeries({
      upColor: theme.palette.success.main,
      downColor: theme.palette.error.main,
      borderVisible: false,
      wickUpColor: theme.palette.success.main,
      wickDownColor: theme.palette.error.main,
    });

    const volumeSeries = chart.addHistogramSeries({
      color: theme.palette.primary.main,
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: '',
    });

    candlestickSeriesRef.current = candlestickSeries;
    volumeSeriesRef.current = volumeSeries;
    chartRef.current = chart;

    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
          height: chartContainerRef.current.clientHeight,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
      }
    };
  }, [theme]);

  const updateChartData = useCallback((data: MarketData) => {
    if (!data.timestamp || !data.open || !data.high || !data.low || !data.close || !data.volume) {
      console.error('Données de marché incomplètes:', data);
      return;
    }

    if (candlestickSeriesRef.current && volumeSeriesRef.current) {
      const candleData: CandlestickData = {
        time: data.timestamp as Time,
        open: data.open,
        high: data.high,
        low: data.low,
        close: data.close,
      };

      const volumeData: HistogramData = {
        time: data.timestamp as Time,
        value: data.volume,
        color: data.close >= data.open ? theme.palette.success.main : theme.palette.error.main,
      };

      try {
        candlestickSeriesRef.current.update(candleData);
        volumeSeriesRef.current.update(volumeData);

        setLastPrice(prevPrice => {
          if (prevPrice !== null && data.close !== prevPrice) {
            const change = ((data.close - prevPrice) / prevPrice) * 100;
            setPriceChange(change);
          }
          return data.close;
        });
      } catch (error) {
        console.error('Erreur lors de la mise à jour du graphique:', error);
      }
    }
  }, [theme.palette.success.main, theme.palette.error.main]);

  useEffect(() => {
    const currentSymbol = symbol;
    connect(currentSymbol, selectedTimeframe);
    return () => {
      if (currentSymbol === symbol) {
        disconnect();
      }
    };
  }, [symbol, selectedTimeframe]);

  useEffect(() => {
    if (marketData[symbol]) {
      updateChartData(marketData[symbol]);
    }
  }, [marketData, symbol, updateChartData]);

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const handleTimeframeChange = (event: any) => {
    setSelectedTimeframe(event.target.value);
  };

  return (
    <Paper
      sx={{
        p: 2,
        height: isFullscreen ? '100vh' : '100%',
        position: isFullscreen ? 'fixed' : 'relative',
        top: isFullscreen ? 0 : 'auto',
        left: isFullscreen ? 0 : 'auto',
        right: isFullscreen ? 0 : 'auto',
        bottom: isFullscreen ? 0 : 'auto',
        zIndex: isFullscreen ? theme.zIndex.modal : 'auto',
        m: isFullscreen ? 0 : 'auto',
        borderRadius: isFullscreen ? 0 : 1,
      }}
    >
      <Grid container spacing={2} alignItems="center" sx={{ mb: 2 }}>
        <Grid item xs>
          <Stack direction="row" spacing={2} alignItems="center">
            <ChartIcon />
            <Typography variant="h6" component="div">
              {symbol}
            </Typography>
            <Chip
              label={lastPrice ? `$${lastPrice.toFixed(2)}` : 'Chargement...'}
              color={priceChange >= 0 ? 'success' : 'error'}
              variant="outlined"
            />
            <Chip
              label={`${priceChange >= 0 ? '+' : ''}${priceChange.toFixed(2)}%`}
              color={priceChange >= 0 ? 'success' : 'error'}
              variant="outlined"
              size="small"
            />
            <FormControl variant="outlined" size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Intervalle</InputLabel>
              <Select
                value={selectedTimeframe}
                onChange={handleTimeframeChange}
                label="Intervalle"
              >
                {Object.entries(TIMEFRAMES).map(([value, label]) => (
                  <MenuItem key={value} value={value}>
                    {label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Stack>
        </Grid>
        <Grid item>
          <Stack direction="row" spacing={1}>
            <Tooltip title="Paramètres">
              <IconButton>
                <Settings />
              </IconButton>
            </Tooltip>
            <Tooltip title="Indicateurs">
              <IconButton>
                <Timeline />
              </IconButton>
            </Tooltip>
            <Tooltip title={isFullscreen ? "Quitter le plein écran" : "Plein écran"}>
              <IconButton onClick={toggleFullscreen}>
                {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
              </IconButton>
            </Tooltip>
          </Stack>
        </Grid>
      </Grid>
      <Divider sx={{ my: 2 }} />
      <Box
        ref={chartContainerRef}
        sx={{
          width: '100%',
          height: isFullscreen ? 'calc(100vh - 200px)' : '500px',
        }}
      />
    </Paper>
  );
};
