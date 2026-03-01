"use client";

import { useQuery } from "@tanstack/react-query";
import { mockOrders } from "@/lib/mock";
import type { OrderDetail } from "@/lib/mock/types";

// Mock API 지연 시뮬레이션
function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/** 주문 목록 전체 조회 훅 */
export function useOrders() {
  return useQuery<OrderDetail[]>({
    queryKey: ["orders", "list"],
    queryFn: async () => {
      await delay(500);
      return mockOrders;
    },
  });
}
