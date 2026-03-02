"use client";

import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import type {
  TradeSignal,
  OrderExecution,
  StrategyPerformance,
  MarketIndex,
} from "@/lib/mock/types";
import { apiClient } from "@/lib/api/client";
import type { HoldingAPI } from "./use-portfolio";
import { useRealtimeQuotes } from "./use-realtime";

/** 백엔드 포트폴리오 요약 응답 타입 */
interface PortfolioSummaryAPI {
  total_evaluation: number;
  total_purchase: number;
  total_profit_loss: number;
  total_profit_loss_rate: number;
  deposit: number;
  holdings_count: number;
  daily_profit_loss?: number;
  daily_profit_rate?: number;
}

/** 백엔드 주문 API 응답 타입 */
interface OrderAPI {
  id: number;
  stock_code: string;
  order_type: string;
  status: string;
  strategy_id: number | null;
  quantity: number | null;
  price: number | null;
  created_at: string;
  updated_at: string;
}

/** 백엔드 전략 성과 API 응답 타입 */
interface StrategyPerformanceAPI {
  id: number;
  name: string;
  trade_count: number;
  buy_count: number;
  sell_count: number;
  win_rate: number;
  active_stocks: number;
  is_active: boolean;
}

/** 백엔드 시장 지수 API 응답 타입 */
interface MarketIndexAPI {
  index_code: string;
  name: string;
  current_value: number;
  change_value: number;
  change_rate: number;
}

/** 포트폴리오 요약 조회 (실제 API) — snake_case → camelCase 변환 */
export function usePortfolioSummary() {
  return useQuery({
    queryKey: ["portfolio", "summary"],
    queryFn: async () => {
      const raw = await apiClient.get<PortfolioSummaryAPI>("/api/v1/holdings/summary");
      return {
        totalEvaluation: raw.total_evaluation,
        totalPurchase: raw.total_purchase,
        totalProfitLoss: raw.total_profit_loss,
        totalProfitRate: raw.total_profit_loss_rate,
        dailyProfitLoss: raw.daily_profit_loss ?? 0,
        dailyProfitRate: raw.daily_profit_rate ?? 0,
        cashBalance: raw.deposit,
        holdingsCount: raw.holdings_count,
      };
    },
    staleTime: 60_000,
  });
}

/** 보유종목 목록 조회 (실제 API) + 실시간 시세 반영 */
export function useHoldings() {
  const query = useQuery<HoldingAPI[]>({
    queryKey: ["portfolio", "holdings"],
    queryFn: () => apiClient.get<HoldingAPI[]>("/api/v1/holdings"),
    staleTime: 60_000,
  });

  // 보유종목 심볼 목록 추출 (실시간 시세 구독용)
  const symbols = useMemo(
    () => (query.data ?? []).map((h) => h.stock_code),
    [query.data]
  );

  // WebSocket 실시간 시세 구독
  const { quotes, connected: wsConnected } = useRealtimeQuotes(symbols);

  // 실시간 시세를 보유종목 데이터에 반영
  const holdingsWithRealtime = useMemo(() => {
    if (!query.data) return query.data;
    return query.data.map((holding) => {
      const realtime = quotes[holding.stock_code];
      if (!realtime) return holding;
      return {
        ...holding,
        current_price: realtime.price,
        profit_loss_rate:
          holding.avg_price > 0
            ? ((realtime.price - holding.avg_price) / holding.avg_price) * 100
            : holding.profit_loss_rate,
      };
    });
  }, [query.data, quotes]);

  return { ...query, data: holdingsWithRealtime, wsConnected };
}

/** 매매 신호: 오늘 주문 목록을 TradeSignal로 변환 */
export function useTradeSignals() {
  return useQuery<TradeSignal[]>({
    queryKey: ["dashboard", "tradeSignals"],
    queryFn: async () => {
      const orders = await apiClient.get<OrderAPI[]>("/api/v1/orders");
      const today = new Date().toISOString().slice(0, 10);
      return orders
        .filter((o) => o.created_at.startsWith(today))
        .map((o) => ({
          id: String(o.id),
          symbol: o.stock_code,
          name: o.stock_code,
          strategyName: o.strategy_id ? `전략 #${o.strategy_id}` : "수동",
          signalType: o.order_type.toUpperCase() as "BUY" | "SELL",
          reason: o.status,
          targetPrice: o.price ?? 0,
          confidence: 100,
          createdAt: o.created_at,
        }));
    },
    refetchInterval: 60_000,
  });
}

/** 주문 체결 내역: 최근 10건을 OrderExecution으로 변환 */
export function useOrderExecutions() {
  return useQuery<OrderExecution[]>({
    queryKey: ["dashboard", "orderExecutions"],
    queryFn: async () => {
      const orders = await apiClient.get<OrderAPI[]>("/api/v1/orders");
      return orders.slice(0, 10).map((o) => ({
        id: String(o.id),
        symbol: o.stock_code,
        name: o.stock_code,
        orderType: o.order_type.toUpperCase() as "BUY" | "SELL",
        quantity: o.quantity ?? 0,
        price: o.price ?? 0,
        status: o.status.toUpperCase() as "FILLED" | "PENDING" | "CANCELLED",
        strategyName: o.strategy_id ? `전략 #${o.strategy_id}` : "수동",
        executedAt: o.created_at,
      }));
    },
    refetchInterval: 60_000,
  });
}

/** 전략 성과: 실제 API 연동 */
export function useStrategyPerformances() {
  return useQuery<StrategyPerformance[]>({
    queryKey: ["dashboard", "strategyPerformances"],
    queryFn: async () => {
      const data = await apiClient.get<StrategyPerformanceAPI[]>("/api/v1/strategies/performance");
      return data.map((s) => ({
        id: String(s.id),
        name: s.name,
        totalReturn: 0,
        winRate: s.win_rate,
        tradeCount: s.trade_count,
        activeStocks: s.active_stocks,
        isActive: s.is_active,
      }));
    },
    refetchInterval: 120_000,
  });
}

/** 시장 지수: 실제 API 연동 */
export function useMarketIndices() {
  return useQuery<MarketIndex[]>({
    queryKey: ["dashboard", "marketIndices"],
    queryFn: async () => {
      const data = await apiClient.get<MarketIndexAPI[]>("/api/v1/stocks/market-index");
      return data.map((d) => ({
        name: d.name,
        currentValue: d.current_value,
        changeValue: d.change_value,
        changeRate: d.change_rate,
        chartData: [],
      }));
    },
    refetchInterval: 60_000,
  });
}
