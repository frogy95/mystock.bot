"""
전략 엔진 모듈
프리셋 매매 전략 3종을 구현하고 매매 신호를 생성한다.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

import pandas as pd

from app.services.indicators import get_indicators_from_df, _ohlcv_to_df

logger = logging.getLogger("mystock.bot")


@dataclass
class Signal:
    """매매 신호 데이터클래스"""

    signal_type: str          # "BUY" | "SELL" | "HOLD"
    confidence: float         # 신뢰도 (0.0 ~ 1.0)
    reason: str               # 신호 발생 이유
    target_price: Optional[float] = None  # 목표 매수/매도가


class BaseStrategy(ABC):
    """전략 추상 기반 클래스"""

    name: str = "Base"
    description: str = ""

    @abstractmethod
    def evaluate(self, df: pd.DataFrame, params: dict[str, Any]) -> Signal:
        """
        지표가 계산된 DataFrame을 받아 매매 신호를 반환한다.
        df: OHLCV + 기술적 지표가 계산된 DataFrame
        params: 전략 파라미터 딕셔너리
        """

    def evaluate_from_ohlcv(
        self, chart_data: list[dict], params: dict[str, Any]
    ) -> Signal:
        """KIS 차트 데이터 리스트에서 직접 신호를 계산한다."""
        if not chart_data or len(chart_data) < 10:
            return Signal(signal_type="HOLD", confidence=0.0, reason="데이터 부족")
        df = _ohlcv_to_df(chart_data)
        # 지표를 DataFrame에 추가
        from app.services.indicators import _calculate_indicators
        _calculate_indicators(df)
        return self.evaluate(df, params)


class GoldenCrossRSIStrategy(BaseStrategy):
    """
    골든크로스 + RSI 전략
    - 매수 조건: SMA(20) > SMA(60) AND RSI < 40 AND 거래량 > 20일 평균 × 1.5
    - 매도 조건: SMA(20) < SMA(60)
    """

    name = "GoldenCrossRSI"
    description = "SMA 골든크로스 + RSI 과매도 + 거래량 폭발 조합 전략"

    def evaluate(self, df: pd.DataFrame, params: dict[str, Any]) -> Signal:
        if len(df) < 60:
            return Signal(signal_type="HOLD", confidence=0.0, reason="데이터 부족 (60일 이상 필요)")

        rsi_threshold = float(params.get("rsi_threshold", 40))
        vol_ratio_threshold = float(params.get("vol_ratio_threshold", 1.5))

        try:
            import pandas_ta as ta
            df_copy = df.copy()
            df_copy.ta.sma(length=20, append=True)
            df_copy.ta.sma(length=60, append=True)
            df_copy.ta.rsi(length=14, append=True)
            df_copy["VOL_RATIO_20"] = df_copy["Volume"] / df_copy["Volume"].rolling(20).mean()

            last = df_copy.iloc[-1]
            sma20 = last.get("SMA_20")
            sma60 = last.get("SMA_60")
            rsi = last.get("RSI_14")
            vol_ratio = last.get("VOL_RATIO_20")

            if any(pd.isna(v) for v in [sma20, sma60, rsi, vol_ratio]):
                return Signal(signal_type="HOLD", confidence=0.0, reason="지표 계산 불가")

            # 매수 조건
            if sma20 > sma60 and rsi < rsi_threshold and vol_ratio > vol_ratio_threshold:
                conf = min(1.0, (rsi_threshold - rsi) / rsi_threshold * 0.5 + (vol_ratio - 1.0) * 0.3)
                return Signal(
                    signal_type="BUY",
                    confidence=round(conf, 2),
                    reason=f"SMA골든크로스+RSI({rsi:.1f}<{rsi_threshold})+거래량폭발({vol_ratio:.1f}x)",
                    target_price=float(last.get("Close", 0)),
                )

            # 매도 조건
            if sma20 < sma60:
                return Signal(
                    signal_type="SELL",
                    confidence=0.6,
                    reason=f"SMA데드크로스 (SMA20={sma20:.0f} < SMA60={sma60:.0f})",
                    target_price=float(last.get("Close", 0)),
                )

        except Exception as e:
            logger.warning(f"GoldenCrossRSI 평가 오류: {e}")

        return Signal(signal_type="HOLD", confidence=0.0, reason="조건 미충족")


class BollingerReversalStrategy(BaseStrategy):
    """
    볼린저밴드 반전 전략
    - 매수 조건: 종가 < BB 하단 AND RSI < 30
    - 매도 조건: 종가 > BB 상단
    """

    name = "BollingerReversal"
    description = "볼린저밴드 하단 이탈 + RSI 과매도 반전 전략"

    def evaluate(self, df: pd.DataFrame, params: dict[str, Any]) -> Signal:
        if len(df) < 20:
            return Signal(signal_type="HOLD", confidence=0.0, reason="데이터 부족 (20일 이상 필요)")

        rsi_threshold = float(params.get("rsi_threshold", 30))

        try:
            import pandas_ta as ta
            df_copy = df.copy()
            df_copy.ta.bbands(length=20, std=2, append=True)
            df_copy.ta.rsi(length=14, append=True)

            last = df_copy.iloc[-1]
            close = last.get("Close")
            # pandas_ta bbands 컬럼명: BBL_20_2.0_2.0 (length_std_ddof)
            bb_lower = last.get("BBL_20_2.0_2.0")
            bb_upper = last.get("BBU_20_2.0_2.0")
            rsi = last.get("RSI_14")

            if any(pd.isna(v) for v in [close, bb_lower, bb_upper, rsi]):
                return Signal(signal_type="HOLD", confidence=0.0, reason="지표 계산 불가")

            # 매수 조건
            if close < bb_lower and rsi < rsi_threshold:
                conf = min(1.0, (rsi_threshold - rsi) / rsi_threshold * 0.6 + 0.3)
                return Signal(
                    signal_type="BUY",
                    confidence=round(conf, 2),
                    reason=f"BB하단이탈+RSI과매도({rsi:.1f})",
                    target_price=float(close),
                )

            # 매도 조건
            if close > bb_upper:
                return Signal(
                    signal_type="SELL",
                    confidence=0.7,
                    reason=f"BB상단 돌파 (종가={close:.0f} > BB상단={bb_upper:.0f})",
                    target_price=float(close),
                )

        except Exception as e:
            logger.warning(f"BollingerReversal 평가 오류: {e}")

        return Signal(signal_type="HOLD", confidence=0.0, reason="조건 미충족")


class ValueMomentumStrategy(BaseStrategy):
    """
    가치 + 모멘텀 전략 (기본 모멘텀 기반 구현)
    PER/PBR/ROE 외부 데이터 미연동 시 모멘텀 신호만 사용한다.
    - 매수 조건: 20일 수익률 > 5% AND RSI < 65
    """

    name = "ValueMomentum"
    description = "모멘텀 + RSI 기반 가치투자 전략 (PER/PBR 연동 시 고도화 가능)"

    def evaluate(self, df: pd.DataFrame, params: dict[str, Any]) -> Signal:
        if len(df) < 20:
            return Signal(signal_type="HOLD", confidence=0.0, reason="데이터 부족")

        momentum_threshold = float(params.get("momentum_threshold", 5.0))
        rsi_max = float(params.get("rsi_max", 65.0))

        try:
            import pandas_ta as ta
            df_copy = df.copy()
            df_copy.ta.rsi(length=14, append=True)

            last = df_copy.iloc[-1]
            prev_20 = df_copy.iloc[-21] if len(df_copy) >= 21 else df_copy.iloc[0]

            close = float(last.get("Close", 0))
            close_20d = float(prev_20.get("Close", 0))
            rsi = last.get("RSI_14")

            if close_20d == 0 or pd.isna(rsi):
                return Signal(signal_type="HOLD", confidence=0.0, reason="지표 계산 불가")

            momentum_20d = (close - close_20d) / close_20d * 100

            # 매수 조건
            if momentum_20d > momentum_threshold and rsi < rsi_max:
                conf = min(1.0, momentum_20d / 20 * 0.5 + (rsi_max - rsi) / rsi_max * 0.3)
                return Signal(
                    signal_type="BUY",
                    confidence=round(conf, 2),
                    reason=f"20일모멘텀+{momentum_20d:.1f}%+RSI({rsi:.1f})",
                    target_price=close,
                )

            # 매도 조건: 모멘텀 반전
            if momentum_20d < -momentum_threshold:
                return Signal(
                    signal_type="SELL",
                    confidence=0.6,
                    reason=f"20일모멘텀{momentum_20d:.1f}% 하락",
                    target_price=close,
                )

        except Exception as e:
            logger.warning(f"ValueMomentum 평가 오류: {e}")

        return Signal(signal_type="HOLD", confidence=0.0, reason="조건 미충족")


# 등록된 전략 레지스트리 (strategy name → 인스턴스)
STRATEGY_REGISTRY: dict[str, BaseStrategy] = {
    "GoldenCrossRSI": GoldenCrossRSIStrategy(),
    "BollingerReversal": BollingerReversalStrategy(),
    "ValueMomentum": ValueMomentumStrategy(),
}

# DB 한글 전략명 → 레지스트리 영문 키 매핑
_NAME_TO_ENGINE: dict[str, str] = {
    "골든크로스+RSI": "GoldenCrossRSI",
    "가치+모멘텀": "ValueMomentum",
    "볼린저밴드반전": "BollingerReversal",
}


def get_strategy(name: str) -> Optional[BaseStrategy]:
    """전략명으로 전략 인스턴스를 반환한다. DB 한글 이름도 지원한다."""
    key = _NAME_TO_ENGINE.get(name, name)
    return STRATEGY_REGISTRY.get(key)
