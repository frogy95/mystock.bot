import type { BacktestResult, BacktestTrade } from "./types";

/**
 * 2025-07-01 ~ 2026-02-28 평일 날짜 목록 생성 (약 175일 평일)
 * equityCurve용 날짜를 약 90개 포인트로 균등 샘플링
 */
function generateWeekdayDates(
  startDate: string,
  endDate: string
): string[] {
  const dates: string[] = [];
  const current = new Date(startDate);
  const end = new Date(endDate);

  while (current <= end) {
    const day = current.getDay();
    // 토요일(6), 일요일(0) 제외
    if (day !== 0 && day !== 6) {
      dates.push(current.toISOString().split("T")[0]);
    }
    current.setDate(current.getDate() + 1);
  }

  return dates;
}

/**
 * 포트폴리오 가치 곡선 생성
 * - 초기값: 100 (기준 지수)
 * - 누적 변동률 적용 (실제 주식처럼 약 +15% 상승, 중간 -8% 낙폭 포함)
 */
function generateEquityCurve(
  dates: string[]
): { date: string; value: number; benchmark: number; stockBuyhold: number }[] {
  // 전략 포트폴리오 가치 변동 시드값
  const strategyChanges = [
    0.003, 0.005, -0.002, 0.004, 0.001, -0.003, 0.006, 0.002, -0.001, 0.004,
    0.003, -0.005, 0.008, 0.001, -0.002, 0.005, 0.002, -0.004, 0.007, 0.003,
    -0.006, 0.004, 0.001, -0.003, 0.005, 0.002, 0.003, -0.008, 0.009, 0.004,
    -0.002, 0.006, 0.001, -0.005, 0.007, 0.003, -0.003, 0.005, 0.002, 0.004,
    -0.007, 0.008, 0.003, -0.002, 0.006, 0.001, -0.004, 0.005, 0.003, -0.001,
    0.004, 0.002, -0.006, 0.009, 0.003, -0.003, 0.005, 0.002, -0.002, 0.004,
    0.003, -0.005, 0.007, 0.001, -0.004, 0.006, 0.002, 0.003, -0.008, 0.01,
    0.004, -0.002, 0.007, 0.001, -0.005, 0.006, 0.003, -0.003, 0.005, 0.002,
    0.004, -0.006, 0.008, 0.003, -0.001, 0.005, 0.002, -0.004, 0.006, 0.003,
  ];

  // 벤치마크(KOSPI) 가치 변동 시드값 (전략보다 보수적인 수익률)
  const benchmarkChanges = [
    0.002, 0.003, -0.001, 0.003, 0.001, -0.002, 0.004, 0.001, -0.002, 0.003,
    0.002, -0.004, 0.005, 0.001, -0.001, 0.003, 0.001, -0.003, 0.004, 0.002,
    -0.005, 0.003, 0.001, -0.002, 0.004, 0.001, 0.002, -0.006, 0.006, 0.002,
    -0.001, 0.004, 0.001, -0.004, 0.005, 0.002, -0.002, 0.003, 0.001, 0.003,
    -0.005, 0.006, 0.002, -0.001, 0.004, 0.001, -0.003, 0.003, 0.002, -0.001,
    0.003, 0.001, -0.004, 0.006, 0.002, -0.002, 0.003, 0.001, -0.001, 0.003,
    0.002, -0.003, 0.005, 0.001, -0.003, 0.004, 0.001, 0.002, -0.006, 0.007,
    0.003, -0.001, 0.005, 0.001, -0.004, 0.004, 0.002, -0.002, 0.003, 0.001,
    0.003, -0.004, 0.005, 0.002, -0.001, 0.003, 0.001, -0.003, 0.004, 0.002,
  ];

  let strategyValue = 100;
  let benchmarkValue = 100;

  return dates.map((date, i) => {
    const idx = i % strategyChanges.length;
    strategyValue = strategyValue * (1 + strategyChanges[idx]);
    benchmarkValue = benchmarkValue * (1 + benchmarkChanges[idx]);

    return {
      date,
      value: Math.round(strategyValue * 100) / 100,
      benchmark: Math.round(benchmarkValue * 100) / 100,
      stockBuyhold: Math.round(benchmarkValue * 100) / 100,
    };
  });
}

// 2025-07-01 ~ 2026-02-28 평일 목록 생성 후 약 90개 포인트로 균등 샘플링
const allWeekdays = generateWeekdayDates("2025-07-01", "2026-02-28");
const sampledDates = allWeekdays.filter((_, i) => i % 2 === 0).slice(0, 90);

/**
 * 골든크로스+RSI 전략 - 삼성전자 백테스팅 결과 Mock 데이터
 * 기간: 2025-07-01 ~ 2026-02-28 (약 8개월)
 */
export const mockBacktestResult: BacktestResult = {
  strategyId: "golden-cross-rsi",
  strategyName: "골든크로스 + RSI",
  symbol: "005930",
  stockName: "삼성전자",
  startDate: "2025-07-01",
  endDate: "2026-02-28",
  totalReturn: 15.32,
  annualReturn: 22.48,
  maxDrawdown: -8.14,
  winRate: 65.2,
  tradeCount: 23,
  sharpeRatio: 1.42,
  benchmarkReturn: 7.85,
  equityCurve: generateEquityCurve(sampledDates),
  trades: [],
};

/**
 * 골든크로스+RSI 전략 - 삼성전자 백테스팅 개별 거래 내역 Mock 데이터
 * 10개 거래 (BUY/SELL 쌍 5세트)
 */
export const mockBacktestTrades: BacktestTrade[] = [
  {
    id: "bt-1",
    date: "2025-07-08",
    type: "BUY",
    price: 68_500,
    quantity: 100,
    amount: 6_850_000,
    profitLoss: null,
    profitRate: null,
    reason: "SMA(20) > SMA(60) 골든크로스 발생, RSI(14) = 32.5 (과매도 회복)",
  },
  {
    id: "bt-2",
    date: "2025-07-25",
    type: "SELL",
    price: 72_300,
    quantity: 100,
    amount: 7_230_000,
    profitLoss: 380_000,
    profitRate: 5.55,
    reason: "RSI(14) = 74.2 (과매수 구간 진입), 목표 수익률 도달",
  },
  {
    id: "bt-3",
    date: "2025-08-14",
    type: "BUY",
    price: 70_000,
    quantity: 100,
    amount: 7_000_000,
    profitLoss: null,
    profitRate: null,
    reason: "SMA(20) > SMA(60) 유지, RSI(14) = 38.1 (과매도 회복)",
  },
  {
    id: "bt-4",
    date: "2025-08-28",
    type: "SELL",
    price: 67_500,
    quantity: 100,
    amount: 6_750_000,
    profitLoss: -250_000,
    profitRate: -3.57,
    reason: "SMA(20) < SMA(60) 데드크로스 발생, 손절 조건 충족",
  },
  {
    id: "bt-5",
    date: "2025-09-18",
    type: "BUY",
    price: 65_800,
    quantity: 150,
    amount: 9_870_000,
    profitLoss: null,
    profitRate: null,
    reason: "SMA(20) > SMA(60) 골든크로스, RSI(14) = 30.8 (강한 과매도)",
  },
  {
    id: "bt-6",
    date: "2025-10-10",
    type: "SELL",
    price: 71_200,
    quantity: 150,
    amount: 10_680_000,
    profitLoss: 810_000,
    profitRate: 8.21,
    reason: "목표 수익률 +8% 도달, RSI(14) = 71.5 (과매수 진입)",
  },
  {
    id: "bt-7",
    date: "2025-11-04",
    type: "BUY",
    price: 69_000,
    quantity: 100,
    amount: 6_900_000,
    profitLoss: null,
    profitRate: null,
    reason: "SMA(20) > SMA(60) 골든크로스, RSI(14) = 36.2",
  },
  {
    id: "bt-8",
    date: "2025-11-21",
    type: "SELL",
    price: 73_500,
    quantity: 100,
    amount: 7_350_000,
    profitLoss: 450_000,
    profitRate: 6.52,
    reason: "볼린저 밴드 상단 돌파, RSI(14) = 76.3 (과매수)",
  },
  {
    id: "bt-9",
    date: "2025-12-16",
    type: "BUY",
    price: 71_500,
    quantity: 100,
    amount: 7_150_000,
    profitLoss: null,
    profitRate: null,
    reason: "SMA(20) > SMA(60) 재확인, RSI(14) = 41.0 (중립 구간 하단)",
  },
  {
    id: "bt-10",
    date: "2026-01-08",
    type: "SELL",
    price: 75_000,
    quantity: 100,
    amount: 7_500_000,
    profitLoss: 350_000,
    profitRate: 4.90,
    reason: "연말 랠리 후 RSI(14) = 72.8 (과매수), 익절 실행",
  },
];
