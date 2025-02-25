// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Mock ResizeObserver qui n'est pas disponible dans jsdom
class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}
window.ResizeObserver = ResizeObserver;

// Mock WebSocket
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

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  send(data: string | ArrayBufferLike | Blob | ArrayBufferView): void {
    if (this.onmessage) {
      // Simuler une réponse du serveur
      const mockResponse = {
        BTCUSDT: {
          price: '50000',
          volume: '100',
        },
      };
      this.onmessage.call(
        this,
        new MessageEvent('message', {
          data: JSON.stringify(mockResponse),
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
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
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

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  dispatchEvent(event: Event): boolean {
    return true;
  }
}

Object.defineProperty(global, 'WebSocket', {
  value: MockWebSocket,
  writable: true,
  configurable: true,
});
