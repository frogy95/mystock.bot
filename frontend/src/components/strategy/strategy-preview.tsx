"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { CustomStrategy, ConditionGroup, ConditionRow, Operand } from "@/lib/mock/custom-strategy-types";
import { OPERATOR_LABELS, BB_POSITION_LABELS } from "@/lib/mock/indicator-definitions";

interface StrategyPreviewProps {
  strategy: CustomStrategy;
}

/** 피연산자를 읽기 쉬운 텍스트로 변환 */
function formatOperand(operand: Operand): string {
  if (operand.type === "value") {
    return String(operand.value);
  }
  const { indicator, params } = operand;
  const paramParts = Object.entries(params).map(([key, val]) => {
    // BB position: 0/1/2 → 문자열로 표시
    if (indicator === "BB" && key === "position") {
      return BB_POSITION_LABELS[val as 0 | 1 | 2] ?? String(val);
    }
    return String(val);
  });
  return paramParts.length > 0
    ? `${indicator}(${paramParts.join(", ")})`
    : indicator;
}

/** 연산자를 짧은 텍스트로 변환 */
function formatOperator(op: ConditionRow["operator"]): string {
  const labels: Record<ConditionRow["operator"], string> = {
    ">": ">",
    ">=": "≥",
    "<": "<",
    "<=": "≤",
    CROSS_ABOVE: "골든크로스",
    CROSS_BELOW: "데드크로스",
  };
  return labels[op] ?? op;
}

/** 조건 행을 텍스트로 변환 */
function formatConditionRow(condition: ConditionRow): string {
  const left = formatOperand(condition.leftOperand);
  const op = formatOperator(condition.operator);
  const right = formatOperand(condition.rightOperand);
  return `${left} ${op} ${right}`;
}

/** 조건 그룹을 읽기 쉬운 텍스트로 변환 */
function formatConditionGroup(group: ConditionGroup): string {
  if (group.conditions.length === 0) return "(조건 없음)";

  return group.conditions
    .map((condition, i) => {
      const conditionText = formatConditionRow(condition);
      if (i === 0) return conditionText;
      const logic = group.logicOperators[i - 1] ?? "AND";
      return `${logic} ${conditionText}`;
    })
    .join("\n");
}

/** 전략 미리보기 컴포넌트 */
export function StrategyPreview({ strategy }: StrategyPreviewProps) {
  const buyText = formatConditionGroup(strategy.buyConditions);
  const sellText = formatConditionGroup(strategy.sellConditions);

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">전략 미리보기</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* 매수 조건 미리보기 */}
        <div className="space-y-1">
          <p className="text-xs font-semibold text-green-600 dark:text-green-400">
            📈 매수 조건
          </p>
          <pre className="text-xs text-muted-foreground whitespace-pre-wrap font-mono bg-muted rounded-md p-3 leading-relaxed">
            {buyText}
          </pre>
        </div>

        {/* 매도 조건 미리보기 */}
        <div className="space-y-1">
          <p className="text-xs font-semibold text-red-600 dark:text-red-400">
            📉 매도 조건
          </p>
          <pre className="text-xs text-muted-foreground whitespace-pre-wrap font-mono bg-muted rounded-md p-3 leading-relaxed">
            {sellText}
          </pre>
        </div>

        {/* OPERATOR_LABELS 활용 (참고용 범례) */}
        {(strategy.buyConditions.conditions.length > 0 ||
          strategy.sellConditions.conditions.length > 0) && (
          <div className="text-xs text-muted-foreground border-t pt-3">
            <span className="font-medium">연산자: </span>
            {Object.entries(OPERATOR_LABELS)
              .slice(0, 4)
              .map(([op, label]) => `${op}=${label.split(" ")[0]}`)
              .join(", ")}
            , ...
          </div>
        )}
      </CardContent>
    </Card>
  );
}
