export interface Theme {
  background: string;
  cardBackground: string;
  toolbarBackground: string;
  chartBackground: string;
  textPrimary: string;
  textSecondary: string;
  border: string;
  borderLight: string;
  accent: string;
  buttonBackground: string;
  buttonText: string;
  hoverBackground: string;
  inputBackground: string;
  chartGrid: string;
  upColor: string;
  downColor: string;
}

export const lightTheme: Theme = {
  background: '#f5f5f5',
  cardBackground: '#ffffff',
  toolbarBackground: '#ffffff',
  chartBackground: '#ffffff',
  textPrimary: '#1a1a1a',
  textSecondary: '#666666',
  border: '#e0e0e0',
  borderLight: '#f0f0f0',
  accent: '#2962ff',
  buttonBackground: '#f5f5f5',
  buttonText: '#1a1a1a',
  hoverBackground: '#f0f0f0',
  inputBackground: '#ffffff',
  chartGrid: '#e0e0e0',
  upColor: '#26a69a',
  downColor: '#ef5350'
};

export const darkTheme: Theme = {
  background: '#121212',
  cardBackground: '#1e1e1e',
  toolbarBackground: '#1e1e1e',
  chartBackground: '#1e1e1e',
  textPrimary: '#ffffff',
  textSecondary: '#b3b3b3',
  border: '#333333',
  borderLight: '#2a2a2a',
  accent: '#2962ff',
  buttonBackground: '#333333',
  buttonText: '#ffffff',
  hoverBackground: '#2a2a2a',
  inputBackground: '#333333',
  chartGrid: '#333333',
  upColor: '#26a69a',
  downColor: '#ef5350'
}; 