import React from 'react';

export function Logo() {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '6px',
      color: '#D1D4DC',
      fontWeight: 'bold',
      fontSize: '16px',
      cursor: 'pointer',
      userSelect: 'none'
    }}>
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path
          d="M4 20L12 4L20 20L12 16L4 20Z"
          stroke="#2962FF"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      CryptoChart Pro
    </div>
  );
} 