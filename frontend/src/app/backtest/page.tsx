"use client";

import { useState } from "react";
import { BacktestConfigForm } from "@/components/backtest/backtest-config-form";
import { BacktestResultCards } from "@/components/backtest/backtest-result-cards";
import { BacktestEquityChart } from "@/components/backtest/backtest-equity-chart";
import { BacktestTradesTable } from "@/components/backtest/backtest-trades-table";
import { useBacktestRun } from "@/hooks/use-backtest";
import type { BacktestResultAPI } from "@/hooks/use-backtest";
import type { BacktestResult, BacktestTrade } from "@/lib/mock/types";

/**
 * BacktestResultAPI → BacktestResult 타입 변환
 * 컴포넌트가 기대하는 필드명으로 매핑한다.
 */
function mapBacktestAPIToResult(api: BacktestResultAPI): BacktestResult {
  return {
    strategyId: String(api.id),
    strategyName: api.strategy_name,
    symbol: api.symbol,
    stockName: api.symbol, // API에 종목명 없으므로 코드로 대체
    startDate: api.start_date,
    endDate: api.end_date,
    totalReturn: api.total_return,
    annualReturn: api.cagr,
    maxDrawdown: api.mdd,
    winRate: api.win_rate,
    tradeCount: api.total_trades,
    sharpeRatio: api.sharpe_ratio,
    benchmarkReturn: api.benchmark_return,
    equityCurve: api.equity_curve.map((point) => ({
      date: point.date,
      value: point.value,
      benchmark: point.benchmark,
    })),
    trades: (api.trades ?? []).map((t, i): BacktestTrade => ({
      id: String(i),
      date: t.date,
      type: t.type as "BUY" | "SELL",
      price: t.price,
      quantity: t.qty,
      amount: t.amount,
      profitLoss: t.pnl,
      profitRate: null,
      reason: "",
    })),
  };
}

export default function BacktestPage() {
  // 백테스팅 실행 mutation 훅
  const backtestRun = useBacktestRun();

  // 현재 화면에 표시할 결과 상태
  const [result, setResult] = useState<BacktestResult | null>(null);

  /**
   * 백테스트 실행 핸들러
   * BacktestConfigForm에서 전달받은 설정으로 실제 API 호출
   */
  const handleRun = (config: {
    strategyId: string;
    symbol: string;
    startDate: string;
    endDate: string;
  }) => {
    backtestRun.mutate(
      {
        strategy_name: config.strategyId,
        symbol: config.symbol,
        start_date: config.startDate,
        end_date: config.endDate,
      },
      {
        onSuccess: (apiResult) => {
          setResult(mapBacktestAPIToResult(apiResult));
        },
      }
    );
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">백테스팅</h2>

      {/* 백테스트 설정 폼 */}
      <BacktestConfigForm onRun={handleRun} isRunning={backtestRun.isPending} />

      {/* API 에러 메시지 */}
      {backtestRun.isError && (
        <p className="text-destructive text-sm">
          백테스트 실행 중 오류가 발생했습니다.
        </p>
      )}

      {/* 백테스트 결과 영역 */}
      {result && (
        <>
          <div className="rounded-lg bg-muted/50 px-4 py-3 text-sm text-muted-foreground">
            선택한 전략의 과거 데이터 기반 시뮬레이션 결과입니다. 실제 투자 성과와 다를 수 있습니다.
          </div>
          <BacktestResultCards result={result} />
          <BacktestEquityChart equityCurve={result.equityCurve} />
          <BacktestTradesTable trades={result.trades} />
        </>
      )}

      {/* 초기 안내 메시지 */}
      {!result && !backtestRun.isPending && (
        <div className="text-center text-muted-foreground py-12">
          백테스트를 실행하면 결과가 여기에 표시됩니다.
        </div>
      )}
    </div>
  );
}
