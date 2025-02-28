import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ThemeProvider, createTheme } from '@mui/material';
import { act } from '@testing-library/react';
import { AlertList } from '../AlertList';
import { WebSocketProvider } from '../../context/WebSocketContext';
import { format } from 'date-fns';
import { Alert, MarketData } from '../../types';
import { useAlerts } from '../../hooks/useAlerts';

// Mock du contexte WebSocket
const mockWebSocket = {
  connect: jest.fn(),
  disconnect: jest.fn(),
  isConnected: true,
  lastAlert: null as Alert | null,
  marketData: {} as Record<string, MarketData>,
  error: null as string | null,
  lastUpdate: null as MarketData | null,
};

jest.mock('../../context/WebSocketContext', () => ({
  WebSocketProvider: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="websocket-provider">{children}</div>
  ),
  useWebSocket: () => mockWebSocket,
}));

// Mock de l'API
jest.mock('../../services/api', () => ({
  api: {
    getAlerts: jest.fn(),
    createAlert: jest.fn(),
    deleteAlert: jest.fn(),
  },
}));

const mockApi = jest.requireMock('../../services/api').api;

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

// Mock Notification API
const mockNotification = jest.fn();

// Mock des hooks
jest.mock('../../hooks/useAlerts', () => ({
  useAlerts: jest.fn(),
}));

beforeAll(() => {
  // @ts-expect-error Mocking Notification API for testing
  global.Notification = class MockNotification {
    constructor(title: string, options?: NotificationOptions) {
      mockNotification(title, options);
    }
  };
  Object.defineProperty(global.Notification, 'permission', {
    writable: true,
    value: 'default',
  });
  Object.defineProperty(global.Notification, 'requestPermission', {
    writable: true,
    value: jest.fn().mockResolvedValue('granted'),
  });
});

beforeEach(() => {
  mockApi.getAlerts.mockReset();
  mockApi.createAlert.mockReset();
  mockApi.deleteAlert.mockReset();
  mockApi.getAlerts.mockResolvedValue({ success: true, data: [] });
  mockWebSocket.lastAlert = null;
  mockWebSocket.error = null;
  mockWebSocket.isConnected = true;
  mockNotification.mockReset();
  Object.defineProperty(global.Notification, 'permission', {
    writable: true,
    value: 'default',
  });
  (global.Notification.requestPermission as jest.Mock).mockReset();
  (global.Notification.requestPermission as jest.Mock).mockResolvedValue('granted');
});

describe('AlertList Component', () => {
  const mockAlerts: Alert[] = [
    {
      id: '1',
      symbol: 'BTC/USDT',
      type: 'price',
      condition: '>',
      value: 50000,
      notificationType: 'browser',
      createdAt: Date.now(),
      triggered: false,
    },
    {
      id: '2',
      symbol: 'ETH/USDT',
      type: 'volume',
      condition: '<',
      value: 1000,
      notificationType: 'browser',
      createdAt: Date.now(),
      triggered: true,
      triggeredAt: Date.now(),
    },
  ];

  const mockDeleteAlert = jest.fn().mockResolvedValue(undefined);
  const mockCreateAlert = jest.fn().mockResolvedValue(undefined);

  beforeEach(() => {
    (useAlerts as jest.Mock).mockReturnValue({
      alerts: mockAlerts,
      loading: false,
      error: null,
      lastTriggered: null,
      createAlert: mockCreateAlert,
      deleteAlert: mockDeleteAlert,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders alert list correctly', () => {
    render(<AlertList />);
    
    // Vérifier que le titre est présent
    expect(screen.getByText(/Alertes/i)).toBeInTheDocument();
    
    // Vérifier que les alertes sont affichées
    expect(screen.getByText('BTC/USDT')).toBeInTheDocument();
    expect(screen.getByText('ETH/USDT')).toBeInTheDocument();
    
    // Vérifier que les détails des conditions sont présents
    expect(screen.getByText(/Prix > 50000/i)).toBeInTheDocument();
    expect(screen.getByText(/Volume < 1000/i)).toBeInTheDocument();
  });

  test('handles loading state', () => {
    (useAlerts as jest.Mock).mockReturnValue({
      alerts: [],
      loading: true,
      error: null,
      lastTriggered: null,
      createAlert: mockCreateAlert,
      deleteAlert: mockDeleteAlert,
    });
    
    render(<AlertList />);
    
    // Vérifier qu'un indicateur de chargement est affiché
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  test('handles error state', () => {
    const errorMessage = 'Failed to load alerts';
    (useAlerts as jest.Mock).mockReturnValue({
      alerts: [],
      loading: false,
      error: errorMessage,
      lastTriggered: null,
      createAlert: mockCreateAlert,
      deleteAlert: mockDeleteAlert,
    });
    
    render(<AlertList />);
    
    // Vérifier que le message d'erreur est affiché
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  test('deletes an alert when delete button is clicked', async () => {
    render(<AlertList />);
    
    // Trouver tous les boutons de suppression et cliquer sur le premier
    const deleteButtons = screen.getAllByRole('button', { name: /supprimer/i });
    fireEvent.click(deleteButtons[0]);
    
    // Vérifier que la fonction de suppression a été appelée avec le bon ID
    await waitFor(() => {
      expect(mockDeleteAlert).toHaveBeenCalledWith('1');
    });
  });

  test('opens alert creation dialog when Add button is clicked', () => {
    render(<AlertList />);
    
    // Trouver le bouton d'ajout et cliquer dessus
    const addButton = screen.getByText(/Ajouter une alerte/i);
    fireEvent.click(addButton);
    
    // Vérifier que le dialogue d'ajout est affiché
    expect(screen.getByText(/Créer une nouvelle alerte/i)).toBeInTheDocument();
  });
});

describe('AlertList', () => {
  beforeEach(() => {
    mockApi.getAlerts.mockReset();
    mockApi.createAlert.mockReset();
    mockApi.deleteAlert.mockReset();
    mockApi.getAlerts.mockResolvedValue({ success: true, data: [] });
    mockWebSocket.lastAlert = null;
    mockWebSocket.error = null;
    mockWebSocket.isConnected = true;
  });

  it('renders alerts title and new alert button', () => {
    renderWithProviders(<AlertList />);
    expect(screen.getByText('Alertes')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /nouvelle alerte/i })).toBeInTheDocument();
  });

  it('loads and displays alerts with all information', async () => {
    const mockDate = new Date('2024-01-27T12:00:00Z');
    const mockAlerts = [
      {
        id: '1',
        symbol: 'BTCUSDT',
        type: 'price',
        condition: 'above',
        value: 50000,
        notification_type: 'browser',
        created_at: mockDate.toISOString(),
        triggered: false,
      },
    ];

    mockApi.getAlerts.mockResolvedValue({ success: true, data: mockAlerts });

    renderWithProviders(<AlertList />);

    await waitFor(() => {
      expect(screen.getByText(/BTCUSDT/)).toBeInTheDocument();
      expect(screen.getByText(/Prix supérieur à 50000/)).toBeInTheDocument();
      expect(
        screen.getByText(new RegExp(`Créée le ${format(mockDate, 'dd/MM/yyyy HH:mm')}`))
      ).toBeInTheDocument();
    });
  });

  it('handles error when loading alerts', async () => {
    mockApi.getAlerts.mockResolvedValue({ success: false, error: 'Failed to load alerts' });

    renderWithProviders(<AlertList />);

    await waitFor(() => {
      expect(screen.getByText('Erreur lors du chargement des alertes')).toBeInTheDocument();
    });
  });

  it('opens create alert dialog with all fields', async () => {
    renderWithProviders(<AlertList />);

    await act(async () => {
      fireEvent.click(screen.getByTestId('new-alert-button'));
    });

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByLabelText('Symbole')).toBeInTheDocument();
      expect(screen.getByLabelText('Type')).toBeInTheDocument();
      expect(screen.getByLabelText('Condition')).toBeInTheDocument();
      expect(screen.getByLabelText('Valeur')).toBeInTheDocument();
      expect(screen.getByLabelText('Type de notification')).toBeInTheDocument();
    });
  });

  it('creates a new alert and updates the list', async () => {
    const newAlert = {
      symbol: 'BTCUSDT',
      type: 'price',
      condition: 'above',
      value: 50000,
      notification_type: 'browser',
    };

    mockApi.createAlert.mockResolvedValue({
      success: true,
      data: {
        ...newAlert,
        id: '1',
        created_at: new Date().toISOString(),
        triggered: false,
        triggered_at: null,
      },
    });

    renderWithProviders(<AlertList />);

    await act(async () => {
      fireEvent.click(screen.getByTestId('new-alert-button'));
    });

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    await act(async () => {
      const symbolInput = screen.getByTestId('symbol-input').querySelector('input');
      const typeSelect = screen.getByTestId('type-select');
      const conditionSelect = screen.getByTestId('condition-select');
      const priceInput = screen.getByTestId('price-input').querySelector('input');
      const notificationTypeSelect = screen.getByTestId('notification-type-select');

      if (symbolInput && priceInput) {
        fireEvent.change(symbolInput, { target: { value: newAlert.symbol } });
        fireEvent.change(priceInput, { target: { value: newAlert.value } });
      }

      // Pour les Select, nous devons d'abord ouvrir le menu
      fireEvent.mouseDown(typeSelect);
      await waitFor(() => {
        const option = screen.getByText('Prix');
        fireEvent.click(option);
      });

      fireEvent.mouseDown(conditionSelect);
      await waitFor(() => {
        const option = screen.getByText('Au-dessus de');
        fireEvent.click(option);
      });

      fireEvent.mouseDown(notificationTypeSelect);
      await waitFor(() => {
        const option = screen.getByText('Navigateur');
        fireEvent.click(option);
      });
    });

    await act(async () => {
      fireEvent.click(screen.getByTestId('create-alert-button'));
    });

    await waitFor(() => {
      expect(mockApi.createAlert).toHaveBeenCalledWith(expect.objectContaining(newAlert));
    });
  });

  it('handles error when creating alert', async () => {
    mockApi.createAlert.mockResolvedValue({ success: false, error: 'Failed to create alert' });

    renderWithProviders(<AlertList />);

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /nouvelle alerte/i }));
    });

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    await act(async () => {
      fireEvent.change(screen.getByLabelText('Symbole'), { target: { value: 'BTCUSDT' } });
      fireEvent.change(screen.getByLabelText('Valeur'), { target: { value: '50000' } });
      fireEvent.click(screen.getByRole('button', { name: /créer/i }));
    });

    await waitFor(() => {
      expect(screen.getByText("Erreur lors de la création de l'alerte")).toBeInTheDocument();
    });
  });

  it('deletes an alert and updates the list', async () => {
    const mockAlert = {
      id: '1',
      symbol: 'BTCUSDT',
      type: 'price',
      condition: 'above',
      value: 50000,
      notification_type: 'browser',
      created_at: new Date().toISOString(),
      triggered: false,
    };

    mockApi.getAlerts.mockResolvedValue({ success: true, data: [mockAlert] });
    mockApi.deleteAlert.mockResolvedValue({ success: true });

    renderWithProviders(<AlertList />);

    await waitFor(() => {
      expect(screen.getByText(/BTCUSDT/)).toBeInTheDocument();
    });

    await act(async () => {
      fireEvent.click(screen.getByTestId('delete-alert-button'));
    });

    await waitFor(() => {
      expect(mockApi.deleteAlert).toHaveBeenCalledWith('1');
      expect(screen.queryByText(/BTCUSDT/)).not.toBeInTheDocument();
    });
  });

  it('handles error when deleting alert', async () => {
    const mockAlert = {
      id: '1',
      symbol: 'BTCUSDT',
      type: 'price',
      condition: 'above',
      value: 50000,
      notification_type: 'browser',
      created_at: new Date().toISOString(),
      triggered: false,
    };

    mockApi.getAlerts.mockResolvedValue({ success: true, data: [mockAlert] });
    mockApi.deleteAlert.mockResolvedValue({ success: false, error: 'Failed to delete alert' });

    renderWithProviders(<AlertList />);

    await waitFor(() => {
      expect(screen.getByText(/BTCUSDT/)).toBeInTheDocument();
    });

    await act(async () => {
      fireEvent.click(screen.getByTestId('delete-alert-button'));
    });

    await waitFor(() => {
      expect(mockApi.deleteAlert).toHaveBeenCalledWith('1');
      expect(screen.getByText("Erreur lors de la suppression de l'alerte")).toBeInTheDocument();
    });
  });
});

describe('AlertList - Notifications', () => {
  beforeEach(() => {
    mockApi.getAlerts.mockReset();
    mockApi.getAlerts.mockResolvedValue({ success: true, data: [] });
  });

  it('requests notification permission on mount', async () => {
    await act(async () => {
      renderWithProviders(<AlertList />);
    });

    expect(global.Notification.requestPermission).toHaveBeenCalled();
  });

  it('shows notification when alert is triggered', async () => {
    const mockAlert = {
      id: '1',
      symbol: 'BTCUSDT',
      type: 'price',
      condition: 'above',
      value: 50000,
      notification_type: 'browser',
      created_at: new Date().toISOString(),
      triggered: true,
      triggered_at: new Date().toISOString(),
    };

    mockWebSocket.lastAlert = mockAlert;
    Object.defineProperty(global.Notification, 'permission', {
      writable: true,
      value: 'granted',
    });

    await act(async () => {
      renderWithProviders(<AlertList />);
    });

    await waitFor(() => {
      expect(mockNotification).toHaveBeenCalledWith(
        expect.stringContaining('BTCUSDT'),
        expect.objectContaining({
          body: expect.stringContaining('50000'),
        })
      );
    });
  });

  it('handles notification permission denied', async () => {
    Object.defineProperty(global.Notification, 'permission', {
      writable: true,
      value: 'denied',
    });
    (global.Notification.requestPermission as jest.Mock).mockResolvedValue('denied');

    await act(async () => {
      renderWithProviders(<AlertList />);
    });

    expect(screen.getByText(/notifications désactivées/i)).toBeInTheDocument();
  });

  it('toggles notifications when button is clicked', async () => {
    Object.defineProperty(global.Notification, 'permission', {
      writable: true,
      value: 'granted',
    });

    await act(async () => {
      renderWithProviders(<AlertList />);
    });

    await act(async () => {
      fireEvent.click(screen.getByTestId('notification-toggle'));
    });

    expect(screen.getByTestId('notification-status')).toHaveTextContent(
      /notifications désactivées/i
    );

    await act(async () => {
      fireEvent.click(screen.getByTestId('notification-toggle'));
    });

    await waitFor(() => {
      expect(global.Notification.requestPermission).toHaveBeenCalled();
      expect(screen.getByTestId('notification-status')).toHaveTextContent(
        /notifications activées/i
      );
    });
  });
});
