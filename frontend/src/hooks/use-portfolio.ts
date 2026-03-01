"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";

/** 백엔드 보유종목 응답 타입 */
export interface HoldingAPI {
  id: number;
  stock_code: string;
  stock_name: string;
  quantity: number;
  avg_price: number;
  current_price: number | null;
  stop_loss_rate: number | null;
  take_profit_rate: number | null;
  sell_strategy_id: number | null;
  synced_at: string | null;
  profit_loss: number | null;
  profit_loss_rate: number | null;
  total_value: number | null;
}

/** 포트폴리오 파이 차트용 가공 타입 */
export interface PortfolioPieData {
  name: string;
  value: number;
  color: string;
}

/** 포트폴리오 보유종목 조회 훅 */
export function usePortfolioHoldings() {
  return useQuery<HoldingAPI[]>({
    queryKey: ["portfolio", "holdings", "detail"],
    queryFn: () => apiClient.get<HoldingAPI[]>("/api/v1/holdings"),
    staleTime: 60_000,
  });
}

/** 포트폴리오 파이 차트 데이터 (보유종목 기반 계산) */
export function usePortfolioPieData() {
  const { data: holdings = [], ...rest } = usePortfolioHoldings();

  // 보유종목 평가금액 기준으로 파이 차트 데이터 생성
  const PIE_COLORS = [
    "#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6",
    "#06B6D4", "#F97316", "#84CC16", "#EC4899", "#6366F1",
  ];

  const pieData: PortfolioPieData[] = holdings
    .filter((h) => h.total_value != null && h.total_value > 0)
    .map((h, i) => ({
      name: h.stock_name,
      value: h.total_value!,
      color: PIE_COLORS[i % PIE_COLORS.length],
    }));

  return { data: pieData, ...rest };
}
