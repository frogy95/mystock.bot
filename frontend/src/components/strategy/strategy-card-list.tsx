"use client";

import { Skeleton } from "@/components/ui/skeleton";
import { useStrategies, useToggleStrategy } from "@/hooks/use-strategy";
import { useStrategyStore } from "@/stores/strategy-store";
import { StrategyCard } from "./strategy-card";

interface StrategyCardListProps {
  onSelectStrategy: (id: string) => void;
}

/** strategy_type → category 매핑 */
function mapStrategyTypeToCategory(type: string): "trend" | "reversal" | "value" | "momentum" {
  const mapping: Record<string, "trend" | "reversal" | "value" | "momentum"> = {
    golden_cross: "trend",
    macd_crossover: "momentum",
    rsi_oversold: "reversal",
    bollinger_bounce: "reversal",
  };
  return mapping[type] ?? "trend";
}

export function StrategyCardList({ onSelectStrategy }: StrategyCardListProps) {
  // TanStack Query로 전략 목록 데이터 로드
  const { data: strategies, isLoading } = useStrategies();

  // 전략 활성화/비활성화 API 뮤테이션
  const toggleStrategyMutation = useToggleStrategy();

  // Zustand 스토어에서 선택 상태 및 액션 가져오기
  const selectedStrategyId = useStrategyStore((s) => s.selectedStrategyId);
  const selectStrategy = useStrategyStore((s) => s.selectStrategy);

  /** 전략 선택 핸들러: 스토어 업데이트 + 부모 콜백 호출 */
  function handleSelect(id: string) {
    selectStrategy(id);
    onSelectStrategy(id);
  }

  /** 전략 활성화 토글 핸들러: 실제 API 호출 */
  function handleToggleActive(id: string) {
    const numericId = Number(id);
    const strategy = strategies?.find((s) => s.id === numericId);
    if (!strategy) return;
    toggleStrategyMutation.mutate({ id: numericId, is_active: !strategy.is_active });
  }

  // 로딩 중: 카드 모양 Skeleton 3개 표시
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="rounded-xl border p-4 space-y-3">
            {/* 카드 상단 Skeleton */}
            <div className="flex items-center justify-between">
              <Skeleton className="h-5 w-32" />
              <Skeleton className="h-5 w-14" />
            </div>
            {/* 지표 Skeleton */}
            <div className="flex justify-between">
              <Skeleton className="h-8 w-16" />
              <Skeleton className="h-8 w-16" />
              <Skeleton className="h-8 w-16" />
            </div>
            {/* 하단 Skeleton */}
            <div className="flex items-center justify-between">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-5 w-10 rounded-full" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  // 데이터가 없는 경우
  if (!strategies || strategies.length === 0) {
    return (
      <p className="text-sm text-muted-foreground text-center py-8">
        등록된 전략이 없습니다.
      </p>
    );
  }

  // StrategyAPI → StrategyDetail 호환 형태로 변환 (API에 없는 필드는 기본값 사용)
  const mapped = strategies.map((s) => ({
    id: String(s.id),
    name: s.name,
    category: mapStrategyTypeToCategory(s.strategy_type),
    description: "",
    params: s.params.map((p) => ({
      key: p.param_key,
      label: p.param_key,
      type: p.param_type as "slider" | "number" | "select",
      value: p.param_value,
    })),
    assignedStocks: [] as string[],
    isActive: s.is_active,
    totalReturn: 0,
    winRate: 0,
    tradeCount: 0,
  }));

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {mapped.map((strategy) => (
        <StrategyCard
          key={strategy.id}
          strategy={strategy}
          isSelected={selectedStrategyId === strategy.id}
          onSelect={handleSelect}
          onToggleActive={handleToggleActive}
        />
      ))}
    </div>
  );
}
