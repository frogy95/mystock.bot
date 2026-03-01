"use client";

import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useStrategyStore } from "@/stores/strategy-store";
import type { StrategyParam } from "@/lib/mock/types";

interface StrategyParamFormProps {
  strategyId: string;
  params: StrategyParam[];
}

/** 전략 파라미터 폼 컴포넌트 */
export function StrategyParamForm({ strategyId, params }: StrategyParamFormProps) {
  // 스토어에서 파라미터 업데이트 함수 가져오기
  const updateParam = useStrategyStore((state) => state.updateParam);

  return (
    <div className="space-y-5">
      {params.map((param) => (
        <div key={param.key} className="space-y-2">
          {/* slider 타입: 슬라이더 + 현재 값 표시 */}
          {param.type === "slider" && (
            <>
              <div className="flex items-center justify-between">
                <Label htmlFor={`param-${param.key}`}>{param.label}</Label>
                <span className="text-sm font-medium tabular-nums">
                  {param.value}
                </span>
              </div>
              <Slider
                id={`param-${param.key}`}
                value={[param.value as number]}
                min={param.min ?? 0}
                max={param.max ?? 100}
                step={param.step ?? 1}
                onValueChange={(values: number[]) =>
                  updateParam(strategyId, param.key, values[0])
                }
              />
            </>
          )}

          {/* number 타입: 숫자 입력 필드 */}
          {param.type === "number" && (
            <>
              <Label htmlFor={`param-${param.key}`}>{param.label}</Label>
              <Input
                id={`param-${param.key}`}
                type="number"
                value={param.value as number}
                min={param.min}
                max={param.max}
                step={param.step ?? 1}
                onChange={(e) =>
                  updateParam(strategyId, param.key, Number(e.target.value))
                }
                className="w-full"
              />
            </>
          )}

          {/* select 타입: 드롭다운 선택 */}
          {param.type === "select" && (
            <>
              <Label htmlFor={`param-${param.key}`}>{param.label}</Label>
              <Select
                value={param.value as string}
                onValueChange={(val) => updateParam(strategyId, param.key, val)}
              >
                <SelectTrigger id={`param-${param.key}`} className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {param.options?.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </>
          )}

          {/* description이 있으면 작은 텍스트로 설명 표시 */}
          {param.description && (
            <p className="text-xs text-muted-foreground">{param.description}</p>
          )}
        </div>
      ))}
    </div>
  );
}
