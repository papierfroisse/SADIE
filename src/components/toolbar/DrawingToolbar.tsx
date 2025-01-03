import React from 'react';
import { DrawingToolType } from '../renderer/DrawingTools';

interface DrawingToolbarProps {
  selectedTool: DrawingToolType;
  onToolSelect: (tool: DrawingToolType) => void;
}

const tools: { type: DrawingToolType; label: string; icon: string }[] = [
  { type: 'line', label: 'Line', icon: '📏' },
  { type: 'horizontalLine', label: 'Horizontal Line', icon: '⚡' },
  { type: 'verticalLine', label: 'Vertical Line', icon: '↕️' },
  { type: 'rectangle', label: 'Rectangle', icon: '⬜' },
  { type: 'fibonacci', label: 'Fibonacci', icon: '🔢' },
  { type: 'text', label: 'Text', icon: '📝' },
  { type: 'brush', label: 'Brush', icon: '🖌️' },
  { type: 'measure', label: 'Measure', icon: '📐' },
  { type: 'ray', label: 'Ray', icon: '↗️' },
  { type: 'arrow', label: 'Arrow', icon: '➡️' }
];

export function DrawingToolbar({ selectedTool, onToolSelect }: DrawingToolbarProps) {
  return (
    <div style={{
      position: 'absolute',
      top: '50%',
      left: '16px',
      transform: 'translateY(-50%)',
      display: 'flex',
      flexDirection: 'column',
      gap: '8px',
      background: '#1E222D',
      padding: '8px',
      borderRadius: '4px',
      border: '1px solid #2A2E39'
    }}>
      {tools.map(tool => (
        <button
          key={tool.type}
          onClick={() => onToolSelect(tool.type)}
          title={tool.label}
          style={{
            width: '32px',
            height: '32px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: tool.type === selectedTool ? '#2962FF' : 'transparent',
            border: '1px solid ' + (tool.type === selectedTool ? '#2962FF' : '#363A45'),
            borderRadius: '4px',
            color: tool.type === selectedTool ? '#FFFFFF' : '#787B86',
            cursor: 'pointer',
            fontSize: '16px',
            padding: 0
          }}
        >
          {tool.icon}
        </button>
      ))}
    </div>
  );
} 