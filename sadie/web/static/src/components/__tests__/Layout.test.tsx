import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material';
import { Layout } from '../Layout';
import { WebSocketProvider } from '../../context/WebSocketContext';

// Mock du contexte WebSocket
jest.mock('../../context/WebSocketContext', () => ({
  WebSocketProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useWebSocket: () => ({
    connect: jest.fn(),
    disconnect: jest.fn(),
    isConnected: true,
    lastAlert: null,
  }),
}));

const theme = createTheme({
  palette: {
    mode: 'dark',
  },
});

const renderWithProviders = (children: React.ReactNode) => {
  return render(
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        <WebSocketProvider>{children}</WebSocketProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
};

describe('Layout Component', () => {
  it('renders the app title', () => {
    renderWithProviders(<Layout>Test Content</Layout>);
    expect(screen.getByText('SADIE Trading')).toBeInTheDocument();
  });

  it('renders all navigation items', () => {
    renderWithProviders(<Layout>Test Content</Layout>);
    expect(screen.getByText('Trading')).toBeInTheDocument();
    expect(screen.getByText('Alertes')).toBeInTheDocument();
    expect(screen.getByText('Paramètres')).toBeInTheDocument();
  });

  it('renders children content', () => {
    renderWithProviders(
      <Layout>
        <div>Test Child Content</div>
      </Layout>
    );
    expect(screen.getByText('Test Child Content')).toBeInTheDocument();
  });

  it('shows connection status', () => {
    renderWithProviders(<Layout>Test Content</Layout>);
    expect(screen.getByText('Connecté')).toBeInTheDocument();
  });

  describe('Notifications', () => {
    it('shows empty notification message when no notifications', () => {
      renderWithProviders(<Layout>Test Content</Layout>);

      const notificationButton = screen.getByTestId('notification-button');
      fireEvent.click(notificationButton);

      expect(screen.getByText('Aucune nouvelle notification')).toBeInTheDocument();
    });

    it('shows notification badge when new alert is received', async () => {
      const mockUseWebSocket = jest.requireMock('../../context/WebSocketContext').useWebSocket;
      mockUseWebSocket.mockImplementation(() => ({
        connect: jest.fn(),
        disconnect: jest.fn(),
        isConnected: true,
        lastAlert: {
          id: '1',
          symbol: 'BTCUSDT',
          condition: 'above',
          value: 50000,
          triggered: true,
        },
      }));

      renderWithProviders(<Layout>Test Content</Layout>);

      await waitFor(() => {
        const badge = screen.getByTestId('notification-badge');
        expect(badge).toHaveTextContent('1');
      });
    });

    it('clears notification count when notifications are viewed', async () => {
      const mockUseWebSocket = jest.requireMock('../../context/WebSocketContext').useWebSocket;
      mockUseWebSocket.mockImplementation(() => ({
        connect: jest.fn(),
        disconnect: jest.fn(),
        isConnected: true,
        lastAlert: {
          id: '1',
          symbol: 'BTCUSDT',
          condition: 'above',
          value: 50000,
          triggered: true,
        },
      }));

      renderWithProviders(<Layout>Test Content</Layout>);

      await waitFor(() => {
        const badge = screen.getByTestId('notification-badge');
        expect(badge).toHaveTextContent('1');
      });

      const notificationButton = screen.getByTestId('notification-button');
      fireEvent.click(notificationButton);
      fireEvent.click(screen.getByText(/BTCUSDT/));

      await waitFor(() => {
        const badge = screen.getByTestId('notification-badge');
        expect(badge).toHaveTextContent('0');
      });
    });

    it('formats notification time correctly', async () => {
      // Mock Date.now() pour avoir un temps constant
      const NOW = 1625097600000; // 2021-07-01 12:00:00
      jest.spyOn(Date, 'now').mockImplementation(() => NOW);

      const mockUseWebSocket = jest.requireMock('../../context/WebSocketContext').useWebSocket;
      mockUseWebSocket.mockImplementation(() => ({
        connect: jest.fn(),
        disconnect: jest.fn(),
        isConnected: true,
        lastAlert: {
          id: '1',
          symbol: 'BTCUSDT',
          condition: 'above',
          value: 50000,
          triggered: true,
        },
      }));

      renderWithProviders(<Layout>Test Content</Layout>);

      // Simuler différents temps de notification
      const notifications = [
        { timestamp: NOW, expected: "À l'instant" },
        { timestamp: NOW - 2 * 60 * 1000, expected: 'Il y a 2 minutes' },
        { timestamp: NOW - 60 * 60 * 1000, expected: 'Il y a 1 heure' },
        { timestamp: NOW - 3 * 60 * 60 * 1000, expected: 'Il y a 3 heures' },
      ];

      for (const { timestamp, expected } of notifications) {
        // Mettre à jour le mock avec un nouveau timestamp
        mockUseWebSocket.mockImplementation(() => ({
          connect: jest.fn(),
          disconnect: jest.fn(),
          isConnected: true,
          lastAlert: {
            id: Date.now().toString(),
            symbol: 'BTCUSDT',
            condition: 'above',
            value: 50000,
            triggered: true,
            timestamp,
          },
        }));

        // Forcer un re-render
        renderWithProviders(<Layout>Test Content</Layout>);

        // Ouvrir le menu des notifications
        const notificationButton = screen.getByTestId('notification-button');
        fireEvent.click(notificationButton);

        // Vérifier le format du temps
        await waitFor(() => {
          expect(screen.getByText(expected)).toBeInTheDocument();
        });

        // Fermer le menu des notifications
        fireEvent.click(screen.getByText(/BTCUSDT/));
      }

      // Restaurer Date.now()
      jest.restoreAllMocks();
    });

    it('limits the number of notifications', async () => {
      const mockUseWebSocket = jest.requireMock('../../context/WebSocketContext').useWebSocket;
      const MAX_NOTIFICATIONS = 10;

      // Créer plus que le maximum de notifications
      for (let i = 0; i < MAX_NOTIFICATIONS + 5; i++) {
        mockUseWebSocket.mockImplementation(() => ({
          connect: jest.fn(),
          disconnect: jest.fn(),
          isConnected: true,
          lastAlert: {
            id: i.toString(),
            symbol: `BTC${i}USDT`,
            condition: 'above',
            value: 50000,
            triggered: true,
          },
        }));

        renderWithProviders(<Layout>Test Content</Layout>);
      }

      // Ouvrir le menu des notifications
      const notificationButton = screen.getByTestId('notification-button');
      fireEvent.click(notificationButton);

      // Vérifier que seules les MAX_NOTIFICATIONS plus récentes sont affichées
      const notifications = screen.getAllByText(/BTC.*USDT/);
      expect(notifications).toHaveLength(MAX_NOTIFICATIONS);
    });
  });
});
