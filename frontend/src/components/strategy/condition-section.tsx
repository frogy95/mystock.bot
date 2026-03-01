"use client";

import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useCustomStrategyStore } from "@/stores/custom-strategy-store";
import { ConditionRowEditor } from "./condition-row-editor";
import type { ConditionGroup } from "@/lib/mock/custom-strategy-types";

interface ConditionSectionProps {
  strategyId: string;
  section: "buy" | "sell";
  title: string;
  conditionGroup: ConditionGroup;
}

/** 매수 또는 매도 조건 그룹 섹션 */
export function ConditionSection({
  strategyId,
  section,
  title,
  conditionGroup,
}: ConditionSectionProps) {
  const addCondition = useCustomStrategyStore((s) => s.addCondition);
  const toggleLogicOperator = useCustomStrategyStore((s) => s.toggleLogicOperator);

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {conditionGroup.conditions.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-4">
            조건을 추가하세요
          </p>
        ) : (
          conditionGroup.conditions.map((condition, i) => (
            <div key={condition.id} className="space-y-2">
              {/* 조건 사이 AND/OR 토글 */}
              {i > 0 && (
                <div className="flex justify-center">
                  <Badge
                    variant={conditionGroup.logicOperators[i - 1] === "AND" ? "default" : "secondary"}
                    className="cursor-pointer select-none hover:opacity-80 transition-opacity px-4"
                    onClick={() => toggleLogicOperator(strategyId, section, i - 1)}
                    title="클릭하여 AND/OR 전환"
                  >
                    {conditionGroup.logicOperators[i - 1] ?? "AND"}
                  </Badge>
                </div>
              )}
              <ConditionRowEditor
                strategyId={strategyId}
                section={section}
                condition={condition}
              />
            </div>
          ))
        )}

        {/* 조건 추가 버튼 */}
        <Button
          variant="outline"
          size="sm"
          className="w-full gap-2"
          onClick={() => addCondition(strategyId, section)}
        >
          <Plus className="h-4 w-4" />
          조건 추가
        </Button>
      </CardContent>
    </Card>
  );
}
