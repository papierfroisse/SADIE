import React from 'react';

interface TopToolbarProps {
  onIndicatorAdd: (indicator: string) => void;
  onAlertAdd: () => void;
  onReplayToggle: () => void;
  onFullscreenToggle: () => void;
  onSettingsOpen: () => void;
}

export function TopToolbar({
  onIndicatorAdd,
  onAlertAdd,
  onReplayToggle,
  onFullscreenToggle,
  onSettingsOpen
}: TopToolbarProps) {
  return (
    <>
      <style>
        {`
          .toolbar-button:hover {
            background: #363A45;
          }
          .toolbar-button.active {
            background: #2962FF;
          }
        `}
      </style>
      <div style={{
        display: 'flex',
        gap: '4px',
        alignItems: 'center'
      }}>
        {/* Indicateurs */}
        <button
          className="toolbar-button"
          onClick={() => onIndicatorAdd('RSI')}
          title="Ajouter un indicateur"
          style={{
            padding: '8px',
            background: '#2A2E39',
            border: 'none',
            borderRadius: '4px',
            color: '#D1D4DC',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            fontSize: '14px'
          }}
        >
          <span style={{ fontSize: '16px' }}>📊</span>
          Indicateurs
        </button>

        {/* Alertes */}
        <button
          className="toolbar-button"
          onClick={onAlertAdd}
          title="Créer une alerte"
          style={{
            padding: '8px',
            background: '#2A2E39',
            border: 'none',
            borderRadius: '4px',
            color: '#D1D4DC',
            cursor: 'pointer'
          }}
        >
          🔔
        </button>

        {/* Replay */}
        <button
          className="toolbar-button"
          onClick={onReplayToggle}
          title="Mode replay"
          style={{
            padding: '8px',
            background: '#2A2E39',
            border: 'none',
            borderRadius: '4px',
            color: '#D1D4DC',
            cursor: 'pointer'
          }}
        >
          ⏮
        </button>

        {/* Séparateur */}
        <div style={{
          width: '1px',
          height: '24px',
          background: '#363A45',
          margin: '0 8px'
        }} />

        {/* Plein écran */}
        <button
          className="toolbar-button"
          onClick={onFullscreenToggle}
          title="Plein écran"
          style={{
            padding: '8px',
            background: '#2A2E39',
            border: 'none',
            borderRadius: '4px',
            color: '#D1D4DC',
            cursor: 'pointer'
          }}
        >
          ⛶
        </button>

        {/* Paramètres */}
        <button
          className="toolbar-button"
          onClick={onSettingsOpen}
          title="Paramètres"
          style={{
            padding: '8px',
            background: '#2A2E39',
            border: 'none',
            borderRadius: '4px',
            color: '#D1D4DC',
            cursor: 'pointer'
          }}
        >
          ⚙️
        </button>
      </div>
    </>
  );
} 