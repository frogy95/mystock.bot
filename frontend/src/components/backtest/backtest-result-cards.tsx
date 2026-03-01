"use client";

import { StatCard } from "@/components/common/stat-card";
import type { BacktestResult } from "@/lib/mock/types";

interface BacktestResultCardsProps {
  result: BacktestResult;
}

export function BacktestResultCards({ result }: BacktestResultCardsProps) {
  const {
    totalReturn,
    annualReturn,
    maxDrawdown,
    winRate,
    tradeCount,
    sharpeRatio,
    benchmarkReturn,
  } = result;

  // 벤치마크 대비 초과 수익률
  const excessReturn = totalReturn - benchmarkReturn;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
      {/* 총 수익률 */}
      <StatCard
        title="총 수익률"
        value={`${totalReturn.toFixed(2)}%`}
        trend={{ value: totalReturn, label: "누적" }}
      />

      {/* 연환산 수익률 */}
      <StatCard
        title="연환산 수익률"
        value={`${annualReturn.toFixed(2)}%`}
        trend={{ value: annualReturn, label: "연간" }}
      />

      {/* 최대 낙폭 (음수이므로 trend.value 그대로 전달) */}
      <StatCard
        title="최대 낙폭"
        value={`${maxDrawdown.toFixed(2)}%`}
        trend={{ value: maxDrawdown, label: "MDD" }}
      />

      {/* 승률 */}
      <StatCard
        title="승률"
        value={`${winRate.toFixed(1)}%`}
      />

      {/* 매매 횟수 */}
      <StatCard
        title="매매 횟수"
        value={`${tradeCount}회`}
      />

      {/* 샤프 지수 */}
      <StatCard
        title="샤프 지수"
        value={`${sharpeRatio.toFixed(2)}`}
      />

      {/* 벤치마크 대비 초과 수익률 */}
      <StatCard
        title="벤치마크 대비"
        value={`${excessReturn.toFixed(2)}%`}
        trend={{ value: excessReturn, label: "vs KOSPI" }}
      />
    </div>
  );
}
