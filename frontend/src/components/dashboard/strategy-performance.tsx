"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Progress } from "@/components/ui/progress";
import { useStrategyPerformances } from "@/hooks/use-dashboard";
import { formatPercent } from "@/lib/format";
import { cn } from "@/lib/utils";

export function StrategyPerformanceCards() {
  const { data: strategies, isLoading } = useStrategyPerformances();

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">전략별 성과</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {isLoading ? (
          Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="p-3 rounded-lg border space-y-2">
              <Skeleton className="h-4 w-32" />
              <Skeleton className="h-2 w-full" />
              <Skeleton className="h-3 w-48" />
            </div>
          ))
        ) : strategies && strategies.length > 0 ? (
          strategies.map((strategy) => (
            <div key={strategy.id} className="p-3 rounded-lg border space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-medium text-sm">{strategy.name}</span>
                <Badge variant={strategy.isActive ? "default" : "outline"} className="text-xs">
                  {strategy.isActive ? "활성" : "비활성"}
                </Badge>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted-foreground w-8">승률</span>
                <Progress value={strategy.winRate} className="h-2 flex-1" />
                <span className="text-xs font-mono w-10 text-right">
                  {strategy.winRate}%
                </span>
              </div>
              <div className="flex items-center gap-4 text-xs text-muted-foreground">
                <span>
                  수익률:{" "}
                  <span
                    className={cn(
                      "font-medium",
                      strategy.totalReturn > 0 ? "text-red-600" : "text-blue-600"
                    )}
                  >
                    {formatPercent(strategy.totalReturn)}
                  </span>
                </span>
                <span>매매 {strategy.tradeCount}건</span>
                <span>{strategy.activeStocks}종목</span>
              </div>
            </div>
          ))
        ) : (
          <p className="text-center text-muted-foreground py-6 text-sm">
            등록된 전략이 없습니다.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
