import React from 'react';
import styled from 'styled-components';

interface TimeScaleProps {
  startTime: number;
  endTime: number;
  width: number;
  interval: string;
}

const ScaleContainer = styled.div`
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 25px;
  background: #131722;
  border-top: 1px solid #2A2E39;
  display: flex;
  align-items: center;
  z-index: 2;
  overflow: hidden;
`;

const TimeLabel = styled.div`
  position: absolute;
  color: #787B86;
  font-size: 11px;
  transform: translateX(-50%);
  white-space: nowrap;
`;

export function TimeScale({ startTime, endTime, width, interval }: TimeScaleProps) {
  const timeRange = endTime - startTime;
  const pixelsPerLabel = 100; // Espacement approximatif entre les labels
  const numLabels = Math.floor(width / pixelsPerLabel);
  const timeStep = timeRange / numLabels;

  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp);
    
    switch (interval) {
      case '1m':
      case '5m':
      case '15m':
      case '30m':
        return date.toLocaleTimeString(undefined, { 
          hour: '2-digit',
          minute: '2-digit'
        });
      case '1h':
      case '4h':
        return date.toLocaleDateString(undefined, {
          month: 'short',
          day: 'numeric',
          hour: '2-digit'
        });
      case '1d':
        return date.toLocaleDateString(undefined, {
          month: 'short',
          day: 'numeric'
        });
      default:
        return date.toLocaleDateString();
    }
  };

  return (
    <ScaleContainer>
      {Array.from({ length: numLabels + 1 }).map((_, i) => {
        const time = startTime + (i * timeStep);
        const position = (i / numLabels) * width;
        
        return (
          <TimeLabel
            key={i}
            style={{ left: `${position}px` }}
          >
            {formatTime(time)}
          </TimeLabel>
        );
      })}
    </ScaleContainer>
  );
} 