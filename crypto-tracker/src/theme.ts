export interface Theme {
  background: string;
  textPrimary: string;
  textSecondary: string;
  accent: string;
}

export const lightTheme: Theme = {
  background: '#ffffff',
  textPrimary: '#000000',
  textSecondary: '#666666',
  accent: '#007bff',
};

export const darkTheme: Theme = {
  background: '#1a1a1a',
  textPrimary: '#ffffff',
  textSecondary: '#999999',
  accent: '#007bff',
}; 