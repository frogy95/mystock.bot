"use client";

import { useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { useStrategyStore } from "@/stores/strategy-store";
import {
  useStrategies,
  useUpdateStrategyParams,
  useRenameStrategy,
  useDeleteStrategy,
} from "@/hooks/use-strategy";
import { StrategyParamForm } from "./strategy-param-form";
import { StrategyStockMapping } from "./strategy-stock-mapping";
import type { StrategyDetail } from "@/lib/mock/types";

interface StrategyDetailPanelProps {
  strategyId: string | null;
  onDeleted?: () => void;
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
export function StrategyDetailPanel({ strategyId, onDeleted }: StrategyDetailPanelProps) {
  // 스토어에서 전략 목록을 가져와 선택된 전략 찾기
  const strategy = useStrategyStore((state) =>
    strategyId ? state.strategies.find((s) => s.id === strategyId) : undefined
  );

  // API 데이터에서 프리셋 여부 및 원본 파라미터 타입 조회
  const { data: apiStrategies } = useStrategies();
  const apiStrategy = strategyId
    ? apiStrategies?.find((s) => String(s.id) === strategyId)
    : undefined;
  const isPreset = apiStrategy?.is_preset ?? false;

  // 파라미터 저장 뮤테이션
  const updateParamsMutation = useUpdateStrategyParams();

  // 이름 변경 상태 및 뮤테이션
  const [isEditingName, setIsEditingName] = useState(false);
  const [editingName, setEditingName] = useState("");
  const renameStrategyMutation = useRenameStrategy();

  // 삭제 뮤테이션
  const deleteStrategyMutation = useDeleteStrategy();

  /** 이름 편집 시작 */
  function handleStartEditName() {
    setEditingName(strategy?.name ?? "");
    setIsEditingName(true);
  }

  /** 이름 저장 */
  function handleSaveName() {
    const trimmed = editingName.trim();
    if (!trimmed || !strategyId) return;
    renameStrategyMutation.mutate(
      { id: Number(strategyId), name: trimmed },
      { onSuccess: () => setIsEditingName(false) }
    );
  }

  /** Enter/Escape 키 처리 */
  function handleNameKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") handleSaveName();
    if (e.key === "Escape") setIsEditingName(false);
  }

  /** 파라미터 저장 핸들러: 스토어 현재값 + API 원본 param_type으로 백엔드 저장 */
  function handleSaveParams() {
    if (!strategy || !strategyId || !apiStrategy) return;
    updateParamsMutation.mutate({
      id: Number(strategyId),
      params: strategy.params.map((p) => {
        const apiParam = apiStrategy.params.find((ap) => ap.param_key === p.key);
        return {
          param_key: p.key,
          param_value: String(p.value),
          param_type: apiParam?.param_type ?? "string",
        };
      }),
    });
  }

  /** 전략 삭제 핸들러 */
  function handleDelete() {
    if (!strategyId) return;
    if (!window.confirm("이 전략을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.")) return;
    deleteStrategyMutation.mutate(
      { id: Number(strategyId) },
      { onSuccess: () => onDeleted?.() }
    );
  }

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
          {isEditingName ? (
            /* 이름 인라인 편집 모드 */
            <div className="flex items-center gap-2 flex-1">
              <Input
                value={editingName}
                onChange={(e) => setEditingName(e.target.value)}
                onKeyDown={handleNameKeyDown}
                onBlur={handleSaveName}
                autoFocus
                className="h-8 text-base font-semibold"
              />
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setIsEditingName(false)}
                className="text-xs"
              >
                취소
              </Button>
            </div>
          ) : (
            /* 이름 표시 모드 */
            <>
              <CardTitle className="text-lg">{strategy.name}</CardTitle>
              {/* 프리셋이 아닌 경우 편집 버튼 표시 */}
              {!isPreset && (
                <button
                  type="button"
                  onClick={handleStartEditName}
                  className="text-xs text-muted-foreground hover:text-foreground underline-offset-2 hover:underline"
                >
                  이름 변경
                </button>
              )}
            </>
          )}
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
          <h3 className="text-sm font-semibold">
            파라미터 설정
            {isPreset && (
              <span className="ml-2 text-xs font-normal text-muted-foreground">
                (프리셋 - 파라미터 변경 불가)
              </span>
            )}
          </h3>
          {isPreset ? (
            <p className="text-sm text-muted-foreground">
              프리셋 전략의 파라미터는 변경할 수 없습니다. &ldquo;내 전략으로 복사&rdquo; 후 수정하세요.
            </p>
          ) : (
            <>
              <StrategyParamForm
                strategyId={strategy.id}
                params={strategy.params}
              />
              <div className="pt-2 flex justify-end">
                <Button
                  size="sm"
                  onClick={handleSaveParams}
                  disabled={updateParamsMutation.isPending}
                >
                  {updateParamsMutation.isPending ? "저장 중..." : "파라미터 저장"}
                </Button>
              </div>
            </>
          )}
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

        {/* 전략 삭제 섹션 (프리셋이 아닌 경우만) */}
        {!isPreset && (
          <div className="space-y-3">
            <Separator />
            <div className="flex justify-end">
              <Button
                variant="destructive"
                size="sm"
                onClick={handleDelete}
                disabled={deleteStrategyMutation.isPending}
              >
                {deleteStrategyMutation.isPending ? "삭제 중..." : "전략 삭제"}
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
