import { useState } from "react";
import { AppLayout } from "./components/layout/AppLayout";
import { ChartContainer } from "./components/chart/ChartContainer";
import { TimeInterval } from "./data/types";

export default function App() {
  const [symbol, setSymbol] = useState("BTCUSDT");
  const [interval, setInterval] = useState<TimeInterval>("1h");

  return (
    <AppLayout>
      <ChartContainer
        symbol={symbol}
        interval={interval}
        onSymbolChange={setSymbol}
        onIntervalChange={setInterval}
      />
    </AppLayout>
  );
} 