import React from 'react';
import { DrawingToolType } from '../renderer/DrawingTools';

interface DrawingToolbarProps {
  selectedTool: DrawingToolType | null;
  onToolSelect: (tool: DrawingToolType | null) => void;
}

const tools = [
  { id: null, icon: '↕', tooltip: 'Curseur' },
  { id: null, icon: '✋', tooltip: 'Main (déplacement)' },
  { id: null, icon: '🔍', tooltip: 'Zoom' },
  { type: 'separator' },
  { id: 'line', icon: '/', tooltip: 'Ligne' },
  { id: 'horizontalLine', icon: '—', tooltip: 'Ligne horizontale' },
  { id: 'verticalLine', icon: '|', tooltip: 'Ligne verticale' },
  { id: 'rectangle', icon: '□', tooltip: 'Rectangle' },
  { id: 'fibonacci', icon: 'F', tooltip: 'Fibonacci' },
  { type: 'separator' },
  { id: 'text', icon: 'T', tooltip: 'Texte' },
  { id: 'brush', icon: '✎', tooltip: 'Pinceau' },
  { type: 'separator' },
  { id: 'measure', icon: '📏', tooltip: 'Mesure' },
  { id: 'ray', icon: '→', tooltip: 'Rayon' },
  { id: 'arrow', icon: '↗', tooltip: 'Flèche' }
];

export function DrawingToolbar({ selectedTool, onToolSelect }: DrawingToolbarProps) {
  return (
    <div style={{
      position: 'absolute',
      left: '8px',
      top: '50%',
      transform: 'translateY(-50%)',
      display: 'flex',
      flexDirection: 'column',
      gap: '4px',
      background: '#1E222D',
      padding: '4px',
      borderRadius: '4px',
      boxShadow: '0 2px 4px rgba(0, 0, 0, 0.2)',
      zIndex: 1000
    }}>
      {tools.map((tool, index) => {
        if (tool.type === 'separator') {
          return (
            <div
              key={`sep-${index}`}
              style={{
                height: '1px',
                background: '#363A45',
                margin: '4px 0'
              }}
            />
          );
        }

        return (
          <button
            key={tool.id || tool.tooltip}
            onClick={() => onToolSelect(tool.id as DrawingToolType)}
            title={tool.tooltip}
            style={{
              width: '32px',
              height: '32px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: selectedTool === tool.id ? '#2962FF' : '#2A2E39',
              border: 'none',
              borderRadius: '4px',
              color: '#D1D4DC',
              cursor: 'pointer',
              fontSize: '16px',
              padding: 0,
              transition: 'background-color 0.2s',
              position: 'relative',
              ':hover': {
                background: selectedTool === tool.id ? '#2962FF' : '#363A45'
              }
            }}
          >
            {tool.icon}
          </button>
        );
      })}
    </div>
  );
} 