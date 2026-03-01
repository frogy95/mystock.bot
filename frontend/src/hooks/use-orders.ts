"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";

/** 백엔드 주문 응답 타입 */
export interface OrderAPI {
  id: number;
  stock_code: string;
  order_type: string;      // "buy" | "sell"
  status: string;          // "pending" | "filled" | "cancelled" | "failed" | "simulated"
  strategy_id: number | null;
  quantity: number | null;
  price: number | null;
  created_at: string;
  updated_at: string;
}

/** 주문 목록 조회 훅 */
export function useOrders() {
  return useQuery<OrderAPI[]>({
    queryKey: ["orders", "list"],
    queryFn: () => apiClient.get<OrderAPI[]>("/api/v1/orders"),
    staleTime: 30_000,
    refetchInterval: 60_000, // 1분마다 자동 갱신
  });
}
