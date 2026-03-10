"use client";

import { useEffect } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { useStrategies, useToggleStrategy, useCloneStrategy } from "@/hooks/use-strategy";
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

/** strategy_type이 퀀트 전략인지 여부 */
function isQuantitativeType(type: string): boolean {
  return type === "quantitative";
}

/** param_key → 한국어 레이블 매핑 */
const PARAM_LABEL: Record<string, string> = {
  rsi_threshold: "RSI 임계값",
  bb_period: "볼린저 밴드 기간",
  bb_std: "표준편차 배수",
  rsi_buy_threshold: "RSI 매수 기준",
  per_ratio: "PER 비율",
  pbr_max: "PBR 최대값",
  roe_min: "ROE 최소값",
};

/** param_key → 설명 매핑 */
const PARAM_DESCRIPTION: Record<string, string> = {
  rsi_threshold: "RSI 과매도 기준값. 이 값 이하일 때 매수 신호를 생성합니다 (기본값: 35)",
  bb_period: "볼린저 밴드 계산에 사용할 봉 개수 (기본값: 20일)",
  bb_std: "볼린저 밴드 상·하단 폭을 결정하는 표준편차 배수 (기본값: 2.0)",
  rsi_buy_threshold: "RSI가 이 값 이하일 때 과매도 구간으로 판단하여 매수 신호를 생성합니다 (기본값: 30)",
  per_ratio: "저평가 종목 필터링에 사용하는 PER 비율 기준값 (기본값: 0.7)",
  pbr_max: "저평가 종목 필터링에 사용하는 PBR 최대값 (기본값: 1.0)",
  roe_min: "수익성 종목 필터링에 사용하는 ROE 최소값 % (기본값: 10.0)",
};

export function StrategyCardList({ onSelectStrategy }: StrategyCardListProps) {
  // TanStack Query로 전략 목록 데이터 로드
  const { data: strategies, isLoading, isError } = useStrategies();

  // 전략 활성화/비활성화 API 뮤테이션
  const toggleStrategyMutation = useToggleStrategy();

  // 프리셋 전략 복사 API 뮤테이션
  const cloneStrategyMutation = useCloneStrategy();

  // Zustand 스토어에서 선택 상태 및 액션 가져오기
  const selectedStrategyId = useStrategyStore((s) => s.selectedStrategyId);
  const selectStrategy = useStrategyStore((s) => s.selectStrategy);
  const setStrategies = useStrategyStore((s) => s.setStrategies);

  /** 전략 선택 핸들러: 스토어 업데이트 + 부모 콜백 호출 */
  function handleSelect(id: string) {
    selectStrategy(id);
    onSelectStrategy(id);
  }

  /** 전략 활성화 토글 핸들러: 프리셋 전략은 차단, 나머지는 API 호출 */
  function handleToggleActive(id: string) {
    const numericId = Number(id);
    const strategy = strategies?.find((s) => s.id === numericId);
    if (!strategy) return;
    // 프리셋 전략은 활성화 토글 차단
    if (strategy.is_preset) return;
    toggleStrategyMutation.mutate({ id: numericId, is_active: !strategy.is_active });
  }

  /** 프리셋 전략 복사 핸들러 */
  function handleClone(id: string, e: React.MouseEvent) {
    e.stopPropagation();
    cloneStrategyMutation.mutate({ id: Number(id) });
  }

  // StrategyAPI → StrategyDetail 호환 형태로 변환 (API에 없는 필드는 기본값 사용)
  const mapped = (strategies ?? []).map((s) => ({
    id: String(s.id),
    name: s.name,
    category: mapStrategyTypeToCategory(s.strategy_type),
    strategyType: s.strategy_type,
    description: "",
    params: s.params.map((p) => ({
      key: p.param_key,
      label: PARAM_LABEL[p.param_key] ?? p.param_key,
      // DB param_type("int","float") → 프론트엔드 타입("number") 변환
      type: (p.param_type === "int" || p.param_type === "float" ? "number" : p.param_type) as "slider" | "number" | "select",
      value: Number(p.param_value),
      description: PARAM_DESCRIPTION[p.param_key],
    })),
    assignedStocks: [] as string[],
    isActive: s.is_active,
    isPreset: s.is_preset,
    totalReturn: 0,
    winRate: 0,
    tradeCount: 0,
  }));

  // 기본 전략(technical) / 퀀트 전략(quantitative) 분류
  const basicStrategies = mapped.filter((s) => !isQuantitativeType(s.strategyType));
  const quantStrategies = mapped.filter((s) => isQuantitativeType(s.strategyType));

  // API 데이터가 바뀔 때마다 Zustand 스토어에 sync (상세 패널이 스토어 데이터를 사용)
  // Rules of Hooks: useEffect는 조건부 return 이전에 호출해야 함
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { setStrategies(mapped); }, [strategies]);

  // 에러 발생 시 안내 메시지 표시
  if (isError) {
    return (
      <p className="text-sm text-destructive text-center py-8">
        전략 목록을 불러오지 못했습니다. 잠시 후 다시 시도해주세요.
      </p>
    );
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

  /** 전략 카드 + 복사 버튼 렌더링 */
  function renderStrategyCard(strategy: (typeof mapped)[0]) {
    return (
      <div key={strategy.id} className="relative">
        <StrategyCard
          strategy={strategy}
          isSelected={selectedStrategyId === strategy.id}
          onSelect={handleSelect}
          onToggleActive={handleToggleActive}
        />
        {/* 프리셋 전략에만 복사 버튼 표시 */}
        {strategy.isPreset && (
          <div className="mt-1 flex justify-end">
            <button
              type="button"
              onClick={(e) => handleClone(strategy.id, e)}
              disabled={cloneStrategyMutation.isPending}
              className="text-xs text-primary underline-offset-2 hover:underline disabled:opacity-50"
            >
              {cloneStrategyMutation.isPending ? "복사 중..." : "내 전략으로 복사"}
            </button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 기본 전략 섹션 */}
      {basicStrategies.length > 0 && (
        <section>
          <h3 className="text-sm font-semibold text-muted-foreground mb-3">기본 전략</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {basicStrategies.map(renderStrategyCard)}
          </div>
        </section>
      )}

      {/* 퀀트 전략 섹션 */}
      {quantStrategies.length > 0 && (
        <section>
          <h3 className="text-sm font-semibold text-muted-foreground mb-3">퀀트 전략</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {quantStrategies.map(renderStrategyCard)}
          </div>
        </section>
      )}
    </div>
  );
}
