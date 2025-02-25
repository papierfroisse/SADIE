/// <reference types="jest" />
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { WebSocketProvider, useWebSocket } from '../WebSocketContext';
import { act } from 'react';
import userEvent from '@testing-library/user-event';
import { MarketData } from '../../types';

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

// Rest of the test file... 

const TestComponent = () => {
  const { marketData, isConnected, error, connect, disconnect } = useWebSocket();
  
  return (
    <div>
      <div data-testid="market-data">{JSON.stringify(marketData)}</div>
      <div data-testid="connection-status">{isConnected ? 'connected' : 'disconnected'}</div>
      {error && <div data-testid="error-message">{error}</div>}
      <button onClick={connect}>Connect</button>
      <button onClick={disconnect}>Disconnect</button>
    </div>
  );
};

describe('WebSocketContext', () => {
  let mockWs: MockWebSocket;

  beforeEach(() => {
    mockWs = new MockWebSocket('ws://localhost:8000/ws/BTCUSDT');
    jest.spyOn(global, 'WebSocket').mockImplementation(() => mockWs);
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('connects to WebSocket', async () => {
    render(
      <WebSocketProvider>
        <TestComponent />
      </WebSocketProvider>
    );

    const connectButton = screen.getByText('Connect');
    await userEvent.click(connectButton);

    // Simulate successful connection
    mockWs.onopen?.(new Event('open'));

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

    const connectButton = screen.getByText('Connect');
    await userEvent.click(connectButton);

    // Simulate successful connection
    mockWs.onopen?.(new Event('open'));

    // Simulate receiving market data
    const marketData = {
      BTCUSDT: {
        price: '50000',
        volume: '100',
        timestamp: Date.now()
      }
    };
    mockWs.onmessage?.(new MessageEvent('message', { data: JSON.stringify(marketData) }));

    await waitFor(() => {
      const data = JSON.parse(screen.getByTestId('market-data').textContent || '{}');
      expect(data).toHaveProperty('BTCUSDT');
      expect(data.BTCUSDT).toHaveProperty('price', '50000');
    });
  });

  it('handles WebSocket errors', async () => {
    render(
      <WebSocketProvider>
        <TestComponent />
      </WebSocketProvider>
    );

    const connectButton = screen.getByText('Connect');
    await userEvent.click(connectButton);

    // Simulate connection error
    mockWs.onerror?.(new Event('error'));
    mockWs.onclose?.(new CloseEvent('close'));

    await waitFor(() => {
      expect(screen.getByTestId('connection-status')).toHaveTextContent('disconnected');
      expect(screen.getByTestId('error-message')).toHaveTextContent('WebSocket connection error');
    });
  });
}); 