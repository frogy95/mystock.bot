"use client";

import { useState } from "react";
import { BacktestConfigForm } from "@/components/backtest/backtest-config-form";
import { BacktestResultCards } from "@/components/backtest/backtest-result-cards";
import { BacktestEquityChart } from "@/components/backtest/backtest-equity-chart";
import { BacktestTradesTable } from "@/components/backtest/backtest-trades-table";
import { BacktestRankingTable } from "@/components/backtest/backtest-ranking-table";
import { BacktestAIRecommendation } from "@/components/backtest/backtest-ai-recommendation";
import { BacktestProgress } from "@/components/backtest/backtest-progress";
import {
  useBacktestRun,
  useBacktestRunMultiSSE,
  useStockStatus,
} from "@/hooks/use-backtest";
import { useStrategies } from "@/hooks/use-strategy";
import type {
  BacktestResultAPI,
  BacktestMultiResponse,
  AIRecommendResultSummary,
} from "@/hooks/use-backtest";
import type { BacktestResult, BacktestTrade } from "@/lib/mock/types";

function mapBacktestAPIToResult(api: BacktestResultAPI): BacktestResult {
  return {
    strategyId: String(api.id),
    strategyName: api.strategy_name,
    symbol: api.symbol,
    stockName: api.symbol,
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
      stockBuyhold: point.stock_buyhold,
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
  const backtestRun = useBacktestRun();
  const backtestMultiSSE = useBacktestRunMultiSSE();
  const { data: strategies } = useStrategies();

  const [singleResult, setSingleResult] = useState<BacktestResult | null>(null);
  const [multiResult, setMultiResult] = useState<BacktestMultiResponse | null>(null);
  const [currentSymbol, setCurrentSymbol] = useState<string | null>(null);
  const [multiStrategyCount, setMultiStrategyCount] = useState(0);

  const { data: stockStatus } = useStockStatus(currentSymbol);

  const isRunning = backtestRun.isPending || backtestMultiSSE.isRunning;

  // SSE ranking이 완료되면 multiResult 구성
  const sseRanking = backtestMultiSSE.ranking;
  const sseResults = backtestMultiSSE.results;

  const handleRun = (config: {
    strategyIds: number[];
    symbol: string;
    startDate: string;
    endDate: string;
  }) => {
    setCurrentSymbol(config.symbol);
    setSingleResult(null);
    setMultiResult(null);

    if (config.strategyIds.length === 1) {
      // 단일 전략 - 기존 API 사용
      const strategy = strategies?.find((s) => s.id === config.strategyIds[0]);
      if (!strategy) return;

      backtestRun.mutate(
        {
          strategy_name: strategy.name,
          symbol: config.symbol,
          start_date: config.startDate,
          end_date: config.endDate,
          strategy_id: strategy.is_preset ? undefined : strategy.id,
        },
        {
          onSuccess: (apiResult) => {
            setSingleResult(mapBacktestAPIToResult(apiResult));
          },
        }
      );
    } else {
      // 다중 전략 - SSE 스트리밍 사용
      setMultiStrategyCount(config.strategyIds.length);
      backtestMultiSSE.run({
        symbol: config.symbol,
        strategy_ids: config.strategyIds,
        start_date: config.startDate,
        end_date: config.endDate,
      });
    }
  };

  // SSE 완료 시 multiResult 구성 (ranking이 채워지면 표시)
  const completedMultiResult: BacktestMultiResponse | null =
    sseRanking.length > 0
      ? { symbol: currentSymbol ?? "", results: sseResults, ranking: sseRanking }
      : null;

  const displayMultiResult = multiResult ?? completedMultiResult;

  const isError = backtestRun.isError || !!backtestMultiSSE.error;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">백테스팅</h2>

      <BacktestConfigForm onRun={handleRun} isRunning={isRunning} />

      {isError && (
        <p className="text-destructive text-sm">
          {backtestMultiSSE.error ?? "백테스트 실행 중 오류가 발생했습니다."}
        </p>
      )}

      {/* 다중 전략 SSE 진행상황 */}
      {backtestMultiSSE.isRunning && (
        <BacktestProgress
          progress={backtestMultiSSE.progress}
          results={backtestMultiSSE.results}
          total={multiStrategyCount}
        />
      )}

      {/* 다중 전략 결과 */}
      {displayMultiResult && currentSymbol && (
        <>
          <div className="rounded-lg bg-muted/50 px-4 py-3 text-sm text-muted-foreground">
            선택한 전략들의 과거 데이터 기반 비교 시뮬레이션 결과입니다. 실제 투자 성과와 다를 수 있습니다.
          </div>
          <BacktestRankingTable
            ranking={displayMultiResult.ranking}
            stockStatus={stockStatus ?? null}
          />
          <BacktestEquityChart multiResults={displayMultiResult.results} />
          <BacktestAIRecommendation
            symbol={currentSymbol}
            resultsSummary={displayMultiResult.results.map((r): AIRecommendResultSummary => ({
              strategy_name: r.strategy_name,
              total_return: r.total_return,
              mdd: r.mdd,
              sharpe_ratio: r.sharpe_ratio,
              win_rate: r.win_rate,
              total_trades: r.total_trades,
            }))}
            stockStatus={stockStatus ?? null}
          />
        </>
      )}

      {/* 단일 전략 결과 */}
      {singleResult && (
        <>
          <div className="rounded-lg bg-muted/50 px-4 py-3 text-sm text-muted-foreground">
            선택한 전략의 과거 데이터 기반 시뮬레이션 결과입니다. 실제 투자 성과와 다를 수 있습니다.
          </div>
          <BacktestResultCards result={singleResult} />
          <BacktestEquityChart equityCurve={singleResult.equityCurve} />
          <BacktestTradesTable trades={singleResult.trades} />
        </>
      )}

      {!singleResult && !displayMultiResult && !isRunning && (
        <div className="text-center text-muted-foreground py-12">
          백테스트를 실행하면 결과가 여기에 표시됩니다.
        </div>
      )}
    </div>
  );
}
