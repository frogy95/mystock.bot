"use client";

import { Skeleton } from "@/components/ui/skeleton";
import { useStrategies } from "@/hooks/use-strategy";
import { useStrategyStore } from "@/stores/strategy-store";
import { StrategyCard } from "./strategy-card";

interface StrategyCardListProps {
  onSelectStrategy: (id: string) => void;
}

export function StrategyCardList({ onSelectStrategy }: StrategyCardListProps) {
  // TanStack Query로 전략 목록 데이터 로드
  const { data: strategies, isLoading } = useStrategies();

  // Zustand 스토어에서 선택 상태 및 액션 가져오기
  const selectedStrategyId = useStrategyStore((s) => s.selectedStrategyId);
  const toggleActive = useStrategyStore((s) => s.toggleActive);
  const selectStrategy = useStrategyStore((s) => s.selectStrategy);

  /** 전략 선택 핸들러: 스토어 업데이트 + 부모 콜백 호출 */
  function handleSelect(id: string) {
    selectStrategy(id);
    onSelectStrategy(id);
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

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {strategies.map((strategy) => (
        <StrategyCard
          key={strategy.id}
          strategy={strategy}
          isSelected={selectedStrategyId === strategy.id}
          onSelect={handleSelect}
          onToggleActive={toggleActive}
        />
      ))}
    </div>
  );
}
