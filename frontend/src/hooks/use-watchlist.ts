"use client";

import { useQuery } from "@tanstack/react-query";
import { mockSearchableStocks } from "@/lib/mock";
import type { StockQuote } from "@/lib/mock/types";

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/** 종목 검색 훅 */
export function useStockSearch(query: string) {
  return useQuery<StockQuote[]>({
    queryKey: ["stocks", "search", query],
    queryFn: async () => {
      await delay(300);
      if (!query.trim()) return [];
      const q = query.trim().toLowerCase();
      return mockSearchableStocks.filter(
        (s) =>
          s.name.toLowerCase().includes(q) ||
          s.symbol.includes(q)
      );
    },
    enabled: query.trim().length > 0,
  });
}
