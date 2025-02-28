export interface MarketData {
    type: string;
    symbol: string;
    timeframe: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
    timestamp: number;
}

export interface Alert {
    id: string;
    symbol: string;
    type: 'price' | 'volume' | 'indicator';
    condition: string;
    value: number;
    notificationType: 'browser' | 'email';
    triggered: boolean;
    createdAt: number;
    triggeredAt?: number;
}

export interface WebSocketMessage {
    type: 'market_data' | 'alert' | 'order' | 'trade';
    symbol: string;
    timeframe?: string;
    timestamp: number;
    open?: number;
    high?: number;
    low?: number;
    close?: number;
    volume?: number;
    data?: any;
}

export interface TechnicalIndicator {
    id: string;
    name: string;
    type: string;
    parameters: Record<string, any>;
    value: number;
    timestamp: number;
}

export interface Order {
    id: string;
    symbol: string;
    type: 'market' | 'limit';
    side: 'buy' | 'sell';
    quantity: number;
    price?: number;
    status: 'open' | 'filled' | 'cancelled';
    createdAt: number;
    updatedAt: number;
}

export interface ApiResponse<T> {
    success: boolean;
    data?: T;
    error?: string;
} 