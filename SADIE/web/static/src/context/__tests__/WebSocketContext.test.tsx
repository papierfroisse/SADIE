import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { WebSocketProvider, useWebSocket } from '../WebSocketContext';
import { act } from 'react';
import { MarketData, Alert } from '../../types';

// Mock WebSocket implementation
class MockWebSocket implements WebSocket {
  static readonly CONNECTING = 0;
  static readonly OPEN = 1;
  static readonly CLOSING = 2;
  static readonly CLOSED = 3;

  readonly CONNECTING = MockWebSocket.CONNECTING;
  readonly OPEN = MockWebSocket.OPEN;
  readonly CLOSING = MockWebSocket.CLOSING;
  readonly CLOSED = MockWebSocket.CLOSED;

  url: string;
  readyState: number = MockWebSocket.OPEN;
  bufferedAmount: number = 0;
  extensions: string = '';
  protocol: string = '';
  binaryType: BinaryType = 'blob';

  onopen: ((this: WebSocket, ev: Event) => void) | null = null;
  onclose: ((this: WebSocket, ev: CloseEvent) => void) | null = null;
  onmessage: ((this: WebSocket, ev: MessageEvent<string>) => void) | null = null;
  onerror: ((this: WebSocket, ev: Event) => void) | null = null;

  constructor(url: string) {
    this.url = url;
    setTimeout(() => {
      if (this.onopen) {
        this.onopen.call(this, new Event('open'));
      }
    }, 0);
  }

  close(code?: number, reason?: string): void {
    this.readyState = MockWebSocket.CLOSED;
    if (this.onclose) {
      this.onclose.call(this, new CloseEvent('close', { code, reason }));
    }
  }

  send(data: string | ArrayBufferLike | Blob | ArrayBufferView): void {
    // Mock implementation
    if (this.onmessage) {
      const mockData: MarketData = {
        symbol: 'BTCUSDT',
        timestamp: Date.now(),
        data: {
          open: 50000,
          high: 51000,
          low: 49000,
          close: 50500,
          volume: 100,
        },
      };
      
      this.onmessage.call(
        this,
        new MessageEvent('message', {
          data: JSON.stringify({
            type: 'market_data',
            data: mockData,
          }),
        })
      );
    }
  }

  addEventListener<K extends keyof WebSocketEventMap>(
    type: K,
    listener: (this: WebSocket, ev: WebSocketEventMap[K]) => void
  ): void {
    switch (type) {
      case 'open':
        this.onopen = listener as (this: WebSocket, ev: Event) => void;
        break;
      case 'close':
        this.onclose = listener as (this: WebSocket, ev: CloseEvent) => void;
        break;
      case 'message':
        this.onmessage = listener as (this: WebSocket, ev: MessageEvent<string>) => void;
        break;
      case 'error':
        this.onerror = listener as (this: WebSocket, ev: Event) => void;
        break;
    }
  }

  removeEventListener<K extends keyof WebSocketEventMap>(
    type: K,
    listener: (this: WebSocket, ev: WebSocketEventMap[K]) => void
  ): void {
    switch (type) {
      case 'open':
        this.onopen = null;
        break;
      case 'close':
        this.onclose = null;
        break;
      case 'message':
        this.onmessage = null;
        break;
      case 'error':
        this.onerror = null;
        break;
    }
  }

  dispatchEvent(event: Event): boolean {
    return true;
  }
}

// Replace global WebSocket with mock
Object.defineProperty(window, 'WebSocket', {
  value: MockWebSocket,
  writable: true,
  configurable: true,
});

// Test component
const TestComponent = () => {
  const { marketData, isConnected, connect, disconnect, error } = useWebSocket();
  return (
    <div>
      <div data-testid="market-data">{JSON.stringify(marketData)}</div>
      <div data-testid="connection-status">{isConnected ? 'connected' : 'disconnected'}</div>
      {error && <div data-testid="error-message">{error}</div>}
      <button onClick={() => connect('BTCUSDT')}>Connect</button>
      <button onClick={disconnect}>Disconnect</button>
    </div>
  );
};

describe('WebSocketContext', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('provides WebSocket context to children', () => {
    render(
      <WebSocketProvider>
        <TestComponent />
      </WebSocketProvider>
    );
    expect(screen.getByTestId('connection-status')).toHaveTextContent('disconnected');
  });

  it('connects to WebSocket when connect is called', async () => {
    render(
      <WebSocketProvider>
        <TestComponent />
      </WebSocketProvider>
    );

    fireEvent.click(screen.getByText('Connect'));

    await waitFor(() => {
      expect(screen.getByTestId('connection-status')).toHaveTextContent('connected');
    });
  });

  it('receives market data messages', async () => {
    render(
      <WebSocketProvider>
        <TestComponent />
      </WebSocketProvider>
    );

    fireEvent.click(screen.getByText('Connect'));

    await waitFor(() => {
      const marketDataElement = screen.getByTestId('market-data');
      const data = JSON.parse(marketDataElement.textContent || '{}');
      expect(data).toHaveProperty('BTCUSDT');
    });
  });

  it('handles WebSocket errors', async () => {
    render(
      <WebSocketProvider>
        <TestComponent />
      </WebSocketProvider>
    );

    fireEvent.click(screen.getByText('Connect'));

    const ws = new MockWebSocket('ws://localhost:8000/ws/BTCUSDT');
    act(() => {
      ws.onerror?.(new Event('error'));
    });

    await waitFor(() => {
      expect(screen.getByTestId('connection-status')).toHaveTextContent('disconnected');
      expect(screen.getByTestId('error-message')).toHaveTextContent('WebSocket connection error');
    });
  });
});
