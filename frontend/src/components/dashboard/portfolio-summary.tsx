"use client";

import { Wallet, TrendingUp, TrendingDown, Banknote } from "lucide-react";
import { StatCard } from "@/components/common/stat-card";
import { StatCardSkeleton } from "@/components/common/loading-skeleton";
import { usePortfolioSummary } from "@/hooks/use-dashboard";
import { formatKRW, formatKRWCompact } from "@/lib/format";
import { cn } from "@/lib/utils";

export function PortfolioSummary() {
  const { data, isLoading, isError, error, isFetching } = usePortfolioSummary();

  // 에러 상태
  if (isError) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="col-span-full p-6 text-center border rounded-lg">
          <p className="text-sm text-muted-foreground">
            포트폴리오 요약을 불러오지 못했습니다.
          </p>
          <p className="text-xs text-destructive mt-1">{(error as Error)?.message}</p>
        </div>
      </div>
    );
  }

  // 로딩 상태 (스켈레톤 + 안내 텍스트)
  if (isLoading || !data) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <StatCardSkeleton key={i} />
        ))}
        <p className="col-span-full text-xs text-center text-muted-foreground">
          KIS 데이터를 불러오는 중...
        </p>
      </div>
    );
  }

  return (
    <div className={cn("grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4",
      isFetching && "opacity-70")}>
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
