"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type {
  CustomStrategy,
  ConditionGroup,
  ConditionRow,
  LogicOperator,
} from "@/lib/mock/custom-strategy-types";

/** 섹션 타입: 매수 또는 매도 조건 */
type ConditionSection = "buy" | "sell";

/** 새 빈 조건 그룹 생성 */
function createEmptyConditionGroup(): ConditionGroup {
  return {
    conditions: [],
    logicOperators: [],
  };
}

/** 기본 조건 행 생성 */
function createDefaultConditionRow(): ConditionRow {
  return {
    id: crypto.randomUUID(),
    leftOperand: {
      type: "indicator",
      indicator: "SMA",
      params: { period: 20 },
    },
    operator: ">",
    rightOperand: {
      type: "value",
      value: 0,
    },
  };
}

/** 새 커스텀 전략 생성 */
function createNewStrategy(name: string): CustomStrategy {
  const now = new Date().toISOString();
  return {
    id: crypto.randomUUID(),
    name,
    description: "",
    buyConditions: createEmptyConditionGroup(),
    sellConditions: createEmptyConditionGroup(),
    isActive: false,
    createdAt: now,
    updatedAt: now,
  };
}

interface CustomStrategyState {
  strategies: CustomStrategy[];
  selectedStrategyId: string | null;

  /** 새 전략 추가 및 자동 선택 */
  addStrategy: (name: string) => void;
  /** 전략 삭제 */
  removeStrategy: (id: string) => void;
  /** 전략 복제 */
  duplicateStrategy: (id: string) => void;
  /** 전략 선택 */
  selectStrategy: (id: string | null) => void;
  /** 활성화 토글 */
  toggleActive: (id: string) => void;
  /** 전략 이름 변경 */
  updateStrategyName: (id: string, name: string) => void;
  /** 전략 설명 변경 */
  updateStrategyDescription: (id: string, description: string) => void;
  /** 매수/매도 조건 행 추가 */
  addCondition: (strategyId: string, section: ConditionSection) => void;
  /** 매수/매도 조건 행 삭제 */
  removeCondition: (strategyId: string, section: ConditionSection, conditionId: string) => void;
  /** 조건 행 수정 */
  updateCondition: (
    strategyId: string,
    section: ConditionSection,
    conditionId: string,
    updates: Partial<Omit<ConditionRow, "id">>
  ) => void;
  /** AND ↔ OR 토글 */
  toggleLogicOperator: (strategyId: string, section: ConditionSection, index: number) => void;
  /** 서버 동기화 완료 후 serverId와 isSynced 업데이트 */
  setServerId: (localId: string, serverId: number) => void;
  /** 서버 데이터로 전체 동기화 (로그인 시 호출) — 서버 전략으로 로컬 덮어씌우기 */
  syncFromServer: (serverStrategies: Array<{
    id: number;
    name: string;
    description?: string | null;
    buy_conditions?: Record<string, unknown> | null;
    sell_conditions?: Record<string, unknown> | null;
    created_at: string;
    is_active: boolean;
  }>) => void;
}

/** 조건 그룹 섹션 키 반환 */
function sectionKey(section: ConditionSection): "buyConditions" | "sellConditions" {
  return section === "buy" ? "buyConditions" : "sellConditions";
}

/** 조건 그룹 수정 헬퍼 */
function updateGroup(
  strategy: CustomStrategy,
  section: ConditionSection,
  updater: (group: ConditionGroup) => ConditionGroup
): CustomStrategy {
  const key = sectionKey(section);
  return {
    ...strategy,
    [key]: updater(strategy[key]),
    updatedAt: new Date().toISOString(),
  };
}

export const useCustomStrategyStore = create<CustomStrategyState>()(
  persist(
    (set) => ({
      strategies: [],
      selectedStrategyId: null,

      addStrategy: (name) => {
        const newStrategy = createNewStrategy(name);
        set((state) => ({
          strategies: [...state.strategies, newStrategy],
          selectedStrategyId: newStrategy.id,
        }));
      },

      removeStrategy: (id) =>
        set((state) => ({
          strategies: state.strategies.filter((s) => s.id !== id),
          selectedStrategyId:
            state.selectedStrategyId === id ? null : state.selectedStrategyId,
        })),

      duplicateStrategy: (id) =>
        set((state) => {
          const original = state.strategies.find((s) => s.id === id);
          if (!original) return state;
          const now = new Date().toISOString();
          const duplicated: CustomStrategy = {
            ...original,
            id: crypto.randomUUID(),
            name: `${original.name} (복사본)`,
            isActive: false,
            createdAt: now,
            updatedAt: now,
            buyConditions: {
              conditions: original.buyConditions.conditions.map((c) => ({
                ...c,
                id: crypto.randomUUID(),
              })),
              logicOperators: [...original.buyConditions.logicOperators],
            },
            sellConditions: {
              conditions: original.sellConditions.conditions.map((c) => ({
                ...c,
                id: crypto.randomUUID(),
              })),
              logicOperators: [...original.sellConditions.logicOperators],
            },
          };
          return {
            strategies: [...state.strategies, duplicated],
            selectedStrategyId: duplicated.id,
          };
        }),

      selectStrategy: (id) => set({ selectedStrategyId: id }),

      toggleActive: (id) =>
        set((state) => ({
          strategies: state.strategies.map((s) =>
            s.id === id ? { ...s, isActive: !s.isActive, updatedAt: new Date().toISOString() } : s
          ),
        })),

      updateStrategyName: (id, name) =>
        set((state) => ({
          strategies: state.strategies.map((s) =>
            s.id === id ? { ...s, name, updatedAt: new Date().toISOString() } : s
          ),
        })),

      updateStrategyDescription: (id, description) =>
        set((state) => ({
          strategies: state.strategies.map((s) =>
            s.id === id ? { ...s, description, updatedAt: new Date().toISOString() } : s
          ),
        })),

      addCondition: (strategyId, section) =>
        set((state) => ({
          strategies: state.strategies.map((s) => {
            if (s.id !== strategyId) return s;
            return updateGroup(s, section, (group) => {
              const newCondition = createDefaultConditionRow();
              return {
                conditions: [...group.conditions, newCondition],
                logicOperators:
                  group.conditions.length > 0
                    ? [...group.logicOperators, "AND"]
                    : group.logicOperators,
              };
            });
          }),
        })),

      removeCondition: (strategyId, section, conditionId) =>
        set((state) => ({
          strategies: state.strategies.map((s) => {
            if (s.id !== strategyId) return s;
            return updateGroup(s, section, (group) => {
              const idx = group.conditions.findIndex((c) => c.id === conditionId);
              if (idx === -1) return group;
              const newConditions = group.conditions.filter((c) => c.id !== conditionId);
              // logicOperators 인덱스 정합성: 조건이 삭제되면 해당 연산자도 제거
              const newLogicOperators = [...group.logicOperators];
              if (idx === 0 && newLogicOperators.length > 0) {
                // 첫 번째 조건 삭제 시 첫 번째 연산자 제거
                newLogicOperators.splice(0, 1);
              } else if (idx > 0) {
                // 그 외 조건 삭제 시 앞쪽 연산자 제거
                newLogicOperators.splice(idx - 1, 1);
              }
              return {
                conditions: newConditions,
                logicOperators: newLogicOperators,
              };
            });
          }),
        })),

      updateCondition: (strategyId, section, conditionId, updates) =>
        set((state) => ({
          strategies: state.strategies.map((s) => {
            if (s.id !== strategyId) return s;
            return updateGroup(s, section, (group) => ({
              ...group,
              conditions: group.conditions.map((c) =>
                c.id === conditionId ? { ...c, ...updates } : c
              ),
            }));
          }),
        })),

      toggleLogicOperator: (strategyId, section, index) =>
        set((state) => ({
          strategies: state.strategies.map((s) => {
            if (s.id !== strategyId) return s;
            return updateGroup(s, section, (group) => {
              const newOps = [...group.logicOperators] as LogicOperator[];
              if (index < 0 || index >= newOps.length) return group;
              newOps[index] = newOps[index] === "AND" ? "OR" : "AND";
              return { ...group, logicOperators: newOps };
            });
          }),
        })),

      setServerId: (localId, serverId) =>
        set((state) => ({
          strategies: state.strategies.map((s) =>
            s.id === localId ? { ...s, serverId, isSynced: true } : s
          ),
        })),

      syncFromServer: (serverStrategies) =>
        set((state) => {
          // 서버 커스텀 전략을 로컬 형식으로 변환
          const serverMapped: CustomStrategy[] = serverStrategies
            .filter((s) => s.buy_conditions && s.sell_conditions)
            .map((s) => ({
              id: crypto.randomUUID(), // 로컬 UUID 새로 발급
              name: s.name,
              description: s.description ?? "",
              buyConditions: (s.buy_conditions as unknown as ConditionGroup) ?? { conditions: [], logicOperators: [] },
              sellConditions: (s.sell_conditions as unknown as ConditionGroup) ?? { conditions: [], logicOperators: [] },
              isActive: s.is_active,
              createdAt: s.created_at,
              updatedAt: s.created_at,
              serverId: s.id,
              isSynced: true,
            }));

          // 서버에 없는 로컬 미동기화 전략도 유지 (오프라인 작성분)
          const localOnlyStrategies = state.strategies.filter(
            (local) => !local.isSynced
          );

          return { strategies: [...serverMapped, ...localOnlyStrategies] };
        }),
    }),
    {
      name: "custom-strategies",
    }
  )
);
