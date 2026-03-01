"use client";

import { useQuery } from "@tanstack/react-query";
import {
  mockTradeSignals,
  mockOrderExecutions,
  mockStrategyPerformances,
  mockMarketIndices,
} from "@/lib/mock";
import type {
  TradeSignal,
  OrderExecution,
  StrategyPerformance,
  MarketIndex,
} from "@/lib/mock/types";
import { apiClient } from "@/lib/api/client";
import type { HoldingAPI } from "./use-portfolio";

/** 백엔드 포트폴리오 요약 응답 타입 */
interface PortfolioSummaryAPI {
  total_evaluation: number;
  total_purchase: number;
  total_profit_loss: number;
  total_profit_loss_rate: number;
  deposit: number;
  holdings_count: number;
}

// Mock 지연 시뮬레이션 (아직 Mock 사용하는 훅들에서만 사용)
function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/** 포트폴리오 요약 조회 (실제 API) */
export function usePortfolioSummary() {
  return useQuery<PortfolioSummaryAPI>({
    queryKey: ["portfolio", "summary"],
    queryFn: () => apiClient.get<PortfolioSummaryAPI>("/api/v1/holdings/summary"),
    staleTime: 60_000,
  });
}

/** 보유종목 목록 조회 (실제 API) */
export function useHoldings() {
  return useQuery<HoldingAPI[]>({
    queryKey: ["portfolio", "holdings"],
    queryFn: () => apiClient.get<HoldingAPI[]>("/api/v1/holdings"),
    staleTime: 60_000,
  });
}

/** 매매 신호 (Sprint 6에서 실제 API 연동 예정) */
export function useTradeSignals() {
  return useQuery<TradeSignal[]>({
    queryKey: ["dashboard", "tradeSignals"],
    queryFn: async () => {
      await delay(400);
      return mockTradeSignals;
    },
  });
}

/** 주문 체결 내역 (Sprint 6에서 실제 API 연동 예정) */
export function useOrderExecutions() {
  return useQuery<OrderExecution[]>({
    queryKey: ["dashboard", "orderExecutions"],
    queryFn: async () => {
      await delay(500);
      return mockOrderExecutions;
    },
  });
}

/** 전략 성과 (Sprint 6에서 실제 API 연동 예정) */
export function useStrategyPerformances() {
  return useQuery<StrategyPerformance[]>({
    queryKey: ["dashboard", "strategyPerformances"],
    queryFn: async () => {
      await delay(300);
      return mockStrategyPerformances;
    },
  });
}

/** 시장 지수 (Sprint 9에서 실제 API 연동 예정) */
export function useMarketIndices() {
  return useQuery<MarketIndex[]>({
    queryKey: ["dashboard", "marketIndices"],
    queryFn: async () => {
      await delay(700);
      return mockMarketIndices;
    },
  });
}
