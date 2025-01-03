import React from 'react';
import { ChartContainer } from './ChartContainer';
import { Logo } from './Logo';

export function AppLayout() {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      background: '#131722'
    }}>
      {/* En-tête principal */}
      <header style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 16px',
        height: '48px',
        background: '#1E222D',
        borderBottom: '1px solid #2A2E39'
      }}>
        <Logo />
        <nav style={{
          display: 'flex',
          gap: '24px',
          color: '#787B86',
          fontSize: '14px'
        }}>
          <span style={{ cursor: 'pointer' }}>Graphiques</span>
          <span style={{ cursor: 'pointer' }}>Screener</span>
          <span style={{ cursor: 'pointer' }}>Marchés</span>
          <span style={{ cursor: 'pointer' }}>Actualités</span>
          <span style={{ cursor: 'pointer' }}>Plus</span>
        </nav>
      </header>

      {/* Contenu principal */}
      <main style={{
        flex: 1,
        display: 'flex',
        overflow: 'hidden'
      }}>
        <ChartContainer
          symbol="BTCUSDT"
          interval="1h"
        />
      </main>
    </div>
  );
} 