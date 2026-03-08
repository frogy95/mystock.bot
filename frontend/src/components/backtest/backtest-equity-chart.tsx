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
import type { BacktestMultiResultItem } from "@/hooks/use-backtest";

/** 단일 전략 모드 Props */
interface SingleModeProps {
  equityCurve: { date: string; value: number; benchmark: number; stockBuyhold: number }[];
  multiResults?: never;
}

/** 다중 전략 모드 Props */
interface MultiModeProps {
  equityCurve?: never;
  multiResults: BacktestMultiResultItem[];
}

type BacktestEquityChartProps = SingleModeProps | MultiModeProps;

/** 전략별 색상 팔레트 */
const STRATEGY_COLORS = [
  "#ef4444", "#3b82f6", "#22c55e", "#f59e0b",
  "#8b5cf6", "#ec4899", "#06b6d4", "#84cc16",
];

export function BacktestEquityChart({ equityCurve, multiResults }: BacktestEquityChartProps) {
  // 다중 전략 모드: 날짜 기준으로 데이터 병합
  if (multiResults && multiResults.length > 0) {
    const dateMap = new Map<string, Record<string, number>>();

    multiResults.forEach((result) => {
      result.equity_curve.forEach((point) => {
        const existing = dateMap.get(point.date) ?? {};
        existing[`strategy_${result.strategy_id}`] = point.value;
        // 벤치마크는 첫 번째 결과에서 가져옴
        if (!existing["benchmark"]) {
          existing["benchmark"] = point.benchmark;
        }
        dateMap.set(point.date, existing);
      });
    });

    const mergedData = Array.from(dateMap.entries())
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([date, values]) => ({ date, ...values }));

    return (
      <Card>
        <CardHeader>
          <CardTitle>수익 곡선 비교 ({multiResults.length}개 전략)</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={360}>
            <LineChart data={mergedData} margin={{ top: 8, right: 16, left: 0, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 11 }}
                tickLine={false}
                interval="preserveStartEnd"
              />
              <YAxis
                tick={{ fontSize: 11 }}
                tickLine={false}
                tickFormatter={(v: number) => `${(v / 10000).toLocaleString("ko-KR")}만`}
                domain={["auto", "auto"]}
              />
              <Tooltip
                formatter={(value: number | string | undefined, name: string | undefined) => {
                  const formatted = typeof value === "number"
                    ? `${(value / 10000).toFixed(1)}만원`
                    : String(value ?? "");
                  if (name === "benchmark") return [formatted, "KOSPI 벤치마크"];
                  // strategy_id → 전략명 매핑
                  const stratId = name?.replace("strategy_", "");
                  const strat = multiResults.find((r) => String(r.strategy_id) === stratId);
                  return [formatted, strat?.strategy_name ?? name ?? ""];
                }}
              />
              <Legend
                formatter={(value: string) => {
                  if (value === "benchmark") return "KOSPI 벤치마크";
                  const stratId = value.replace("strategy_", "");
                  const strat = multiResults.find((r) => String(r.strategy_id) === stratId);
                  return strat?.strategy_name ?? value;
                }}
              />

              {/* 전략별 라인 */}
              {multiResults.map((result, idx) => (
                <Line
                  key={result.strategy_id}
                  type="monotone"
                  dataKey={`strategy_${result.strategy_id}`}
                  stroke={STRATEGY_COLORS[idx % STRATEGY_COLORS.length]}
                  dot={false}
                  strokeWidth={2}
                  name={`strategy_${result.strategy_id}`}
                />
              ))}

              {/* 벤치마크 라인 */}
              <Line
                type="monotone"
                dataKey="benchmark"
                stroke="#94a3b8"
                dot={false}
                strokeWidth={1.5}
                strokeDasharray="4 2"
                name="benchmark"
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    );
  }

  // 단일 전략 모드 (기존 동작 유지)
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
            <XAxis
              dataKey="date"
              tick={{ fontSize: 11 }}
              tickLine={false}
              interval="preserveStartEnd"
            />
            <YAxis
              tick={{ fontSize: 11 }}
              tickLine={false}
              tickFormatter={(v: number) => `${(v / 10000).toLocaleString("ko-KR")}만`}
              domain={["auto", "auto"]}
              label={{ value: "포트폴리오 가치(만원)", angle: -90, position: "insideLeft", style: { fontSize: 11 } }}
            />
            <Tooltip
              formatter={(value: number | string | undefined, name: string | undefined) => {
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
            <Line
              type="monotone"
              dataKey="value"
              stroke="#ef4444"
              dot={false}
              strokeWidth={2}
              name="value"
            />
            <Line
              type="monotone"
              dataKey="benchmark"
              stroke="#94a3b8"
              dot={false}
              strokeWidth={2}
              name="benchmark"
            />
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
