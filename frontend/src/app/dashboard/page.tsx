"use client";

import { PortfolioSummary } from "@/components/dashboard/portfolio-summary";
import { HoldingsTable } from "@/components/dashboard/holdings-table";
import { TradeSignals } from "@/components/dashboard/trade-signals";
import { OrderTimeline } from "@/components/dashboard/order-timeline";
import { StrategyPerformanceCards } from "@/components/dashboard/strategy-performance";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">대시보드</h2>
        <p className="text-muted-foreground text-sm mt-1">
          포트폴리오 현황과 매매 신호를 한눈에 확인합니다.
        </p>
      </div>

      {/* 포트폴리오 요약 카드 */}
      <PortfolioSummary />

      {/* 보유종목 테이블 */}
      <HoldingsTable />

      {/* 매매 신호 + 주문 타임라인 + 전략 성과 (3단 그리드) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <TradeSignals />
        <OrderTimeline />
        <StrategyPerformanceCards />
      </div>
    </div>
  );
}
