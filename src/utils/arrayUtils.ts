import { formatDateForChart } from './dateUtils';

interface CandleData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
}

export const removeDuplicatesAndSort = (data: CandleData[]): CandleData[] => {
  const uniqueMap = new Map();
  
  data.forEach(candle => {
    const key = formatDateForChart(candle.time);
    if (!uniqueMap.has(key) || 
        new Date(candle.time).getTime() > new Date(uniqueMap.get(key).time).getTime()) {
      uniqueMap.set(key, candle);
    }
  });

  return Array.from(uniqueMap.values())
    .sort((a, b) => new Date(a.time).getTime() - new Date(b.time).getTime());
}; 