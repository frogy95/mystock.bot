"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import type { HoldingAPI } from "./use-portfolio";

/** KIS 잔고 동기화 응답 타입 */
interface SyncResponse {
  synced_count: number;
  holdings: HoldingAPI[];
}

/** KIS 잔고 동기화 훅 (수동 - 실패 시 에러 토스트 표시) */
export function useSyncHoldings() {
  const queryClient = useQueryClient();
  return useMutation<SyncResponse, Error, void>({
    mutationFn: () => apiClient.post<SyncResponse>("/api/v1/holdings/sync", {}),
    onSuccess: () => {
      // 동기화 후 보유종목 및 대시보드 캐시 무효화
      queryClient.invalidateQueries({ queryKey: ["portfolio"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

/** KIS 잔고 자동 동기화 훅 (silent - 실패 시 에러 토스트 생략) */
export function useSilentSyncHoldings() {
  const queryClient = useQueryClient();
  return useMutation<SyncResponse, Error, void>({
    mutationFn: () => apiClient.post<SyncResponse>("/api/v1/holdings/sync", {}),
    meta: { silent: true },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["portfolio"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

/** 손절/익절 설정 훅 */
export function useUpdateStopLoss() {
  const queryClient = useQueryClient();
  return useMutation<
    HoldingAPI,
    Error,
    { holdingId: number; stop_loss_rate: number | null; take_profit_rate: number | null }
  >({
    mutationFn: ({ holdingId, stop_loss_rate, take_profit_rate }) =>
      apiClient.put<HoldingAPI>(`/api/v1/holdings/${holdingId}/stop-loss`, {
        stop_loss_rate,
        take_profit_rate,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["portfolio", "holdings"] });
    },
  });
}

/** 매도 전략 설정 훅 */
export function useUpdateSellStrategy() {
  const queryClient = useQueryClient();
  return useMutation<
    HoldingAPI,
    Error,
    { holdingId: number; sell_strategy_id: number | null }
  >({
    mutationFn: ({ holdingId, sell_strategy_id }) =>
      apiClient.put<HoldingAPI>(`/api/v1/holdings/${holdingId}/sell-strategy`, {
        sell_strategy_id,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["portfolio", "holdings"] });
    },
  });
}
