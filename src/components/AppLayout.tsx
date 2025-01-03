import React from 'react';
import { Logo } from './Logo';

interface AppLayoutProps {
  children: React.ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      background: '#131722'
    }}>
      {/* En-tête */}
      <header style={{
        display: 'flex',
        alignItems: 'center',
        height: '48px',
        padding: '0 16px',
        background: '#1E222D',
        borderBottom: '1px solid #2A2E39'
      }}>
        <Logo />
        <nav style={{
          display: 'flex',
          gap: '24px',
          marginLeft: '48px'
        }}>
          <a href="#" style={{ color: '#D1D4DC', textDecoration: 'none' }}>Graphiques</a>
          <a href="#" style={{ color: '#787B86', textDecoration: 'none' }}>Screener</a>
          <a href="#" style={{ color: '#787B86', textDecoration: 'none' }}>Marchés</a>
          <a href="#" style={{ color: '#787B86', textDecoration: 'none' }}>Actualités</a>
          <a href="#" style={{ color: '#787B86', textDecoration: 'none' }}>Plus</a>
        </nav>
      </header>

      {/* Contenu principal */}
      <main style={{
        flex: 1,
        overflow: 'hidden'
      }}>
        {children}
      </main>
    </div>
  );
} 