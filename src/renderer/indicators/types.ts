import { Candle } from '../CandlestickRenderer';

// Types de base pour les indicateurs
export type IndicatorType = 'sma' | 'ema' | 'rsi' | 'macd' | 'bb' | 'stoch' | 'volume' | 'fi';

export interface IndicatorValue {
  time: number;
  value: number;
  color?: string;
}

export interface IndicatorStyle {
  color: string;
  lineWidth: number;
  opacity: number;
  dashArray?: number[];
  fillColor?: string;
  fillOpacity?: number;
}

export interface IndicatorParams {
  period?: number;
  source?: 'open' | 'high' | 'low' | 'close' | 'volume';
  fastPeriod?: number;
  slowPeriod?: number;
  signalPeriod?: number;
  standardDeviations?: number;
  kPeriod?: number;
  dPeriod?: number;
  smoothK?: number;
  smoothD?: number;
  overBought?: number;
  overSold?: number;
}

export interface IndicatorConfig {
  id: string;
  type: IndicatorType;
  params: IndicatorParams;
  style: IndicatorStyle;
  visible: boolean;
  overlay: boolean;
  height?: number;
  precision?: number;
}

// Interface pour les indicateurs
export interface Indicator {
  // Configuration
  getConfig(): IndicatorConfig;
  setParams(params: Partial<IndicatorParams>): void;
  setStyle(style: Partial<IndicatorStyle>): void;
  setVisible(visible: boolean): void;
  
  // Calcul des valeurs
  calculate(candles: Candle[]): IndicatorValue[];
  
  // Rendu
  render(ctx: CanvasRenderingContext2D, viewport: Viewport): void;
  
  // Gestion des événements
  onMouseMove?(x: number, y: number): void;
  onClick?(x: number, y: number): void;
}

// Interface pour le gestionnaire d'indicateurs
export interface IndicatorManager {
  // Gestion des indicateurs
  addIndicator(indicator: Indicator): void;
  removeIndicator(id: string): void;
  getIndicator(id: string): Indicator | null;
  getAllIndicators(): Indicator[];
  
  // Calcul et mise en cache
  calculateAll(candles: Candle[]): void;
  clearCache(): void;
  
  // Rendu
  render(viewport: Viewport): void;
  resize(width: number, height: number): void;
  dispose(): void;
}

// Interface pour le viewport (reprise de ChartRenderer)
export interface Viewport {
  xMin: number;
  xMax: number;
  yMin: number;
  yMax: number;
} 