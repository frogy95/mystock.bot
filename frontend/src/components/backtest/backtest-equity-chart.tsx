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
  equityCurve: { date: string; value: number; benchmark: number }[];
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

            {/* Y축: 포트폴리오 지수값 */}
            <YAxis
              tick={{ fontSize: 11 }}
              tickLine={false}
              tickFormatter={(v: number) => `${v.toFixed(0)}`}
              domain={["auto", "auto"]}
            />

            <Tooltip
              formatter={(
                value: number | string | undefined,
                name: string | undefined
              ) => [
                typeof value === "number" ? value.toFixed(2) : String(value ?? ""),
                name === "value" ? "전략 수익" : "벤치마크",
              ]}
            />

            <Legend
              formatter={(value: string) =>
                value === "value" ? "전략 수익" : "벤치마크"
              }
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
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
