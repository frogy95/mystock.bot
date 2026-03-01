"use client";

import { useQuery } from "@tanstack/react-query";
import { mockHoldings } from "@/lib/mock";
import { mockPortfolioPieData } from "@/lib/mock/portfolio";
import type { HoldingItem } from "@/lib/mock/types";
import type { PortfolioPieData } from "@/lib/mock/portfolio";

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export function usePortfolioHoldings() {
  return useQuery<HoldingItem[]>({
    queryKey: ["portfolio", "holdings"],
    queryFn: async () => {
      await delay(500);
      return mockHoldings;
    },
  });
}

export function usePortfolioPieData() {
  return useQuery<PortfolioPieData[]>({
    queryKey: ["portfolio", "pie"],
    queryFn: async () => {
      await delay(400);
      return mockPortfolioPieData;
    },
  });
}
