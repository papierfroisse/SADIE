import React from 'react';
import { TimeInterval } from '../data/types';

interface ChartToolbarProps {
  onIntervalChange: (interval: TimeInterval) => void;
  onIndicatorAdd: (type: string) => void;
  currentInterval: TimeInterval;
}

export function ChartToolbar({
  onIntervalChange,
  onIndicatorAdd,
  currentInterval
}: ChartToolbarProps) {
  return (
    <div className="chart-toolbar">
      {/* Groupe des intervalles */}
      <div className="chart-toolbar-group">
        <button
          className={currentInterval === '1m' ? 'active' : ''}
          onClick={() => onIntervalChange('1m')}
        >
          1m
        </button>
        <button
          className={currentInterval === '5m' ? 'active' : ''}
          onClick={() => onIntervalChange('5m')}
        >
          5m
        </button>
        <button
          className={currentInterval === '15m' ? 'active' : ''}
          onClick={() => onIntervalChange('15m')}
        >
          15m
        </button>
        <button
          className={currentInterval === '1h' ? 'active' : ''}
          onClick={() => onIntervalChange('1h')}
        >
          1h
        </button>
        <button
          className={currentInterval === '4h' ? 'active' : ''}
          onClick={() => onIntervalChange('4h')}
        >
          4h
        </button>
        <button
          className={currentInterval === '1d' ? 'active' : ''}
          onClick={() => onIntervalChange('1d')}
        >
          1D
        </button>
      </div>

      {/* Groupe des indicateurs */}
      <div className="chart-toolbar-group">
        <button onClick={() => onIndicatorAdd('rsi')}>
          <svg viewBox="0 0 24 24">
            <path d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V7H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 7v2h14V7H7z"/>
          </svg>
          Indicateurs
        </button>
      </div>

      {/* Groupe des outils de dessin */}
      <div className="chart-toolbar-group">
        <button>
          <svg viewBox="0 0 24 24">
            <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
          </svg>
          Dessiner
        </button>
      </div>

      {/* Groupe des paramètres */}
      <div className="chart-toolbar-group">
        <button>
          <svg viewBox="0 0 24 24">
            <path d="M19.43 12.98c.04-.32.07-.64.07-.98s-.03-.66-.07-.98l2.11-1.65c.19-.15.24-.42.12-.64l-2-3.46c-.12-.22-.39-.3-.61-.22l-2.49 1c-.52-.4-1.08-.73-1.69-.98l-.38-2.65C14.46 2.18 14.25 2 14 2h-4c-.25 0-.46.18-.49.42l-.38 2.65c-.61.25-1.17.59-1.69.98l-2.49-1c-.23-.09-.49 0-.61.22l-2 3.46c-.13.22-.07.49.12.64l2.11 1.65c-.04.32-.07.65-.07.98s.03.66.07.98l-2.11 1.65c-.19.15-.24.42-.12.64l2 3.46c.12.22.39.3.61.22l2.49-1c.52.4 1.08.73 1.69.98l.38 2.65c.03.24.24.42.49.42h4c.25 0 .46-.18.49-.42l.38-2.65c.61-.25 1.17-.59 1.69-.98l2.49 1c.23.09.49 0 .61-.22l2-3.46c.12-.22.07-.49-.12-.64l-2.11-1.65zM12 15.5c-1.93 0-3.5-1.57-3.5-3.5s1.57-3.5 3.5-3.5 3.5 1.57 3.5 3.5-1.57 3.5-3.5 3.5z"/>
          </svg>
        </button>
        <button>
          <svg viewBox="0 0 24 24">
            <path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
          </svg>
        </button>
      </div>
    </div>
  );
} 