import React, { useRef, useEffect, useState } from 'react';
import styled from 'styled-components';
import { ChartRenderer } from '../../renderer/ChartRenderer';
import { DrawingToolType } from '../../renderer/DrawingTools';
import { TimeInterval } from '../../data/types';
import { useMarketData } from '../../hooks/useMarketData';
import { useChartSync as useChartSyncHook } from '../../hooks/useChartSync';
import { ChartSyncProvider } from '../../contexts/ChartSyncContext';
import { ChartToolbar } from '../toolbar/ChartToolbar';
import { DrawingToolbar } from '../toolbar/DrawingToolbar';
import { TopTickers } from '../widgets/TopTickers';
import { PriceScale } from './PriceScale';
import { TimeScale } from './TimeScale';
import { IndicatorPanel } from '../indicators/IndicatorPanel';
import { VerticalToolbar } from '../toolbar/VerticalToolbar';

type IndicatorType = 'rsi' | 'macd' | 'volume';

const Container = styled.div`
  display: flex;
  height: 100%;
  width: 100%;
  position: relative;
  background: #131722;
`;

const MainContent = styled.div`
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  margin-right: 300px; // Espace pour le SidePanel
  position: relative;
  margin-left: 40px; // Espace pour la VerticalToolbar
`;

const ChartArea = styled.div`
  flex: 1;
  position: relative;
  min-height: 0;
  display: flex;
  flex-direction: column;
`;

const ChartContent = styled.div`
  width: 100%;
  height: 100%;
  position: relative;
  flex: 1;
  min-height: 0;
`;

const ChartCanvas = styled.div`
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
`;

const ToolbarContainer = styled.div`
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 10;
  display: flex;
  gap: 8px;
  align-items: center;
`;

const DrawingToolbarContainer = styled.div`
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 10;
`;

const SidePanel = styled.div`
  position: fixed;
  top: 0;
  right: 0;
  width: 300px;
  height: 100%;
  border-left: 1px solid #2A2E39;
  background: #1E222D;
  z-index: 20;
`;

const IndicatorsContainer = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
  background: #131722;
  border-top: 1px solid #2A2E39;
`;

const LoadingOverlay = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #D1D4DC;
  font-size: 14px;
`;

const VerticalToolbarContainer = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  height: 100%;
  z-index: 20;
`;

interface ChartContainerProps {
  symbol: string;
  interval: TimeInterval;
  onIntervalChange: (interval: TimeInterval) => void;
  onSymbolChange: (symbol: string) => void;
}

export function ChartContainer({ 
  symbol, 
  interval, 
  onIntervalChange,
  onSymbolChange 
}: ChartContainerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedTool, setSelectedTool] = useState<DrawingToolType>(null);
  const [renderer, setRenderer] = useState<ChartRenderer | null>(null);
  const { data, loading, error } = useMarketData({ symbol, interval });
  const [activeIndicators, setActiveIndicators] = useState<IndicatorType[]>([]);

  // État pour les échelles
  const [priceRange, setPriceRange] = useState({ min: 0, max: 0 });
  const [timeRange, setTimeRange] = useState({ start: 0, end: 0 });

  // Synchronisation du graphique
  const chartSync = useChartSyncHook({
    onRangeChange: (start, end) => {
      setTimeRange({ start, end });
      if (renderer) {
        renderer.setVisibleRange(start, end);
      }
    },
    onZoom: (factor, center) => {
      if (renderer) {
        renderer.zoom(factor, center);
      }
    },
    onPan: (delta) => {
      if (renderer) {
        renderer.pan(delta);
      }
    }
  });

  useEffect(() => {
    if (containerRef.current) {
      const newRenderer = new ChartRenderer(containerRef.current);
      setRenderer(newRenderer);
      return () => {
        newRenderer.destroy();
      };
    }
  }, []);

  useEffect(() => {
    if (renderer) {
      renderer.setSymbol(symbol);
      renderer.setInterval(interval);
    }
  }, [renderer, symbol, interval]);

  useEffect(() => {
    if (renderer && data?.candles) {
      renderer.setData(data.candles);
      
      // Mettre à jour les échelles
      const candles = data.candles;
      if (candles.length > 0) {
        const prices = candles.flatMap(c => [c.high, c.low]);
        const times = candles.map(c => c.timestamp);
        
        setPriceRange({
          min: Math.min(...prices),
          max: Math.max(...prices)
        });
        
        const start = Math.min(...times);
        const end = Math.max(...times);
        setTimeRange({ start, end });
        chartSync.setVisibleRange(start, end);
      }
    }
  }, [renderer, data]);

  const handleToolSelect = (tool: DrawingToolType) => {
    setSelectedTool(tool);
    if (renderer) {
      renderer.setDrawingTool(tool);
    }
  };

  const handleIndicatorAdd = (type: IndicatorType) => {
    if (!activeIndicators.includes(type)) {
      setActiveIndicators([...activeIndicators, type]);
      if (renderer) {
        renderer.addIndicator(type);
      }
    }
  };

  const handleIndicatorRemove = (type: IndicatorType) => {
    setActiveIndicators(activeIndicators.filter(t => t !== type));
    if (renderer) {
      renderer.removeIndicator(type);
    }
  };

  const handleIndicatorResize = (type: IndicatorType, height: number) => {
    // TODO: Sauvegarder la hauteur dans les préférences utilisateur
    console.log(`Indicator ${type} resized to ${height}px`);
  };

  if (error) {
    return <div style={{ color: '#EF5350', padding: '20px' }}>Error: {error.message}</div>;
  }

  const syncValue = {
    visibleRange: timeRange,
    zoomLevel: chartSync.zoomLevel,
    onRangeChange: chartSync.setVisibleRange,
    onZoom: (factor: number, center: number) => {
      if (renderer) {
        renderer.zoom(factor, center);
      }
    },
    onPan: (delta: number) => {
      if (renderer) {
        renderer.pan(delta);
      }
    }
  };

  return (
    <Container>
      <VerticalToolbarContainer>
        <VerticalToolbar
          selectedTool={selectedTool}
          onToolSelect={handleToolSelect}
        />
      </VerticalToolbarContainer>

      <MainContent>
        <ChartArea>
          <ChartContent ref={chartSync.containerRef}>
            <ChartCanvas ref={containerRef} />
            
            <ToolbarContainer>
              <ChartToolbar
                onIntervalChange={onIntervalChange}
                currentInterval={interval}
                onIndicatorAdd={handleIndicatorAdd}
              />
            </ToolbarContainer>

            {loading && (
              <LoadingOverlay>Loading...</LoadingOverlay>
            )}
            
            <PriceScale
              min={priceRange.min}
              max={priceRange.max}
              height={containerRef.current?.clientHeight || 0}
              position="right"
            />
            
            <PriceScale
              min={priceRange.min}
              max={priceRange.max}
              height={containerRef.current?.clientHeight || 0}
              position="left"
            />
            
            <TimeScale
              startTime={timeRange.start}
              endTime={timeRange.end}
              width={containerRef.current?.clientWidth || 0}
              interval={interval}
            />
          </ChartContent>
        </ChartArea>

        {activeIndicators.length > 0 && (
          <ChartSyncProvider value={syncValue}>
            <IndicatorsContainer>
              {activeIndicators.map(type => (
                <IndicatorPanel
                  key={type}
                  type={type}
                  data={data?.candles || []}
                  onClose={() => handleIndicatorRemove(type)}
                  onResize={(height) => handleIndicatorResize(type, height)}
                />
              ))}
            </IndicatorsContainer>
          </ChartSyncProvider>
        )}
      </MainContent>
      
      <SidePanel>
        <TopTickers onSymbolSelect={onSymbolChange} />
      </SidePanel>
    </Container>
  );
} 