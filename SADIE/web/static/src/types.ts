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
    triggered: boolean;
    createdAt: number;
    triggeredAt?: number;
} 