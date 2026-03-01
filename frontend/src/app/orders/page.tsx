"use client";

import { useOrdersStore } from "@/stores/orders-store";
import { OrdersFilter } from "@/components/orders/orders-filter";
import { OrdersTable } from "@/components/orders/orders-table";
import type { OrderDetail } from "@/lib/mock/types";

/** 필터 조건에 따라 주문 목록을 필터링하는 함수 */
function getFilteredOrders(
  orders: OrderDetail[],
  statusFilter: string,
  orderTypeFilter: string,
  symbolFilter: string
): OrderDetail[] {
  return orders.filter((order) => {
    // 상태 필터 적용
    if (statusFilter !== "ALL" && order.status !== statusFilter) return false;

    // 매수/매도 필터 적용
    if (orderTypeFilter !== "ALL" && order.orderType !== orderTypeFilter) return false;

    // 종목코드 검색어 필터 적용 (대소문자 무관)
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
  // 스토어에서 상태 및 액션 가져오기
  const orders = useOrdersStore((state) => state.orders);
  const statusFilter = useOrdersStore((state) => state.statusFilter);
  const orderTypeFilter = useOrdersStore((state) => state.orderTypeFilter);
  const symbolFilter = useOrdersStore((state) => state.symbolFilter);
  const setStatusFilter = useOrdersStore((state) => state.setStatusFilter);
  const setOrderTypeFilter = useOrdersStore((state) => state.setOrderTypeFilter);
  const setSymbolFilter = useOrdersStore((state) => state.setSymbolFilter);
  const cancelOrder = useOrdersStore((state) => state.cancelOrder);

  // 필터 적용된 주문 목록 계산
  const filteredOrders = getFilteredOrders(
    orders,
    statusFilter,
    orderTypeFilter,
    symbolFilter
  );

  return (
    <div className="space-y-4">
      {/* 페이지 제목 */}
      <h2 className="text-2xl font-semibold">주문 내역</h2>

      {/* 필터 컴포넌트 */}
      <OrdersFilter
        statusFilter={statusFilter}
        orderTypeFilter={orderTypeFilter}
        symbolFilter={symbolFilter}
        onStatusFilterChange={(v) =>
          setStatusFilter(v as "ALL" | "FILLED" | "PENDING" | "CANCELLED")
        }
        onOrderTypeFilterChange={(v) =>
          setOrderTypeFilter(v as "ALL" | "BUY" | "SELL")
        }
        onSymbolFilterChange={setSymbolFilter}
      />

      {/* 주문 테이블 컴포넌트 */}
      <OrdersTable orders={filteredOrders} onCancel={cancelOrder} />
    </div>
  );
}
