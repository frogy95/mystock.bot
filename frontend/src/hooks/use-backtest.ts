"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";

/** 백엔드 Equity Curve 포인트 타입 */
export interface EquityPoint {
  date: string;   // "YYYY-MM-DD"
  value: number;  // 포트폴리오 가치 (원)
}

/** 백엔드 백테스팅 결과 응답 타입 */
export interface BacktestResultAPI {
  id: number;
  symbol: string;
  strategy_name: string;
  start_date: string;
  end_date: string;
  total_return: number;       // 총 수익률 (%)
  cagr: number;               // 연환산 수익률 (%)
  mdd: number;                // 최대 낙폭 (%)
  sharpe_ratio: number;       // 샤프 지수
  total_trades: number;       // 총 거래 횟수
  win_rate: number;           // 승률 (%)
  benchmark_return: number;   // 벤치마크 수익률 (%)
  equity_curve: EquityPoint[]; // 자산 가치 곡선
  created_at: string;
}

/** 백테스팅 실행 요청 타입 */
export interface BacktestRunRequest {
  symbol: string;
  strategy_name: string;
  params?: Record<string, number | string>;
  start_date: string;   // "YYYY-MM-DD"
  end_date: string;     // "YYYY-MM-DD"
  initial_cash?: number;
}

/**
 * 백테스팅 결과 목록 조회 훅
 * GET /api/v1/backtest/results
 */
export function useBacktestResults() {
  return useQuery<BacktestResultAPI[]>({
    queryKey: ["backtest", "results"],
    queryFn: () => apiClient.get<BacktestResultAPI[]>("/api/v1/backtest/results"),
    staleTime: 30_000,
  });
}

/**
 * 특정 백테스팅 결과 조회 훅
 * GET /api/v1/backtest/results/{id}
 */
export function useBacktestResult(id: number) {
  return useQuery<BacktestResultAPI>({
    queryKey: ["backtest", "result", id],
    queryFn: () => apiClient.get<BacktestResultAPI>(`/api/v1/backtest/results/${id}`),
    enabled: id > 0,
    staleTime: 60_000,
  });
}

/**
 * 백테스팅 실행 뮤테이션 훅
 * POST /api/v1/backtest/run
 */
export function useBacktestRun() {
  const queryClient = useQueryClient();
  return useMutation<BacktestResultAPI, Error, BacktestRunRequest>({
    mutationFn: (request) =>
      apiClient.post<BacktestResultAPI>("/api/v1/backtest/run", request),
    onSuccess: () => {
      // 결과 목록 캐시 무효화
      queryClient.invalidateQueries({ queryKey: ["backtest", "results"] });
    },
    onError: (error) => {
      // 백테스팅 실행 실패 로깅 (toast는 MutationCache 글로벌 핸들러에서 처리)
      console.error("[useBacktestRun] 백테스팅 실행 실패:", error);
    },
  });
}
