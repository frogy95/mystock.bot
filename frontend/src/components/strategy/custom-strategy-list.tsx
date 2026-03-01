"use client";

import { useState } from "react";
import { Plus, Trash2, Copy } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { useCustomStrategyStore } from "@/stores/custom-strategy-store";
import { cn } from "@/lib/utils";

/** 커스텀 전략 목록 + 생성/삭제 UI */
export function CustomStrategyList() {
  const strategies = useCustomStrategyStore((s) => s.strategies);
  const selectedId = useCustomStrategyStore((s) => s.selectedStrategyId);
  const addStrategy = useCustomStrategyStore((s) => s.addStrategy);
  const removeStrategy = useCustomStrategyStore((s) => s.removeStrategy);
  const duplicateStrategy = useCustomStrategyStore((s) => s.duplicateStrategy);
  const selectStrategy = useCustomStrategyStore((s) => s.selectStrategy);
  const toggleActive = useCustomStrategyStore((s) => s.toggleActive);

  const [isCreating, setIsCreating] = useState(false);
  const [newName, setNewName] = useState("");

  function handleCreate() {
    if (isCreating) {
      const name = newName.trim() || "새 전략";
      addStrategy(name);
      setNewName("");
      setIsCreating(false);
    } else {
      setIsCreating(true);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter") handleCreate();
    if (e.key === "Escape") {
      setIsCreating(false);
      setNewName("");
    }
  }

  return (
    <div className="flex flex-col gap-3">
      {/* 새 전략 만들기 버튼 */}
      {isCreating ? (
        <div className="flex gap-2">
          <input
            autoFocus
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="전략 이름 입력..."
            className="flex-1 h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
          />
          <Button size="sm" onClick={handleCreate}>
            추가
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => {
              setIsCreating(false);
              setNewName("");
            }}
          >
            취소
          </Button>
        </div>
      ) : (
        <Button
          variant="outline"
          className="w-full justify-start gap-2"
          onClick={handleCreate}
        >
          <Plus className="h-4 w-4" />
          새 전략 만들기
        </Button>
      )}

      {/* 전략 목록 */}
      {strategies.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-lg border border-dashed p-8 text-center">
          <p className="text-sm text-muted-foreground">
            아직 커스텀 전략이 없습니다.
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            &apos;새 전략 만들기&apos;를 클릭하여 시작하세요.
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {strategies.map((strategy) => {
            const buyCount = strategy.buyConditions.conditions.length;
            const sellCount = strategy.sellConditions.conditions.length;
            const isSelected = strategy.id === selectedId;

            return (
              <div
                key={strategy.id}
                onClick={() => selectStrategy(strategy.id)}
                className={cn(
                  "flex flex-col gap-2 rounded-lg border p-3 cursor-pointer transition-colors hover:bg-accent",
                  isSelected && "ring-2 ring-primary bg-accent"
                )}
              >
                {/* 전략 이름 + Switch */}
                <div className="flex items-center justify-between gap-2">
                  <span className="text-sm font-medium truncate flex-1">
                    {strategy.name}
                  </span>
                  <Switch
                    checked={strategy.isActive}
                    onCheckedChange={() => toggleActive(strategy.id)}
                    onClick={(e) => e.stopPropagation()}
                  />
                </div>

                {/* 조건 수 + 액션 버튼 */}
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">
                    매수 {buyCount}개 / 매도 {sellCount}개 조건
                  </span>
                  <div className="flex gap-1">
                    <Button
                      size="icon"
                      variant="ghost"
                      className="h-6 w-6"
                      onClick={(e) => {
                        e.stopPropagation();
                        duplicateStrategy(strategy.id);
                      }}
                      title="복제"
                    >
                      <Copy className="h-3 w-3" />
                    </Button>
                    <Button
                      size="icon"
                      variant="ghost"
                      className="h-6 w-6 text-destructive hover:text-destructive"
                      onClick={(e) => {
                        e.stopPropagation();
                        removeStrategy(strategy.id);
                      }}
                      title="삭제"
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
