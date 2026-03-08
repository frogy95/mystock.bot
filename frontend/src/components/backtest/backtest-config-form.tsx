"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Search } from "lucide-react";
import { useStrategies } from "@/hooks/use-strategy";
import { useStockSearch } from "@/hooks/use-watchlist";

interface BacktestConfigFormProps {
  onRun: (config: {
    strategyId: string;
    symbol: string;
    startDate: string;
    endDate: string;
  }) => void;
  isRunning: boolean;
}

export function BacktestConfigForm({ onRun, isRunning }: BacktestConfigFormProps) {
  const [strategyId, setStrategyId] = useState("");
  const [symbol, setSymbol] = useState("");
  const [stockQuery, setStockQuery] = useState("");
  const [debouncedStockQuery, setDebouncedStockQuery] = useState("");
  const [stockSearchOpen, setStockSearchOpen] = useState(false);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const { data: strategies, isLoading: strategiesLoading } = useStrategies();

  // 종목 검색 디바운스 처리
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedStockQuery(stockQuery), 300);
    return () => clearTimeout(timer);
  }, [stockQuery]);

  const { data: stockResults, isLoading: stockSearchLoading } = useStockSearch(debouncedStockQuery);

  // 모든 필드가 채워져야 버튼 활성화
  const isFormValid =
    strategyId.trim() !== "" &&
    symbol.trim() !== "" &&
    startDate !== "" &&
    endDate !== "";

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!isFormValid) return;
    // "종목명 (229200)" 형태로 입력된 경우 괄호 안 코드만 추출
    const match = symbol.match(/\((\w+)\)\s*$/);
    const resolvedSymbol = match ? match[1] : symbol.trim();
    onRun({ strategyId, symbol: resolvedSymbol, startDate, endDate });
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>백테스트 설정</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* 전략 선택 */}
          <div className="space-y-1.5">
            <Label htmlFor="strategy-select">전략 선택</Label>
            <Select value={strategyId} onValueChange={setStrategyId}>
              <SelectTrigger id="strategy-select">
                <SelectValue placeholder={strategiesLoading ? "로딩 중..." : "전략을 선택하세요"} />
              </SelectTrigger>
              <SelectContent>
                {strategies?.map((strategy) => (
                  <SelectItem key={String(strategy.id)} value={strategy.name}>
                    {strategy.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
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
                      // 직접 종목코드 입력 시 symbol도 같이 업데이트
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
                <ScrollArea className="max-h-[200px]">
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
            {isRunning ? "백테스트 실행 중..." : "백테스트 실행"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
