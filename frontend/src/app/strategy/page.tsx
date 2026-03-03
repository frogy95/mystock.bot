"use client";

import { StrategyCardList } from "@/components/strategy/strategy-card-list";
import { StrategyDetailPanel } from "@/components/strategy/strategy-detail-panel";
import { CustomStrategyBuilder } from "@/components/strategy/custom-strategy-builder";
import { useStrategyStore } from "@/stores/strategy-store";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";

export default function StrategyPage() {
  // Zustand 스토어에서 선택된 전략 ID와 전략 선택 액션 가져오기
  const selectedStrategyId = useStrategyStore((s) => s.selectedStrategyId);
  const selectStrategy = useStrategyStore((s) => s.selectStrategy);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">전략 설정</h2>

      <Tabs defaultValue="preset">
        <TabsList>
          <TabsTrigger value="preset">프리셋 전략</TabsTrigger>
          <TabsTrigger value="custom">커스텀 전략</TabsTrigger>
        </TabsList>

        {/* 프리셋 전략 탭 */}
        <TabsContent value="preset" className="space-y-6 mt-4">
          <StrategyCardList onSelectStrategy={selectStrategy} />
          <StrategyDetailPanel
            strategyId={selectedStrategyId}
            onDeleted={() => selectStrategy(null)}
          />
        </TabsContent>

        {/* 커스텀 전략 탭 */}
        <TabsContent value="custom" className="mt-4">
          <CustomStrategyBuilder />
        </TabsContent>
      </Tabs>
    </div>
  );
}
