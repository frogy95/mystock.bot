"""
손절/익절 관리 엔진
보유종목의 현재 상태를 평가하여 손절/익절 신호를 생성한다.
- 고정비율 손절
- 트레일링 스탑
- ATR 기반 동적 손절
- 분할 익절 (목표가의 50% 도달 시)
손절/익절 발동 시 텔레그램 알림을 fire-and-forget 방식으로 전송한다.
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Optional

from app.models.holding import Holding
from app.services.strategy_engine import Signal
from app.services.telegram_notifier import notify_risk_triggered

logger = logging.getLogger("mystock.bot")

# Redis 트레일링 스탑 최고가 캐시 키 접두사
_TRAILING_HIGH_KEY = "trailing_high:{user_id}:{stock_code}"


@dataclass
class RiskSignal:
    """손절/익절 신호"""

    action: str          # "STOP_LOSS" | "TAKE_PROFIT" | "PARTIAL_TAKE_PROFIT" | "HOLD"
    reason: str
    quantity: int        # 매도할 수량 (0: 전량, 부분 익절 시 반량)


async def evaluate_holding_risk(holding: Holding) -> RiskSignal:
    """
    보유종목의 현재가를 기준으로 손절/익절 신호를 평가한다.
    설정된 손절/익절 비율이 없으면 HOLD를 반환한다.
    """
    if holding.current_price is None or holding.avg_price is None:
        return RiskSignal(action="HOLD", reason="현재가 없음", quantity=0)

    current = float(holding.current_price)
    avg = float(holding.avg_price)
    qty = holding.quantity

    if avg == 0 or qty == 0:
        return RiskSignal(action="HOLD", reason="평균가 또는 수량 없음", quantity=0)

    change_rate = (current - avg) / avg * 100

    # 1. 고정비율 손절
    if holding.stop_loss_rate is not None:
        stop_loss = float(holding.stop_loss_rate)
        if change_rate <= -stop_loss:
            reason = f"고정비율 손절 ({change_rate:.2f}% ≤ -{stop_loss}%)"
            # 텔레그램 알림 (fire-and-forget 방식)
            asyncio.create_task(
                notify_risk_triggered(
                    stock_code=holding.stock_code,
                    action="STOP_LOSS",
                    current_price=current,
                    avg_price=avg,
                    reason=reason,
                )
            )
            return RiskSignal(action="STOP_LOSS", reason=reason, quantity=qty)

    # 2. 익절
    if holding.take_profit_rate is not None:
        take_profit = float(holding.take_profit_rate)
        # 전량 익절: 목표가 도달 시 전량 매도 (분할 익절보다 먼저 체크)
        if change_rate >= take_profit:
            reason = f"전량 익절 ({change_rate:.2f}% ≥ {take_profit}%)"
            # 텔레그램 알림 (fire-and-forget 방식)
            asyncio.create_task(
                notify_risk_triggered(
                    stock_code=holding.stock_code,
                    action="TAKE_PROFIT",
                    current_price=current,
                    avg_price=avg,
                    reason=reason,
                )
            )
            return RiskSignal(action="TAKE_PROFIT", reason=reason, quantity=qty)
        # 분할 익절: 목표가 50% 도달 시 반량 매도
        if change_rate >= take_profit * 0.5 and qty >= 2:
            partial_qty = qty // 2
            reason = f"분할 익절 ({change_rate:.2f}% ≥ 목표 {take_profit}%의 50%)"
            # 텔레그램 알림 (fire-and-forget 방식)
            asyncio.create_task(
                notify_risk_triggered(
                    stock_code=holding.stock_code,
                    action="PARTIAL_TAKE_PROFIT",
                    current_price=current,
                    avg_price=avg,
                    reason=reason,
                )
            )
            return RiskSignal(action="PARTIAL_TAKE_PROFIT", reason=reason, quantity=partial_qty)

    return RiskSignal(action="HOLD", reason="조건 미충족", quantity=0)


async def evaluate_trailing_stop(
    holding: Holding,
    trail_rate: float,
) -> RiskSignal:
    """
    트레일링 스탑: Redis에 저장된 최고가 대비 trail_rate% 하락 시 손절.
    """
    if holding.current_price is None:
        return RiskSignal(action="HOLD", reason="현재가 없음", quantity=0)

    from app.services.redis_client import get_redis
    redis = get_redis()

    cache_key = _TRAILING_HIGH_KEY.format(
        user_id=holding.user_id, stock_code=holding.stock_code
    )

    current = float(holding.current_price)

    # 저장된 최고가 조회
    stored_high = await redis.get(cache_key)
    high = float(stored_high) if stored_high else current

    # 최고가 업데이트
    if current > high:
        high = current
        await redis.setex(cache_key, 86400, str(high))  # 24시간 TTL

    change_from_high = (current - high) / high * 100

    if change_from_high <= -trail_rate:
        return RiskSignal(
            action="STOP_LOSS",
            reason=f"트레일링 스탑 (고점 {high:.0f}원 대비 {change_from_high:.2f}% 하락)",
            quantity=holding.quantity,
        )

    return RiskSignal(action="HOLD", reason="트레일링 스탑 조건 미충족", quantity=0)


async def evaluate_atr_stop(
    holding: Holding,
    symbol: str,
    atr_multiplier: float = 2.0,
) -> RiskSignal:
    """
    ATR 기반 동적 손절: 현재가가 (평균가 - ATR × 배수) 이하이면 손절.
    """
    if holding.current_price is None:
        return RiskSignal(action="HOLD", reason="현재가 없음", quantity=0)

    from app.services.indicators import get_indicators
    indicators = await get_indicators(symbol)

    atr = indicators.get("atr_14")
    if atr is None:
        return RiskSignal(action="HOLD", reason="ATR 계산 불가", quantity=0)

    current = float(holding.current_price)
    avg = float(holding.avg_price)
    stop_price = avg - (atr * atr_multiplier)

    if current <= stop_price:
        return RiskSignal(
            action="STOP_LOSS",
            reason=f"ATR 손절 (현재가 {current:.0f} ≤ 손절가 {stop_price:.0f})",
            quantity=holding.quantity,
        )

    return RiskSignal(action="HOLD", reason="ATR 손절 조건 미충족", quantity=0)


def to_signal(risk_signal: RiskSignal) -> Signal:
    """RiskSignal을 order_executor 호환 Signal로 변환한다."""
    if risk_signal.action == "HOLD":
        return Signal(signal_type="HOLD", confidence=0.0, reason=risk_signal.reason)
    return Signal(
        signal_type="SELL",
        confidence=1.0,
        reason=risk_signal.reason,
    )
