export interface CandleData {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface Point {
  x: number;
  y: number;
}

export interface Drawing {
  type: 'line' | 'rectangle';
  points: Point[];
  color?: string;
}

export interface Annotation {
  text: string;
  position: Point;
  color?: string;
} 