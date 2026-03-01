"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { OrderDetailDialog } from "./order-detail-dialog";
import type { OrderDetail } from "@/lib/mock/types";

interface OrdersTableProps {
  orders: OrderDetail[];
  onCancel: (id: string) => void;
}

/** 주문 구분 Badge (BUY: 빨간색, SELL: 파란색) */
function OrderTypeBadge({ orderType }: { orderType: "BUY" | "SELL" }) {
  if (orderType === "BUY") {
    return (
      <Badge className="bg-red-500 hover:bg-red-600 text-white">매수</Badge>
    );
  }
  return (
    <Badge className="bg-blue-500 hover:bg-blue-600 text-white">매도</Badge>
  );
}

/** 주문 상태 Badge */
function StatusBadge({ status }: { status: "FILLED" | "PENDING" | "CANCELLED" }) {
  if (status === "FILLED") return <Badge>체결완료</Badge>;
  if (status === "PENDING") return <Badge variant="secondary">미체결</Badge>;
  return <Badge variant="outline">취소</Badge>;
}

/** 주문 내역 테이블 컴포넌트 */
export function OrdersTable({ orders, onCancel }: OrdersTableProps) {
  return (
    <Card>
      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>종목</TableHead>
              <TableHead>구분</TableHead>
              <TableHead>상태</TableHead>
              <TableHead className="text-right">수량</TableHead>
              <TableHead className="text-right">가격</TableHead>
              <TableHead className="text-right">총액</TableHead>
              <TableHead>전략</TableHead>
              <TableHead>생성일</TableHead>
              <TableHead>액션</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {orders.length === 0 ? (
              // 빈 목록 메시지
              <TableRow>
                <TableCell
                  colSpan={9}
                  className="h-24 text-center text-muted-foreground"
                >
                  조회된 주문이 없습니다
                </TableCell>
              </TableRow>
            ) : (
              orders.map((order) => (
                <TableRow key={order.id}>
                  {/* 종목: name (symbol) 형식, 클릭 시 상세 다이얼로그 */}
                  <TableCell>
                    <OrderDetailDialog
                      order={order}
                      trigger={
                        <button className="text-left hover:underline cursor-pointer">
                          <span className="font-medium">{order.name}</span>
                          <br />
                          <span className="text-xs text-muted-foreground">
                            {order.symbol}
                          </span>
                        </button>
                      }
                    />
                  </TableCell>

                  {/* 구분 Badge */}
                  <TableCell>
                    <OrderTypeBadge orderType={order.orderType} />
                  </TableCell>

                  {/* 상태 Badge */}
                  <TableCell>
                    <StatusBadge status={order.status} />
                  </TableCell>

                  {/* 수량 */}
                  <TableCell className="text-right">
                    {order.quantity.toLocaleString("ko-KR")}
                  </TableCell>

                  {/* 가격 */}
                  <TableCell className="text-right">
                    {order.price.toLocaleString("ko-KR")}
                  </TableCell>

                  {/* 총액 */}
                  <TableCell className="text-right">
                    {order.totalAmount.toLocaleString("ko-KR")}
                  </TableCell>

                  {/* 전략 */}
                  <TableCell className="text-sm">{order.strategyName}</TableCell>

                  {/* 생성일 (날짜만 표시) */}
                  <TableCell className="text-sm">
                    {order.createdAt.split("T")[0]}
                  </TableCell>

                  {/* 액션: PENDING인 경우 취소 버튼, 아니면 빈칸 */}
                  <TableCell>
                    {order.status === "PENDING" ? (
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => onCancel(order.id)}
                      >
                        취소
                      </Button>
                    ) : null}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
