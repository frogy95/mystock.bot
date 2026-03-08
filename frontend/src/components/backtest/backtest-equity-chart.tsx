"use client";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface BacktestEquityChartProps {
  equityCurve: { date: string; value: number; benchmark: number; stockBuyhold: number }[];
}

export function BacktestEquityChart({ equityCurve }: BacktestEquityChartProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>수익 곡선</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={320}>
          <LineChart
            data={equityCurve}
            margin={{ top: 8, right: 16, left: 0, bottom: 4 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />

            {/* X축: 날짜 문자열 */}
            <XAxis
              dataKey="date"
              tick={{ fontSize: 11 }}
              tickLine={false}
              // 날짜 레이블이 너무 많으면 간격 조정
              interval="preserveStartEnd"
            />

            {/* Y축: 포트폴리오 가치 (만원 단위) */}
            <YAxis
              tick={{ fontSize: 11 }}
              tickLine={false}
              tickFormatter={(v: number) => `${(v / 10000).toLocaleString("ko-KR")}만`}
              domain={["auto", "auto"]}
              label={{ value: "포트폴리오 가치(만원)", angle: -90, position: "insideLeft", style: { fontSize: 11 } }}
            />

            <Tooltip
              formatter={(
                value: number | string | undefined,
                name: string | undefined
              ) => {
                const formatted = typeof value === "number"
                  ? `${(value / 10000).toFixed(1)}만원`
                  : String(value ?? "");
                let label = name ?? "";
                if (name === "value") label = "전략 수익";
                else if (name === "benchmark") label = "KOSPI 벤치마크";
                else if (name === "stockBuyhold") label = "종목 바이앤홀드";
                return [formatted, label];
              }}
            />

            <Legend
              formatter={(value: string) => {
                if (value === "value") return "전략 수익";
                if (value === "benchmark") return "KOSPI 벤치마크";
                if (value === "stockBuyhold") return "종목 바이앤홀드";
                return value;
              }}
            />

            {/* 전략 수익 라인 - 빨간색 */}
            <Line
              type="monotone"
              dataKey="value"
              stroke="#ef4444"
              dot={false}
              strokeWidth={2}
              name="value"
            />

            {/* 벤치마크 라인 - 회색 */}
            <Line
              type="monotone"
              dataKey="benchmark"
              stroke="#94a3b8"
              dot={false}
              strokeWidth={2}
              name="benchmark"
            />

            {/* 종목 바이앤홀드 라인 - 녹색 */}
            <Line
              type="monotone"
              dataKey="stockBuyhold"
              stroke="#22c55e"
              dot={false}
              strokeWidth={2}
              name="stockBuyhold"
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
