"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useOrderExecutions } from "@/hooks/use-dashboard";
import { formatKRW, formatDateTime } from "@/lib/format";
import { cn } from "@/lib/utils";

const statusMap = {
  FILLED: { label: "체결", variant: "default" as const, dotClass: "bg-green-500" },
  PENDING: { label: "대기", variant: "secondary" as const, dotClass: "bg-yellow-500" },
  CANCELLED: { label: "취소", variant: "outline" as const, dotClass: "bg-gray-400" },
};

export function OrderTimeline() {
  const { data: orders, isLoading } = useOrderExecutions();

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">최근 주문</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="flex items-center gap-3">
                <Skeleton className="h-2.5 w-2.5 rounded-full" />
                <div className="flex-1 space-y-1">
                  <Skeleton className="h-4 w-40" />
                  <Skeleton className="h-3 w-24" />
                </div>
              </div>
            ))}
          </div>
        ) : orders && orders.length > 0 ? (
          <div className="relative">
            {/* 타임라인 세로선 */}
            <div className="absolute left-[5px] top-2 bottom-2 w-px bg-border" />
            <div className="space-y-4">
              {orders.map((order) => {
                const statusInfo = statusMap[order.status];
                return (
                  <div key={order.id} className="flex items-start gap-3 relative">
                    {/* 타임라인 점 */}
                    <div
                      className={cn(
                        "h-2.5 w-2.5 rounded-full shrink-0 mt-1.5 z-10",
                        statusInfo.dotClass
                      )}
                    />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-sm">{order.name}</span>
                        <Badge
                          variant={order.orderType === "BUY" ? "destructive" : "default"}
                          className="text-xs"
                        >
                          {order.orderType === "BUY" ? "매수" : "매도"}
                        </Badge>
                        <Badge variant={statusInfo.variant} className="text-xs">
                          {statusInfo.label}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {order.quantity}주 × {formatKRW(order.price)} | {order.strategyName}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {formatDateTime(order.executedAt)}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          <p className="text-center text-muted-foreground py-6 text-sm">
            최근 주문이 없습니다.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
