import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { Layout } from './components/Layout';
import { TradingChart } from './components/TradingChart';
import { AlertList } from './components/AlertList';
import { WebSocketProvider } from './context/WebSocketContext';
import { getTheme } from './theme/theme';
import Metrics from './pages/Metrics';
import DashboardPage from './pages/Dashboard';
import PrometheusSettings from './pages/PrometheusSettings';
import Login from './pages/Login';
import UserProfile from './pages/UserProfile';
import { isAuthenticated } from './services/api';

// Composant pour protéger les routes
interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const location = useLocation();
  
  if (!isAuthenticated()) {
    // Rediriger vers login si non authentifié
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }

  return <>{children}</>;
};

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
          <Routes>
            {/* Route publique pour la connexion */}
            <Route path="/login" element={<Login />} />
            
            {/* Routes protégées */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Layout onToggleTheme={handleToggleTheme} isDarkMode={isDarkMode}>
                    <DashboardPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/trading/:symbol"
              element={
                <ProtectedRoute>
                  <Layout onToggleTheme={handleToggleTheme} isDarkMode={isDarkMode}>
                    <TradingChart symbol="BTCUSDT" />
                  </Layout>
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/alerts"
              element={
                <ProtectedRoute>
                  <Layout onToggleTheme={handleToggleTheme} isDarkMode={isDarkMode}>
                    <AlertList />
                  </Layout>
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/metrics"
              element={
                <ProtectedRoute>
                  <Layout onToggleTheme={handleToggleTheme} isDarkMode={isDarkMode}>
                    <Metrics />
                  </Layout>
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/settings/prometheus"
              element={
                <ProtectedRoute>
                  <Layout onToggleTheme={handleToggleTheme} isDarkMode={isDarkMode}>
                    <PrometheusSettings />
                  </Layout>
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <Layout onToggleTheme={handleToggleTheme} isDarkMode={isDarkMode}>
                    <UserProfile />
                  </Layout>
                </ProtectedRoute>
              }
            />
            
            {/* Redirection par défaut vers le dashboard */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </WebSocketProvider>
    </ThemeProvider>
  );
};

export default App;
