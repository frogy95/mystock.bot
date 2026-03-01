"use client";

import { useQuery } from "@tanstack/react-query";
import { mockStrategies } from "@/lib/mock";
import type { StrategyDetail } from "@/lib/mock/types";

// Mock API 지연 시뮬레이션
function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/** 전략 목록 전체 조회 훅 */
export function useStrategies() {
  return useQuery<StrategyDetail[]>({
    queryKey: ["strategy", "list"],
    queryFn: async () => {
      await delay(400);
      return mockStrategies;
    },
  });
}

/** 단일 전략 조회 훅 */
export function useStrategy(id: string) {
  return useQuery<StrategyDetail | undefined>({
    queryKey: ["strategy", id],
    queryFn: async () => {
      await delay(300);
      return mockStrategies.find((strategy) => strategy.id === id);
    },
  });
}
