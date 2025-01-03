import React, { useRef, useEffect } from 'react';
import styled from 'styled-components';
import { Candle } from '../../data/types';
import { RSIIndicator } from '../../renderer/indicators/RSI';
import { MACDIndicator } from '../../renderer/indicators/MACD';
import { VolumeIndicator } from '../../renderer/indicators/Volume';
import { ResizablePanel } from '../common/ResizablePanel';
import { useChartSync } from '../../contexts/ChartSyncContext';

interface IndicatorPanelProps {
  type: 'rsi' | 'macd' | 'volume';
  data: Candle[];
  defaultHeight?: number;
  onClose?: () => void;
  onResize?: (height: number) => void;
}

const Panel = styled.div`
  width: 100%;
  height: 100%;
  background: #131722;
  border-top: 1px solid #2A2E39;
  display: flex;
  flex-direction: column;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  background: #1E222D;
  border-bottom: 1px solid #2A2E39;
  height: 37px;
`;

const Title = styled.div`
  color: #D1D4DC;
  font-size: 13px;
  font-weight: 500;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: #787B86;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    color: #D1D4DC;
  }
`;

const Canvas = styled.canvas`
  width: 100%;
  flex: 1;
`;

export function IndicatorPanel({
  type,
  data,
  defaultHeight = 200,
  onClose,
  onResize
}: IndicatorPanelProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const indicatorRef = useRef<RSIIndicator | MACDIndicator | VolumeIndicator | null>(null);
  const chartSync = useChartSync();

  useEffect(() => {
    if (!canvasRef.current) return;

    // Créer l'indicateur approprié
    switch (type) {
      case 'rsi':
        indicatorRef.current = new RSIIndicator(canvasRef.current);
        break;
      case 'macd':
        indicatorRef.current = new MACDIndicator(canvasRef.current);
        break;
      case 'volume':
        indicatorRef.current = new VolumeIndicator(canvasRef.current);
        break;
    }

    // Gérer le redimensionnement
    const resizeObserver = new ResizeObserver(() => {
      if (indicatorRef.current) {
        indicatorRef.current.resize();
      }
    });
    resizeObserver.observe(canvasRef.current);

    return () => {
      if (indicatorRef.current) {
        indicatorRef.current.destroy();
      }
      resizeObserver.disconnect();
    };
  }, [type]);

  useEffect(() => {
    if (indicatorRef.current && data.length > 0) {
      // Filtrer les données selon la plage visible
      const { start, end } = chartSync.visibleRange;
      const visibleData = data.filter(
        candle => candle.timestamp >= start && candle.timestamp <= end
      );
      
      indicatorRef.current.draw(visibleData);
    }
  }, [data, chartSync.visibleRange]);

  const getTitle = () => {
    switch (type) {
      case 'rsi':
        return 'RSI (14)';
      case 'macd':
        return 'MACD (12, 26, 9)';
      case 'volume':
        return 'Volume';
      default:
        return type;
    }
  };

  const handleResize = (height: number) => {
    onResize?.(height);
    if (indicatorRef.current) {
      indicatorRef.current.resize();
    }
  };

  return (
    <ResizablePanel
      defaultHeight={defaultHeight}
      minHeight={150}
      maxHeight={400}
      onResize={handleResize}
    >
      <Panel>
        <Header>
          <Title>{getTitle()}</Title>
          {onClose && (
            <CloseButton onClick={onClose}>
              <svg width="16" height="16" viewBox="0 0 16 16">
                <path
                  fill="currentColor"
                  d="M8 9.41L3.71 13.7a1 1 0 1 1-1.42-1.42L6.59 8 2.3 3.71A1 1 0 0 1 3.7 2.3L8 6.59l4.29-4.3a1 1 0 0 1 1.42 1.42L9.41 8l4.3 4.29a1 1 0 0 1-1.42 1.42L8 9.41z"
                />
              </svg>
            </CloseButton>
          )}
        </Header>
        <Canvas ref={canvasRef} />
      </Panel>
    </ResizablePanel>
  );
} 