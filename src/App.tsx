import React, { useState, useCallback } from 'react';
import { ChartContainer } from './components/ChartContainer';
import { TopToolbar } from './components/TopToolbar';
import { SymbolList } from './components/SymbolList';
import { DrawingToolbar } from './components/DrawingToolbar';
import { MainHeader } from './components/MainHeader';
import { MarketInfoPanel } from './components/MarketInfoPanel';
import { TimeInterval } from './data/types';
import { DrawingToolType } from './renderer/DrawingTools';

const intervals: TimeInterval[] = ['1m', '5m', '15m', '1h', '4h', '1d'];

// Données de marché d'exemple
const marketData = {
  symbol: 'BTCUSDT',
  price: 47000,
  change: 1250.5,
  changePercent: 2.73,
  volume: 1234567890,
  high24h: 47500,
  low24h: 45500,
  marketCap: 890000000000,
  totalVolume: 25000000000
};

export default function App() {
  const [symbol, setSymbol] = useState('BTCUSDT');
  const [interval, setInterval] = useState<TimeInterval>('1h');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [selectedTool, setSelectedTool] = useState<DrawingToolType | null>(null);
  const [showSymbolList, setShowSymbolList] = useState(true);
  const [showMarketInfo, setShowMarketInfo] = useState(true);

  // Gestionnaires d'événements pour la barre d'outils supérieure
  const handleIndicatorAdd = useCallback((indicator: string) => {
    console.log('Add indicator:', indicator);
    // TODO: Implémenter l'ajout d'indicateur
  }, []);

  const handleAlertAdd = useCallback(() => {
    console.log('Add alert');
    // TODO: Implémenter l'ajout d'alerte
  }, []);

  const handleReplayToggle = useCallback(() => {
    console.log('Toggle replay mode');
    // TODO: Implémenter le mode replay
  }, []);

  const handleFullscreenToggle = useCallback(() => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  }, []);

  const handleSettingsOpen = useCallback(() => {
    console.log('Open settings');
    // TODO: Implémenter l'ouverture des paramètres
  }, []);

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      background: '#121212',
      color: '#fff'
    }}>
      {/* En-tête principal */}
      <MainHeader
        symbol={symbol}
        price={marketData.price}
        change={marketData.change}
        changePercent={marketData.changePercent}
      />

      {/* Zone principale */}
      <div style={{
        flex: 1,
        display: 'flex',
        overflow: 'hidden'
      }}>
        {/* Liste des symboles */}
        {showSymbolList && (
          <SymbolList
            selectedSymbol={symbol}
            onSymbolSelect={setSymbol}
          />
        )}

        {/* Zone du graphique */}
        <div style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          position: 'relative'
        }}>
          {/* Barre d'outils supérieure */}
          <div style={{
            display: 'flex',
            gap: '8px',
            padding: '8px 16px',
            alignItems: 'center',
            borderBottom: '1px solid #363A45'
          }}>
            <TopToolbar
              onIndicatorAdd={handleIndicatorAdd}
              onAlertAdd={handleAlertAdd}
              onReplayToggle={handleReplayToggle}
              onFullscreenToggle={handleFullscreenToggle}
              onSettingsOpen={handleSettingsOpen}
            />

            {/* Sélection de l'intervalle */}
            <div style={{
              display: 'flex',
              gap: '4px'
            }}>
              {intervals.map(i => (
                <button
                  key={i}
                  onClick={() => setInterval(i)}
                  style={{
                    padding: '8px 12px',
                    background: interval === i ? '#2962FF' : '#2A2E39',
                    border: 'none',
                    borderRadius: '4px',
                    color: '#fff',
                    cursor: 'pointer',
                    fontSize: '14px'
                  }}
                >
                  {i}
                </button>
              ))}
            </div>
          </div>

          {/* Zone du graphique avec outils de dessin */}
          <div style={{ flex: 1, position: 'relative' }}>
            <DrawingToolbar
              selectedTool={selectedTool}
              onToolSelect={setSelectedTool}
            />
            
            <ChartContainer
              symbol={symbol}
              interval={interval}
              width={isFullscreen ? window.innerWidth - (showSymbolList ? 300 : 0) - (showMarketInfo ? 300 : 0) : window.innerWidth - 320 - (showSymbolList ? 300 : 0) - (showMarketInfo ? 300 : 0)}
              height={isFullscreen ? window.innerHeight - 120 : window.innerHeight - 140}
            />
          </div>
        </div>

        {/* Panneau d'informations */}
        {showMarketInfo && (
          <MarketInfoPanel data={marketData} />
        )}
      </div>
    </div>
  );
} 