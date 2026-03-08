/** 지표 ID 타입 */
export type IndicatorId =
  | "SMA"
  | "EMA"
  | "RSI"
  | "MACD"
  | "BB"
  | "ATR"
  | "VOLUME_RATIO"
  | "PRICE";

/** 비교 연산자 타입 */
export type ComparisonOperator =
  | ">"
  | ">="
  | "<"
  | "<="
  | "CROSS_ABOVE"
  | "CROSS_BELOW";

/** 논리 연산자 타입 */
export type LogicOperator = "AND" | "OR";

/** 피연산자: 지표 또는 고정값 */
export type Operand =
  | { type: "indicator"; indicator: IndicatorId; params: Record<string, number> }
  | { type: "value"; value: number };

/** 조건 행 */
export interface ConditionRow {
  id: string;
  leftOperand: Operand;
  operator: ComparisonOperator;
  rightOperand: Operand;
}

/** 조건 그룹 (매수 또는 매도) */
export interface ConditionGroup {
  conditions: ConditionRow[];
  /** 길이 = conditions.length - 1 */
  logicOperators: LogicOperator[];
}

/** 커스텀 전략 */
export interface CustomStrategy {
  id: string;
  name: string;
  description: string;
  buyConditions: ConditionGroup;
  sellConditions: ConditionGroup;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
  /** 서버 DB ID (동기화 완료 후 설정) */
  serverId?: number;
  /** 서버와 동기화 여부 */
  isSynced?: boolean;
}
