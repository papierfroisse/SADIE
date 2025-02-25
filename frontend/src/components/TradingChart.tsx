import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Select, 
  MenuItem, 
  FormControl, 
  InputLabel, 
  Grid, 
  Alert, 
  CircularProgress,
  Typography,
  SelectChangeEvent
} from '@mui/material';
import { Line } from 'react-chartjs-2';
import {
  Chart,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartData,
  ChartOptions
} from 'chart.js';
import useWebSocket from '../hooks/useWebSocket';

Chart.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface KrakenOHLCData {
  time: number;
  etime: number;
  open: string;
  high: string;
  low: string;
  close: string;
  vwap: string;
  volume: string;
  count: number;
}

interface KrakenTickerData {
  p: [string, string];  // price array [today's first trade price, last trade price]
  v: [string, string];  // volume array [today, last 24 hours]
  t: [number, number];  // number of trades array [today, last 24 hours]
}

interface TradingChartProps {
  symbols: string[];
  defaultSymbol?: string;
  defaultInterval?: string;
}

const TradingChart: React.FC<TradingChartProps> = ({ 
  symbols, 
  defaultSymbol = 'XBT/USD',
  defaultInterval = '1m' 
}) => {
  const [selectedSymbol, setSelectedSymbol] = useState(defaultSymbol);
  const [selectedInterval, setSelectedInterval] = useState(defaultInterval);
  const [ohlcData, setOHLCData] = useState<KrakenOHLCData[]>([]);
  const [tickerData, setTickerData] = useState<KrakenTickerData | null>(null);
  
  const { state, isConnected } = useWebSocket(selectedSymbol, selectedInterval);

  useEffect(() => {
    if (state?.marketData && state.marketData[selectedSymbol]) {
      const newData = state.marketData[selectedSymbol];
      const newOHLC = {
        time: newData.timestamp,
        etime: newData.timestamp,
        open: newData.price.toString(),
        high: newData.price.toString(),
        low: newData.price.toString(),
        close: newData.price.toString(),
        vwap: '0',
        volume: newData.quantity.toString(),
        count: 1
      };
      
      setOHLCData(prev => {
        const updated = [...prev, newOHLC].slice(-100);
        return updated;
      });

      // Mise à jour des données du ticker
      setTickerData({
        p: [newData.price.toString(), newData.price.toString()],
        v: [newData.quantity.toString(), newData.quantity.toString()],
        t: [Date.now(), Date.now()]
      });
    }
  }, [state, selectedSymbol]);

  const chartData: ChartData<'line'> = {
    labels: ohlcData.map(d => new Date(d.time).toLocaleTimeString()),
    datasets: [
      {
        label: `${selectedSymbol} Price`,
        data: ohlcData.map(d => parseFloat(d.close)),
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
        fill: false
      }
    ]
  };

  const chartOptions: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: `${selectedSymbol} Chart`,
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      },
      x: {
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      }
    },
    animation: {
      duration: 0
    }
  };

  const handleSymbolChange = (event: SelectChangeEvent<string>) => {
    setSelectedSymbol(event.target.value);
  };

  const handleIntervalChange = (event: SelectChangeEvent<string>) => {
    setSelectedInterval(event.target.value);
  };

  return (
    <Box sx={{ p: 2 }}>
      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid item xs={12}>
          {!isConnected && (
            <Alert severity="warning" sx={{ mb: 2 }}>
              Connexion au serveur en cours... <CircularProgress size={20} sx={{ ml: 1 }} />
            </Alert>
          )}
        </Grid>
        <Grid item xs={6}>
          <FormControl fullWidth>
            <InputLabel>Symbol</InputLabel>
            <Select<string>
              value={selectedSymbol}
              label="Symbol"
              onChange={handleSymbolChange}
            >
              {symbols.map((symbol) => (
                <MenuItem key={symbol} value={symbol}>
                  {symbol}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={6}>
          <FormControl fullWidth>
            <InputLabel>Interval</InputLabel>
            <Select<string>
              value={selectedInterval}
              label="Interval"
              onChange={handleIntervalChange}
            >
              <MenuItem value="1m">1 minute</MenuItem>
              <MenuItem value="5m">5 minutes</MenuItem>
              <MenuItem value="15m">15 minutes</MenuItem>
              <MenuItem value="30m">30 minutes</MenuItem>
              <MenuItem value="1h">1 hour</MenuItem>
              <MenuItem value="4h">4 hours</MenuItem>
              <MenuItem value="1d">1 day</MenuItem>
            </Select>
          </FormControl>
        </Grid>
      </Grid>
      
      <Box sx={{ height: 500, position: 'relative' }}>
        <Line data={chartData} options={chartOptions} />
      </Box>
      
      {tickerData && (
        <Grid container spacing={2} sx={{ mt: 2 }}>
          <Grid item xs={4}>
            <Box sx={{ 
              p: 2, 
              bgcolor: 'background.paper', 
              borderRadius: 1,
              textAlign: 'center'
            }}>
              <Typography variant="subtitle2" color="textSecondary">
                Last Price
              </Typography>
              <Typography variant="h6">
                {parseFloat(tickerData.p[1]).toFixed(2)}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={4}>
            <Box sx={{ 
              p: 2, 
              bgcolor: 'background.paper', 
              borderRadius: 1,
              textAlign: 'center'
            }}>
              <Typography variant="subtitle2" color="textSecondary">
                24h Volume
              </Typography>
              <Typography variant="h6">
                {parseFloat(tickerData.v[1]).toFixed(2)}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={4}>
            <Box sx={{ 
              p: 2, 
              bgcolor: 'background.paper', 
              borderRadius: 1,
              textAlign: 'center'
            }}>
              <Typography variant="subtitle2" color="textSecondary">
                24h Change
              </Typography>
              <Typography variant="h6" color={
                parseFloat(tickerData.p[1]) > parseFloat(tickerData.p[0]) 
                  ? 'success.main' 
                  : 'error.main'
              }>
                {(((parseFloat(tickerData.p[1]) - parseFloat(tickerData.p[0])) / 
                   parseFloat(tickerData.p[0])) * 100).toFixed(2)}%
              </Typography>
            </Box>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default TradingChart; 
