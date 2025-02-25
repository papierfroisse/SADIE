import React, { useState } from 'react';
import { Box, Grid, Paper, AppBar, Toolbar, Typography, IconButton, CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import { Menu as MenuIcon, Notifications as NotificationsIcon } from '@mui/icons-material';
import { AlertPanel } from './components/trading/AlertPanel';
import { TimeframeSelector } from './components/trading/TimeframeSelector';
import { Sidebar } from './components/layout/Sidebar';
import AlertList from './components/AlertList';
import TradingChart from './components/TradingChart';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
});

// Liste des symboles Kraken supportés
const KRAKEN_SYMBOLS = [
  'XBT/USD',  // Bitcoin
  'ETH/USD',  // Ethereum
  'XMR/USD',  // Monero
  'ADA/USD',  // Cardano
  'USDT/USD', // Tether
];

function App() {
  const [timeframe, setTimeframe] = useState('1h');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ display: 'flex' }}>
        <AppBar position="fixed" sx={{ zIndex: theme => theme.zIndex.drawer + 1 }}>
          <Toolbar>
            <IconButton
              color="inherit"
              edge="start"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
              SADIE Trading Platform
            </Typography>
            <IconButton color="inherit">
              <NotificationsIcon />
            </IconButton>
          </Toolbar>
        </AppBar>

        <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <Box
          component="main"
          sx={{
            flexGrow: 1,
            height: '100vh',
            overflow: 'auto',
            pt: 8,
            px: 3,
            pb: 3,
          }}
        >
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Paper sx={{ p: 2, backgroundColor: '#132F4C' }}>
                <TimeframeSelector value={timeframe} onChange={setTimeframe} />
              </Paper>
            </Grid>
            <Grid item xs={12} md={9}>
              <Paper 
                sx={{ 
                  p: 2, 
                  height: 'calc(100vh - 200px)',
                  backgroundColor: '#132F4C'
                }}
              >
                <TradingChart 
                  symbols={KRAKEN_SYMBOLS}
                  defaultSymbol="XBT/USD"
                  defaultInterval="5"
                />
              </Paper>
            </Grid>
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, height: 'calc(100vh - 200px)', backgroundColor: '#132F4C' }}>
                <AlertPanel />
              </Paper>
            </Grid>
            <Grid item xs={12}>
              <Paper sx={{ p: 2 }}>
                <AlertList />
              </Paper>
            </Grid>
          </Grid>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App; 