"use client";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Progress } from "@/components/ui/progress";
import type { OrderDetail } from "@/lib/mock/types";

interface OrderDetailDialogProps {
  order: OrderDetail;
  trigger: React.ReactNode; // 다이얼로그 트리거 버튼
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

/** 주문 상세 다이얼로그 컴포넌트 */
export function OrderDetailDialog({ order, trigger }: OrderDetailDialogProps) {
  return (
    <Dialog>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 flex-wrap">
            <span>{order.name}</span>
            <OrderTypeBadge orderType={order.orderType} />
            <StatusBadge status={order.status} />
          </DialogTitle>
        </DialogHeader>

        <Separator />

        {/* 상세 정보 그리드 */}
        <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
          <div className="text-muted-foreground">수량</div>
          <div className="font-medium">{order.quantity.toLocaleString("ko-KR")} 주</div>

          <div className="text-muted-foreground">가격</div>
          <div className="font-medium">{order.price.toLocaleString("ko-KR")} 원</div>

          <div className="text-muted-foreground">총액</div>
          <div className="font-medium">{order.totalAmount.toLocaleString("ko-KR")} 원</div>

          <div className="text-muted-foreground">전략</div>
          <div className="font-medium">{order.strategyName}</div>

          <div className="text-muted-foreground">생성일</div>
          <div className="font-medium">{order.createdAt.split("T")[0]}</div>

          <div className="text-muted-foreground">체결일</div>
          <div className="font-medium">
            {order.executedAt ? order.executedAt.split("T")[0] : "-"}
          </div>
        </div>

        <Separator />

        {/* 판단 근거 섹션 */}
        <div className="space-y-2">
          <p className="text-sm font-semibold">판단 근거</p>
          <p className="text-sm text-muted-foreground leading-relaxed">{order.reason}</p>
        </div>

        {/* 신뢰도 Progress 바 */}
        <div className="space-y-1">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">신뢰도</span>
            <span className="font-medium">{order.confidence}%</span>
          </div>
          <Progress value={order.confidence} />
        </div>
      </DialogContent>
    </Dialog>
  );
}
