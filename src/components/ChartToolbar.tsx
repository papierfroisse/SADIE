import React from 'react';
import { DrawingToolType } from '../renderer/DrawingTools';

interface ChartToolbarProps {
  onToolSelect: (tool: DrawingToolType | null) => void;
  onColorSelect: (color: string) => void;
  onLineWidthSelect: (width: number) => void;
  onClear: () => void;
  onUndo: () => void;
  onExport: () => void;
  selectedTool: DrawingToolType | null;
}

const tools: { id: DrawingToolType; label: string; icon: string }[] = [
  { id: 'line', label: 'Ligne', icon: '/' },
  { id: 'horizontalLine', label: 'Ligne horizontale', icon: '—' },
  { id: 'rectangle', label: 'Rectangle', icon: '□' },
  { id: 'fibonacci', label: 'Fibonacci', icon: 'F' }
];

const colors = ['#2962FF', '#FF6B6B', '#51CF66', '#FAB005', '#BE4BDB', '#868E96'];
const lineWidths = [1, 2, 3, 4];

export function ChartToolbar({
  onToolSelect,
  onColorSelect,
  onLineWidthSelect,
  onClear,
  onUndo,
  onExport,
  selectedTool
}: ChartToolbarProps) {
  return (
    <div style={{
      display: 'flex',
      gap: '8px',
      padding: '8px',
      background: '#1E222D',
      borderRadius: '4px',
      alignItems: 'center'
    }}>
      {/* Outils de dessin */}
      <div style={{ display: 'flex', gap: '4px' }}>
        <button
          onClick={() => onToolSelect(null)}
          style={{
            padding: '8px',
            background: !selectedTool ? '#2962FF' : '#2A2E39',
            border: 'none',
            borderRadius: '4px',
            color: '#fff',
            cursor: 'pointer'
          }}
        >
          ↕
        </button>
        {tools.map(tool => (
          <button
            key={tool.id}
            onClick={() => onToolSelect(tool.id)}
            title={tool.label}
            style={{
              padding: '8px',
              background: selectedTool === tool.id ? '#2962FF' : '#2A2E39',
              border: 'none',
              borderRadius: '4px',
              color: '#fff',
              cursor: 'pointer'
            }}
          >
            {tool.icon}
          </button>
        ))}
      </div>

      {/* Séparateur */}
      <div style={{ width: 1, height: 24, background: '#363A45' }} />

      {/* Couleurs */}
      <div style={{ display: 'flex', gap: '4px' }}>
        {colors.map(color => (
          <button
            key={color}
            onClick={() => onColorSelect(color)}
            style={{
              width: 24,
              height: 24,
              background: color,
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          />
        ))}
      </div>

      {/* Séparateur */}
      <div style={{ width: 1, height: 24, background: '#363A45' }} />

      {/* Épaisseur de ligne */}
      <div style={{ display: 'flex', gap: '4px' }}>
        {lineWidths.map(width => (
          <button
            key={width}
            onClick={() => onLineWidthSelect(width)}
            style={{
              width: 24,
              height: 24,
              background: '#2A2E39',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <div
              style={{
                width: '12px',
                height: `${width}px`,
                background: '#fff'
              }}
            />
          </button>
        ))}
      </div>

      {/* Séparateur */}
      <div style={{ width: 1, height: 24, background: '#363A45' }} />

      {/* Actions */}
      <button
        onClick={onUndo}
        style={{
          padding: '8px',
          background: '#2A2E39',
          border: 'none',
          borderRadius: '4px',
          color: '#fff',
          cursor: 'pointer'
        }}
      >
        ↩
      </button>
      <button
        onClick={onClear}
        style={{
          padding: '8px',
          background: '#2A2E39',
          border: 'none',
          borderRadius: '4px',
          color: '#fff',
          cursor: 'pointer'
        }}
      >
        🗑
      </button>
      <button
        onClick={onExport}
        style={{
          padding: '8px',
          background: '#2A2E39',
          border: 'none',
          borderRadius: '4px',
          color: '#fff',
          cursor: 'pointer'
        }}
      >
        💾
      </button>
    </div>
  );
} 