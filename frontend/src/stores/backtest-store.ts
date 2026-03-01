"use client";

import { create } from "zustand";
import type { BacktestResult, BacktestTrade } from "@/lib/mock/types";

interface BacktestState {
  /** 백테스팅 결과 */
  result: BacktestResult | null;
  /** 거래 내역 */
  trades: BacktestTrade[];
  /** 백테스트 실행 중 여부 */
  isRunning: boolean;

  /** 결과 저장 */
  setResult: (result: BacktestResult, trades: BacktestTrade[]) => void;
  /** 실행 상태 변경 */
  setRunning: (v: boolean) => void;
  /** 결과 초기화 */
  reset: () => void;
}

export const useBacktestStore = create<BacktestState>((set) => ({
  result: null,
  trades: [],
  isRunning: false,

  setResult: (result, trades) => set({ result, trades }),

  setRunning: (v) => set({ isRunning: v }),

  reset: () => set({ result: null, trades: [], isRunning: false }),
}));
