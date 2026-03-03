"""
매매 안전장치 모듈
일일 손실 한도, 최대 주문 수, 포지션 비중, 긴급 전체 매도를 관리한다.
주문 실행 전 모든 체크를 통과해야 한다.
"""
from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.holding import Holding
from app.models.order import Order
from app.models.settings import SystemSetting

logger = logging.getLogger("mystock.bot")

# 기본 안전장치 설정값
_DEFAULT_DAILY_LOSS_LIMIT_PCT = 5.0   # 일일 최대 손실 5%
_DEFAULT_MAX_DAILY_ORDERS = 10        # 일일 최대 주문 10건
_DEFAULT_MAX_POSITION_RATIO = 30.0    # 단일 종목 최대 비중 30%
_REDIS_DAILY_ORDERS_KEY = "daily_orders:{user_id}:{date}"
_REDIS_AUTO_TRADE_KEY = "auto_trade_enabled:{user_id}"


async def _get_setting(
    user_id: int, key: str, default: str, db: AsyncSession
) -> str:
    """DB에서 사용자 설정값을 조회한다. 없으면 기본값 반환."""
    result = await db.execute(
        select(SystemSetting).where(
            SystemSetting.setting_key == key,
            (SystemSetting.user_id == user_id) | (SystemSetting.user_id == None),
        ).order_by(SystemSetting.user_id.desc())  # 사용자 설정 우선
    )
    setting = result.scalar_one_or_none()
    return setting.setting_value if setting else default


async def is_auto_trade_enabled(user_id: int, db: AsyncSession) -> bool:
    """자동매매 활성화 여부를 확인한다."""
    from app.services.redis_client import get_redis
    redis = get_redis()

    # Redis 캐시 우선
    cached = await redis.get(_REDIS_AUTO_TRADE_KEY.format(user_id=user_id))
    if cached is not None:
        return cached == "1"

    # DB 조회
    val = await _get_setting(user_id, "auto_trade_enabled", "false", db)
    return val.lower() in ("true", "1", "yes")


async def set_auto_trade(user_id: int, enabled: bool, db: AsyncSession) -> None:
    """자동매매 활성화 상태를 DB와 Redis에 저장한다."""
    from app.services.redis_client import get_redis
    redis = get_redis()

    # Redis 업데이트 (즉시 반영)
    await redis.setex(
        _REDIS_AUTO_TRADE_KEY.format(user_id=user_id),
        86400,
        "1" if enabled else "0",
    )

    # DB 업데이트
    result = await db.execute(
        select(SystemSetting).where(
            SystemSetting.setting_key == "auto_trade_enabled",
            SystemSetting.user_id == user_id,
        )
    )
    setting = result.scalar_one_or_none()
    if setting:
        setting.setting_value = "true" if enabled else "false"
    else:
        db.add(SystemSetting(
            user_id=user_id,
            setting_key="auto_trade_enabled",
            setting_value="true" if enabled else "false",
            setting_type="bool",
        ))
    await db.commit()


async def check_daily_loss_limit(user_id: int, db: AsyncSession) -> tuple[bool, str]:
    """
    미실현 평가 손실이 한도를 초과했는지 확인한다.
    (주의: 진정한 일일 손실이 아닌 전체 보유기간 미실현 손익률 기준)
    Returns: (통과 여부, 메시지)
    """
    limit_pct = float(
        await _get_setting(user_id, "daily_loss_limit_pct", str(_DEFAULT_DAILY_LOSS_LIMIT_PCT), db)
    )

    # 보유종목의 현재 전체 미실현 손익률 계산
    result = await db.execute(
        select(Holding).where(Holding.user_id == user_id, Holding.quantity > 0)
    )
    holdings = result.scalars().all()

    if not holdings:
        return True, "보유종목 없음"

    total_purchase = sum(float(h.avg_price) * h.quantity for h in holdings)
    total_current = sum(
        float(h.current_price) * h.quantity
        for h in holdings
        if h.current_price is not None
    )

    if total_purchase == 0:
        return True, "매입금액 없음"

    unrealized_loss_pct = (total_current - total_purchase) / total_purchase * 100
    if unrealized_loss_pct <= -limit_pct:
        return False, f"미실현 평가 손실 한도 초과 ({unrealized_loss_pct:.2f}% ≤ -{limit_pct}%)"

    return True, f"미실현 손실률 {unrealized_loss_pct:.2f}%"


async def check_max_daily_orders(user_id: int, db: AsyncSession) -> tuple[bool, str]:
    """
    일일 최대 주문 수를 초과했는지 확인한다.
    """
    max_orders = int(
        await _get_setting(user_id, "max_daily_orders", str(_DEFAULT_MAX_DAILY_ORDERS), db)
    )

    from datetime import date
    from sqlalchemy import cast, Date
    today = date.today()

    result = await db.execute(
        select(func.count(Order.id)).where(
            Order.user_id == user_id,
            Order.status != "failed",
            func.date(Order.created_at) == today,
        )
    )
    count = result.scalar_one()

    if count >= max_orders:
        return False, f"일일 최대 주문 수 초과 ({count}/{max_orders})"
    return True, f"오늘 주문 수 {count}/{max_orders}"


async def check_position_ratio(
    user_id: int,
    stock_code: str,
    order_quantity: int,
    order_price: float,
    db: AsyncSession,
) -> tuple[bool, str]:
    """
    단일 종목 최대 비중을 초과하지 않는지 확인한다.
    """
    max_ratio = float(
        await _get_setting(user_id, "max_position_ratio_pct", str(_DEFAULT_MAX_POSITION_RATIO), db)
    )

    result = await db.execute(
        select(Holding).where(Holding.user_id == user_id, Holding.quantity > 0)
    )
    holdings = result.scalars().all()

    total_value = sum(
        float(h.current_price or h.avg_price) * h.quantity for h in holdings
    )
    order_value = order_quantity * order_price

    if total_value + order_value == 0:
        return True, "포트폴리오 가치 없음"

    new_ratio = order_value / (total_value + order_value) * 100
    if new_ratio > max_ratio:
        return False, f"단일 종목 비중 초과 ({new_ratio:.1f}% > {max_ratio}%)"

    return True, f"비중 {new_ratio:.1f}%"


async def run_all_checks(
    user_id: int,
    stock_code: str,
    quantity: int,
    price: float,
    db: AsyncSession,
) -> tuple[bool, str]:
    """
    주문 실행 전 모든 안전장치를 검사한다.
    Returns: (모든 검사 통과 여부, 실패 메시지)
    """
    # 자동매매 활성화 확인
    if not await is_auto_trade_enabled(user_id, db):
        return False, "자동매매 비활성화 상태"

    # 일일 손실 한도
    ok, msg = await check_daily_loss_limit(user_id, db)
    if not ok:
        return False, msg

    # 일일 최대 주문 수
    ok, msg = await check_max_daily_orders(user_id, db)
    if not ok:
        return False, msg

    # 포지션 비중
    if price > 0:
        ok, msg = await check_position_ratio(user_id, stock_code, quantity, price, db)
        if not ok:
            return False, msg

    return True, "모든 안전장치 통과"


async def emergency_sell_all(user_id: int, db: AsyncSession) -> dict:
    """
    긴급 전체 매도: 모든 보유종목을 시장가로 즉시 매도한다.
    """
    from app.services.order_executor import execute_signal
    from app.services.strategy_engine import Signal

    result = await db.execute(
        select(Holding).where(Holding.user_id == user_id, Holding.quantity > 0)
    )
    holdings = result.scalars().all()

    executed_count = 0
    failed_count = 0

    for holding in holdings:
        signal = Signal(
            signal_type="SELL",
            confidence=1.0,
            reason="긴급 전체 매도",
        )
        order = await execute_signal(
            user_id=user_id,
            stock_code=holding.stock_code,
            signal=signal,
            quantity=holding.quantity,
            strategy_id=None,
            db=db,
        )
        if order and order.status not in ("failed",):
            executed_count += 1
        else:
            failed_count += 1

    # 자동매매 비활성화
    await set_auto_trade(user_id, False, db)

    logger.warning(f"긴급 전체 매도 완료: 성공 {executed_count}건, 실패 {failed_count}건")
    return {
        "executed_count": executed_count,
        "failed_count": failed_count,
        "auto_trade_disabled": True,
    }
