import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider } from '@mui/material';
import { AlertList } from '../AlertList';
import { createTheme } from '@mui/material';
import '@testing-library/jest-dom';

const mockApiService = {
  getAlerts: jest.fn(),
  createAlert: jest.fn(),
  deleteAlert: jest.fn()
};

jest.mock('../../services/api', () => ({
  apiService: mockApiService
}));

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2'
    }
  }
});

const renderWithTheme = (component: React.ReactNode) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('AlertList', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockApiService.getAlerts.mockResolvedValue({ 
      success: true, 
      data: [{ id: '1', symbol: 'BTCUSDT', price: 50000, condition: '>', createdAt: new Date() }] 
    });
  });

  it('renders alerts title', () => {
    renderWithTheme(<AlertList />);
    expect(screen.getByText('Alertes')).toBeInTheDocument();
  });

  it('loads and displays alerts', async () => {
    renderWithTheme(<AlertList />);
    expect(mockApiService.getAlerts).toHaveBeenCalled();
    expect(await screen.findByText('BTCUSDT')).toBeInTheDocument();
  });

  it('opens create alert dialog when button is clicked', async () => {
    renderWithTheme(<AlertList />);
    fireEvent.click(screen.getByText('Nouvelle Alerte'));
    expect(screen.getByText('Créer une Alerte')).toBeInTheDocument();
  });

  it('creates a new alert', async () => {
    mockApiService.createAlert.mockResolvedValue({ success: true, data: { id: '2' } });
    renderWithTheme(<AlertList />);
    
    fireEvent.click(screen.getByText('Nouvelle Alerte'));
    
    const symbolInput = screen.getByLabelText('Symbole');
    const priceInput = screen.getByLabelText('Prix');
    const conditionSelect = screen.getByLabelText('Condition');
    
    fireEvent.change(symbolInput, { target: { value: 'ETHUSDT' } });
    fireEvent.change(priceInput, { target: { value: '3000' } });
    fireEvent.change(conditionSelect, { target: { value: '>' } });
    
    fireEvent.click(screen.getByText('Créer'));
    
    expect(mockApiService.createAlert).toHaveBeenCalledWith({
      symbol: 'ETHUSDT',
      price: 3000,
      condition: '>'
    });
  });

  it('deletes an alert', async () => {
    mockApiService.deleteAlert.mockResolvedValue({ success: true });
    mockApiService.getAlerts.mockResolvedValue({ 
      success: true, 
      data: [{ id: '1', symbol: 'BTCUSDT', price: 50000, condition: '>', createdAt: new Date() }] 
    });
    
    renderWithTheme(<AlertList />);
    
    await screen.findByText('BTCUSDT');
    
    const deleteButton = await screen.findByTestId('delete-alert-1');
    fireEvent.click(deleteButton);
    
    expect(mockApiService.deleteAlert).toHaveBeenCalledWith('1');
  });
}); 
