"""
시스템 안전장치 모듈
Redis 분산 락과 연속 에러 임계값 기반 자동매매 중단을 담당한다.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from app.services.redis_client import get_redis

logger = logging.getLogger("mystock.bot")

# Redis 키 상수
_ORDER_LOCK_KEY = "order_lock:{user_id}:{stock_code}"
_ERROR_COUNT_KEY = "error_count:{user_id}"
_LOCK_TTL = 10         # 주문 락 TTL (10초)
_ERROR_TTL = 3600      # 에러 카운터 TTL (1시간)
_MAX_ERRORS = 5        # 자동매매 중단 임계값


@asynccontextmanager
async def acquire_order_lock(
    user_id: int, stock_code: str
) -> AsyncIterator[bool]:
    """
    주문 실행 전 Redis 분산 락을 획득한다.
    동일 사용자+종목의 동시 주문을 방지한다.

    사용법:
    async with acquire_order_lock(user_id, stock_code) as acquired:
        if not acquired:
            return  # 이미 주문 처리 중
        # 주문 실행
    """
    redis = get_redis()
    lock_key = _ORDER_LOCK_KEY.format(user_id=user_id, stock_code=stock_code)

    # SET NX EX로 원자적 락 획득
    acquired = await redis.set(lock_key, "1", nx=True, ex=_LOCK_TTL)
    try:
        yield bool(acquired)
    finally:
        if acquired:
            await redis.delete(lock_key)


async def record_error(user_id: int) -> int:
    """에러를 기록하고 현재 에러 카운트를 반환한다."""
    redis = get_redis()
    key = _ERROR_COUNT_KEY.format(user_id=user_id)

    count = await redis.incr(key)
    if count == 1:
        # 첫 에러 시 TTL 설정
        await redis.expire(key, _ERROR_TTL)

    logger.warning(f"사용자 {user_id} 에러 카운트: {count}/{_MAX_ERRORS}")
    return count


async def clear_errors(user_id: int) -> None:
    """에러 카운트를 초기화한다."""
    redis = get_redis()
    await redis.delete(_ERROR_COUNT_KEY.format(user_id=user_id))


async def check_error_threshold(
    user_id: int, db
) -> tuple[bool, str]:
    """
    에러 임계값 초과 시 자동매매를 중단하고 False를 반환한다.
    Returns: (계속 진행 가능 여부, 메시지)
    """
    redis = get_redis()
    key = _ERROR_COUNT_KEY.format(user_id=user_id)
    count_str = await redis.get(key)
    count = int(count_str) if count_str else 0

    if count >= _MAX_ERRORS:
        from app.services.safety_guard import set_auto_trade
        await set_auto_trade(user_id, False, db)
        logger.error(
            f"사용자 {user_id} 연속 에러 {count}회 - 자동매매 자동 중단"
        )
        return False, f"연속 에러 {count}회 초과 - 자동매매 중단"

    return True, f"에러 카운트 {count}/{_MAX_ERRORS}"


async def get_system_status(user_id: int) -> dict:
    """현재 시스템 상태를 반환한다."""
    redis = get_redis()

    error_count_str = await redis.get(_ERROR_COUNT_KEY.format(user_id=user_id))
    error_count = int(error_count_str) if error_count_str else 0

    return {
        "error_count": error_count,
        "max_errors": _MAX_ERRORS,
        "is_healthy": error_count < _MAX_ERRORS,
    }
