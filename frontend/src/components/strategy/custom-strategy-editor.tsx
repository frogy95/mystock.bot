"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { useCustomStrategyStore } from "@/stores/custom-strategy-store";
import { useCreateCustomStrategy, useUpdateCustomStrategy } from "@/hooks/use-strategy";
import { ConditionSection } from "./condition-section";
import { StrategyPreview } from "./strategy-preview";

/** 커스텀 전략 편집기 */
export function CustomStrategyEditor() {
  const strategies = useCustomStrategyStore((s) => s.strategies);
  const selectedId = useCustomStrategyStore((s) => s.selectedStrategyId);
  const updateStrategyName = useCustomStrategyStore((s) => s.updateStrategyName);
  const setServerId = useCustomStrategyStore((s) => s.setServerId);

  const [saveStatus, setSaveStatus] = useState<"idle" | "saving" | "saved" | "error">("idle");

  const createMutation = useCreateCustomStrategy();
  const updateMutation = useUpdateCustomStrategy();

  const strategy = strategies.find((s) => s.id === selectedId);

  const handleSave = async () => {
    if (!strategy) return;
    setSaveStatus("saving");
    try {
      if (strategy.serverId) {
        // 기존 서버 전략 업데이트
        await updateMutation.mutateAsync({
          id: strategy.serverId,
          buy_conditions: strategy.buyConditions as unknown as Record<string, unknown>,
          sell_conditions: strategy.sellConditions as unknown as Record<string, unknown>,
          description: strategy.description,
        });
      } else {
        // 신규 생성
        const result = await createMutation.mutateAsync({
          name: strategy.name,
          description: strategy.description,
          buy_conditions: strategy.buyConditions as unknown as Record<string, unknown>,
          sell_conditions: strategy.sellConditions as unknown as Record<string, unknown>,
        });
        setServerId(strategy.id, result.id);
      }
      setSaveStatus("saved");
      setTimeout(() => setSaveStatus("idle"), 2000);
    } catch {
      setSaveStatus("error");
      setTimeout(() => setSaveStatus("idle"), 3000);
    }
  };

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

  const saveLabel =
    saveStatus === "saving"
      ? "저장 중..."
      : saveStatus === "saved"
      ? "저장됨 ✓"
      : saveStatus === "error"
      ? "저장 실패"
      : strategy.isSynced
      ? "업데이트"
      : "서버에 저장";

  return (
    <div className="space-y-6">
      {/* 전략 이름 편집 + 저장 버튼 */}
      <div className="flex items-end gap-3">
        <div className="flex-1 space-y-2">
          <Label htmlFor="strategy-name">전략 이름</Label>
          <Input
            id="strategy-name"
            value={strategy.name}
            onChange={(e) => updateStrategyName(strategy.id, e.target.value)}
            placeholder="전략 이름 입력..."
          />
        </div>
        <Button
          onClick={handleSave}
          disabled={saveStatus === "saving"}
          variant={saveStatus === "saved" ? "outline" : saveStatus === "error" ? "destructive" : "default"}
          size="sm"
          className="shrink-0"
        >
          {saveLabel}
        </Button>
      </div>

      {/* 동기화 상태 표시 */}
      {!strategy.isSynced && (
        <p className="text-xs text-muted-foreground">
          ⚠ 로컬에만 저장된 전략입니다. 서버에 저장하면 다른 기기에서도 사용할 수 있습니다.
        </p>
      )}

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
