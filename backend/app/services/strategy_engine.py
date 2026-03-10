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

    def set_market_data(self, market_returns: pd.Series) -> None:
        """시장 수익률 데이터를 주입한다. 시장 의존 전략에서 오버라이드한다."""
        pass

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
            df_copy.ta.macd(fast=12, slow=26, signal=9, append=True)
            df_copy["VOL_RATIO_20"] = df_copy["Volume"] / df_copy["Volume"].rolling(20).mean()

            last = df_copy.iloc[-1]
            sma20 = last.get("SMA_20")
            sma60 = last.get("SMA_60")
            rsi = last.get("RSI_14")
            vol_ratio = last.get("VOL_RATIO_20")
            macd_hist = last.get("MACDh_12_26_9")

            if any(pd.isna(v) for v in [sma20, sma60, rsi, vol_ratio]):
                return Signal(signal_type="HOLD", confidence=0.0, reason="지표 계산 불가")

            # 매수 조건: SMA골든크로스 AND RSI과매도 AND 거래량폭발 AND MACD_hist 양전환
            macd_ok = (not pd.isna(macd_hist)) and (float(macd_hist) > 0)
            if sma20 > sma60 and rsi < rsi_threshold and vol_ratio > vol_ratio_threshold and macd_ok:
                rsi_score = (rsi_threshold - rsi) / rsi_threshold  # 0~1
                vol_score = min(1.0, (vol_ratio - 1.0) / 2.0)      # 0~1
                conf = min(1.0, 0.5 + rsi_score * 0.25 + vol_score * 0.25)
                return Signal(
                    signal_type="BUY",
                    confidence=round(conf, 2),
                    reason=f"SMA골든크로스+RSI({rsi:.1f}<{rsi_threshold})+거래량폭발({vol_ratio:.1f}x)+MACD양전환",
                    target_price=float(last.get("Close", 0)),
                )

            # 매도 조건: SMA 데드크로스 OR RSI 과매수(75 초과)
            if rsi > 75:
                conf = min(1.0, 0.5 + (rsi - 75) / 25 * 0.4)
                return Signal(
                    signal_type="SELL",
                    confidence=round(conf, 2),
                    reason=f"RSI과매수({rsi:.1f}>75)",
                    target_price=float(last.get("Close", 0)),
                )

            if sma20 < sma60:
                sma_gap = (sma60 - sma20) / sma60
                conf = min(1.0, 0.5 + min(1.0, sma_gap * 10) * 0.4)
                return Signal(
                    signal_type="SELL",
                    confidence=round(conf, 2),
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
        if len(df) < 60:
            return Signal(signal_type="HOLD", confidence=0.0, reason="데이터 부족 (60일 이상 필요)")

        rsi_threshold = float(params.get("rsi_threshold", 35))

        try:
            import pandas_ta as ta
            df_copy = df.copy()
            df_copy.ta.bbands(length=20, std=2, append=True)
            df_copy.ta.rsi(length=14, append=True)
            df_copy.ta.sma(length=60, append=True)

            last = df_copy.iloc[-1]
            close = last.get("Close")
            # pandas_ta bbands 컬럼명: BBL_20_2.0_2.0 (length_std_ddof)
            bb_lower = last.get("BBL_20_2.0_2.0")
            bb_upper = last.get("BBU_20_2.0_2.0")
            rsi = last.get("RSI_14")

            # SMA(60) 5일 기울기 (상승 추세에서만 눌림목 매수)
            sma60_series = df_copy["SMA_60"].dropna()
            sma60_slope = float(sma60_series.iloc[-1] - sma60_series.iloc[-6]) if len(sma60_series) >= 6 else None

            if any(pd.isna(v) for v in [close, bb_lower, bb_upper, rsi]):
                return Signal(signal_type="HOLD", confidence=0.0, reason="지표 계산 불가")

            # 매수 조건: BB하단 이탈 AND RSI 과매도 AND SMA(60) 상승 추세
            if close < bb_lower and rsi < rsi_threshold and sma60_slope is not None and sma60_slope > 0:
                rsi_score = (rsi_threshold - rsi) / rsi_threshold  # 0~1
                conf = min(1.0, 0.5 + rsi_score * 0.4)
                return Signal(
                    signal_type="BUY",
                    confidence=round(conf, 2),
                    reason=f"BB하단이탈+RSI과매도({rsi:.1f})+SMA60상승추세",
                    target_price=float(close),
                )

            # 매도 조건: BB 상단 돌파 OR RSI 과매수
            if close > bb_upper or rsi > 70:
                if close > bb_upper:
                    bb_excess = (close - bb_upper) / bb_upper
                    conf = min(1.0, 0.5 + min(1.0, bb_excess * 20) * 0.4)
                    reason = f"BB상단 돌파 (종가={close:.0f} > BB상단={bb_upper:.0f})"
                else:
                    conf = min(1.0, 0.5 + (rsi - 70) / 30 * 0.4)
                    reason = f"RSI과매수({rsi:.1f}>70)"
                return Signal(
                    signal_type="SELL",
                    confidence=round(conf, 2),
                    reason=reason,
                    target_price=float(close),
                )

        except Exception as e:
            logger.warning(f"BollingerReversal 평가 오류: {e}")

        return Signal(signal_type="HOLD", confidence=0.0, reason="조건 미충족")


class ValueMomentumStrategy(BaseStrategy):
    """
    가치 + 모멘텀 전략 (Dual Momentum 축소 적용)
    20일 + 60일 이중 모멘텀으로 추세 강도를 확인한다.
    - 매수 조건: 60일 모멘텀 > 3% AND 20일 모멘텀 > 2% AND RSI < 65
    - 매도 조건: 60일 모멘텀 < -3% OR (20일 모멘텀 < -5% AND RSI > 60)
    """

    name = "ValueMomentum"
    description = "이중 모멘텀(20일+60일) + RSI 기반 전략 (Dual Momentum 핵심 차용)"

    def evaluate(self, df: pd.DataFrame, params: dict[str, Any]) -> Signal:
        if len(df) < 61:
            return Signal(signal_type="HOLD", confidence=0.0, reason="데이터 부족 (61일 이상 필요)")

        rsi_max = float(params.get("rsi_max", 65.0))

        try:
            import pandas_ta as ta
            df_copy = df.copy()
            df_copy.ta.rsi(length=14, append=True)

            last = df_copy.iloc[-1]
            close = float(last.get("Close", 0))
            rsi = last.get("RSI_14")

            close_20d = float(df_copy.iloc[-21].get("Close", 0)) if len(df_copy) >= 21 else 0.0
            close_60d = float(df_copy.iloc[-61].get("Close", 0)) if len(df_copy) >= 61 else 0.0

            if close_20d == 0 or close_60d == 0 or pd.isna(rsi):
                return Signal(signal_type="HOLD", confidence=0.0, reason="지표 계산 불가")

            momentum_20d = (close - close_20d) / close_20d * 100
            momentum_60d = (close - close_60d) / close_60d * 100

            # 매수 조건: 60일 > 3% AND 20일 > 2% AND RSI < 65
            if momentum_60d > 3.0 and momentum_20d > 2.0 and rsi < rsi_max:
                momentum_score = min(1.0, (momentum_60d + momentum_20d) / 30.0)
                rsi_score = (rsi_max - rsi) / rsi_max
                conf = min(1.0, 0.5 + momentum_score * 0.3 + rsi_score * 0.2)
                return Signal(
                    signal_type="BUY",
                    confidence=round(conf, 2),
                    reason=f"이중모멘텀(60d:{momentum_60d:.1f}%,20d:{momentum_20d:.1f}%)+RSI({rsi:.1f})",
                    target_price=close,
                )

            # 매도 조건: 60일 모멘텀 < -3% OR (20일 < -5% AND RSI > 60)
            if momentum_60d < -3.0 or (momentum_20d < -5.0 and rsi > 60):
                reasons = []
                if momentum_60d < -3.0:
                    reasons.append(f"60d모멘텀하락({momentum_60d:.1f}%)")
                if momentum_20d < -5.0 and rsi > 60:
                    reasons.append(f"20d급락({momentum_20d:.1f}%)+RSI({rsi:.1f})")
                conf = min(1.0, 0.5 + min(1.0, abs(momentum_60d) / 15.0) * 0.4)
                return Signal(
                    signal_type="SELL",
                    confidence=round(conf, 2),
                    reason="+".join(reasons),
                    target_price=close,
                )

        except Exception as e:
            logger.warning(f"ValueMomentum 평가 오류: {e}")

        return Signal(signal_type="HOLD", confidence=0.0, reason="조건 미충족")


class MACDTrendStrategy(BaseStrategy):
    """
    MACD 추세추종 전략
    - 매수 조건: MACD > Signal AND MACD_hist > 0 AND MACD_hist 증가 추세 AND RSI < 65
    - 매도 조건: MACD < Signal AND MACD_hist < 0
    """

    name = "MACDTrend"
    description = "MACD 추세추종 - MACD/Signal 교차 + 히스토그램 증가 추세"

    def evaluate(self, df: pd.DataFrame, params: dict[str, Any]) -> Signal:
        if len(df) < 35:
            return Signal(signal_type="HOLD", confidence=0.0, reason="데이터 부족 (35일 이상 필요)")

        rsi_max = float(params.get("rsi_max", 65.0))

        try:
            import pandas_ta as ta
            df_copy = df.copy()
            df_copy.ta.macd(fast=12, slow=26, signal=9, append=True)
            df_copy.ta.rsi(length=14, append=True)

            last = df_copy.iloc[-1]
            prev = df_copy.iloc[-2]

            macd = last.get("MACD_12_26_9")
            signal_val = last.get("MACDs_12_26_9")
            macd_hist = last.get("MACDh_12_26_9")
            prev_macd_hist = prev.get("MACDh_12_26_9")
            rsi = last.get("RSI_14")

            if any(pd.isna(v) for v in [macd, signal_val, macd_hist, prev_macd_hist, rsi]):
                return Signal(signal_type="HOLD", confidence=0.0, reason="지표 계산 불가")

            # 매수 조건: MACD > Signal AND hist 양수 AND hist 증가 AND RSI < rsi_max
            if macd > signal_val and macd_hist > 0 and macd_hist > prev_macd_hist and rsi < rsi_max:
                hist_score = min(1.0, abs(macd_hist) / max(abs(float(macd)), 0.001))
                rsi_score = (rsi_max - rsi) / rsi_max
                conf = min(1.0, 0.5 + hist_score * 0.25 + rsi_score * 0.25)
                return Signal(
                    signal_type="BUY",
                    confidence=round(conf, 2),
                    reason=f"MACD추세상승(hist:{macd_hist:.4f}↑)+RSI({rsi:.1f})",
                    target_price=float(last.get("Close", 0)),
                )

            # 매도 조건: MACD < Signal AND hist 음수
            if macd < signal_val and macd_hist < 0:
                conf = min(1.0, 0.5 + min(1.0, abs(macd_hist) / max(abs(float(macd)), 0.001)) * 0.4)
                return Signal(
                    signal_type="SELL",
                    confidence=round(conf, 2),
                    reason=f"MACD하락전환(MACD:{macd:.4f}<Signal:{signal_val:.4f})",
                    target_price=float(last.get("Close", 0)),
                )

        except Exception as e:
            logger.warning(f"MACDTrend 평가 오류: {e}")

        return Signal(signal_type="HOLD", confidence=0.0, reason="조건 미충족")


class LowBetaMomentumStrategy(BaseStrategy):
    """
    저베타 모멘텀 전략 (BAB 롱 레그 차용)
    저베타 종목 중 모멘텀이 양호한 것만 매수한다.
    - 매수 조건: beta < 0.8 AND 20일 모멘텀 > 0% AND RSI < 60
    - 매도 조건: beta > 1.2 OR 20일 모멘텀 < -5% OR RSI > 75
    """

    name = "LowBetaMomentum"
    description = "저베타 모멘텀 (BAB 롱 레그): 저베타 종목 중 모멘텀 양호한 것만 매수"

    def __init__(self) -> None:
        self._market_returns: Optional[pd.Series] = None

    def set_market_data(self, market_returns: pd.Series) -> None:
        self._market_returns = market_returns

    def evaluate(self, df: pd.DataFrame, params: dict[str, Any]) -> Signal:
        if len(df) < 60:
            return Signal(signal_type="HOLD", confidence=0.0, reason="데이터 부족 (60일 이상 필요)")
        if self._market_returns is None:
            return Signal(signal_type="HOLD", confidence=0.0, reason="시장 데이터 없음 (KOSPI 필요)")

        beta_max = float(params.get("beta_max", 0.8))
        beta_period = int(params.get("beta_period", 60))
        momentum_min = float(params.get("momentum_min", 0.0))
        rsi_max = float(params.get("rsi_max", 60.0))

        try:
            import pandas_ta as ta
            from app.services.indicators import calculate_beta

            df_copy = df.copy()
            df_copy.ta.rsi(length=14, append=True)

            last = df_copy.iloc[-1]
            close_now = float(last.get("Close", 0))
            rsi = last.get("RSI_14")

            # 베타 계산: 종목 일별 수익률 vs KOSPI
            stock_returns = df_copy["Close"].pct_change().dropna()
            aligned_market = self._market_returns.reindex(
                stock_returns.index, method="nearest"
            ).dropna()
            aligned_stock = stock_returns.reindex(aligned_market.index).dropna()

            if len(aligned_stock) < beta_period:
                return Signal(signal_type="HOLD", confidence=0.0, reason="베타 계산 데이터 부족")

            s_ret = aligned_stock.iloc[-beta_period:]
            m_ret = aligned_market.iloc[-beta_period:]
            beta = calculate_beta(s_ret, m_ret)

            # 20일 모멘텀
            close_20d = float(df_copy.iloc[-21].get("Close", 0)) if len(df_copy) >= 21 else 0.0
            momentum_20d = (close_now - close_20d) / close_20d * 100 if close_20d != 0 else 0.0

            if pd.isna(rsi):
                return Signal(signal_type="HOLD", confidence=0.0, reason="지표 계산 불가")

            # 매도 조건 (우선 체크)
            if beta > 1.2 or momentum_20d < -5.0 or rsi > 75:
                reasons = []
                if beta > 1.2:
                    reasons.append(f"베타상승({beta:.2f}>1.2)")
                if momentum_20d < -5.0:
                    reasons.append(f"모멘텀하락({momentum_20d:.1f}%)")
                if rsi > 75:
                    reasons.append(f"RSI과매수({rsi:.1f})")
                return Signal(
                    signal_type="SELL",
                    confidence=0.6,
                    reason="+".join(reasons),
                    target_price=close_now,
                )

            # 매수 조건
            if beta < beta_max and momentum_20d > momentum_min and rsi < rsi_max:
                beta_score = (beta_max - beta) / beta_max
                rsi_score = (rsi_max - rsi) / rsi_max
                conf = min(1.0, 0.5 + beta_score * 0.3 + rsi_score * 0.2)
                return Signal(
                    signal_type="BUY",
                    confidence=round(conf, 2),
                    reason=f"저베타({beta:.2f}<{beta_max})+모멘텀({momentum_20d:.1f}%)+RSI({rsi:.1f})",
                    target_price=close_now,
                )

        except Exception as e:
            logger.warning(f"LowBetaMomentum 평가 오류: {e}")

        return Signal(signal_type="HOLD", confidence=0.0, reason="조건 미충족")


class MomentumRiskSwitchStrategy(BaseStrategy):
    """
    모멘텀 리스크 스위치 전략 (Dual Momentum 차용)
    KOSPI 시장 추세를 보고 리스크온/오프를 전환한다.
    - 매수 조건: KOSPI 60일 모멘텀 > 0% AND 종목 20일 모멘텀 > 5% AND RSI < 60 AND MACD_hist > 0
    - 매도 조건: KOSPI 60일 모멘텀 < -3% OR 종목 모멘텀 < -7% OR RSI > 75
    """

    name = "MomentumRiskSwitch"
    description = "모멘텀 리스크 스위치 (Dual Momentum): 시장 추세 기반 리스크온/오프 전환"

    def __init__(self) -> None:
        self._market_returns: Optional[pd.Series] = None

    def set_market_data(self, market_returns: pd.Series) -> None:
        self._market_returns = market_returns

    def evaluate(self, df: pd.DataFrame, params: dict[str, Any]) -> Signal:
        if len(df) < 60:
            return Signal(signal_type="HOLD", confidence=0.0, reason="데이터 부족 (60일 이상 필요)")
        if self._market_returns is None:
            return Signal(signal_type="HOLD", confidence=0.0, reason="시장 데이터 없음 (KOSPI 필요)")

        market_momentum_period = int(params.get("market_momentum_period", 60))
        stock_momentum_min = float(params.get("stock_momentum_min", 5.0))
        market_risk_off = float(params.get("market_risk_off", -3.0))
        rsi_max = float(params.get("rsi_max", 60.0))

        try:
            import pandas_ta as ta
            df_copy = df.copy()
            df_copy.ta.macd(fast=12, slow=26, signal=9, append=True)
            df_copy.ta.rsi(length=14, append=True)

            last = df_copy.iloc[-1]
            rsi = last.get("RSI_14")
            macd_hist = last.get("MACDh_12_26_9")

            # KOSPI 60일 누적 수익률
            if len(self._market_returns) < market_momentum_period:
                return Signal(signal_type="HOLD", confidence=0.0, reason="시장 데이터 부족")
            market_recent = self._market_returns.iloc[-market_momentum_period:]
            kospi_momentum_60d = float((1 + market_recent).prod() - 1) * 100

            # 종목 20일 모멘텀
            close_now = float(last.get("Close", 0))
            close_20d = float(df_copy.iloc[-21].get("Close", 0)) if len(df_copy) >= 21 else 0.0
            momentum_20d = (close_now - close_20d) / close_20d * 100 if close_20d != 0 else 0.0

            if any(pd.isna(v) for v in [rsi, macd_hist]):
                return Signal(signal_type="HOLD", confidence=0.0, reason="지표 계산 불가")

            # 매도 조건 (리스크오프) — 우선 체크
            if kospi_momentum_60d < market_risk_off or momentum_20d < -7.0 or rsi > 75:
                reasons = []
                if kospi_momentum_60d < market_risk_off:
                    reasons.append(f"시장리스크오프(KOSPI:{kospi_momentum_60d:.1f}%)")
                if momentum_20d < -7.0:
                    reasons.append(f"종목급락({momentum_20d:.1f}%)")
                if rsi > 75:
                    reasons.append(f"RSI과매수({rsi:.1f})")
                return Signal(
                    signal_type="SELL",
                    confidence=0.65,
                    reason="+".join(reasons),
                    target_price=close_now,
                )

            # 매수 조건 (리스크온)
            if (
                kospi_momentum_60d > 0
                and momentum_20d > stock_momentum_min
                and rsi < rsi_max
                and macd_hist > 0
            ):
                kospi_score = min(1.0, kospi_momentum_60d / 10.0)
                stock_score = min(1.0, (momentum_20d - stock_momentum_min) / 10.0)
                rsi_score = (rsi_max - rsi) / rsi_max
                conf = min(1.0, 0.5 + kospi_score * 0.2 + stock_score * 0.2 + rsi_score * 0.1)
                return Signal(
                    signal_type="BUY",
                    confidence=round(conf, 2),
                    reason=f"리스크온(KOSPI:{kospi_momentum_60d:.1f}%)+종목({momentum_20d:.1f}%)+RSI({rsi:.1f})",
                    target_price=close_now,
                )

        except Exception as e:
            logger.warning(f"MomentumRiskSwitch 평가 오류: {e}")

        return Signal(signal_type="HOLD", confidence=0.0, reason="조건 미충족")


class DynamicStrategy(BaseStrategy):
    """
    동적 커스텀 전략 - JSONB 조건 구조를 파싱하여 매매 신호를 생성한다.

    지원 지표: SMA, EMA, RSI, MACD, BB_UPPER, BB_LOWER, ATR, VOLUME_RATIO, PRICE
    지원 연산자: >, >=, <, <=, CROSS_ABOVE, CROSS_BELOW
    """

    name = "DynamicStrategy"
    description = "커스텀 조건 기반 동적 전략"

    def __init__(self, buy_conditions: dict, sell_conditions: dict) -> None:
        self._buy_conditions = buy_conditions
        self._sell_conditions = sell_conditions

    def _compute_indicator(self, df: pd.DataFrame, operand: dict) -> Optional[pd.Series]:
        """좌변/우변 피연산자를 DataFrame 시리즈로 변환한다."""
        if operand.get("type") == "value":
            # 상수값 → 전체 행과 같은 크기의 Series
            return pd.Series([float(operand["value"])] * len(df), index=df.index)

        indicator = operand.get("indicator", "")
        params = operand.get("params", {})

        try:
            import pandas_ta as ta

            if indicator == "SMA":
                period = int(params.get("period", 20))
                return df.ta.sma(length=period)
            elif indicator == "EMA":
                period = int(params.get("period", 12))
                return df.ta.ema(length=period)
            elif indicator == "RSI":
                period = int(params.get("period", 14))
                return df.ta.rsi(length=period)
            elif indicator == "MACD":
                macd_df = df.ta.macd(fast=12, slow=26, signal=9)
                if macd_df is not None:
                    return macd_df.iloc[:, 0]  # MACD 라인
            elif indicator == "BB_UPPER":
                period = int(params.get("period", 20))
                bb_df = df.ta.bbands(length=period, std=2)
                if bb_df is not None:
                    # BBU_20_2.0 컬럼
                    upper_col = [c for c in bb_df.columns if c.startswith("BBU")]
                    return bb_df[upper_col[0]] if upper_col else None
            elif indicator == "BB_LOWER":
                period = int(params.get("period", 20))
                bb_df = df.ta.bbands(length=period, std=2)
                if bb_df is not None:
                    lower_col = [c for c in bb_df.columns if c.startswith("BBL")]
                    return bb_df[lower_col[0]] if lower_col else None
            elif indicator == "ATR":
                period = int(params.get("period", 14))
                return df.ta.atr(length=period)
            elif indicator == "VOLUME_RATIO":
                period = int(params.get("period", 20))
                return df["Volume"] / df["Volume"].rolling(period).mean()
            elif indicator == "PRICE":
                return df["Close"]
        except Exception as e:
            logger.warning(f"DynamicStrategy 지표 계산 오류 ({indicator}): {e}")

        return None

    def _evaluate_condition(self, df: pd.DataFrame, condition: dict) -> Optional[bool]:
        """단일 조건 행을 최신 시점 기준으로 평가한다."""
        left_series = self._compute_indicator(df, condition.get("leftOperand", {}))
        right_series = self._compute_indicator(df, condition.get("rightOperand", {}))
        operator = condition.get("operator", ">")

        if left_series is None or right_series is None:
            return None
        if left_series.isna().iloc[-1] or right_series.isna().iloc[-1]:
            return None

        left_val = float(left_series.iloc[-1])
        right_val = float(right_series.iloc[-1])

        if operator == ">":
            return left_val > right_val
        elif operator == ">=":
            return left_val >= right_val
        elif operator == "<":
            return left_val < right_val
        elif operator == "<=":
            return left_val <= right_val
        elif operator == "CROSS_ABOVE":
            # 직전 행에서 left <= right이고 현재 행에서 left > right
            if len(left_series) < 2 or len(right_series) < 2:
                return None
            prev_left = float(left_series.iloc[-2])
            prev_right = float(right_series.iloc[-2])
            return prev_left <= prev_right and left_val > right_val
        elif operator == "CROSS_BELOW":
            if len(left_series) < 2 or len(right_series) < 2:
                return None
            prev_left = float(left_series.iloc[-2])
            prev_right = float(right_series.iloc[-2])
            return prev_left >= prev_right and left_val < right_val

        return None

    def _evaluate_group(self, df: pd.DataFrame, group: dict) -> bool:
        """조건 그룹 전체를 AND/OR 로직으로 평가한다."""
        conditions = group.get("conditions", [])
        logic_operators = group.get("logicOperators", [])

        if not conditions:
            return False

        results = [self._evaluate_condition(df, c) for c in conditions]
        # None(평가 불가)은 False로 처리
        bool_results = [r if r is not None else False for r in results]

        if len(bool_results) == 1:
            return bool_results[0]

        # AND/OR 로직 순차 적용
        result = bool_results[0]
        for i, op in enumerate(logic_operators):
            if i + 1 >= len(bool_results):
                break
            if op == "AND":
                result = result and bool_results[i + 1]
            else:  # OR
                result = result or bool_results[i + 1]

        return result

    def evaluate(self, df: pd.DataFrame, params: dict[str, Any]) -> Signal:
        if len(df) < 5:
            return Signal(signal_type="HOLD", confidence=0.0, reason="데이터 부족")

        try:
            is_buy = self._evaluate_group(df, self._buy_conditions)
            is_sell = self._evaluate_group(df, self._sell_conditions)

            if is_buy:
                return Signal(
                    signal_type="BUY",
                    confidence=0.7,
                    reason="커스텀 매수 조건 충족",
                    target_price=float(df["Close"].iloc[-1]),
                )
            if is_sell:
                return Signal(
                    signal_type="SELL",
                    confidence=0.7,
                    reason="커스텀 매도 조건 충족",
                    target_price=float(df["Close"].iloc[-1]),
                )
        except Exception as e:
            logger.warning(f"DynamicStrategy 평가 오류: {e}")

        return Signal(signal_type="HOLD", confidence=0.0, reason="조건 미충족")


def get_dynamic_strategy(buy_conditions: dict, sell_conditions: dict) -> DynamicStrategy:
    """JSONB 조건 딕셔너리로 DynamicStrategy 인스턴스를 생성한다."""
    return DynamicStrategy(buy_conditions, sell_conditions)


# 등록된 전략 레지스트리 (strategy name → 인스턴스)
STRATEGY_REGISTRY: dict[str, BaseStrategy] = {
    "GoldenCrossRSI": GoldenCrossRSIStrategy(),
    "BollingerReversal": BollingerReversalStrategy(),
    "ValueMomentum": ValueMomentumStrategy(),
    "MACDTrend": MACDTrendStrategy(),
    "LowBetaMomentum": LowBetaMomentumStrategy(),
    "MomentumRiskSwitch": MomentumRiskSwitchStrategy(),
}

# DB 한글 전략명 → 레지스트리 영문 키 매핑
_NAME_TO_ENGINE: dict[str, str] = {
    "골든크로스+RSI": "GoldenCrossRSI",
    "가치+모멘텀": "ValueMomentum",
    "볼린저밴드반전": "BollingerReversal",
    "MACD추세추종": "MACDTrend",
    "저베타모멘텀": "LowBetaMomentum",
    "모멘텀리스크스위치": "MomentumRiskSwitch",
}


def get_strategy(name: str) -> Optional[BaseStrategy]:
    """전략명으로 전략 인스턴스를 반환한다. DB 한글 이름도 지원한다."""
    key = _NAME_TO_ENGINE.get(name, name)
    return STRATEGY_REGISTRY.get(key)
