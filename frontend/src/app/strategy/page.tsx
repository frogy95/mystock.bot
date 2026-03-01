"use client";

import { StrategyCardList } from "@/components/strategy/strategy-card-list";
import { StrategyDetailPanel } from "@/components/strategy/strategy-detail-panel";
import { useStrategyStore } from "@/stores/strategy-store";

export default function StrategyPage() {
  // Zustand 스토어에서 선택된 전략 ID와 전략 선택 액션 가져오기
  const selectedStrategyId = useStrategyStore((s) => s.selectedStrategyId);
  const selectStrategy = useStrategyStore((s) => s.selectStrategy);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">전략 설정</h2>

      {/* 전략 카드 목록 */}
      <StrategyCardList onSelectStrategy={selectStrategy} />

      {/* 선택된 전략 상세 */}
      <StrategyDetailPanel strategyId={selectedStrategyId} />
    </div>
  );
}
