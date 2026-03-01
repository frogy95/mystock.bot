"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { useCustomStrategyStore } from "@/stores/custom-strategy-store";
import { ConditionSection } from "./condition-section";
import { StrategyPreview } from "./strategy-preview";

/** 커스텀 전략 편집기 */
export function CustomStrategyEditor() {
  const strategies = useCustomStrategyStore((s) => s.strategies);
  const selectedId = useCustomStrategyStore((s) => s.selectedStrategyId);
  const updateStrategyName = useCustomStrategyStore((s) => s.updateStrategyName);

  const strategy = strategies.find((s) => s.id === selectedId);

  // 전략 미선택 시 빈 상태 안내
  if (!strategy) {
    return (
      <div className="flex h-64 items-center justify-center rounded-lg border border-dashed">
        <p className="text-sm text-muted-foreground">
          좌측에서 전략을 선택하거나 새로 만드세요.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 전략 이름 편집 */}
      <div className="space-y-2">
        <Label htmlFor="strategy-name">전략 이름</Label>
        <Input
          id="strategy-name"
          value={strategy.name}
          onChange={(e) => updateStrategyName(strategy.id, e.target.value)}
          placeholder="전략 이름 입력..."
        />
      </div>

      {/* 매수 조건 섹션 */}
      <ConditionSection
        strategyId={strategy.id}
        section="buy"
        title="매수 조건"
        conditionGroup={strategy.buyConditions}
      />

      <Separator />

      {/* 매도 조건 섹션 */}
      <ConditionSection
        strategyId={strategy.id}
        section="sell"
        title="매도 조건"
        conditionGroup={strategy.sellConditions}
      />

      <Separator />

      {/* 전략 미리보기 */}
      <StrategyPreview strategy={strategy} />
    </div>
  );
}
