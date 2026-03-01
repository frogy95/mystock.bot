"use client";

import { useQuery } from "@tanstack/react-query";
import {
  mockPortfolioSummary,
  mockHoldings,
  mockTradeSignals,
  mockOrderExecutions,
  mockStrategyPerformances,
  mockMarketIndices,
} from "@/lib/mock";
import type {
  PortfolioSummary,
  HoldingItem,
  TradeSignal,
  OrderExecution,
  StrategyPerformance,
  MarketIndex,
} from "@/lib/mock/types";

// Mock API 지연 시뮬레이션
function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export function usePortfolioSummary() {
  return useQuery<PortfolioSummary>({
    queryKey: ["portfolio", "summary"],
    queryFn: async () => {
      await delay(500);
      return mockPortfolioSummary;
    },
  });
}

export function useHoldings() {
  return useQuery<HoldingItem[]>({
    queryKey: ["portfolio", "holdings"],
    queryFn: async () => {
      await delay(600);
      return mockHoldings;
    },
  });
}

export function useTradeSignals() {
  return useQuery<TradeSignal[]>({
    queryKey: ["dashboard", "tradeSignals"],
    queryFn: async () => {
      await delay(400);
      return mockTradeSignals;
    },
  });
}

export function useOrderExecutions() {
  return useQuery<OrderExecution[]>({
    queryKey: ["dashboard", "orderExecutions"],
    queryFn: async () => {
      await delay(500);
      return mockOrderExecutions;
    },
  });
}

export function useStrategyPerformances() {
  return useQuery<StrategyPerformance[]>({
    queryKey: ["dashboard", "strategyPerformances"],
    queryFn: async () => {
      await delay(300);
      return mockStrategyPerformances;
    },
  });
}

export function useMarketIndices() {
  return useQuery<MarketIndex[]>({
    queryKey: ["dashboard", "marketIndices"],
    queryFn: async () => {
      await delay(700);
      return mockMarketIndices;
    },
  });
}
