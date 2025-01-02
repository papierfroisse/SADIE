import React, { useEffect, useState, useRef, useCallback } from 'react';
import styled, { ThemeProvider } from 'styled-components';
import { Responsive as ResponsiveGrid, WidthProvider } from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';
import axios from 'axios';
import { FaMoon, FaSun, FaChartLine, FaSearch, FaStar, FaExpand, FaCompress, FaChartArea, FaChartBar } from 'react-icons/fa';
import { Theme } from './theme';
import { useTheme } from './hooks/useTheme';
import { CandleData, Drawing, Annotation } from './types/chart';
import { drawChart, initializeChart } from './components/Chart';
import { calculateSMA, calculateBollingerBands } from './utils/indicators';
import { fetchExchangeData } from './services/exchanges';
import type { ExchangeData } from './services/exchanges';
import { TimeframeButton, ToolButton } from './components/StyledComponents';
import { useAuth } from './hooks/useAuth';
import Auth from './components/auth/Auth';
import { signOut } from 'firebase/auth';
import { auth } from './config/firebase';

const EXCHANGES = ['binance', 'kraken'] as const;
type Exchange = typeof EXCHANGES[number];

const formatNumber = (num: number): string => {
  if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
  if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
  if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
  return num.toFixed(2);
};

interface Layouts {
  [key: string]: Array<{
    i: string;
    x: number;
    y: number;
    w: number;
    h: number;
  }>;
}

interface Crypto extends ExchangeData {
  marketCap?: number;
  rank?: number;
  priceChange1h?: number;
  priceChange7d?: number;
}

const ResponsiveGridLayout = WidthProvider(ResponsiveGrid);

const IconButton = styled.button<{ theme: Theme }>`
  background: ${({ theme }) => theme.buttonBackground};
  color: ${({ theme }) => theme.buttonText};
  border: 1px solid ${({ theme }) => theme.border};
  border-radius: 4px;
  padding: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;

  &:hover {
    background: ${({ theme }) => theme.hoverBackground};
  }
`;

const AppWrapper = styled.div<{ theme: Theme }>`
  min-height: 100vh;
  background: ${({ theme }) => theme.background};
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
`;

const TopBar = styled.div<{ theme: Theme }>`
  background: ${({ theme }) => theme.toolbarBackground};
  border-bottom: 1px solid ${({ theme }) => theme.border};
  padding: 8px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const Logo = styled.div<{ theme: Theme }>`
  color: ${({ theme }) => theme.textPrimary};
  font-size: 1.2rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const SearchBar = styled.div<{ theme: Theme }>`
  position: relative;
  width: 300px;

  input {
    width: 100%;
    padding: 8px 12px 8px 36px;
    border-radius: 6px;
    border: 1px solid ${({ theme }) => theme.border};
    background: ${({ theme }) => theme.inputBackground};
    color: ${({ theme }) => theme.textPrimary};
    font-size: 0.9rem;

    &:focus {
      outline: none;
      border-color: ${({ theme }) => theme.accent};
    }
  }

  svg {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: ${({ theme }) => theme.textSecondary};
  }
`;

const Controls = styled.div`
  display: flex;
  gap: 12px;
  align-items: center;
`;

const MainContent = styled.div`
  flex: 1;
  padding: 16px;
  overflow: hidden;
`;

const MarketsList = styled.div<{ theme: Theme }>`
  flex: 1;
  overflow-y: auto;
  background: ${({ theme }) => theme.cardBackground};

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: ${({ theme }) => theme.background};
  }

  &::-webkit-scrollbar-thumb {
    background: ${({ theme }) => theme.borderLight};
    border-radius: 3px;
  }
`;

const MarketItem = styled.div<{ theme: Theme; isSelected: boolean }>`
  padding: 12px 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-left: 3px solid ${({ theme, isSelected }) => isSelected ? theme.accent : 'transparent'};
  background: ${({ theme, isSelected }) => isSelected ? theme.hoverBackground : 'transparent'};

  &:hover {
    background: ${({ theme }) => theme.hoverBackground};
  }
`;

const AssetInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const AssetName = styled.div<{ theme: Theme }>`
  color: ${({ theme }) => theme.textPrimary};
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;

  span {
    font-size: 0.85rem;
    color: ${({ theme }) => theme.textSecondary};
  }
`;

const PriceInfo = styled.div`
  text-align: right;
`;

const Price = styled.div<{ theme: Theme }>`
  color: ${({ theme }) => theme.textPrimary};
  font-weight: 500;
`;

const PriceChange = styled.div<{ isPositive: boolean; theme: Theme }>`
  color: ${({ isPositive, theme }) => isPositive ? theme.upColor : theme.downColor};
  font-size: 0.85rem;
`;

const ChartContainer = styled.div<{ theme: Theme; isFullscreen: boolean }>`
  flex: 1;
  background: ${({ theme }) => theme.chartBackground};
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 0;
  overflow: hidden;
`;

const Canvas = styled.canvas`
  width: 100%;
  height: 100%;
  display: block;
`;

const FullscreenButton = styled(IconButton)`
  position: absolute;
  top: 24px;
  right: 24px;
  z-index: 10;
  background: ${({ theme }) => theme.cardBackground};
  opacity: 0.8;
  &:hover {
    opacity: 1;
  }
`;

const ExchangeSelect = styled.select<{ theme: Theme }>`
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid ${({ theme }) => theme.border};
  background: ${({ theme }) => theme.buttonBackground};
  color: ${({ theme }) => theme.textPrimary};
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: ${({ theme }) => theme.hoverBackground};
  }

  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.accent};
  }
`;

const DrawingTools = styled.div<{ theme: Theme }>`
  width: 48px;
  background: ${({ theme }) => theme.cardBackground};
  border-right: 1px solid ${({ theme }) => theme.border};
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const ToolIcon: React.FC<{ type: string }> = ({ type }) => {
  switch (type) {
    case 'line':
      return <span>━</span>;
    case 'horizontalLine':
      return <span>―</span>;
    case 'verticalLine':
      return <span>│</span>;
    case 'rectangle':
      return <span>□</span>;
    case 'fibonacci':
      return <span>𝒇</span>;
    default:
      return null;
  }
};

const GridItemWrapper = styled.div<{ theme: Theme }>`
  background: ${({ theme }) => theme.cardBackground};
  border: 1px solid ${({ theme }) => theme.border};
  border-radius: 4px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%;
  
  .drag-handle {
    cursor: move;
    padding: 8px;
    background: ${({ theme }) => theme.toolbarBackground};
    border-bottom: 1px solid ${({ theme }) => theme.border};
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .resize-handle {
    position: absolute;
    right: 0;
    bottom: 0;
    cursor: se-resize;
  }
`;

const ChartHeader = styled.div<{ theme: Theme }>`
  padding: 12px 16px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid ${({ theme }) => theme.border};
  background: ${({ theme }) => theme.toolbarBackground};

  .symbol {
    font-size: 1.1rem;
    font-weight: 500;
    margin-right: 16px;
  }

  .price {
    color: ${({ theme }) => theme.textSecondary};
  }
`;

const ChartLayout = styled.div`
  display: flex;
  flex: 1;
  height: 100%;
`;

const ChartControls = styled.div`
  display: flex;
  gap: 8px;
  align-items: center;
  margin-left: auto;
`;

const timeframeToKrakenInterval: Record<string, string> = {
  '1m': '1',
  '5m': '5',
  '15m': '15',
  '1h': '60',
  '4h': '240',
  '1d': '1440'
};

const UserMenu = styled.div`
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;

  &:hover {
    background: ${({ theme }) => theme.hoverBackground};
  }
`;

const UserAvatar = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: ${({ theme }) => theme.accent};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 500;
`;

const App: React.FC = () => {
  const { theme, isDarkMode, setIsDarkMode } = useTheme();
  const [cryptos, setCryptos] = useState<Crypto[]>([]);
  const [selectedCrypto, setSelectedCrypto] = useState<string>('BTCUSDT');
  const [candleData, setCandleData] = useState<CandleData[]>([]);
  const [selectedExchange, setSelectedExchange] = useState<Exchange>('binance');
  const [searchTerm, setSearchTerm] = useState('');
  const [timeframe, setTimeframe] = useState('1h');
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [drawings, setDrawings] = useState<Drawing[]>([]);
  const [annotations, setAnnotations] = useState<Annotation[]>([]);
  const [selectedTool, setSelectedTool] = useState<'none' | 'line' | 'horizontalLine' | 'verticalLine' | 'rectangle' | 'fibonacci'>('none');
  const [drawingInProgress, setDrawingInProgress] = useState<Drawing | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [layouts, setLayouts] = useState<Layouts>({
    lg: [
      { i: 'chart', x: 0, y: 0, w: 9, h: 12 },
      { i: 'markets', x: 9, y: 0, w: 3, h: 12 }
    ]
  });
  const [isLogScale, setIsLogScale] = useState(false);
  const { user, loading } = useAuth();

  const getTimestampFromX = useCallback((x: number): number => {
    const canvas = canvasRef.current;
    if (!canvas || candleData.length === 0) return 0;

    const rect = canvas.getBoundingClientRect();
    const normalizedX = (x - 60) / (rect.width - 120);
    const index = Math.floor(normalizedX * candleData.length);
    return candleData[Math.min(Math.max(0, index), candleData.length - 1)].timestamp;
  }, [candleData]);

  const getPriceFromY = useCallback((y: number): number => {
    const canvas = canvasRef.current;
    if (!canvas || candleData.length === 0) return 0;

    const rect = canvas.getBoundingClientRect();
    const normalizedY = (y - 30) / (rect.height - 60);
    const prices = candleData.map(d => d.close);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    return maxPrice - normalizedY * (maxPrice - minPrice);
  }, [candleData]);

  const drawChartCallback = useCallback(() => {
    if (canvasRef.current && candleData.length > 0) {
      console.log('Drawing chart with candleData length:', candleData.length);
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      
      if (ctx) {
        // Effacer le canvas avant de dessiner
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        const prices = candleData.map(d => d.close);
        const sma20 = calculateSMA(prices, 20);
        const bollinger = calculateBollingerBands(prices);
        
        // Ajuster la taille du canvas à son conteneur
        const container = canvas.parentElement;
        if (container) {
          const rect = container.getBoundingClientRect();
          console.log('Canvas dimensions:', rect.width, rect.height);
          const dpr = window.devicePixelRatio || 1;
          canvas.width = rect.width * dpr;
          canvas.height = rect.height * dpr;
          canvas.style.width = `${rect.width}px`;
          canvas.style.height = `${rect.height}px`;
          ctx.scale(dpr, dpr);
        }

        drawChart(ctx, candleData, {
          width: canvas.width / (window.devicePixelRatio || 1),
          height: canvas.height / (window.devicePixelRatio || 1),
          padding: 20,
          backgroundColor: theme.chartBackground,
          candleColors: {
            up: theme.upColor,
            down: theme.downColor
          },
          gridColor: theme.chartGrid,
          textColor: theme.textPrimary,
          isLogScale,
          indicators: [
            {
              name: 'SMA20',
              data: sma20,
              color: theme.accent
            },
            {
              name: 'BB Upper',
              data: bollinger.upper,
              color: theme.textSecondary
            },
            {
              name: 'BB Lower',
              data: bollinger.lower,
              color: theme.textSecondary
            }
          ],
          drawings: [...drawings, ...(drawingInProgress ? [drawingInProgress] : [])],
          annotations
        });
      }
    }
  }, [candleData, theme, drawings, drawingInProgress, annotations, isLogScale]);

  useEffect(() => {
    drawChartCallback();
  }, [drawChartCallback]);

  useEffect(() => {
    const resizeObserver = new ResizeObserver(() => {
      if (canvasRef.current) {
        const container = canvasRef.current.parentElement;
        if (container) {
          const { width, height } = container.getBoundingClientRect();
          const dpr = window.devicePixelRatio || 1;
          canvasRef.current.width = width * dpr;
          canvasRef.current.height = height * dpr;
          canvasRef.current.style.width = `${width}px`;
          canvasRef.current.style.height = `${height}px`;
          drawChartCallback();
        }
      }
    });

    if (canvasRef.current?.parentElement) {
      resizeObserver.observe(canvasRef.current.parentElement);
    }

    return () => resizeObserver.disconnect();
  }, [drawChartCallback]);

  useEffect(() => {
    if (canvasRef.current) {
      initializeChart(canvasRef.current, {
        width: canvasRef.current.width,
        height: canvasRef.current.height,
        padding: 20,
        backgroundColor: theme.chartBackground,
        candleColors: {
          up: theme.upColor,
          down: theme.downColor
        },
        gridColor: theme.chartGrid,
        textColor: theme.textPrimary,
        indicators: []
      });

      const canvas = canvasRef.current;

      const handleMouseDown = (e: MouseEvent) => {
        if (selectedTool === 'none') return;

        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const timestamp = getTimestampFromX(x);
        const price = getPriceFromY(y);

        setDrawingInProgress({
          type: selectedTool,
          points: [{ timestamp, price }],
          color: theme.accent
        });
      };

      const handleMouseMove = (e: MouseEvent) => {
        if (!drawingInProgress) return;

        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const timestamp = getTimestampFromX(x);
        const price = getPriceFromY(y);

        setDrawingInProgress({
          ...drawingInProgress,
          points: [...drawingInProgress.points.slice(0, 1), { timestamp, price }]
        });
      };

      const handleMouseUp = () => {
        if (drawingInProgress) {
          setDrawings([...drawings, drawingInProgress]);
          setDrawingInProgress(null);
          setSelectedTool('none');
        }
      };

      const handleDoubleClick = (e: MouseEvent) => {
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const timestamp = getTimestampFromX(x);
        const price = getPriceFromY(y);

        const text = prompt('Enter annotation text:');
        if (text) {
          setAnnotations([...annotations, {
            timestamp,
            price,
            text,
            color: theme.accent
          }]);
        }
      };

      canvas.addEventListener('mousedown', handleMouseDown);
      canvas.addEventListener('mousemove', handleMouseMove);
      canvas.addEventListener('mouseup', handleMouseUp);
      canvas.addEventListener('dblclick', handleDoubleClick);

      return () => {
        canvas.removeEventListener('mousedown', handleMouseDown);
        canvas.removeEventListener('mousemove', handleMouseMove);
        canvas.removeEventListener('mouseup', handleMouseUp);
        canvas.removeEventListener('dblclick', handleDoubleClick);
      };
    }
  }, [
    selectedTool,
    drawingInProgress,
    theme,
    drawings,
    annotations,
    candleData,
    getTimestampFromX,
    getPriceFromY
  ]);

  useEffect(() => {
    const fetchCryptoData = async () => {
      try {
        const data = await fetchExchangeData(selectedExchange);
        const sortedCryptos = (data as ExchangeData[])
          .filter((crypto) => crypto.symbol.endsWith('USDT'))
          .sort((a, b) => b.quoteVolume - a.quoteVolume)
          .slice(0, 20)
          .map(crypto => ({
            ...crypto,
            marketCap: undefined,
            rank: undefined,
            priceChange1h: undefined,
            priceChange7d: undefined
          }));
        
        setCryptos(sortedCryptos);
      } catch (error) {
        console.error('Error fetching crypto data:', error);
      }
    };

    fetchCryptoData();
    const interval = setInterval(fetchCryptoData, 10000);
    return () => clearInterval(interval);
  }, [selectedExchange]);

  useEffect(() => {
    const fetchCandleData = async () => {
      try {
        console.log('Fetching candle data with timeframe:', timeframe);
        if (selectedExchange === 'binance') {
          const response = await axios.get<any[]>(
            `https://api.binance.com/api/v3/klines`,
            {
              params: {
                symbol: selectedCrypto,
                interval: timeframe,
                limit: 168
              }
            }
          );
          
          const formattedData: CandleData[] = response.data.map((d) => ({
            timestamp: d[0],
            open: parseFloat(d[1]),
            high: parseFloat(d[2]),
            low: parseFloat(d[3]),
            close: parseFloat(d[4]),
            volume: parseFloat(d[5])
          }));

          console.log('Setting new candle data with length:', formattedData.length);
          setCandleData(formattedData);
        } else if (selectedExchange === 'kraken') {
          const krakenSymbol = selectedCrypto
            .replace('BTC', 'XBT')
            .replace('USDT', '/USDT');

          const response = await axios.get<{
            result: {
              [key: string]: [number, string, string, string, string, string, string, string][];
            };
          }>(
            `https://api.kraken.com/0/public/OHLC`,
            {
              params: {
                pair: krakenSymbol,
                interval: timeframeToKrakenInterval[timeframe],
                since: Math.floor(Date.now() / 1000) - (168 * 60 * 60)
              }
            }
          );
          
          const pairData = response.data.result[Object.keys(response.data.result)[0]];
          const formattedData: CandleData[] = pairData.map((d) => ({
            timestamp: d[0] * 1000,
            open: parseFloat(d[1]),
            high: parseFloat(d[2]),
            low: parseFloat(d[3]),
            close: parseFloat(d[4]),
            volume: parseFloat(d[6])
          }));

          setCandleData(formattedData);
        }
      } catch (error) {
        console.error('Error fetching candle data:', error);
      }
    };

    if (selectedCrypto) {
      fetchCandleData();
    }
  }, [selectedCrypto, selectedExchange, timeframe]);

  const filteredCryptos = cryptos.filter((crypto) =>
    crypto.baseAsset.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const onLayoutChange = (_currentLayout: any, allLayouts: Layouts) => {
    setLayouts(allLayouts);
  };

  if (loading) {
    return (
      <ThemeProvider theme={theme}>
        <AppWrapper theme={theme}>
          <div>Chargement...</div>
        </AppWrapper>
      </ThemeProvider>
    );
  }

  if (!user) {
    return (
      <ThemeProvider theme={theme}>
        <Auth />
      </ThemeProvider>
    );
  }

  const handleLogout = async () => {
    try {
      await signOut(auth);
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <AppWrapper theme={theme}>
        <TopBar theme={theme}>
          <Logo theme={theme}>
            <FaChartLine />
            Crypto Market Watch
          </Logo>
          <SearchBar theme={theme}>
            <FaSearch size={14} />
            <input
              type="text"
              placeholder="Search markets..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </SearchBar>
          <Controls>
            <ExchangeSelect 
              theme={theme}
              value={selectedExchange} 
              onChange={(e) => setSelectedExchange(e.target.value as Exchange)}
            >
              {EXCHANGES.map(exchange => (
                <option key={exchange} value={exchange}>
                  {exchange.charAt(0).toUpperCase() + exchange.slice(1)}
                </option>
              ))}
            </ExchangeSelect>
            <IconButton theme={theme} onClick={() => setIsDarkMode(!isDarkMode)}>
              {isDarkMode ? <FaSun size={18} /> : <FaMoon size={18} />}
            </IconButton>
            <UserMenu onClick={handleLogout}>
              <UserAvatar>
                {user.email?.[0].toUpperCase()}
              </UserAvatar>
              <span>Se déconnecter</span>
            </UserMenu>
          </Controls>
        </TopBar>

        <MainContent>
          <ResponsiveGridLayout
            className="layout"
            layouts={layouts}
            breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
            cols={{ lg: 12, md: 12, sm: 6, xs: 4, xxs: 2 }}
            rowHeight={30}
            onLayoutChange={onLayoutChange}
            isDraggable
            isResizable
            margin={[16, 16]}
          >
            <GridItemWrapper key="markets" theme={theme}>
              <div className="drag-handle">
                <span>Markets</span>
              </div>
              <MarketsList theme={theme}>
                {filteredCryptos.map((crypto) => (
                  <MarketItem
                    key={crypto.symbol}
                    onClick={() => setSelectedCrypto(crypto.symbol)}
                    isSelected={selectedCrypto === crypto.symbol}
                    theme={theme}
                  >
                    <AssetInfo>
                      <AssetName theme={theme}>
                        {crypto.baseAsset}
                        <span>USDT</span>
                        <FaStar size={12} style={{ color: theme.textSecondary }} />
                      </AssetName>
                      <span style={{ fontSize: '0.85rem', color: theme.textSecondary }}>
                        Vol: ${formatNumber(crypto.quoteVolume)}
                      </span>
                    </AssetInfo>
                    <PriceInfo>
                      <Price theme={theme}>${crypto.price.toFixed(2)}</Price>
                      <PriceChange isPositive={crypto.priceChangePercent >= 0} theme={theme}>
                        {crypto.priceChangePercent >= 0 ? '+' : ''}{crypto.priceChangePercent.toFixed(2)}%
                      </PriceChange>
                    </PriceInfo>
                  </MarketItem>
                ))}
              </MarketsList>
            </GridItemWrapper>

            <GridItemWrapper key="chart" theme={theme}>
              <ChartHeader theme={theme}>
                <span className="symbol">{selectedCrypto}</span>
                <span className="price">
                  ${cryptos.find(c => c.symbol === selectedCrypto)?.price.toFixed(2) || '0.00'}
                </span>
                <ChartControls>
                  {['1m', '5m', '15m', '1h', '4h', '1d'].map((tf) => (
                    <TimeframeButton
                      key={tf}
                      isActive={timeframe === tf}
                      onClick={() => {
                        console.log('Changing timeframe to:', tf);
                        setTimeframe(tf);
                      }}
                      theme={theme}
                    >
                      {tf.toUpperCase()}
                    </TimeframeButton>
                  ))}
                  <IconButton
                    theme={theme}
                    onClick={() => setIsLogScale(!isLogScale)}
                    title={isLogScale ? "Switch to Linear Scale" : "Switch to Log Scale"}
                  >
                    {isLogScale ? <FaChartArea size={16} /> : <FaChartBar size={16} />}
                  </IconButton>
                  <FullscreenButton 
                    theme={theme}
                    onClick={() => setIsFullscreen(!isFullscreen)}
                  >
                    {isFullscreen ? <FaCompress size={16} /> : <FaExpand size={16} />}
                  </FullscreenButton>
                </ChartControls>
              </ChartHeader>
              <ChartLayout>
                <DrawingTools theme={theme}>
                  {['line', 'horizontalLine', 'verticalLine', 'rectangle', 'fibonacci'].map((tool) => (
                    <ToolButton
                      key={tool}
                      data-active={selectedTool === tool}
                      onClick={() => setSelectedTool(selectedTool === tool ? 'none' : tool as any)}
                      theme={theme}
                    >
                      <ToolIcon type={tool} />
                    </ToolButton>
                  ))}
                </DrawingTools>
                <ChartContainer isFullscreen={isFullscreen} theme={theme}>
                  <Canvas ref={canvasRef} />
                </ChartContainer>
              </ChartLayout>
            </GridItemWrapper>
          </ResponsiveGridLayout>
        </MainContent>
      </AppWrapper>
    </ThemeProvider>
  );
};

export default App; 