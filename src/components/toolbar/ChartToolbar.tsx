import React from 'react';
import styled from 'styled-components';
import { TimeInterval } from '../../data/types';

interface ChartToolbarProps {
  symbol: string;
  interval: TimeInterval;
  onIntervalChange: (interval: TimeInterval) => void;
}

const Container = styled.div`
  display: flex;
  align-items: center;
  height: 38px;
  background: #1E222D;
  border-bottom: 1px solid #2A2E39;
  padding: 0 48px;
`;

const LeftSection = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const RightSection = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
`;

const SymbolInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 8px;
  height: 28px;
  border-radius: 4px;
  cursor: pointer;

  &:hover {
    background: rgba(42, 46, 57, 0.5);
  }
`;

const Symbol = styled.div`
  color: #D1D4DC;
  font-size: 14px;
  font-weight: 600;
`;

const Exchange = styled.div`
  color: #787B86;
  font-size: 12px;
`;

interface StyledButtonProps {
  $active?: boolean;
}

const IntervalButton = styled.button<StyledButtonProps>`
  background: ${props => props.$active ? '#2962FF' : 'transparent'};
  border: none;
  color: ${props => props.$active ? '#FFFFFF' : '#787B86'};
  padding: 4px 8px;
  font-size: 13px;
  cursor: pointer;
  border-radius: 4px;
  height: 28px;
  min-width: 28px;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    background: ${props => props.$active ? '#2962FF' : 'rgba(42, 46, 57, 0.5)'};
    color: ${props => props.$active ? '#FFFFFF' : '#D1D4DC'};
  }
`;

const ToolButton = styled.button`
  background: transparent;
  border: none;
  color: #787B86;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 4px;
  padding: 0;

  &:hover {
    background: rgba(42, 46, 57, 0.5);
    color: #D1D4DC;
  }

  svg {
    width: 16px;
    height: 16px;
  }
`;

const Separator = styled.div`
  width: 1px;
  height: 18px;
  background: #2A2E39;
  margin: 0 8px;
`;

const intervals: TimeInterval[] = ['1m', '5m', '15m', '30m', '1h', '4h', '1d'];

export const ChartToolbar: React.FC<ChartToolbarProps> = ({
  symbol,
  interval,
  onIntervalChange,
}) => {
  return (
    <Container>
      <LeftSection>
        <SymbolInfo>
          <Symbol>{symbol}</Symbol>
          <Exchange>BINANCE</Exchange>
        </SymbolInfo>

        <Separator />

        {intervals.map(int => (
          <IntervalButton
            key={int}
            $active={interval === int}
            onClick={() => onIntervalChange(int)}
          >
            {int}
          </IntervalButton>
        ))}

        <Separator />

        <ToolButton title="Indicators">
          <svg viewBox="0 0 24 24">
            <path fill="currentColor" d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V7H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 7v2h14V7H7z"/>
          </svg>
        </ToolButton>

        <ToolButton title="Compare">
          <svg viewBox="0 0 24 24">
            <path fill="currentColor" d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/>
          </svg>
        </ToolButton>
      </LeftSection>

      <RightSection>
        <ToolButton title="Settings">
          <svg viewBox="0 0 24 24">
            <path fill="currentColor" d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>
          </svg>
        </ToolButton>

        <ToolButton title="Fullscreen">
          <svg viewBox="0 0 24 24">
            <path fill="currentColor" d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
          </svg>
        </ToolButton>
      </RightSection>
    </Container>
  );
}; 