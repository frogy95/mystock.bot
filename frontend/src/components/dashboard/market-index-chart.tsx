"use client";

import { useEffect, useRef } from "react";
import { createChart, type IChartApi, ColorType } from "lightweight-charts";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { PriceChangeBadge } from "@/components/common/price-change-badge";
import { useMarketIndices } from "@/hooks/use-dashboard";

function MiniChart({
  data,
  name,
  currentValue,
  changeValue,
  changeRate,
}: {
  data: { time: string; open: number; high: number; low: number; close: number }[];
  name: string;
  currentValue: number;
  changeValue: number;
  changeRate: number;
}) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current || data.length === 0) return;

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 120,
      layout: {
        background: { type: ColorType.Solid, color: "transparent" },
        textColor: "#9ca3af",
        fontSize: 10,
      },
      grid: {
        vertLines: { visible: false },
        horzLines: { color: "#f3f4f6" },
      },
      rightPriceScale: { borderVisible: false },
      timeScale: {
        borderVisible: false,
        tickMarkFormatter: () => "",
      },
      crosshair: {
        vertLine: { visible: false },
        horzLine: { visible: false },
      },
      handleScroll: false,
      handleScale: false,
    });

    const areaSeries = chart.addAreaSeries({
      lineColor: changeRate >= 0 ? "#ef4444" : "#3b82f6",
      topColor: changeRate >= 0 ? "rgba(239, 68, 68, 0.2)" : "rgba(59, 130, 246, 0.2)",
      bottomColor: changeRate >= 0 ? "rgba(239, 68, 68, 0.02)" : "rgba(59, 130, 246, 0.02)",
      lineWidth: 2,
    });

    areaSeries.setData(data.map((d) => ({ time: d.time as `${number}-${number}-${number}`, value: d.close })));
    chart.timeScale().fitContent();
    chartRef.current = chart;

    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
    };
  }, [data, changeRate]);

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-2">
          <div>
            <p className="text-sm font-medium text-muted-foreground">{name}</p>
            <p className="text-xl font-bold">{currentValue.toLocaleString()}</p>
          </div>
          <PriceChangeBadge
            changeRate={changeRate}
            changePrice={changeValue}
            showPrice
          />
        </div>
        <div ref={chartContainerRef} />
      </CardContent>
    </Card>
  );
}

export function MarketIndexCharts() {
  const { data: indices, isLoading } = useMarketIndices();

  if (isLoading || !indices) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Array.from({ length: 2 }).map((_, i) => (
          <Card key={i}>
            <CardContent className="p-4">
              <Skeleton className="h-4 w-16 mb-2" />
              <Skeleton className="h-6 w-24 mb-3" />
              <Skeleton className="h-[120px] w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {indices.map((index) => (
        <MiniChart
          key={index.name}
          data={index.chartData}
          name={index.name}
          currentValue={index.currentValue}
          changeValue={index.changeValue}
          changeRate={index.changeRate}
        />
      ))}
    </div>
  );
}
