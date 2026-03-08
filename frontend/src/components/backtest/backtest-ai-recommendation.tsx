"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  useAIRecommend,
  type AIRecommendationResponse,
  type AIRecommendResultSummary,
} from "@/hooks/use-backtest";
import type { StockStatusAPI } from "@/hooks/use-backtest";

interface BacktestAIRecommendationProps {
  symbol: string;
  resultsSummary: AIRecommendResultSummary[];
  stockStatus: StockStatusAPI | null;
}

/** 신뢰도 뱃지 색상 */
function ConfidenceBadge({ confidence }: { confidence: string }) {
  const variant =
    confidence === "높음"
      ? "default"
      : confidence === "보통"
        ? "secondary"
        : "destructive";
  return <Badge variant={variant}>신뢰도: {confidence}</Badge>;
}

export function BacktestAIRecommendation({
  symbol,
  resultsSummary,
  stockStatus,
}: BacktestAIRecommendationProps) {
  const [result, setResult] = useState<AIRecommendationResponse | null>(null);
  const aiRecommend = useAIRecommend();

  const handleAnalyze = () => {
    aiRecommend.mutate(
      {
        symbol,
        stock_name: symbol,
        results_summary: resultsSummary,
        is_holding: stockStatus?.is_holding ?? false,
        is_watchlist: stockStatus?.is_watchlist ?? false,
      },
      {
        onSuccess: (data) => setResult(data),
      }
    );
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">AI 전략 분석</CardTitle>
          <Button
            size="sm"
            onClick={handleAnalyze}
            disabled={aiRecommend.isPending || resultsSummary.length === 0}
          >
            {aiRecommend.isPending ? "분석 중..." : "AI 분석 요청"}
          </Button>
        </div>
      </CardHeader>

      {aiRecommend.isError && (
        <CardContent>
          <p className="text-sm text-destructive">
            AI 분석 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.
          </p>
        </CardContent>
      )}

      {result && (
        <CardContent className="space-y-4">
          {/* 추천 전략 + 신뢰도 */}
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium text-muted-foreground">추천 전략</span>
            <span className="font-semibold">{result.recommended_strategy}</span>
            <ConfidenceBadge confidence={result.confidence} />
          </div>

          {/* 분석 코멘트 */}
          <div className="rounded-md bg-muted/50 p-3 text-sm">
            <p className="mb-1 font-medium text-muted-foreground">분석</p>
            <p>{result.analysis}</p>
          </div>

          {/* 리스크 경고 */}
          <div className="rounded-md bg-destructive/10 p-3 text-sm">
            <p className="mb-1 font-medium text-destructive">리스크 경고</p>
            <p className="text-destructive/90">{result.risk_warning}</p>
          </div>

          {/* 포지션 조언 */}
          <div className="rounded-md bg-primary/5 p-3 text-sm">
            <p className="mb-1 font-medium text-primary">포지션 조언</p>
            <p>{result.position_advice}</p>
          </div>

          <p className="text-xs text-muted-foreground">
            * AI 분석은 과거 데이터 기반 참고용이며 투자 권유가 아닙니다.
          </p>
        </CardContent>
      )}
    </Card>
  );
}
