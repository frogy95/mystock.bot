"use client";

import { Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  INDICATOR_DEFINITIONS,
  RIGHT_OPERAND_INDICATORS,
  OPERATOR_LABELS,
  BB_POSITION_LABELS,
  getIndicatorById,
} from "@/lib/mock/indicator-definitions";
import type { ConditionRow, Operand, IndicatorId } from "@/lib/mock/custom-strategy-types";
import { useCustomStrategyStore } from "@/stores/custom-strategy-store";

interface ConditionRowEditorProps {
  strategyId: string;
  section: "buy" | "sell";
  condition: ConditionRow;
}

/** 단일 조건 행 편집 컴포넌트 */
export function ConditionRowEditor({
  strategyId,
  section,
  condition,
}: ConditionRowEditorProps) {
  const updateCondition = useCustomStrategyStore((s) => s.updateCondition);
  const removeCondition = useCustomStrategyStore((s) => s.removeCondition);

  // 좌변 지표 정의
  const leftIndicatorId =
    condition.leftOperand.type === "indicator"
      ? condition.leftOperand.indicator
      : "SMA";
  const leftIndicatorDef = getIndicatorById(leftIndicatorId);

  function handleLeftIndicatorChange(indicatorId: IndicatorId) {
    const def = getIndicatorById(indicatorId);
    const newLeftOperand: Operand = {
      type: "indicator",
      indicator: indicatorId,
      params: { ...def.defaultParams },
    };
    // 지표가 바뀌면 지원하는 연산자 중 첫 번째로 리셋
    const firstOperator = def.supportedOperators[0];
    // 우변도 초기화 (MACD는 시그널=0으로 제한)
    let newRightOperand: Operand = { type: "value", value: 0 };
    if (indicatorId === "MACD") {
      newRightOperand = { type: "value", value: 0 };
    }
    updateCondition(strategyId, section, condition.id, {
      leftOperand: newLeftOperand,
      operator: firstOperator,
      rightOperand: newRightOperand,
    });
  }

  function handleLeftParamChange(key: string, value: number) {
    if (condition.leftOperand.type !== "indicator") return;
    updateCondition(strategyId, section, condition.id, {
      leftOperand: {
        ...condition.leftOperand,
        params: { ...condition.leftOperand.params, [key]: value },
      },
    });
  }

  function handleOperatorChange(op: string) {
    updateCondition(strategyId, section, condition.id, {
      operator: op as ConditionRow["operator"],
    });
  }

  function handleRightTypeChange(type: "value" | "indicator") {
    if (type === "value") {
      updateCondition(strategyId, section, condition.id, {
        rightOperand: { type: "value", value: 0 },
      });
    } else {
      const firstRightIndicator = RIGHT_OPERAND_INDICATORS[0];
      updateCondition(strategyId, section, condition.id, {
        rightOperand: {
          type: "indicator",
          indicator: firstRightIndicator.id,
          params: { ...firstRightIndicator.defaultParams },
        },
      });
    }
  }

  function handleRightIndicatorChange(indicatorId: IndicatorId) {
    const def = getIndicatorById(indicatorId);
    updateCondition(strategyId, section, condition.id, {
      rightOperand: {
        type: "indicator",
        indicator: indicatorId,
        params: { ...def.defaultParams },
      },
    });
  }

  function handleRightParamChange(key: string, value: number) {
    if (condition.rightOperand.type !== "indicator") return;
    updateCondition(strategyId, section, condition.id, {
      rightOperand: {
        ...condition.rightOperand,
        params: { ...condition.rightOperand.params, [key]: value },
      },
    });
  }

  function handleRightValueChange(value: number) {
    updateCondition(strategyId, section, condition.id, {
      rightOperand: { type: "value", value },
    });
  }

  // MACD 우변은 시그널(0) 또는 고정값(0)으로만 허용
  const isMacd = leftIndicatorId === "MACD";
  // BB 특수 처리: position 파라미터를 Select로 렌더링
  const isBb = leftIndicatorId === "BB";

  return (
    <div className="flex flex-wrap items-start gap-2 p-3 rounded-md border bg-card">
      {/* 좌변 지표 선택 */}
      <div className="flex flex-col gap-1 min-w-[130px]">
        <span className="text-xs text-muted-foreground">지표</span>
        <Select value={leftIndicatorId} onValueChange={handleLeftIndicatorChange}>
          <SelectTrigger className="h-8 text-xs">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {INDICATOR_DEFINITIONS.map((def) => (
              <SelectItem key={def.id} value={def.id} className="text-xs">
                {def.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* 좌변 지표 파라미터 */}
      {condition.leftOperand.type === "indicator" &&
        leftIndicatorDef.params.map((paramDef) => {
          const currentVal = condition.leftOperand.type === "indicator"
            ? (condition.leftOperand.params[paramDef.key] ?? paramDef.defaultValue)
            : paramDef.defaultValue;

          // BB position: Select로 렌더링
          if (isBb && paramDef.key === "position") {
            return (
              <div key={paramDef.key} className="flex flex-col gap-1 min-w-[90px]">
                <span className="text-xs text-muted-foreground">위치</span>
                <Select
                  value={String(currentVal)}
                  onValueChange={(v) => handleLeftParamChange(paramDef.key, Number(v))}
                >
                  <SelectTrigger className="h-8 text-xs">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(BB_POSITION_LABELS).map(([val, label]) => (
                      <SelectItem key={val} value={val} className="text-xs">
                        {label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            );
          }

          return (
            <div key={paramDef.key} className="flex flex-col gap-1 w-[72px]">
              <span className="text-xs text-muted-foreground">{paramDef.label}</span>
              <Input
                type="number"
                value={currentVal}
                min={paramDef.min}
                max={paramDef.max}
                step={paramDef.step}
                onChange={(e) =>
                  handleLeftParamChange(paramDef.key, Number(e.target.value))
                }
                className="h-8 text-xs px-2"
              />
            </div>
          );
        })}

      {/* 비교 연산자 선택 */}
      <div className="flex flex-col gap-1 min-w-[140px]">
        <span className="text-xs text-muted-foreground">조건</span>
        <Select
          value={condition.operator}
          onValueChange={handleOperatorChange}
        >
          <SelectTrigger className="h-8 text-xs">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {leftIndicatorDef.supportedOperators.map((op) => (
              <SelectItem key={op} value={op} className="text-xs">
                {OPERATOR_LABELS[op]}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* 우변 선택 (MACD는 고정: 시그널선 또는 0) */}
      {isMacd ? (
        <div className="flex flex-col gap-1 min-w-[90px]">
          <span className="text-xs text-muted-foreground">기준</span>
          <Select
            value="0"
            onValueChange={() => {}}
          >
            <SelectTrigger className="h-8 text-xs">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="0" className="text-xs">시그널선 / 0</SelectItem>
            </SelectContent>
          </Select>
        </div>
      ) : (
        <>
          {/* 우변 타입 선택: 고정값 or 지표 */}
          <div className="flex flex-col gap-1 min-w-[80px]">
            <span className="text-xs text-muted-foreground">우변 종류</span>
            <Select
              value={condition.rightOperand.type}
              onValueChange={(v) => handleRightTypeChange(v as "value" | "indicator")}
            >
              <SelectTrigger className="h-8 text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="value" className="text-xs">고정값</SelectItem>
                {RIGHT_OPERAND_INDICATORS.length > 0 && (
                  <SelectItem value="indicator" className="text-xs">지표</SelectItem>
                )}
              </SelectContent>
            </Select>
          </div>

          {/* 우변 값/지표 */}
          {condition.rightOperand.type === "value" ? (
            <div className="flex flex-col gap-1 w-[80px]">
              <span className="text-xs text-muted-foreground">값</span>
              <Input
                type="number"
                value={condition.rightOperand.value}
                step="any"
                onChange={(e) => handleRightValueChange(Number(e.target.value))}
                className="h-8 text-xs px-2"
              />
            </div>
          ) : (
            <>
              <div className="flex flex-col gap-1 min-w-[110px]">
                <span className="text-xs text-muted-foreground">우변 지표</span>
                <Select
                  value={
                    condition.rightOperand.type === "indicator"
                      ? condition.rightOperand.indicator
                      : RIGHT_OPERAND_INDICATORS[0]?.id
                  }
                  onValueChange={handleRightIndicatorChange}
                >
                  <SelectTrigger className="h-8 text-xs">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {RIGHT_OPERAND_INDICATORS.map((def) => (
                      <SelectItem key={def.id} value={def.id} className="text-xs">
                        {def.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              {/* 우변 지표 파라미터 */}
              {condition.rightOperand.type === "indicator" &&
                getIndicatorById(condition.rightOperand.indicator).params.map((paramDef) => {
                  const val =
                    condition.rightOperand.type === "indicator"
                      ? (condition.rightOperand.params[paramDef.key] ?? paramDef.defaultValue)
                      : paramDef.defaultValue;
                  return (
                    <div key={paramDef.key} className="flex flex-col gap-1 w-[72px]">
                      <span className="text-xs text-muted-foreground">{paramDef.label}</span>
                      <Input
                        type="number"
                        value={val}
                        min={paramDef.min}
                        max={paramDef.max}
                        step={paramDef.step}
                        onChange={(e) =>
                          handleRightParamChange(paramDef.key, Number(e.target.value))
                        }
                        className="h-8 text-xs px-2"
                      />
                    </div>
                  );
                })}
            </>
          )}
        </>
      )}

      {/* 삭제 버튼 */}
      <div className="flex flex-col justify-end">
        <Button
          size="icon"
          variant="ghost"
          className="h-8 w-8 text-destructive hover:text-destructive mt-auto"
          onClick={() => removeCondition(strategyId, section, condition.id)}
          title="조건 삭제"
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
