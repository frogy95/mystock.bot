"use client";

import { create } from "zustand";
import { mockStrategies } from "@/lib/mock";
import type { StrategyDetail } from "@/lib/mock/types";

interface StrategyState {
  strategies: StrategyDetail[];
  selectedStrategyId: string | null;

  // 전략 목록 일괄 교체 (API 데이터 sync용)
  setStrategies: (strategies: StrategyDetail[]) => void;
  // 선택된 전략 변경
  selectStrategy: (id: string | null) => void;
  // 전략 활성화/비활성화 토글
  toggleActive: (id: string) => void;
  // 파라미터 값 업데이트
  updateParam: (strategyId: string, paramKey: string, value: number | string) => void;
  // assignedStocks에 종목 추가 (중복 체크)
  addStock: (strategyId: string, symbol: string) => void;
  // assignedStocks에서 종목 제거
  removeStock: (strategyId: string, symbol: string) => void;
}

export const useStrategyStore = create<StrategyState>((set) => ({
  strategies: mockStrategies,
  selectedStrategyId: null,

  setStrategies: (strategies) => set({ strategies }),

  selectStrategy: (id) => set({ selectedStrategyId: id }),

  toggleActive: (id) =>
    set((state) => ({
      strategies: state.strategies.map((strategy) =>
        strategy.id === id
          ? { ...strategy, isActive: !strategy.isActive }
          : strategy
      ),
    })),

  updateParam: (strategyId, paramKey, value) =>
    set((state) => ({
      strategies: state.strategies.map((strategy) => {
        if (strategy.id !== strategyId) return strategy;
        return {
          ...strategy,
          params: strategy.params.map((param) =>
            param.key === paramKey ? { ...param, value } : param
          ),
        };
      }),
    })),

  addStock: (strategyId, symbol) =>
    set((state) => ({
      strategies: state.strategies.map((strategy) => {
        if (strategy.id !== strategyId) return strategy;
        // 중복 체크: 이미 존재하는 종목이면 추가하지 않음
        if (strategy.assignedStocks.includes(symbol)) return strategy;
        return {
          ...strategy,
          assignedStocks: [...strategy.assignedStocks, symbol],
        };
      }),
    })),

  removeStock: (strategyId, symbol) =>
    set((state) => ({
      strategies: state.strategies.map((strategy) => {
        if (strategy.id !== strategyId) return strategy;
        return {
          ...strategy,
          assignedStocks: strategy.assignedStocks.filter((s) => s !== symbol),
        };
      }),
    })),
}));
