"use client";

import { create } from "zustand";
import { mockOrders } from "@/lib/mock";
import type { OrderDetail } from "@/lib/mock/types";

// 상태 필터 타입
type StatusFilter = "ALL" | "FILLED" | "PENDING" | "CANCELLED";

// 주문 유형 필터 타입
type OrderTypeFilter = "ALL" | "BUY" | "SELL";

interface OrdersState {
  // 주문 목록 (mockOrders로 초기화)
  orders: OrderDetail[];

  // 상태 필터 (전체 / 체결완료 / 미체결 / 취소)
  statusFilter: StatusFilter;

  // 매수/매도 필터
  orderTypeFilter: OrderTypeFilter;

  // 종목코드 검색어
  symbolFilter: string;

  // 상태 필터 변경
  setStatusFilter: (status: StatusFilter) => void;

  // 매수/매도 필터 변경
  setOrderTypeFilter: (type: OrderTypeFilter) => void;

  // 종목코드 필터 변경
  setSymbolFilter: (symbol: string) => void;

  // 주문 취소 (PENDING 상태인 경우만 CANCELLED로 변경)
  cancelOrder: (id: string) => void;
}

export const useOrdersStore = create<OrdersState>((set) => ({
  orders: mockOrders,
  statusFilter: "ALL",
  orderTypeFilter: "ALL",
  symbolFilter: "",

  setStatusFilter: (status) => set({ statusFilter: status }),

  setOrderTypeFilter: (type) => set({ orderTypeFilter: type }),

  setSymbolFilter: (symbol) => set({ symbolFilter: symbol }),

  cancelOrder: (id) =>
    set((state) => ({
      orders: state.orders.map((order) =>
        // PENDING 상태인 주문만 CANCELLED로 변경
        order.id === id && order.status === "PENDING"
          ? { ...order, status: "CANCELLED" as const }
          : order
      ),
    })),
}));
