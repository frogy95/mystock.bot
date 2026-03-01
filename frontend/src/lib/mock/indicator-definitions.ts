import type { ComparisonOperator, IndicatorId } from "./custom-strategy-types";

/** 지표 파라미터 정의 */
export interface IndicatorParamDef {
  key: string;
  label: string;
  min: number;
  max: number;
  step: number;
  defaultValue: number;
}

/** 지표 메타데이터 */
export interface IndicatorDefinition {
  id: IndicatorId;
  label: string;
  /** 지표가 우변(rightOperand)에 사용 가능한지 여부 */
  canBeRightOperand: boolean;
  /** 지원하는 비교 연산자 목록 */
  supportedOperators: ComparisonOperator[];
  /** 파라미터 정의 목록 */
  params: IndicatorParamDef[];
  /** 기본 파라미터 값 맵 */
  defaultParams: Record<string, number>;
}

/** 모든 지표 메타데이터 목록 */
export const INDICATOR_DEFINITIONS: IndicatorDefinition[] = [
  {
    id: "SMA",
    label: "SMA (단순이동평균)",
    canBeRightOperand: true,
    supportedOperators: [">", ">=", "<", "<=", "CROSS_ABOVE", "CROSS_BELOW"],
    params: [
      {
        key: "period",
        label: "기간",
        min: 5,
        max: 200,
        step: 1,
        defaultValue: 20,
      },
    ],
    defaultParams: { period: 20 },
  },
  {
    id: "EMA",
    label: "EMA (지수이동평균)",
    canBeRightOperand: true,
    supportedOperators: [">", ">=", "<", "<=", "CROSS_ABOVE", "CROSS_BELOW"],
    params: [
      {
        key: "period",
        label: "기간",
        min: 5,
        max: 200,
        step: 1,
        defaultValue: 20,
      },
    ],
    defaultParams: { period: 20 },
  },
  {
    id: "RSI",
    label: "RSI (상대강도지수)",
    canBeRightOperand: false,
    supportedOperators: [">", ">=", "<", "<="],
    params: [
      {
        key: "period",
        label: "기간",
        min: 5,
        max: 30,
        step: 1,
        defaultValue: 14,
      },
    ],
    defaultParams: { period: 14 },
  },
  {
    id: "MACD",
    label: "MACD",
    canBeRightOperand: false,
    supportedOperators: [">", "<", "CROSS_ABOVE", "CROSS_BELOW"],
    params: [
      {
        key: "fastPeriod",
        label: "단기 기간",
        min: 2,
        max: 50,
        step: 1,
        defaultValue: 12,
      },
      {
        key: "slowPeriod",
        label: "장기 기간",
        min: 5,
        max: 100,
        step: 1,
        defaultValue: 26,
      },
      {
        key: "signalPeriod",
        label: "시그널 기간",
        min: 2,
        max: 20,
        step: 1,
        defaultValue: 9,
      },
    ],
    defaultParams: { fastPeriod: 12, slowPeriod: 26, signalPeriod: 9 },
  },
  {
    id: "BB",
    label: "볼린저밴드 (BB)",
    canBeRightOperand: false,
    supportedOperators: [">", "<"],
    params: [
      {
        key: "period",
        label: "기간",
        min: 5,
        max: 50,
        step: 1,
        defaultValue: 20,
      },
      {
        key: "stdDev",
        label: "표준편차 배수",
        min: 1,
        max: 4,
        step: 0.5,
        defaultValue: 2,
      },
      {
        key: "position",
        label: "밴드 위치 (0=하단, 1=중단, 2=상단)",
        min: 0,
        max: 2,
        step: 1,
        defaultValue: 2,
      },
    ],
    defaultParams: { period: 20, stdDev: 2, position: 2 },
  },
  {
    id: "ATR",
    label: "ATR (평균진실범위)",
    canBeRightOperand: false,
    supportedOperators: [">", ">=", "<", "<="],
    params: [
      {
        key: "period",
        label: "기간",
        min: 7,
        max: 28,
        step: 1,
        defaultValue: 14,
      },
    ],
    defaultParams: { period: 14 },
  },
  {
    id: "VOLUME_RATIO",
    label: "거래량 비율",
    canBeRightOperand: false,
    supportedOperators: [">", ">=", "<", "<="],
    params: [
      {
        key: "period",
        label: "기준 기간",
        min: 5,
        max: 30,
        step: 1,
        defaultValue: 20,
      },
    ],
    defaultParams: { period: 20 },
  },
  {
    id: "PRICE",
    label: "현재가",
    canBeRightOperand: false,
    supportedOperators: [">", ">=", "<", "<="],
    params: [],
    defaultParams: {},
  },
];

/** ID로 지표 정의 검색 */
export function getIndicatorById(id: IndicatorId): IndicatorDefinition {
  const def = INDICATOR_DEFINITIONS.find((d) => d.id === id);
  if (!def) throw new Error(`Unknown indicator: ${id}`);
  return def;
}

/** 우변(rightOperand)에 사용 가능한 지표 목록 */
export const RIGHT_OPERAND_INDICATORS = INDICATOR_DEFINITIONS.filter(
  (d) => d.canBeRightOperand
);

/** 연산자 한국어 레이블 */
export const OPERATOR_LABELS: Record<ComparisonOperator, string> = {
  ">": "> (초과)",
  ">=": ">= (이상)",
  "<": "< (미만)",
  "<=": "<= (이하)",
  CROSS_ABOVE: "골든크로스 (상향돌파)",
  CROSS_BELOW: "데드크로스 (하향돌파)",
};

/** BB 밴드 위치 레이블 */
export const BB_POSITION_LABELS: Record<number, string> = {
  0: "하단밴드",
  1: "중단밴드",
  2: "상단밴드",
};
