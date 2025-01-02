import { useState, useEffect } from 'react';

const lightTheme = {
  background: '#ffffff',
  textPrimary: '#1a1a1a',
  textSecondary: '#666666',
  accent: '#2196f3',
};

const darkTheme = {
  background: '#1a1a1a',
  textPrimary: '#ffffff',
  textSecondary: '#999999',
  accent: '#2196f3',
};

export const useTheme = () => {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(isDarkMode));
  }, [isDarkMode]);

  const theme = isDarkMode ? darkTheme : lightTheme;

  return { theme, isDarkMode, setIsDarkMode };
}; 