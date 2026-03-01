"use client";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { cn } from "@/lib/utils";
import type { StrategyDetail } from "@/lib/mock/types";

interface StrategyCardProps {
  strategy: StrategyDetail;
  isSelected: boolean;
  onSelect: (id: string) => void;
  onToggleActive: (id: string) => void;
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

export function StrategyCard({
  strategy,
  isSelected,
  onSelect,
  onToggleActive,
}: StrategyCardProps) {
  const { id, name, category, totalReturn, winRate, tradeCount, assignedStocks, isActive } =
    strategy;

  return (
    <Card
      className={cn(
        "cursor-pointer transition-all",
        // 선택된 카드에 ring 효과 적용
        isSelected && "ring-2 ring-primary"
      )}
      onClick={() => onSelect(id)}
    >
      {/* 카드 상단: 전략명 + 카테고리 Badge */}
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between gap-2">
          <CardTitle className="text-base leading-tight">{name}</CardTitle>
          <Badge variant={categoryVariant[category]}>
            {categoryLabel[category]}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {/* 카드 중간: 요약 지표 3개 수평 배치 */}
        <div className="flex items-center justify-between text-sm">
          {/* 총 수익률: 양수=빨간색, 음수=파란색 */}
          <div className="flex flex-col items-center gap-0.5">
            <span className="text-xs text-muted-foreground">총 수익률</span>
            <span
              className={cn(
                "font-semibold",
                totalReturn > 0 && "text-red-600",
                totalReturn < 0 && "text-blue-600",
                totalReturn === 0 && "text-muted-foreground"
              )}
            >
              {totalReturn > 0 ? "+" : ""}
              {totalReturn.toFixed(2)}%
            </span>
          </div>

          {/* 승률 */}
          <div className="flex flex-col items-center gap-0.5">
            <span className="text-xs text-muted-foreground">승률</span>
            <span className="font-semibold">{winRate.toFixed(1)}%</span>
          </div>

          {/* 매매 횟수 */}
          <div className="flex flex-col items-center gap-0.5">
            <span className="text-xs text-muted-foreground">매매횟수</span>
            <span className="font-semibold">{tradeCount}회</span>
          </div>
        </div>

        {/* 카드 하단: 적용 종목 수 + Switch 토글 */}
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">
            {assignedStocks.length}개 종목 적용 중
          </span>
          {/* Switch 클릭 시 카드 선택 이벤트 차단 */}
          <Switch
            checked={isActive}
            onCheckedChange={() => onToggleActive(id)}
            onClick={(e) => e.stopPropagation()}
            aria-label={`${name} 전략 활성화 토글`}
          />
        </div>
      </CardContent>
    </Card>
  );
}
