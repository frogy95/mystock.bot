"use client";

import { useState } from "react";
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
import { mockStrategies } from "@/lib/mock";

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
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  // 모든 필드가 채워져야 버튼 활성화
  const isFormValid =
    strategyId.trim() !== "" &&
    symbol.trim() !== "" &&
    startDate !== "" &&
    endDate !== "";

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!isFormValid) return;
    onRun({ strategyId, symbol, startDate, endDate });
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
                <SelectValue placeholder="전략을 선택하세요" />
              </SelectTrigger>
              <SelectContent>
                {mockStrategies.map((strategy) => (
                  <SelectItem key={strategy.id} value={strategy.id}>
                    {strategy.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* 종목코드 */}
          <div className="space-y-1.5">
            <Label htmlFor="symbol-input">종목코드</Label>
            <Input
              id="symbol-input"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              placeholder="005930"
            />
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
