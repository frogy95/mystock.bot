"use client";

import { Wallet, TrendingUp, TrendingDown, Banknote } from "lucide-react";
import { StatCard } from "@/components/common/stat-card";
import { StatCardSkeleton } from "@/components/common/loading-skeleton";
import { usePortfolioSummary } from "@/hooks/use-dashboard";
import { formatKRW, formatKRWCompact } from "@/lib/format";

export function PortfolioSummary() {
  const { data, isLoading } = usePortfolioSummary();

  if (isLoading || !data) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <StatCardSkeleton key={i} />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        title="총 평가금액"
        value={formatKRWCompact(data.totalEvaluation)}
        icon={Wallet}
        trend={{
          value: data.totalProfitRate,
          label: "총 수익률",
        }}
      />
      <StatCard
        title="일일 손익"
        value={formatKRW(data.dailyProfitLoss)}
        icon={data.dailyProfitLoss >= 0 ? TrendingUp : TrendingDown}
        trend={{
          value: data.dailyProfitRate,
          label: "전일 대비",
        }}
      />
      <StatCard
        title="총 평가손익"
        value={formatKRW(data.totalProfitLoss)}
        icon={data.totalProfitLoss >= 0 ? TrendingUp : TrendingDown}
        trend={{
          value: data.totalProfitRate,
          label: "총 수익률",
        }}
      />
      <StatCard
        title="예수금"
        value={formatKRWCompact(data.cashBalance)}
        icon={Banknote}
        description="투자 가능 금액"
      />
    </div>
  );
}
