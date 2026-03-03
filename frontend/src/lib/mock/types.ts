/** 종목 기본 정보 */
export interface Stock {
  symbol: string; // 종목코드 (예: "005930")
  name: string; // 종목명 (예: "삼성전자")
  market: "KOSPI" | "KOSDAQ";
}

/** 현재가 정보 */
export interface StockQuote extends Stock {
  currentPrice: number; // 현재가
  changePrice: number; // 전일 대비 등락금액
  changeRate: number; // 전일 대비 등락률 (%)
  volume: number; // 거래량
  high: number; // 고가
  low: number; // 저가
  open: number; // 시가
}

/** OHLCV 캔들 데이터 */
export interface CandleData {
  time: string; // "YYYY-MM-DD"
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

/** 보유종목 */
export interface HoldingItem {
  symbol: string;
  name: string;
  quantity: number; // 보유 수량
  avgPrice: number; // 평균 매입가
  currentPrice: number; // 현재가
  evalAmount: number; // 평가금액
  profitLoss: number; // 평가손익
  profitRate: number; // 수익률 (%)
  stopLossRate: number | null; // 손절률 (%)
  takeProfitRate: number | null; // 익절률 (%)
  sellStrategy: string | null; // 매도 전략
}

/** 포트폴리오 요약 */
export interface PortfolioSummary {
  totalEvaluation: number; // 총 평가금액
  totalInvestment: number; // 총 투자금액
  totalProfitLoss: number; // 총 평가손익
  totalProfitRate: number; // 총 수익률 (%)
  dailyProfitLoss: number; // 일일 손익
  dailyProfitRate: number; // 일일 손익률 (%)
  cashBalance: number; // 예수금
}

/** 매매 신호 */
export interface TradeSignal {
  id: string;
  symbol: string;
  name: string;
  strategyName: string;
  signalType: "BUY" | "SELL";
  reason: string; // 판단 근거
  targetPrice: number;
  confidence: number; // 신뢰도 (0-100)
  createdAt: string; // ISO 날짜
}

/** 실행된 주문 */
export interface OrderExecution {
  id: string;
  symbol: string;
  name: string;
  orderType: "BUY" | "SELL";
  quantity: number;
  price: number;
  status: "FILLED" | "PENDING" | "CANCELLED";
  strategyName: string;
  executedAt: string; // ISO 날짜
}

/** 전략 성과 */
export interface StrategyPerformance {
  id: string;
  name: string;
  totalReturn: number; // 총 수익률 (%)
  winRate: number; // 승률 (%)
  tradeCount: number; // 매매 횟수
  activeStocks: number; // 적용 종목 수
  isActive: boolean; // 활성화 여부
}

/** 시장 지수 데이터 */
export interface MarketIndex {
  name: string; // "KOSPI" | "KOSDAQ"
  currentValue: number;
  changeValue: number;
  changeRate: number; // (%)
  chartData: CandleData[];
}

/** 관심종목 그룹 */
export interface WatchlistGroup {
  id: string;
  name: string;
  items: WatchlistItem[];
}

/** 관심종목 아이템 */
export interface WatchlistItem {
  id: string;
  symbol: string;
  name: string;
  market: "KOSPI" | "KOSDAQ";
  currentPrice: number;
  changeRate: number; // (%)
  changePrice: number;
  volume: number;
  per: number | null; // PER
  pbr: number | null; // PBR
  marketCap: number; // 시가총액 (억원)
  assignedStrategy: string | null;
}

/** 전략 파라미터 */
export interface StrategyParam {
  key: string;
  label: string;
  type: "slider" | "number" | "select";
  value: number | string;
  min?: number;
  max?: number;
  step?: number;
  options?: { label: string; value: string }[];
  description?: string;
}

/** 전략 상세 (관리 화면용) */
export interface StrategyDetail {
  id: string;
  name: string;
  category: "trend" | "reversal" | "value" | "momentum";
  description: string;
  params: StrategyParam[];
  assignedStocks: string[]; // symbol 배열
  isActive: boolean;
  isPreset?: boolean; // 프리셋 여부 (true면 수정 불가)
  totalReturn: number;
  winRate: number;
  tradeCount: number;
}

/** 백테스팅 결과 */
export interface BacktestResult {
  strategyId: string;
  strategyName: string;
  symbol: string;
  stockName: string;
  startDate: string;
  endDate: string;
  totalReturn: number;      // 총 수익률 (%)
  annualReturn: number;     // 연환산 수익률 (%)
  maxDrawdown: number;      // 최대 낙폭 (%)
  winRate: number;          // 승률 (%)
  tradeCount: number;       // 총 매매 횟수
  sharpeRatio: number;      // 샤프 지수
  benchmarkReturn: number;  // 벤치마크(KOSPI) 수익률 (%)
  equityCurve: { date: string; value: number; benchmark: number }[];
}

/** 백테스팅 개별 거래 */
export interface BacktestTrade {
  id: string;
  date: string;
  type: "BUY" | "SELL";
  price: number;
  quantity: number;
  amount: number;
  profitLoss: number | null; // SELL 시 손익
  profitRate: number | null; // SELL 시 수익률
  reason: string;
}

/** 주문 상세 (주문 내역 화면용) */
export interface OrderDetail {
  id: string;
  symbol: string;
  name: string;
  orderType: "BUY" | "SELL";
  quantity: number;
  price: number;
  totalAmount: number;
  status: "FILLED" | "PENDING" | "CANCELLED";
  strategyId: string;
  strategyName: string;
  reason: string;        // 판단 근거
  confidence: number;    // 신뢰도 (0-100)
  createdAt: string;     // ISO
  executedAt: string | null; // 체결 시각
}

/** KIS API 설정 */
export interface KisApiConfig {
  // 모의투자 앱 키 (주문/잔고 - KIS_ENVIRONMENT=vts 시)
  vtsAppKey: string;
  vtsAppSecret: string;
  vtsAccountNumber: string;
  // 실전투자 앱 키 (시세 API 항상 사용 + KIS_ENVIRONMENT=real 시 주문/잔고에도 사용)
  realAppKey: string;
  realAppSecret: string;
  realAccountNumber: string;
  htsId: string;
  mode: "vts" | "real"; // 모의투자 / 실전투자
}

/** 텔레그램 설정 */
export interface TelegramConfig {
  botToken: string;
  chatId: string;
  enabled: boolean;
  notifyOnSignal: boolean;
  notifyOnOrder: boolean;
  notifyOnError: boolean;
}

/** 매매 시간 설정 */
export interface TradingTimeConfig {
  startTime: string; // "HH:MM"
  endTime: string;   // "HH:MM"
  excludeLastMinutes: number; // 장 마감 전 n분 거래 제외
}

/** 안전장치 설정 */
export interface SafetyConfig {
  dailyLossLimit: number;   // 일일 손실 한도 (%)
  maxOrdersPerDay: number;  // 일일 최대 주문 횟수
  maxPositionRatio: number; // 종목당 최대 비중 (%)
  stopLossRate: number;     // 기본 손절률 (%)
}

/** 시스템 설정 전체 */
export interface SystemSettings {
  kisApi: KisApiConfig;
  telegram: TelegramConfig;
  tradingTime: TradingTimeConfig;
  safety: SafetyConfig;
  autoTradeEnabled: boolean;
}
