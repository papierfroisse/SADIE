import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { Layout } from './components/Layout';
import { TradingChart } from './components/TradingChart';
import { AlertList } from './components/AlertList';
import { WebSocketProvider } from './context/WebSocketContext';
import { getTheme } from './theme/theme';
import Metrics from './pages/Metrics';
import DashboardPage from './pages/Dashboard';
import PrometheusSettings from './pages/PrometheusSettings';

const App: React.FC = () => {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const savedMode = localStorage.getItem('theme-mode');
    return savedMode
      ? savedMode === 'dark'
      : window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    localStorage.setItem('theme-mode', isDarkMode ? 'dark' : 'light');
  }, [isDarkMode]);

  const handleToggleTheme = () => {
    setIsDarkMode(prev => !prev);
  };

  return (
    <ThemeProvider theme={getTheme(isDarkMode)}>
      <CssBaseline />
      <WebSocketProvider>
        <Router>
          <Layout onToggleTheme={handleToggleTheme} isDarkMode={isDarkMode}>
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/trading/:symbol" element={<TradingChart symbol="BTCUSDT" />} />
              <Route path="/alerts" element={<AlertList />} />
              <Route path="/metrics" element={<Metrics />} />
              <Route path="/settings/prometheus" element={<PrometheusSettings />} />
            </Routes>
          </Layout>
        </Router>
      </WebSocketProvider>
    </ThemeProvider>
  );
};

export default App;
