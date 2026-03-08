"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Search } from "lucide-react";
import { useStrategies } from "@/hooks/use-strategy";
import { useStockSearch } from "@/hooks/use-watchlist";

interface BacktestConfigFormProps {
  onRun: (config: {
    strategyIds: number[];
    symbol: string;
    startDate: string;
    endDate: string;
  }) => void;
  isRunning: boolean;
}

export function BacktestConfigForm({ onRun, isRunning }: BacktestConfigFormProps) {
  const [selectedStrategyIds, setSelectedStrategyIds] = useState<number[]>([]);
  const [symbol, setSymbol] = useState("");
  const [stockQuery, setStockQuery] = useState("");
  const [debouncedStockQuery, setDebouncedStockQuery] = useState("");
  const [stockSearchOpen, setStockSearchOpen] = useState(false);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const { data: strategies, isLoading: strategiesLoading } = useStrategies();

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedStockQuery(stockQuery), 300);
    return () => clearTimeout(timer);
  }, [stockQuery]);

  const { data: stockResults, isLoading: stockSearchLoading } = useStockSearch(debouncedStockQuery);

  const presetStrategies = strategies?.filter((s) => s.is_preset) ?? [];
  const customStrategies = strategies?.filter((s) => !s.is_preset) ?? [];

  const isFormValid =
    selectedStrategyIds.length > 0 &&
    symbol.trim() !== "" &&
    startDate !== "" &&
    endDate !== "";

  function toggleStrategy(id: number) {
    setSelectedStrategyIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  }

  function toggleAll() {
    const allIds = strategies?.map((s) => s.id) ?? [];
    if (selectedStrategyIds.length === allIds.length) {
      setSelectedStrategyIds([]);
    } else {
      setSelectedStrategyIds(allIds);
    }
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!isFormValid) return;
    const match = symbol.match(/\((\w+)\)\s*$/);
    const resolvedSymbol = match ? match[1] : symbol.trim();
    onRun({ strategyIds: selectedStrategyIds, symbol: resolvedSymbol, startDate, endDate });
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>백테스트 설정</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* 전략 선택 (체크박스 리스트) */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label>전략 선택</Label>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="h-auto py-0 text-xs text-muted-foreground"
                onClick={toggleAll}
                disabled={!strategies || strategies.length === 0}
              >
                {selectedStrategyIds.length === (strategies?.length ?? 0) && strategies?.length
                  ? "전체 해제"
                  : "전체 선택"}
              </Button>
            </div>

            {strategiesLoading ? (
              <p className="text-sm text-muted-foreground">로딩 중...</p>
            ) : (
              <div className="rounded-md border p-3 space-y-3">
                {/* 프리셋 전략 그룹 */}
                {presetStrategies.length > 0 && (
                  <div>
                    <p className="text-xs font-medium text-muted-foreground mb-2">프리셋 전략</p>
                    <div className="space-y-2">
                      {presetStrategies.map((s) => (
                        <div key={s.id} className="flex items-center gap-2">
                          <Checkbox
                            id={`strategy-${s.id}`}
                            checked={selectedStrategyIds.includes(s.id)}
                            onCheckedChange={() => toggleStrategy(s.id)}
                          />
                          <label
                            htmlFor={`strategy-${s.id}`}
                            className="text-sm cursor-pointer"
                          >
                            {s.name}
                          </label>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* 커스텀 전략 그룹 */}
                {customStrategies.length > 0 && (
                  <div>
                    <p className="text-xs font-medium text-muted-foreground mb-2">커스텀 전략</p>
                    <div className="space-y-2">
                      {customStrategies.map((s) => (
                        <div key={s.id} className="flex items-center gap-2">
                          <Checkbox
                            id={`strategy-${s.id}`}
                            checked={selectedStrategyIds.includes(s.id)}
                            onCheckedChange={() => toggleStrategy(s.id)}
                          />
                          <label
                            htmlFor={`strategy-${s.id}`}
                            className="text-sm cursor-pointer"
                          >
                            {s.name}
                          </label>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {selectedStrategyIds.length > 0 && (
              <p className="text-xs text-muted-foreground">
                {selectedStrategyIds.length}개 전략 선택됨
              </p>
            )}
          </div>

          {/* 종목 검색 */}
          <div className="space-y-1.5">
            <Label htmlFor="symbol-input">종목</Label>
            <Popover
              open={stockSearchOpen && debouncedStockQuery.length > 0}
              onOpenChange={setStockSearchOpen}
            >
              <PopoverTrigger asChild>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="symbol-input"
                    value={stockQuery}
                    onChange={(e) => {
                      setStockQuery(e.target.value);
                      setSymbol(e.target.value);
                      setStockSearchOpen(true);
                    }}
                    onFocus={() => stockQuery.length > 0 && setStockSearchOpen(true)}
                    placeholder="종목코드 또는 종목명으로 검색..."
                    className="pl-9"
                  />
                </div>
              </PopoverTrigger>
              <PopoverContent
                className="w-[350px] p-0"
                align="start"
                onOpenAutoFocus={(e) => e.preventDefault()}
              >
                <ScrollArea className="max-h-[200px] overflow-hidden">
                  {stockSearchLoading ? (
                    <div className="p-3 text-sm text-muted-foreground text-center">검색 중...</div>
                  ) : stockResults && stockResults.length > 0 ? (
                    <div className="divide-y">
                      {stockResults.map((stock) => (
                        <div
                          key={stock.symbol}
                          className="p-3 hover:bg-accent cursor-pointer transition-colors"
                          onClick={() => {
                            setSymbol(stock.symbol);
                            setStockQuery(`${stock.name} (${stock.symbol})`);
                            setStockSearchOpen(false);
                          }}
                        >
                          <p className="font-medium text-sm">{stock.name}</p>
                          <p className="text-xs text-muted-foreground">
                            {stock.symbol} | {stock.market}
                          </p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="p-3 text-sm text-muted-foreground text-center">
                      검색 결과가 없습니다.
                    </div>
                  )}
                </ScrollArea>
              </PopoverContent>
            </Popover>
            {symbol && symbol !== stockQuery && (
              <p className="text-xs text-muted-foreground">선택된 종목코드: {symbol}</p>
            )}
          </div>

          {/* 시작일 */}
          <div className="space-y-1.5">
            <Label htmlFor="start-date">시작일</Label>
            <Input
              id="start-date"
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </div>

          {/* 종료일 */}
          <div className="space-y-1.5">
            <Label htmlFor="end-date">종료일</Label>
            <Input
              id="end-date"
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </div>

          <Button
            type="submit"
            className="w-full"
            disabled={!isFormValid || isRunning}
          >
            {isRunning
              ? "백테스트 실행 중..."
              : selectedStrategyIds.length > 1
              ? `${selectedStrategyIds.length}개 전략 백테스트 실행`
              : "백테스트 실행"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
