"use client";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { useStrategyStore } from "@/stores/strategy-store";
import { StrategyParamForm } from "./strategy-param-form";
import { StrategyStockMapping } from "./strategy-stock-mapping";
import type { StrategyDetail } from "@/lib/mock/types";

interface StrategyDetailPanelProps {
  strategyId: string | null;
}

/** 카테고리별 Badge variant 매핑 */
const categoryVariant: Record<
  StrategyDetail["category"],
  "secondary" | "outline" | "default" | "destructive"
> = {
  trend: "secondary",
  reversal: "outline",
  value: "default",
  momentum: "destructive",
};

/** 카테고리 한국어 레이블 */
const categoryLabel: Record<StrategyDetail["category"], string> = {
  trend: "추세추종",
  reversal: "반전",
  value: "가치",
  momentum: "모멘텀",
};

/** 전략 상세 패널 - 파라미터 설정 및 종목 매핑을 함께 표시 */
export function StrategyDetailPanel({ strategyId }: StrategyDetailPanelProps) {
  // 스토어에서 전략 목록을 가져와 선택된 전략 찾기
  const strategy = useStrategyStore((state) =>
    strategyId ? state.strategies.find((s) => s.id === strategyId) : undefined
  );

  // 선택된 전략이 없으면 안내 메시지 표시
  if (!strategyId || !strategy) {
    return (
      <div className="flex h-full items-center justify-center rounded-lg border border-dashed p-8">
        <p className="text-sm text-muted-foreground">전략을 선택하세요</p>
      </div>
    );
  }

  return (
    <Card className="h-full overflow-auto">
      {/* 상단: 전략명 + 카테고리 Badge + 설명 */}
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2 flex-wrap">
          <CardTitle className="text-lg">{strategy.name}</CardTitle>
          <Badge variant={categoryVariant[strategy.category]}>
            {categoryLabel[strategy.category]}
          </Badge>
        </div>
        <p className="text-sm text-muted-foreground mt-1">{strategy.description}</p>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* 파라미터 설정 섹션 */}
        <div className="space-y-3">
          <Separator />
          <h3 className="text-sm font-semibold">파라미터 설정</h3>
          <StrategyParamForm
            strategyId={strategy.id}
            params={strategy.params}
          />
        </div>

        {/* 종목 매핑 섹션 */}
        <div className="space-y-3">
          <Separator />
          <h3 className="text-sm font-semibold">종목 매핑</h3>
          <StrategyStockMapping
            strategyId={strategy.id}
            assignedStocks={strategy.assignedStocks}
          />
        </div>
      </CardContent>
    </Card>
  );
}
