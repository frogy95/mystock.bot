/** 포트폴리오 파이차트용 비중 데이터 */
export interface PortfolioPieData {
  name: string;
  symbol: string;
  value: number; // 평가금액
  percentage: number; // 비중 (%)
  color: string; // 차트 색상
}

export const mockPortfolioPieData: PortfolioPieData[] = [
  { name: "삼성전자", symbol: "005930", value: 7_450_000, percentage: 28.8, color: "#2563eb" },
  { name: "SK하이닉스", symbol: "000660", value: 5_565_000, percentage: 21.5, color: "#7c3aed" },
  { name: "삼성SDI", symbol: "006400", value: 6_480_000, percentage: 25.0, color: "#059669" },
  { name: "LG화학", symbol: "051910", value: 3_950_000, percentage: 15.3, color: "#d97706" },
  { name: "카카오", symbol: "035720", value: 2_415_000, percentage: 9.3, color: "#dc2626" },
];

/** 매도 전략 옵션 */
export const sellStrategyOptions = [
  { value: "golden-cross-rsi", label: "골든크로스 + RSI" },
  { value: "value-momentum", label: "가치 + 모멘텀" },
  { value: "bollinger-reversal", label: "볼린저 밴드 반전" },
  { value: "manual", label: "수동 매도" },
];
