export interface CandleData {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface ChartOptions {
  width: number;
  height: number;
  padding: number;
  backgroundColor: string;
  candleColors: {
    up: string;
    down: string;
  };
  gridColor: string;
  textColor: string;
  isLogScale?: boolean;
  visibleRange?: {
    start: number;
    end: number;
  };
  indicators: Array<{
    name: string;
    data: number[];
    color: string;
  }>;
  drawings?: Drawing[];
  annotations?: Annotation[];
}

export interface Point {
  timestamp: number;
  price: number;
}

export interface Drawing {
  type: 'line' | 'horizontalLine' | 'verticalLine' | 'rectangle' | 'fibonacci';
  points: Point[];
  color: string;
}

export interface Annotation {
  timestamp: number;
  price: number;
  text: string;
  color: string;
} 