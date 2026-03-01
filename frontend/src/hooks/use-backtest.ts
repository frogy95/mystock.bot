"use client";

import { useQuery } from "@tanstack/react-query";
import { mockBacktestResult } from "@/lib/mock";
import type { BacktestResult } from "@/lib/mock/types";

// Mock API 지연 시뮬레이션
function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/** 백테스팅 결과 조회 훅 */
export function useBacktestResult() {
  return useQuery<BacktestResult>({
    queryKey: ["backtest", "result"],
    queryFn: async () => {
      await delay(800);
      return mockBacktestResult;
    },
  });
}
