import React, { createContext, useContext, ReactNode } from 'react';

interface ChartSyncContextValue {
  visibleRange: { start: number; end: number };
  zoomLevel: number;
  onRangeChange: (start: number, end: number) => void;
  onZoom: (factor: number, center: number) => void;
  onPan: (delta: number) => void;
}

const ChartSyncContext = createContext<ChartSyncContextValue | null>(null);

interface ChartSyncProviderProps {
  children: ReactNode;
  value: ChartSyncContextValue;
}

export function ChartSyncProvider({ children, value }: ChartSyncProviderProps) {
  return (
    <ChartSyncContext.Provider value={value}>
      {children}
    </ChartSyncContext.Provider>
  );
}

export function useChartSync() {
  const context = useContext(ChartSyncContext);
  if (!context) {
    throw new Error('useChartSync must be used within a ChartSyncProvider');
  }
  return context;
} 