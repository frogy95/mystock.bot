"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";

/** 백엔드 전략 파라미터 응답 타입 */
export interface StrategyParamAPI {
  id: number;
  param_key: string;
  param_value: string;
  param_type: string;
}

/** 백엔드 전략 응답 타입 */
export interface StrategyAPI {
  id: number;
  name: string;
  strategy_type: string;
  is_active: boolean;
  is_preset: boolean;
  user_id: number | null;
  params: StrategyParamAPI[];
  created_at: string;
}

/** 전략 신호 응답 타입 */
export interface StrategySignalAPI {
  symbol: string;
  signal_type: "BUY" | "SELL" | "HOLD";
  confidence: number;
  reason: string;
  target_price: number | null;
}

/** 전략 목록 조회 훅 */
export function useStrategies() {
  return useQuery<StrategyAPI[]>({
    queryKey: ["strategy", "list"],
    queryFn: () => apiClient.get<StrategyAPI[]>("/api/v1/strategies"),
    staleTime: 60_000,
  });
}

/** 단일 전략 조회 훅 */
export function useStrategy(id: number) {
  return useQuery<StrategyAPI>({
    queryKey: ["strategy", id],
    queryFn: () => apiClient.get<StrategyAPI>(`/api/v1/strategies/${id}`),
    enabled: id > 0,
    staleTime: 60_000,
  });
}

/** 전략 활성화/비활성화 훅 */
export function useToggleStrategy() {
  const queryClient = useQueryClient();
  return useMutation<StrategyAPI, Error, { id: number; is_active: boolean }>({
    mutationFn: ({ id, is_active }) =>
      apiClient.put<StrategyAPI>(`/api/v1/strategies/${id}/activate`, { is_active }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["strategy"] });
    },
  });
}

/** 전략 파라미터 업데이트 훅 */
export function useUpdateStrategyParams() {
  const queryClient = useQueryClient();
  return useMutation<
    StrategyAPI,
    Error,
    { id: number; params: Array<{ param_key: string; param_value: string; param_type: string }> }
  >({
    mutationFn: ({ id, params }) =>
      apiClient.put<StrategyAPI>(`/api/v1/strategies/${id}/params`, { params }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["strategy"] });
    },
  });
}

/** 전략 신호 평가 훅 */
export function useEvaluateSignal() {
  return useMutation<StrategySignalAPI, Error, { strategyId: number; symbol: string }>({
    mutationFn: ({ strategyId, symbol }) =>
      apiClient.post<StrategySignalAPI>(
        `/api/v1/strategies/${strategyId}/evaluate/${symbol}`,
        {}
      ),
  });
}

/** 프리셋 전략 복사(클론) 훅 */
export function useCloneStrategy() {
  const queryClient = useQueryClient();
  return useMutation<StrategyAPI, Error, { id: number }>({
    mutationFn: ({ id }) =>
      apiClient.post<StrategyAPI>(`/api/v1/strategies/${id}/clone`, {}),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["strategy"] });
    },
  });
}

/** 전략 이름 변경 훅 */
export function useRenameStrategy() {
  const queryClient = useQueryClient();
  return useMutation<StrategyAPI, Error, { id: number; name: string }>({
    mutationFn: ({ id, name }) =>
      apiClient.put<StrategyAPI>(`/api/v1/strategies/${id}/name`, { name }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["strategy"] });
    },
  });
}

/** 전략 삭제 훅 */
export function useDeleteStrategy() {
  const queryClient = useQueryClient();
  return useMutation<void, Error, { id: number }>({
    mutationFn: ({ id }) =>
      apiClient.delete<void>(`/api/v1/strategies/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["strategy"] });
    },
  });
}
