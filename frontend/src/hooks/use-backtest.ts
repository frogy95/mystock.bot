"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";

/** 백엔드 시뮬레이션 거래 내역 타입 */
export interface BacktestTradeAPI {
  type: string;       // "BUY" | "SELL"
  date: string;       // "YYYY-MM-DD"
  price: number;
  qty: number;
  amount: number;
  pnl: number | null; // SELL 시 손익, BUY는 null
}

/** 백엔드 Equity Curve 포인트 타입 */
export interface EquityPoint {
  date: string;           // "YYYY-MM-DD"
  value: number;          // 포트폴리오 가치 (원)
  benchmark: number;      // 벤치마크 가치 (원)
  stock_buyhold: number;  // 종목 바이앤홀드 가치 (원)
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
  trades: BacktestTradeAPI[];  // 시뮬레이션 거래 내역
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
  strategy_id?: number;  // 커스텀 전략 DB ID
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

// ── Sprint 24: 다중 백테스트 훅 ──────────────────────────────────────

/** 랭킹 항목 타입 */
export interface BacktestRankingEntry {
  strategy_id: number;
  strategy_name: string;
  rank: number;
  score: number;
  total_return: number;
  cagr: number;
  mdd: number;
  sharpe_ratio: number;
  win_rate: number;
  total_trades: number;
}

/** 다중 백테스트 개별 결과 */
export interface BacktestMultiResultItem {
  strategy_id: number;
  strategy_name: string;
  total_return: number;
  cagr: number;
  mdd: number;
  sharpe_ratio: number;
  win_rate: number;
  total_trades: number;
  benchmark_return: number;
  equity_curve: EquityPoint[];
}

/** 다중 백테스트 응답 타입 */
export interface BacktestMultiResponse {
  symbol: string;
  results: BacktestMultiResultItem[];
  ranking: BacktestRankingEntry[];
}

/** 다중 백테스트 실행 요청 타입 */
export interface BacktestMultiRunRequest {
  symbol: string;
  strategy_ids: number[];
  start_date: string;
  end_date: string;
  initial_cash?: number;
}

/** 관심종목 상태 항목 */
export interface WatchlistStatusItem {
  item_id: number;
  group_name: string;
  current_strategy: string | null;
}

/** 종목 보유/관심 상태 응답 */
export interface StockStatusAPI {
  is_holding: boolean;
  holding_id: number | null;
  current_sell_strategy: string | null;
  is_watchlist: boolean;
  watchlist_items: WatchlistStatusItem[];
}

/** 다중 백테스트 실행 훅 */
export function useBacktestRunMulti() {
  return useMutation<BacktestMultiResponse, Error, BacktestMultiRunRequest>({
    mutationFn: (request) =>
      apiClient.post<BacktestMultiResponse>("/api/v1/backtest/run-multi", request),
    onError: (error) => {
      console.error("[useBacktestRunMulti] 다중 백테스트 실패:", error);
    },
  });
}

/** 종목 보유/관심 상태 조회 훅 */
export function useStockStatus(symbol: string | null) {
  return useQuery<StockStatusAPI>({
    queryKey: ["backtest", "stock-status", symbol],
    queryFn: () => apiClient.get<StockStatusAPI>(`/api/v1/backtest/stock-status/${symbol}`),
    enabled: !!symbol,
    staleTime: 30_000,
  });
}

// ── Sprint 25: AI 추천 훅 ─────────────────────────────────────────────

/** AI 추천 요청 내 전략 성과 요약 */
export interface AIRecommendResultSummary {
  strategy_name: string;
  total_return: number;
  mdd: number;
  sharpe_ratio: number;
  win_rate: number;
  total_trades: number;
}

/** AI 전략 추천 요청 타입 */
export interface AIRecommendRequest {
  symbol: string;
  stock_name?: string;
  results_summary: AIRecommendResultSummary[];
  is_holding: boolean;
  is_watchlist: boolean;
}

/** AI 전략 추천 응답 타입 */
export interface AIRecommendationResponse {
  recommended_strategy: string;
  confidence: "높음" | "보통" | "낮음";
  analysis: string;
  risk_warning: string;
  position_advice: string;
}

/** AI 전략 추천 뮤테이션 훅 */
export function useAIRecommend() {
  return useMutation<AIRecommendationResponse, Error, AIRecommendRequest>({
    mutationFn: (request) =>
      apiClient.post<AIRecommendationResponse>("/api/v1/backtest/ai-recommend", request),
    onError: (error) => {
      console.error("[useAIRecommend] AI 추천 실패:", error);
    },
  });
}
