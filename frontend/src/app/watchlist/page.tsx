"use client";

import { useMemo, useEffect } from "react";
import { StockSearch } from "@/components/watchlist/stock-search";
import { WatchlistGroupTabs } from "@/components/watchlist/watchlist-group-tabs";
import { useWatchlistStore } from "@/stores/watchlist-store";
import { useRealtimeQuotes } from "@/hooks/use-realtime";

export default function WatchlistPage() {
  const { groups, updateItemQuote } = useWatchlistStore();

  // 모든 그룹의 심볼 목록 추출 (WebSocket 구독용)
  const symbols = useMemo(
    () => [...new Set(groups.flatMap((g) => g.items.map((i) => i.symbol)))],
    [groups]
  );

  // WebSocket 실시간 시세 구독
  const { quotes } = useRealtimeQuotes(symbols);

  // 시세 변경 시 스토어 업데이트
  useEffect(() => {
    Object.entries(quotes).forEach(([sym, quote]) => {
      updateItemQuote(sym, {
        currentPrice: quote.price,
        changeRate: quote.changeRate,
        changePrice: quote.change,
        volume: quote.volume,
      });
    });
  }, [quotes, updateItemQuote]);

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
