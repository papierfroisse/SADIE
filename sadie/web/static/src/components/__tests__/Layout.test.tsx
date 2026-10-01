import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material';
import { Layout } from '../Layout';
import { WebSocketProvider } from '../../context/WebSocketContext';

// Mock du contexte WebSocket.
// `useWebSocket` doit être un `jest.fn` : plusieurs tests appellent
// `mockImplementation` dessus. Déclaré comme simple fonction fléchée, l'appel
// levait « mockUseWebSocket.mockImplementation is not a function ».
jest.mock('../../context/WebSocketContext', () => ({
  WebSocketProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useWebSocket: jest.fn(() => ({
    connect: jest.fn(),
    disconnect: jest.fn(),
    isConnected: true,
    lastAlert: null,
  })),
}));

const theme = createTheme({
  palette: {
    mode: 'dark',
  },
});

// Arbre réutilisable : `rerender` a besoin d'un arbre neuf mais
// structurellement identique pour se réconcilier sur la même instance.
const withProviders = (children: React.ReactNode) => (
  <BrowserRouter>
    <ThemeProvider theme={theme}>
      <WebSocketProvider>{children}</WebSocketProvider>
    </ThemeProvider>
  </BrowserRouter>
);

const renderWithProviders = (children: React.ReactNode) => render(withProviders(children));

const mockUseWebSocket = jest.requireMock('../../context/WebSocketContext')
  .useWebSocket as jest.Mock;

// Contexte neutre, réutilisé par chaque test.
const mockContexte = (lastAlert: unknown = null) => ({
  connect: jest.fn(),
  disconnect: jest.fn(),
  isConnected: true,
  lastAlert,
});

describe('Layout Component', () => {
  beforeEach(() => {
    // Chaque test repart d'un contexte neutre : sans cette remise à zéro, le
    // `mockImplementation` posé par un test (alerte déclenchée, déconnexion…)
    // fuyait sur les tests suivants et faussait leurs assertions.
    mockUseWebSocket.mockReset();
    mockUseWebSocket.mockImplementation(() => mockContexte());
  });

  it('renders the app title', () => {
    renderWithProviders(<Layout>Test Content</Layout>);
    expect(screen.getByText(/SADIE - Système d'Analyse de Données/)).toBeInTheDocument();
  });

  it('renders all navigation items', () => {
    renderWithProviders(<Layout>Test Content</Layout>);
    expect(screen.getByText('Trading Chart')).toBeInTheDocument();
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
    expect(screen.getByText('En ligne')).toBeInTheDocument();
  });

  it('shows the disconnected status when the socket is down', () => {
    mockUseWebSocket.mockImplementation(() => ({ ...mockContexte(), isConnected: false }));
    renderWithProviders(<Layout>Test Content</Layout>);
    expect(screen.getByText('Hors ligne')).toBeInTheDocument();
  });

  describe('Notifications', () => {
    const alerte = {
      id: '1',
      symbol: 'BTCUSDT',
      condition: 'above',
      value: 50000,
      triggered: true,
    };

    it('shows empty notification message when no notifications', () => {
      renderWithProviders(<Layout>Test Content</Layout>);

      fireEvent.click(screen.getByTestId('notification-button'));

      expect(screen.getByText('Aucune nouvelle notification')).toBeInTheDocument();
    });

    it('shows notification badge when new alert is received', async () => {
      mockUseWebSocket.mockImplementation(() => mockContexte(alerte));

      renderWithProviders(<Layout>Test Content</Layout>);

      await waitFor(() => {
        expect(screen.getByTestId('notification-button')).toHaveAccessibleName('Notifications (1)');
      });
    });

    it('lists the received alert with its relative time', async () => {
      mockUseWebSocket.mockImplementation(() => mockContexte(alerte));

      renderWithProviders(<Layout>Test Content</Layout>);

      await waitFor(() => {
        expect(screen.getByTestId('notification-button')).toHaveAccessibleName('Notifications (1)');
      });

      fireEvent.click(screen.getByTestId('notification-button'));

      expect(screen.getByText('Alerte BTCUSDT: above 50000')).toBeInTheDocument();
      expect(screen.getByText(/instant/i)).toBeInTheDocument();
    });

    it('clears notification count when notifications are viewed', async () => {
      mockUseWebSocket.mockImplementation(() => mockContexte(alerte));

      renderWithProviders(<Layout>Test Content</Layout>);

      await waitFor(() => {
        expect(screen.getByTestId('notification-button')).toHaveAccessibleName('Notifications (1)');
      });

      fireEvent.click(screen.getByTestId('notification-button'));
      fireEvent.click(screen.getByText('Alerte BTCUSDT: above 50000'));

      await waitFor(() => {
        expect(screen.getByTestId('notification-button')).toHaveAccessibleName('Notifications');
      });
    });

    it('does not count the same alert twice', async () => {
      // Le fournisseur peut renvoyer un objet `lastAlert` neuf à chaque rendu
      // sans que l'alerte change : elle ne doit être comptée qu'une seule fois.
      mockUseWebSocket.mockImplementation(() => mockContexte(alerte));

      const view = renderWithProviders(<Layout>Test Content</Layout>);
      view.rerender(withProviders(<Layout>Test Content</Layout>));
      view.rerender(withProviders(<Layout>Test Content</Layout>));

      await waitFor(() => {
        expect(screen.getByTestId('notification-button')).toHaveAccessibleName('Notifications (1)');
      });
    });

    it('keeps only the ten most recent notifications', () => {
      const view = renderWithProviders(<Layout>Test Content</Layout>);

      for (let i = 0; i < 15; i++) {
        mockUseWebSocket.mockImplementation(() =>
          mockContexte({
            id: `alert-${i}`,
            symbol: `BTC${i}USDT`,
            condition: 'above',
            value: 50000,
            triggered: true,
          })
        );
        view.rerender(withProviders(<Layout>Test Content</Layout>));
      }

      fireEvent.click(screen.getByTestId('notification-button'));

      expect(screen.getAllByText(/Alerte BTC\d+USDT: above 50000/)).toHaveLength(10);
    });
  });
});
