import React, { useState } from 'react';
import { TimeInterval } from '../data/types';

interface ChartToolbarProps {
  onIntervalChange: (interval: TimeInterval) => void;
  onIndicatorAdd: (type: string) => void;
  currentInterval: TimeInterval;
}

const timeIntervals: TimeInterval[] = ['1m', '5m', '15m', '1h', '4h', '1d'];

const buttonBaseStyle: React.CSSProperties = {
  background: 'transparent',
  border: 'none',
  color: '#787B86',
  padding: '6px 12px',
  borderRadius: '4px',
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  gap: '4px',
  fontSize: '14px',
  transition: 'background-color 0.2s'
};

const buttonHoverStyle: React.CSSProperties = {
  ...buttonBaseStyle,
  backgroundColor: '#2A2E39'
};

export function ChartToolbar({ onIntervalChange, onIndicatorAdd, currentInterval }: ChartToolbarProps) {
  const [hoveredButton, setHoveredButton] = useState<string | null>(null);

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      padding: '8px',
      background: '#131722',
      borderBottom: '1px solid #2A2E39'
    }}>
      {/* Bouton Indicateurs */}
      <button
        style={hoveredButton === 'indicators' ? buttonHoverStyle : buttonBaseStyle}
        onMouseEnter={() => setHoveredButton('indicators')}
        onMouseLeave={() => setHoveredButton(null)}
        onClick={() => onIndicatorAdd('indicators')}
      >
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
          <path d="M3 3V15H15" stroke="currentColor" strokeWidth="1.2"/>
          <path d="M6 11L9 8L12 11L15 7" stroke="currentColor" strokeWidth="1.2"/>
        </svg>
        Indicateurs
      </button>

      {/* Séparateur */}
      <div style={{
        width: '1px',
        height: '24px',
        background: '#2A2E39',
        margin: '0 8px'
      }} />

      {/* Intervalles de temps */}
      <div style={{
        display: 'flex',
        gap: '2px'
      }}>
        {timeIntervals.map(interval => (
          <button
            key={interval}
            style={{
              ...buttonBaseStyle,
              backgroundColor: interval === currentInterval ? '#2962FF' 
                : hoveredButton === interval ? '#2A2E39'
                : 'transparent',
              color: interval === currentInterval ? '#FFFFFF' : '#787B86'
            }}
            onMouseEnter={() => setHoveredButton(interval)}
            onMouseLeave={() => setHoveredButton(null)}
            onClick={() => onIntervalChange(interval)}
          >
            {interval}
          </button>
        ))}
      </div>

      {/* Séparateur */}
      <div style={{
        width: '1px',
        height: '24px',
        background: '#2A2E39',
        margin: '0 8px'
      }} />

      {/* Outils de dessin */}
      <button
        style={hoveredButton === 'draw' ? buttonHoverStyle : buttonBaseStyle}
        onMouseEnter={() => setHoveredButton('draw')}
        onMouseLeave={() => setHoveredButton(null)}
      >
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
          <path d="M3 15L15 3M3 3L15 15" stroke="currentColor" strokeWidth="1.2"/>
        </svg>
        Dessiner
      </button>

      {/* Plein écran */}
      <button
        style={{
          ...buttonBaseStyle,
          padding: '6px',
          marginLeft: 'auto',
          backgroundColor: hoveredButton === 'fullscreen' ? '#2A2E39' : 'transparent'
        }}
        onMouseEnter={() => setHoveredButton('fullscreen')}
        onMouseLeave={() => setHoveredButton(null)}
      >
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
          <path d="M3 3H7M3 3V7M3 3L7 7M15 3H11M15 3V7M15 3L11 7M3 15H7M3 15V11M3 15L7 11M15 15H11M15 15V11M15 15L11 11" stroke="currentColor" strokeWidth="1.2"/>
        </svg>
      </button>
    </div>
  );
} 