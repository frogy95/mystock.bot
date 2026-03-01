"use client";

import { StockSearch } from "@/components/watchlist/stock-search";
import { WatchlistGroupTabs } from "@/components/watchlist/watchlist-group-tabs";

export default function WatchlistPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">관심종목</h2>
        <p className="text-muted-foreground text-sm mt-1">
          관심 종목을 그룹별로 관리하고 전략을 할당합니다.
        </p>
      </div>

      {/* 종목 검색 */}
      <StockSearch />

      {/* 그룹별 관심종목 테이블 */}
      <WatchlistGroupTabs />
    </div>
  );
}
