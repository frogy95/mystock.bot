"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useStrategyStore } from "@/stores/strategy-store";

interface StrategyStockMappingProps {
  strategyId: string;
  assignedStocks: string[];
}

/** 전략-종목 매핑 관리 컴포넌트 */
export function StrategyStockMapping({
  strategyId,
  assignedStocks,
}: StrategyStockMappingProps) {
  // 종목코드 입력 로컬 상태
  const [inputValue, setInputValue] = useState("");

  // 스토어에서 종목 추가/제거 함수 가져오기
  const addStock = useStrategyStore((state) => state.addStock);
  const removeStock = useStrategyStore((state) => state.removeStock);

  /** 종목 추가 처리 */
  const handleAdd = () => {
    const trimmed = inputValue.trim();
    if (!trimmed) return;
    addStock(strategyId, trimmed);
    // 추가 후 입력 초기화
    setInputValue("");
  };

  /** Enter 키로 종목 추가 */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleAdd();
    }
  };

  return (
    <div className="space-y-4">
      {/* 종목 추가 영역 */}
      <div className="flex gap-2">
        <Input
          placeholder="종목코드 입력 (예: 005930)"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          className="flex-1"
        />
        <Button
          onClick={handleAdd}
          disabled={!inputValue.trim()}
          size="sm"
        >
          추가
        </Button>
      </div>

      {/* 안내: 종목 할당은 관심종목 페이지에서 strategy_id를 설정하여 관리됨 */}
      <p className="text-xs text-muted-foreground">
        * 종목 할당은 <strong>관심종목</strong> 페이지에서 각 종목에 전략을 지정하는 방식으로 관리됩니다. 아래 목록은 현재 세션에서 임시로 메모할 수 있습니다.
      </p>

      {/* 매핑된 종목 테이블 */}
      {assignedStocks.length > 0 ? (
        /* 모바일에서 가로 스크롤 허용 */
        <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>종목코드</TableHead>
              <TableHead className="text-right">액션</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {assignedStocks.map((symbol) => (
              <TableRow key={symbol}>
                <TableCell className="font-mono">{symbol}</TableCell>
                <TableCell className="text-right">
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => removeStock(strategyId, symbol)}
                  >
                    삭제
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        </div>
      ) : (
        // 매핑된 종목이 없을 때 안내 메시지
        <p className="text-sm text-muted-foreground text-center py-4">
          매핑된 종목이 없습니다
        </p>
      )}
    </div>
  );
}
