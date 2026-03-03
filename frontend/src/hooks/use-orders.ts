"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import type { OrderAPI } from "@/lib/api/types";

export type { OrderAPI };

/** 주문 목록 조회 훅 */
export function useOrders() {
  return useQuery<OrderAPI[]>({
    queryKey: ["orders", "list"],
    queryFn: () => apiClient.get<OrderAPI[]>("/api/v1/orders"),
    staleTime: 30_000,
    refetchInterval: 60_000, // 1분마다 자동 갱신
  });
}

/** 주문 취소 mutation 훅 */
export function useCancelOrder() {
  const queryClient = useQueryClient();
  return useMutation<OrderAPI, Error, number>({
    mutationFn: (orderId: number) =>
      apiClient.put<OrderAPI>(`/api/v1/orders/${orderId}/cancel`, {}),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["orders", "list"] });
    },
  });
}
