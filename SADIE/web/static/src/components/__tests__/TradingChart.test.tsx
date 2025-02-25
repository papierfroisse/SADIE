import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ThemeProvider, createTheme } from '@mui/material';
import { TradingChart } from '../TradingChart';
import { WebSocketProvider } from '../../context/WebSocketContext';

// Mock du contexte WebSocket
jest.mock('../../context/WebSocketContext', () => ({
  WebSocketProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useWebSocket: () => ({
    connect: jest.fn(),
    disconnect: jest.fn(),
    marketData: {},
    isConnected: true,
  }),
}));

// Mock de lightweight-charts
jest.mock('lightweight-charts', () => ({
  createChart: () => ({
    applyOptions: jest.fn(),
    addCandlestickSeries: () => ({
      update: jest.fn(),
    }),
    addHistogramSeries: () => ({
      update: jest.fn(),
      priceScale: () => ({
        applyOptions: jest.fn(),
      }),
    }),
    remove: jest.fn(),
  }),
}));

const theme = createTheme({
  palette: {
    mode: 'dark',
  },
});

const renderWithProviders = (children: React.ReactNode) => {
  return render(
    <ThemeProvider theme={theme}>
      <WebSocketProvider>{children}</WebSocketProvider>
    </ThemeProvider>
  );
};

describe('TradingChart Component', () => {
  const symbol = 'BTCUSDT';

  beforeEach(() => {
    // Reset des mocks
    jest.clearAllMocks();
  });

  it('renders the symbol', () => {
    renderWithProviders(<TradingChart symbol={symbol} />);
    expect(screen.getByText(/BTCUSDT/)).toBeInTheDocument();
  });

  it('shows connection status', () => {
    renderWithProviders(<TradingChart symbol={symbol} />);
    const statusElements = screen.getAllByText((content, element) => {
      return (
        (element?.textContent?.includes('BTCUSDT') && element?.textContent?.includes('🟢')) || false
      );
    });
    expect(statusElements.length).toBeGreaterThan(0);
  });

  it('creates a chart container', () => {
    renderWithProviders(<TradingChart symbol={symbol} />);
    const container = screen.getByTestId('chart-container');
    expect(container).toBeInTheDocument();
  });
});
