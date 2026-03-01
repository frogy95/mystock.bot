"use client";

import { create } from "zustand";
import { mockSystemSettings } from "@/lib/mock";
import type {
  SystemSettings,
  KisApiConfig,
  TelegramConfig,
  TradingTimeConfig,
  SafetyConfig,
} from "@/lib/mock/types";

interface SettingsState {
  settings: SystemSettings;

  // KIS API 설정 업데이트
  updateKisApi: (updates: Partial<KisApiConfig>) => void;
  // 텔레그램 설정 업데이트
  updateTelegram: (updates: Partial<TelegramConfig>) => void;
  // 매매 시간 설정 업데이트
  updateTradingTime: (updates: Partial<TradingTimeConfig>) => void;
  // 안전장치 설정 업데이트
  updateSafety: (updates: Partial<SafetyConfig>) => void;
  // 자동매매 마스터 스위치 토글
  toggleAutoTrade: () => void;
}

export const useSettingsStore = create<SettingsState>((set) => ({
  // mock 데이터로 초기화
  settings: mockSystemSettings,

  updateKisApi: (updates) =>
    set((state) => ({
      settings: {
        ...state.settings,
        kisApi: { ...state.settings.kisApi, ...updates },
      },
    })),

  updateTelegram: (updates) =>
    set((state) => ({
      settings: {
        ...state.settings,
        telegram: { ...state.settings.telegram, ...updates },
      },
    })),

  updateTradingTime: (updates) =>
    set((state) => ({
      settings: {
        ...state.settings,
        tradingTime: { ...state.settings.tradingTime, ...updates },
      },
    })),

  updateSafety: (updates) =>
    set((state) => ({
      settings: {
        ...state.settings,
        safety: { ...state.settings.safety, ...updates },
      },
    })),

  toggleAutoTrade: () =>
    set((state) => ({
      settings: {
        ...state.settings,
        autoTradeEnabled: !state.settings.autoTradeEnabled,
      },
    })),
}));
