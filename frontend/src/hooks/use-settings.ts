"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";

/** 백엔드 설정 항목 타입 */
export interface SettingItemAPI {
  setting_key: string;
  setting_value: string;
  setting_type: string;
}

/** 안전장치 상태 타입 */
export interface SafetyStatusAPI {
  auto_trade_enabled: boolean;
  daily_loss_check: { ok: boolean; message: string };
  daily_order_check: { ok: boolean; message: string };
  system: { error_count: number; max_errors: number; is_healthy: boolean };
}

/** 긴급 매도 결과 타입 */
export interface EmergencySellResult {
  executed_count: number;
  failed_count: number;
  auto_trade_disabled: boolean;
}

/** 시스템 설정 전체 조회 훅 */
export function useSystemSettings() {
  return useQuery<SettingItemAPI[]>({
    queryKey: ["settings", "system"],
    queryFn: () => apiClient.get<SettingItemAPI[]>("/api/v1/system-settings"),
    staleTime: 60_000,
  });
}

/** 안전장치 상태 조회 훅 */
export function useSafetyStatus() {
  return useQuery<SafetyStatusAPI>({
    queryKey: ["safety", "status"],
    queryFn: () => apiClient.get<SafetyStatusAPI>("/api/v1/safety/status"),
    staleTime: 30_000,
    refetchInterval: 60_000, // 1분마다 자동 갱신
  });
}

/** 설정 일괄 업데이트 훅 */
export function useUpdateSettings() {
  const queryClient = useQueryClient();
  return useMutation<SettingItemAPI[], Error, SettingItemAPI[]>({
    mutationFn: (settings) =>
      apiClient.put<SettingItemAPI[]>("/api/v1/system-settings", { settings }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["settings"] });
    },
  });
}

/** 자동매매 토글 훅 */
export function useToggleAutoTrade() {
  const queryClient = useQueryClient();
  return useMutation<{ auto_trade_enabled: boolean }, Error, boolean>({
    mutationFn: (enabled) =>
      apiClient.post<{ auto_trade_enabled: boolean }>("/api/v1/safety/auto-trade", {
        enabled,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["safety"] });
    },
  });
}

/** 긴급 전체 매도 훅 */
export function useEmergencySell() {
  const queryClient = useQueryClient();
  return useMutation<EmergencySellResult, Error, void>({
    mutationFn: () =>
      apiClient.post<EmergencySellResult>("/api/v1/safety/emergency-sell", {}),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["portfolio"] });
      queryClient.invalidateQueries({ queryKey: ["safety"] });
    },
  });
}
