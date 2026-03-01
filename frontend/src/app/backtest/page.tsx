"use client";

import { BacktestConfigForm } from "@/components/backtest/backtest-config-form";
import { BacktestResultCards } from "@/components/backtest/backtest-result-cards";
import { BacktestEquityChart } from "@/components/backtest/backtest-equity-chart";
import { BacktestTradesTable } from "@/components/backtest/backtest-trades-table";
import { useBacktestStore } from "@/stores/backtest-store";
import { mockBacktestResult, mockBacktestTrades } from "@/lib/mock";

export default function BacktestPage() {
  // 백테스팅 스토어에서 상태 및 액션 가져오기
  const { result, trades, isRunning, setResult, setRunning, reset } =
    useBacktestStore();

  /**
   * 백테스트 실행 핸들러
   * 1.5초 시뮬레이션 후 Mock 결과 데이터를 스토어에 저장
   */
  const handleRun = () => {
    setRunning(true);
    setTimeout(() => {
      setResult(mockBacktestResult, mockBacktestTrades);
      setRunning(false);
    }, 1500);
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">백테스팅</h2>

      {/* 백테스트 설정 폼 */}
      <BacktestConfigForm onRun={handleRun} isRunning={isRunning} />

      {/* 백테스트 결과 영역 */}
      {result && (
        <>
          {/* 요약 지표 카드 */}
          <BacktestResultCards result={result} />

          {/* 자산 곡선 차트 */}
          <BacktestEquityChart equityCurve={result.equityCurve} />

          {/* 거래 내역 테이블 */}
          <BacktestTradesTable trades={trades} />
        </>
      )}

      {/* 초기 안내 메시지 (결과 없고 실행 중이 아닐 때) */}
      {!result && !isRunning && (
        <div className="text-center text-muted-foreground py-12">
          백테스트를 실행하면 결과가 여기에 표시됩니다.
        </div>
      )}
    </div>
  );
}
