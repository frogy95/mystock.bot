import type { StrategyDetail } from "./types";

/**
 * 전략 상세 Mock 데이터
 * 3개의 대표 전략: 골든크로스+RSI, 볼린저 밴드 반전, 가치+모멘텀
 */
export const mockStrategies: StrategyDetail[] = [
  {
    id: "golden-cross-rsi",
    name: "골든크로스 + RSI",
    category: "trend",
    description:
      "단기 이동평균선(SMA20)이 장기 이동평균선(SMA60)을 상향 돌파하는 골든크로스 시점에, RSI가 과매도 구간에서 회복되는 경우 매수 신호를 생성합니다. 추세 추종 전략으로, 강한 상승 모멘텀이 발생하는 초기에 진입합니다.",
    params: [
      {
        key: "shortPeriod",
        label: "단기 이동평균 기간",
        type: "slider",
        value: 20,
        min: 5,
        max: 50,
        step: 5,
        description: "단기 SMA 계산에 사용할 봉 개수 (기본값: 20일)",
      },
      {
        key: "longPeriod",
        label: "장기 이동평균 기간",
        type: "slider",
        value: 60,
        min: 20,
        max: 120,
        step: 10,
        description: "장기 SMA 계산에 사용할 봉 개수 (기본값: 60일)",
      },
      {
        key: "rsiPeriod",
        label: "RSI 기간",
        type: "number",
        value: 14,
        min: 5,
        max: 30,
        step: 1,
        description: "RSI 계산에 사용할 봉 개수 (기본값: 14일)",
      },
      {
        key: "rsiOversold",
        label: "RSI 과매도 기준",
        type: "slider",
        value: 35,
        min: 20,
        max: 50,
        step: 5,
        description: "이 값 이하일 때 과매도 구간으로 판단 (기본값: 35)",
      },
    ],
    // 삼성전자, SK하이닉스, LG화학에 적용
    assignedStocks: ["005930", "000660", "051910"],
    isActive: true,
    totalReturn: 8.5,
    winRate: 65,
    tradeCount: 23,
  },
  {
    id: "bollinger-reversal",
    name: "볼린저 밴드 반전",
    category: "reversal",
    description:
      "종가가 볼린저 밴드 하단을 이탈했다가 다시 진입하는 시점에 매수, 상단 밴드를 돌파하거나 RSI가 과매수 구간에 진입하면 매도합니다. 평균 회귀 특성이 강한 종목에 적합한 역추세 전략입니다.",
    params: [
      {
        key: "bbPeriod",
        label: "볼린저 밴드 기간",
        type: "slider",
        value: 20,
        min: 10,
        max: 40,
        step: 5,
        description: "볼린저 밴드 중심선(SMA) 기간 (기본값: 20일)",
      },
      {
        key: "bbStdDev",
        label: "표준편차 배수",
        type: "select",
        value: "2.0",
        options: [
          { label: "1.5σ (좁은 밴드)", value: "1.5" },
          { label: "2.0σ (표준)", value: "2.0" },
          { label: "2.5σ (넓은 밴드)", value: "2.5" },
        ],
        description: "밴드 폭을 결정하는 표준편차 배수",
      },
      {
        key: "rsiOverbought",
        label: "RSI 과매수 기준",
        type: "slider",
        value: 70,
        min: 60,
        max: 85,
        step: 5,
        description: "이 값 이상일 때 과매수 구간으로 판단 (기본값: 70)",
      },
    ],
    // SK하이닉스, 카카오에 적용
    assignedStocks: ["000660", "035720"],
    isActive: false,
    totalReturn: 12.1,
    winRate: 72,
    tradeCount: 18,
  },
  {
    id: "value-momentum",
    name: "가치 + 모멘텀",
    category: "value",
    description:
      "PER, PBR 등 밸류에이션 지표가 업종 평균 대비 저평가된 종목 중, 최근 3~6개월 모멘텀(수익률)이 양수인 종목에 투자합니다. 저평가 우량주를 발굴하여 중장기 보유하는 전략입니다.",
    params: [
      {
        key: "perRatio",
        label: "업종 평균 PER 비율",
        type: "slider",
        value: 0.7,
        min: 0.3,
        max: 1.0,
        step: 0.1,
        description:
          "종목 PER이 업종 평균의 이 비율 이하인 경우 저평가로 판단 (기본값: 0.7)",
      },
      {
        key: "momentumPeriod",
        label: "모멘텀 측정 기간",
        type: "select",
        value: "3m",
        options: [
          { label: "1개월", value: "1m" },
          { label: "3개월", value: "3m" },
          { label: "6개월", value: "6m" },
        ],
        description: "모멘텀(수익률) 계산에 사용할 기간",
      },
      {
        key: "minMarketCap",
        label: "최소 시가총액 (억원)",
        type: "number",
        value: 5000,
        min: 1000,
        max: 50000,
        step: 1000,
        description: "투자 대상 종목의 최소 시가총액 기준 (기본값: 5,000억)",
      },
    ],
    // 카카오, 에코프로비엠에 적용
    assignedStocks: ["035720", "247540"],
    isActive: true,
    totalReturn: 5.2,
    winRate: 58,
    tradeCount: 12,
  },
];
