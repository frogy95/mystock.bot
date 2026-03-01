"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useTradeSignals } from "@/hooks/use-dashboard";
import { formatKRW, formatTime } from "@/lib/format";
import { cn } from "@/lib/utils";
import { ArrowUpCircle, ArrowDownCircle } from "lucide-react";

export function TradeSignals() {
  const { data: signals, isLoading } = useTradeSignals();

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">오늘의 매매 신호</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {isLoading ? (
          Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="flex items-start gap-3 p-3 rounded-lg border">
              <Skeleton className="h-8 w-8 rounded-full" />
              <div className="flex-1 space-y-1">
                <Skeleton className="h-4 w-32" />
                <Skeleton className="h-3 w-48" />
              </div>
            </div>
          ))
        ) : signals && signals.length > 0 ? (
          signals.map((signal) => (
            <div
              key={signal.id}
              className={cn(
                "flex items-start gap-3 p-3 rounded-lg border",
                signal.signalType === "BUY"
                  ? "border-red-200 bg-red-50/50 dark:border-red-900 dark:bg-red-950/30"
                  : "border-blue-200 bg-blue-50/50 dark:border-blue-900 dark:bg-blue-950/30"
              )}
            >
              {signal.signalType === "BUY" ? (
                <ArrowUpCircle className="h-5 w-5 text-red-500 shrink-0 mt-0.5" />
              ) : (
                <ArrowDownCircle className="h-5 w-5 text-blue-500 shrink-0 mt-0.5" />
              )}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-sm">{signal.name}</span>
                  <Badge
                    variant={signal.signalType === "BUY" ? "destructive" : "default"}
                    className="text-xs"
                  >
                    {signal.signalType === "BUY" ? "매수" : "매도"}
                  </Badge>
                  <span className="text-xs text-muted-foreground ml-auto">
                    {formatTime(signal.createdAt)}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground mt-1 truncate">
                  {signal.reason}
                </p>
                <div className="flex items-center gap-3 mt-1.5 text-xs">
                  <span>목표가: {formatKRW(signal.targetPrice)}</span>
                  <span>신뢰도: {signal.confidence}%</span>
                  <Badge variant="outline" className="text-xs">
                    {signal.strategyName}
                  </Badge>
                </div>
              </div>
            </div>
          ))
        ) : (
          <p className="text-center text-muted-foreground py-6 text-sm">
            오늘 발생한 매매 신호가 없습니다.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
