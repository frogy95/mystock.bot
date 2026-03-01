import type {
  PortfolioSummary,
  HoldingItem,
  TradeSignal,
  OrderExecution,
  StrategyPerformance,
  MarketIndex,
  CandleData,
} from "./types";

// KOSPI/KOSDAQ 차트 Mock 데이터 생성 (최근 30일)
function generateChartData(
  basePrice: number,
  days: number,
  volatility: number
): CandleData[] {
  const data: CandleData[] = [];
  let price = basePrice;
  const startDate = new Date("2026-01-20");

  for (let i = 0; i < days; i++) {
    const date = new Date(startDate);
    date.setDate(date.getDate() + i);
    // 주말 건너뛰기
    if (date.getDay() === 0 || date.getDay() === 6) continue;

    const change = (Math.random() - 0.48) * volatility;
    const open = price;
    const close = price + change;
    const high = Math.max(open, close) + Math.random() * volatility * 0.5;
    const low = Math.min(open, close) - Math.random() * volatility * 0.5;
    const volume = Math.floor(Math.random() * 500000000 + 100000000);

    data.push({
      time: date.toISOString().split("T")[0],
      open: Math.round(open * 100) / 100,
      high: Math.round(high * 100) / 100,
      low: Math.round(low * 100) / 100,
      close: Math.round(close * 100) / 100,
      volume,
    });

    price = close;
  }
  return data;
}

export const mockPortfolioSummary: PortfolioSummary = {
  totalEvaluation: 52_340_000,
  totalInvestment: 50_000_000,
  totalProfitLoss: 2_340_000,
  totalProfitRate: 4.68,
  dailyProfitLoss: 185_000,
  dailyProfitRate: 0.35,
  cashBalance: 12_500_000,
};

export const mockHoldings: HoldingItem[] = [
  {
    symbol: "005930",
    name: "삼성전자",
    quantity: 100,
    avgPrice: 72_000,
    currentPrice: 74_500,
    evalAmount: 7_450_000,
    profitLoss: 250_000,
    profitRate: 3.47,
    stopLossRate: -5,
    takeProfitRate: 15,
    sellStrategy: "골든크로스 + RSI",
  },
  {
    symbol: "000660",
    name: "SK하이닉스",
    quantity: 30,
    avgPrice: 178_000,
    currentPrice: 185_500,
    evalAmount: 5_565_000,
    profitLoss: 225_000,
    profitRate: 4.21,
    stopLossRate: -7,
    takeProfitRate: 20,
    sellStrategy: "볼린저 밴드 반전",
  },
  {
    symbol: "035720",
    name: "카카오",
    quantity: 50,
    avgPrice: 52_000,
    currentPrice: 48_300,
    evalAmount: 2_415_000,
    profitLoss: -185_000,
    profitRate: -7.12,
    stopLossRate: -10,
    takeProfitRate: 15,
    sellStrategy: "가치 + 모멘텀",
  },
  {
    symbol: "051910",
    name: "LG화학",
    quantity: 10,
    avgPrice: 380_000,
    currentPrice: 395_000,
    evalAmount: 3_950_000,
    profitLoss: 150_000,
    profitRate: 3.95,
    stopLossRate: -5,
    takeProfitRate: 12,
    sellStrategy: "골든크로스 + RSI",
  },
  {
    symbol: "006400",
    name: "삼성SDI",
    quantity: 15,
    avgPrice: 420_000,
    currentPrice: 432_000,
    evalAmount: 6_480_000,
    profitLoss: 180_000,
    profitRate: 2.86,
    stopLossRate: -5,
    takeProfitRate: 15,
    sellStrategy: null,
  },
];

export const mockTradeSignals: TradeSignal[] = [
  {
    id: "sig-1",
    symbol: "005930",
    name: "삼성전자",
    strategyName: "골든크로스 + RSI",
    signalType: "BUY",
    reason: "SMA(20) > SMA(60) 돌파, RSI(14) = 35",
    targetPrice: 73_500,
    confidence: 82,
    createdAt: "2026-03-01T09:15:00Z",
  },
  {
    id: "sig-2",
    symbol: "035720",
    name: "카카오",
    strategyName: "볼린저 밴드 반전",
    signalType: "SELL",
    reason: "종가가 BB_Upper 돌파, RSI(14) = 78",
    targetPrice: 49_000,
    confidence: 71,
    createdAt: "2026-03-01T10:30:00Z",
  },
  {
    id: "sig-3",
    symbol: "247540",
    name: "에코프로비엠",
    strategyName: "가치 + 모멘텀",
    signalType: "BUY",
    reason: "PER < 업종평균 0.7, 3개월 수익률 > 0",
    targetPrice: 155_000,
    confidence: 65,
    createdAt: "2026-03-01T11:00:00Z",
  },
];

export const mockOrderExecutions: OrderExecution[] = [
  {
    id: "ord-1",
    symbol: "005930",
    name: "삼성전자",
    orderType: "BUY",
    quantity: 50,
    price: 72_000,
    status: "FILLED",
    strategyName: "골든크로스 + RSI",
    executedAt: "2026-03-01T09:32:00Z",
  },
  {
    id: "ord-2",
    symbol: "000660",
    name: "SK하이닉스",
    orderType: "BUY",
    quantity: 10,
    price: 183_000,
    status: "FILLED",
    strategyName: "볼린저 밴드 반전",
    executedAt: "2026-03-01T10:15:00Z",
  },
  {
    id: "ord-3",
    symbol: "035720",
    name: "카카오",
    orderType: "SELL",
    quantity: 20,
    price: 49_200,
    status: "PENDING",
    strategyName: "볼린저 밴드 반전",
    executedAt: "2026-03-01T13:45:00Z",
  },
  {
    id: "ord-4",
    symbol: "051910",
    name: "LG화학",
    orderType: "BUY",
    quantity: 5,
    price: 388_000,
    status: "CANCELLED",
    strategyName: "가치 + 모멘텀",
    executedAt: "2026-02-28T14:20:00Z",
  },
];

export const mockStrategyPerformances: StrategyPerformance[] = [
  {
    id: "strat-1",
    name: "골든크로스 + RSI",
    totalReturn: 8.5,
    winRate: 65,
    tradeCount: 23,
    activeStocks: 3,
    isActive: true,
  },
  {
    id: "strat-2",
    name: "가치 + 모멘텀",
    totalReturn: 5.2,
    winRate: 58,
    tradeCount: 12,
    activeStocks: 2,
    isActive: true,
  },
  {
    id: "strat-3",
    name: "볼린저 밴드 반전",
    totalReturn: 12.1,
    winRate: 72,
    tradeCount: 18,
    activeStocks: 2,
    isActive: false,
  },
];

export const mockMarketIndices: MarketIndex[] = [
  {
    name: "KOSPI",
    currentValue: 2_645.32,
    changeValue: 12.45,
    changeRate: 0.47,
    chartData: generateChartData(2_580, 45, 25),
  },
  {
    name: "KOSDAQ",
    currentValue: 842.15,
    changeValue: -3.21,
    changeRate: -0.38,
    chartData: generateChartData(820, 45, 10),
  },
];
