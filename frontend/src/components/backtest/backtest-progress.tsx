"use client";

import { CheckCircle2, XCircle, Loader2 } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import type { BacktestProgressEvent, BacktestMultiResultItem } from "@/hooks/use-backtest";

interface BacktestProgressProps {
  progress: BacktestProgressEvent | null;
  results: BacktestMultiResultItem[];
  total: number;
}

export function BacktestProgress({ progress, results, total }: BacktestProgressProps) {
  const completed = progress?.completed ?? 0;
  const percent = total > 0 ? Math.round((completed / total) * 100) : 0;

  // 완료된 전략 이름 목록 (result 이벤트 기반)
  const completedNames = new Set(results.map((r) => r.strategy_name));

  return (
    <div className="rounded-lg border p-4 space-y-4">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium">백테스트 진행 중...</span>
        <span className="text-muted-foreground">
          {completed} / {total}
        </span>
      </div>

      <Progress value={percent} className="h-2" />

      {progress?.status === "running" && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-3.5 w-3.5 animate-spin" />
          <span>{progress.strategy_name}: {progress.step ?? "분석 중..."}</span>
        </div>
      )}

      {/* 전략별 완료 상태 */}
      {results.length > 0 && (
        <div className="space-y-1.5 max-h-[160px] overflow-y-auto">
          {results.map((r) => (
            <div key={r.strategy_id} className="flex items-center gap-2 text-xs">
              <CheckCircle2 className="h-3.5 w-3.5 text-green-500 shrink-0" />
              <span>{r.strategy_name}</span>
              <span className="text-muted-foreground ml-auto">
                {r.total_return >= 0 ? "+" : ""}
                {r.total_return.toFixed(2)}%
              </span>
            </div>
          ))}
          {/* 실패한 전략 표시 */}
          {progress?.status === "error" && !completedNames.has(progress.strategy_name) && (
            <div className="flex items-center gap-2 text-xs">
              <XCircle className="h-3.5 w-3.5 text-destructive shrink-0" />
              <span className="text-destructive">{progress.strategy_name} (실패)</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
