"use client";

import { useState } from "react";
import { useOrders } from "@/hooks/use-orders";
import type { OrderAPI } from "@/hooks/use-orders";
import { OrdersFilter } from "@/components/orders/orders-filter";
import { OrdersTable } from "@/components/orders/orders-table";
import type { OrderDetail } from "@/lib/mock/types";

type StatusFilter = "ALL" | "FILLED" | "PENDING" | "CANCELLED";
type OrderTypeFilter = "ALL" | "BUY" | "SELL";

/**
 * API 소문자 status → 컴포넌트 대문자 타입 변환
 * "failed", "simulated" 등 미지원 상태는 "CANCELLED"로 폴백
 */
function normalizeStatus(status: string): "FILLED" | "PENDING" | "CANCELLED" {
  switch (status.toLowerCase()) {
    case "filled": return "FILLED";
    case "pending": return "PENDING";
    case "cancelled": return "CANCELLED";
    default: return "CANCELLED";
  }
}

/** OrderAPI → OrderDetail 타입 변환 */
function mapOrderAPIToDetail(order: OrderAPI): OrderDetail {
  return {
    id: String(order.id),
    symbol: order.stock_code,
    name: order.stock_code, // API에 종목명 없으므로 코드로 대체
    orderType: order.order_type.toLowerCase() === "sell" ? "SELL" : "BUY",
    quantity: order.quantity ?? 0,
    price: order.price ?? 0,
    totalAmount: (order.quantity ?? 0) * (order.price ?? 0),
    status: normalizeStatus(order.status),
    strategyId: String(order.strategy_id ?? ""),
    strategyName: "-",
    reason: "-",
    confidence: 0,
    createdAt: order.created_at,
    executedAt: null,
  };
}

/** 필터 조건에 따라 주문 목록을 필터링하는 함수 */
function getFilteredOrders(
  orders: OrderDetail[],
  statusFilter: StatusFilter,
  orderTypeFilter: OrderTypeFilter,
  symbolFilter: string
): OrderDetail[] {
  return orders.filter((order) => {
    if (statusFilter !== "ALL" && order.status !== statusFilter) return false;
    if (orderTypeFilter !== "ALL" && order.orderType !== orderTypeFilter) return false;
    if (
      symbolFilter.trim() !== "" &&
      !order.symbol.toLowerCase().includes(symbolFilter.toLowerCase()) &&
      !order.name.toLowerCase().includes(symbolFilter.toLowerCase())
    ) {
      return false;
    }
    return true;
  });
}

/** 주문 내역 페이지 */
export default function OrdersPage() {
  // 실제 API 훅으로 주문 목록 조회
  const { data: apiOrders, isLoading, isError } = useOrders();

  // 필터 상태를 로컬 상태로 관리
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("ALL");
  const [orderTypeFilter, setOrderTypeFilter] = useState<OrderTypeFilter>("ALL");
  const [symbolFilter, setSymbolFilter] = useState("");

  // API 응답을 컴포넌트 타입으로 변환
  const orders: OrderDetail[] = (apiOrders ?? []).map(mapOrderAPIToDetail);
  const filteredOrders = getFilteredOrders(orders, statusFilter, orderTypeFilter, symbolFilter);

  return (
    <div className="space-y-4">
      {/* 페이지 제목 */}
      <h2 className="text-2xl font-semibold">주문 내역</h2>

      {isLoading && <p className="text-muted-foreground">로딩 중...</p>}
      {isError && <p className="text-destructive">주문 목록을 불러오는 중 오류가 발생했습니다.</p>}

      {!isLoading && !isError && (
        <>
          {/* 필터 컴포넌트 */}
          <OrdersFilter
            statusFilter={statusFilter}
            orderTypeFilter={orderTypeFilter}
            symbolFilter={symbolFilter}
            onStatusFilterChange={(v) => setStatusFilter(v as StatusFilter)}
            onOrderTypeFilterChange={(v) => setOrderTypeFilter(v as OrderTypeFilter)}
            onSymbolFilterChange={setSymbolFilter}
          />

          {/* 주문 테이블 (취소 API 없으므로 noop 전달) */}
          <OrdersTable orders={filteredOrders} onCancel={() => {}} />
        </>
      )}
    </div>
  );
}
