import { AppLayout } from './components/AppLayout';
import { ChartContainer } from './components/ChartContainer';

export default function App() {
  return (
    <AppLayout>
      <ChartContainer
        symbol="BTCUSDT"
        interval="1h"
      />
    </AppLayout>
  );
} 