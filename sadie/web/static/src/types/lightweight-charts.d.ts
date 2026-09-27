declare module 'lightweight-charts' {
  export interface ChartOptions {
    width?: number;
    height?: number;
    layout?: {
      backgroundColor?: string;
      textColor?: string;
      background?: {
        color: string;
        type?: 'solid' | 'gradient';
        gradient?: {
          startColor: string;
          endColor: string;
        };
      };
      fontFamily?: string;
      fontSize?: number;
    };
    grid?: {
      vertLines?: {
        color?: string;
        style?: number;
        visible?: boolean;
      };
      horzLines?: {
        color?: string;
        style?: number;
        visible?: boolean;
      };
    };
    crosshair?: {
      mode?: number;
      vertLine?: {
        color?: string;
        width?: number;
        style?: number;
        visible?: boolean;
        labelVisible?: boolean;
      };
      horzLine?: {
        color?: string;
        width?: number;
        style?: number;
        visible?: boolean;
        labelVisible?: boolean;
      };
    };
    rightPriceScale?: {
      borderColor?: string;
      borderVisible?: boolean;
      scaleMargins?: {
        top?: number;
        bottom?: number;
      };
      visible?: boolean;
      alignLabels?: boolean;
    };
    timeScale?: {
      rightOffset?: number;
      barSpacing?: number;
      fixLeftEdge?: boolean;
      lockVisibleTimeRangeOnResize?: boolean;
      rightBarStaysOnScroll?: boolean;
      borderVisible?: boolean;
      borderColor?: string;
      visible?: boolean;
      timeVisible?: boolean;
      secondsVisible?: boolean;
      tickMarkFormatter?: (time: Time, tickMarkType: string, locale: string) => string;
    };
    localization?: {
      locale?: string;
      dateFormat?: string;
    };
    handleScroll?: {
      mouseWheel?: boolean;
      pressedMouseMove?: boolean;
      horzTouchDrag?: boolean;
      vertTouchDrag?: boolean;
    };
    handleScale?: {
      axisPressedMouseMove?: boolean;
      mouseWheel?: boolean;
      pinch?: boolean;
    };
  }

  export interface CandlestickData {
    time: Time;
    open: number;
    high: number;
    low: number;
    close: number;
  }

  export interface HistogramData {
    time: Time;
    value: number;
    color?: string;
  }

  export type Time = number | string | Date;

  export interface PriceScaleOptions {
    scaleMargins?: {
      top?: number;
      bottom?: number;
    };
  }

  export interface PriceScale {
    applyOptions(options: PriceScaleOptions): void;
  }

  export interface CandlestickSeriesOptions extends SeriesOptions {
    upColor?: string;
    downColor?: string;
    borderVisible?: boolean;
    wickUpColor?: string;
    wickDownColor?: string;
  }

  export interface HistogramSeriesOptions extends SeriesOptions {
    color?: string;
    base?: number;
  }

  export interface SeriesStyleOptions {
    color?: string;
    lineWidth?: number;
    lineStyle?: number;
    lineType?: number;
    crosshairMarkerVisible?: boolean;
    crosshairMarkerRadius?: number;
    crosshairMarkerBorderColor?: string;
    crosshairMarkerBackgroundColor?: string;
    lastPriceAnimation?: number;
  }

  export interface SeriesOptions {
    priceFormat?: {
      type: 'price' | 'volume' | 'percent';
      precision?: number;
      minMove?: number;
    };
    priceScaleId?: string;
    autoscaleInfoProvider?: () => { priceRange: { minValue: number; maxValue: number } };
    scaleMargins?: {
      top?: number;
      bottom?: number;
    };
    visible?: boolean;
    styleOptions?: SeriesStyleOptions;
  }

  export interface ISeriesApi<T> {
    setData(data: T[]): void;
    update(data: T): void;
    priceScale(): PriceScale;
    applyOptions(options: SeriesOptions): void;
  }

  export type CandlestickSeriesApi = ISeriesApi<CandlestickData>;
  export type HistogramSeriesApi = ISeriesApi<HistogramData>;

  export interface IChartApi {
    addCandlestickSeries(options?: CandlestickSeriesOptions): CandlestickSeriesApi;
    addHistogramSeries(options?: HistogramSeriesOptions): HistogramSeriesApi;
    timeScale(): {
      fitContent(): void;
    };
    resize(width: number, height: number): void;
    applyOptions(options: ChartOptions): void;
    remove(): void;
  }

  export function createChart(container: HTMLElement, options?: ChartOptions): IChartApi;
}
