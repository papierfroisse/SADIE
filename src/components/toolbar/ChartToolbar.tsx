import React from 'react';
import styled from 'styled-components';
import { TimeInterval } from '../../data/types';

interface ChartToolbarProps {
  currentInterval: TimeInterval;
  onIntervalChange: (interval: TimeInterval) => void;
  onIndicatorAdd: (type: 'rsi' | 'macd' | 'volume') => void;
}

const Container = styled.div`
  display: flex;
  gap: 1px;
  background: #1E222D;
  border-radius: 4px;
  padding: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
`;

const Group = styled.div`
  display: flex;
  gap: 1px;
  
  &:not(:last-child) {
    margin-right: 8px;
    padding-right: 8px;
    border-right: 1px solid #2A2E39;
  }
`;

const Button = styled.button<{ active?: boolean }>`
  background: ${props => props.active ? '#2962FF' : 'transparent'};
  border: none;
  color: ${props => props.active ? '#FFFFFF' : '#787B86'};
  padding: 6px 12px;
  font-size: 13px;
  cursor: pointer;
  border-radius: 3px;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 4px;

  &:hover {
    background: ${props => props.active ? '#2962FF' : '#363A45'};
    color: ${props => props.active ? '#FFFFFF' : '#D1D4DC'};
  }

  svg {
    width: 14px;
    height: 14px;
  }
`;

const intervals: TimeInterval[] = ['1m', '5m', '15m', '30m', '1h', '4h', '1d'];

export function ChartToolbar({ currentInterval, onIntervalChange, onIndicatorAdd }: ChartToolbarProps) {
  return (
    <Container>
      <Group>
        {intervals.map(interval => (
          <Button
            key={interval}
            active={interval === currentInterval}
            onClick={() => onIntervalChange(interval)}
          >
            {interval}
          </Button>
        ))}
      </Group>

      <Group>
        <Button onClick={() => onIndicatorAdd('rsi')}>
          <svg viewBox="0 0 24 24">
            <path fill="currentColor" d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V7H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 7v2h14V7H7z"/>
          </svg>
          RSI
        </Button>
        <Button onClick={() => onIndicatorAdd('macd')}>
          <svg viewBox="0 0 24 24">
            <path fill="currentColor" d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/>
          </svg>
          MACD
        </Button>
        <Button onClick={() => onIndicatorAdd('volume')}>
          <svg viewBox="0 0 24 24">
            <path fill="currentColor" d="M18 20H4V6h14v14zm0-16H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm-8 14h2V10h-2v8zm-4 0h2v-4H6v4zm12-4h-2v4h2v-4z"/>
          </svg>
          Volume
        </Button>
      </Group>
    </Container>
  );
} 