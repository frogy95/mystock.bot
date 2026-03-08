"use client";

import { useEffect } from "react";
import { StrategyCardList } from "@/components/strategy/strategy-card-list";
import { StrategyDetailPanel } from "@/components/strategy/strategy-detail-panel";
import { CustomStrategyBuilder } from "@/components/strategy/custom-strategy-builder";
import { useStrategyStore } from "@/stores/strategy-store";
import { useCustomStrategyStore } from "@/stores/custom-strategy-store";
import { useStrategies } from "@/hooks/use-strategy";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";

export default function StrategyPage() {
  const selectedStrategyId = useStrategyStore((s) => s.selectedStrategyId);
  const selectStrategy = useStrategyStore((s) => s.selectStrategy);
  const syncFromServer = useCustomStrategyStore((s) => s.syncFromServer);

  const { data: allStrategies } = useStrategies();

  // 서버 커스텀 전략으로 로컬 스토어 동기화 (비프리셋 + buy_conditions 있는 전략)
  useEffect(() => {
    if (!allStrategies) return;
    const customStrategies = allStrategies.filter(
      (s) => !s.is_preset && s.buy_conditions && s.sell_conditions
    );
    if (customStrategies.length > 0) {
      syncFromServer(
        customStrategies.map((s) => ({
          id: s.id,
          name: s.name,
          description: s.description,
          buy_conditions: s.buy_conditions as Record<string, unknown>,
          sell_conditions: s.sell_conditions as Record<string, unknown>,
          created_at: s.created_at,
          is_active: s.is_active,
        }))
      );
    }
  }, [allStrategies, syncFromServer]);

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
