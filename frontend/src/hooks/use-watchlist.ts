"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";

/** 백엔드 종목 검색 응답 타입 */
export interface StockSearchItem {
  symbol: string;
  name: string;
  market: string;
}

/** 백엔드 관심종목 항목 응답 타입 */
export interface WatchlistItemAPI {
  id: number;
  group_id: number;
  stock_code: string;
  stock_name: string;
  strategy_id: number | null;
  created_at: string;
}

/** 백엔드 관심종목 그룹 응답 타입 */
export interface WatchlistGroupAPI {
  id: number;
  name: string;
  sort_order: number;
  items: WatchlistItemAPI[];
  created_at: string;
}

/** 종목 검색 훅 (Redis 캐시 기반 실시간 검색) */
export function useStockSearch(query: string) {
  return useQuery<StockSearchItem[]>({
    queryKey: ["stocks", "search", query],
    queryFn: () =>
      apiClient.get<StockSearchItem[]>(
        `/api/v1/stocks/search?q=${encodeURIComponent(query)}`
      ),
    enabled: query.trim().length > 0,
    staleTime: 30_000,
  });
}

/** 관심종목 그룹 전체 조회 훅 */
export function useWatchlistGroups() {
  return useQuery<WatchlistGroupAPI[]>({
    queryKey: ["watchlist", "groups"],
    queryFn: () => apiClient.get<WatchlistGroupAPI[]>("/api/v1/watchlist/groups"),
    staleTime: 60_000,
  });
}
