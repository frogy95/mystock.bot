"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import type { WatchlistGroupAPI, WatchlistItemAPI } from "./use-watchlist";

/** 관심종목 그룹 생성 */
export function useCreateWatchlistGroup() {
  const queryClient = useQueryClient();
  return useMutation<WatchlistGroupAPI, Error, { name: string }>({
    mutationFn: (body) =>
      apiClient.post<WatchlistGroupAPI>("/api/v1/watchlist/groups", body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["watchlist", "groups"] });
    },
  });
}

/** 관심종목 그룹 수정 */
export function useUpdateWatchlistGroup() {
  const queryClient = useQueryClient();
  return useMutation<WatchlistGroupAPI, Error, { groupId: number; name: string }>({
    mutationFn: ({ groupId, name }) =>
      apiClient.put<WatchlistGroupAPI>(`/api/v1/watchlist/groups/${groupId}`, { name }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["watchlist", "groups"] });
    },
  });
}

/** 관심종목 그룹 삭제 */
export function useDeleteWatchlistGroup() {
  const queryClient = useQueryClient();
  return useMutation<void, Error, number>({
    mutationFn: (groupId) =>
      apiClient.delete<void>(`/api/v1/watchlist/groups/${groupId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["watchlist", "groups"] });
    },
  });
}

/** 관심종목 항목 추가 */
export function useAddWatchlistItem() {
  const queryClient = useQueryClient();
  return useMutation<
    WatchlistItemAPI,
    Error,
    { groupId: number; stock_code: string; stock_name: string }
  >({
    mutationFn: ({ groupId, stock_code, stock_name }) =>
      apiClient.post<WatchlistItemAPI>(
        `/api/v1/watchlist/groups/${groupId}/items`,
        { stock_code, stock_name }
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["watchlist", "groups"] });
    },
  });
}

/** 관심종목 항목 삭제 */
export function useRemoveWatchlistItem() {
  const queryClient = useQueryClient();
  return useMutation<void, Error, { groupId: number; itemId: number }>({
    mutationFn: ({ groupId, itemId }) =>
      apiClient.delete<void>(`/api/v1/watchlist/groups/${groupId}/items/${itemId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["watchlist", "groups"] });
    },
  });
}

/** 관심종목 전략 할당/해제 */
export function useAssignWatchlistStrategy() {
  const queryClient = useQueryClient();
  return useMutation<
    WatchlistItemAPI,
    Error,
    { itemId: number; strategy_id: number | null }
  >({
    mutationFn: ({ itemId, strategy_id }) =>
      apiClient.put<WatchlistItemAPI>(`/api/v1/watchlist/items/${itemId}/strategy`, {
        strategy_id,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["watchlist", "groups"] });
    },
  });
}
