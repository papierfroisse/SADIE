import { useState, useEffect } from 'react';
import { Theme, lightTheme, darkTheme } from '../theme';

export const useTheme = () => {
  const [isDarkMode, setIsDarkMode] = useState(() => 
    window.matchMedia('(prefers-color-scheme: dark)').matches
  );

  const theme: Theme = isDarkMode ? darkTheme : lightTheme;

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e: MediaQueryListEvent) => setIsDarkMode(e.matches);
    
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  return { theme, isDarkMode, setIsDarkMode };
}; 