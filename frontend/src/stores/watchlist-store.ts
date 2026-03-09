"use client";

import { create } from "zustand";
import { mockWatchlistGroups } from "@/lib/mock";
import type { WatchlistGroup, WatchlistItem, StockQuote } from "@/lib/mock/types";

interface WatchlistState {
  groups: WatchlistGroup[];
  activeGroupId: string;
  setActiveGroup: (groupId: string) => void;
  addItem: (groupId: string, stock: StockQuote) => void;
  removeItem: (groupId: string, itemId: string) => void;
  assignStrategy: (groupId: string, itemId: string, strategy: string | null) => void;
  addGroup: (name: string) => void;
  removeGroup: (groupId: string) => void;
  updateItemQuote: (symbol: string, quote: { currentPrice: number; changeRate: number; changePrice: number; volume: number }) => void;
}

export const useWatchlistStore = create<WatchlistState>((set) => ({
  groups: mockWatchlistGroups,
  activeGroupId: mockWatchlistGroups[0]?.id ?? "",

  setActiveGroup: (groupId) => set({ activeGroupId: groupId }),

  addItem: (groupId, stock) =>
    set((state) => ({
      groups: state.groups.map((group) => {
        if (group.id !== groupId) return group;
        // 중복 체크
        if (group.items.some((item) => item.symbol === stock.symbol)) return group;
        const newItem: WatchlistItem = {
          id: `wi-${Date.now()}`,
          symbol: stock.symbol,
          name: stock.name,
          market: stock.market,
          currentPrice: stock.currentPrice,
          changeRate: stock.changeRate,
          changePrice: stock.changePrice,
          volume: stock.volume,
          per: null,
          pbr: null,
          marketCap: 0,
          assignedStrategy: null,
        };
        return { ...group, items: [...group.items, newItem] };
      }),
    })),

  removeItem: (groupId, itemId) =>
    set((state) => ({
      groups: state.groups.map((group) => {
        if (group.id !== groupId) return group;
        return { ...group, items: group.items.filter((item) => item.id !== itemId) };
      }),
    })),

  assignStrategy: (groupId, itemId, strategy) =>
    set((state) => ({
      groups: state.groups.map((group) => {
        if (group.id !== groupId) return group;
        return {
          ...group,
          items: group.items.map((item) =>
            item.id === itemId ? { ...item, assignedStrategy: strategy } : item
          ),
        };
      }),
    })),

  addGroup: (name) =>
    set((state) => ({
      groups: [
        ...state.groups,
        { id: `grp-${Date.now()}`, name, items: [] },
      ],
    })),

  removeGroup: (groupId) =>
    set((state) => ({
      groups: state.groups.filter((g) => g.id !== groupId),
      activeGroupId:
        state.activeGroupId === groupId
          ? (state.groups.find((g) => g.id !== groupId)?.id ?? "")
          : state.activeGroupId,
    })),

  updateItemQuote: (symbol, quote) =>
    set((state) => ({
      groups: state.groups.map((group) => ({
        ...group,
        items: group.items.map((item) =>
          item.symbol === symbol ? { ...item, ...quote } : item
        ),
      })),
    })),
}));
