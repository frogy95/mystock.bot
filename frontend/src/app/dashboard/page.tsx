"use client";

import { PortfolioSummary } from "@/components/dashboard/portfolio-summary";
import { MarketIndexCharts } from "@/components/dashboard/market-index-chart";
import { HoldingsTable } from "@/components/dashboard/holdings-table";
import { TradeSignals } from "@/components/dashboard/trade-signals";
import { OrderTimeline } from "@/components/dashboard/order-timeline";
import { StrategyPerformanceCards } from "@/components/dashboard/strategy-performance";
import { PortfolioHoldingsTable } from "@/components/portfolio/portfolio-holdings-table";
import { PortfolioPieChart } from "@/components/portfolio/portfolio-pie-chart";
import { Separator } from "@/components/ui/separator";

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

      {/* 시장 지수 미니 차트 */}
      <MarketIndexCharts />

      {/* 보유종목 요약 테이블 */}
      <HoldingsTable />

      {/* 매매 신호 + 주문 타임라인 + 전략 성과 (3단 그리드) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <TradeSignals />
        <OrderTimeline />
        <StrategyPerformanceCards />
      </div>

      <Separator />

      {/* 포트폴리오 상세 섹션 */}
      <div>
        <h3 className="text-xl font-semibold mb-4">포트폴리오 상세</h3>
        <div className="grid grid-cols-1 xl:grid-cols-[1fr_350px] gap-6">
          <PortfolioHoldingsTable />
          <PortfolioPieChart />
        </div>
      </div>
    </div>
  );
}
