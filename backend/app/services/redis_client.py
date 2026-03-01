"""
Redis 클라이언트 모듈
애플리케이션 전역에서 사용하는 Redis 싱글턴 클라이언트를 제공한다.
"""
import logging
from typing import Optional

import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger("mystock.bot")

# 전역 Redis 클라이언트 인스턴스
_redis_client: Optional[aioredis.Redis] = None


def get_redis() -> aioredis.Redis:
    """Redis 싱글턴 클라이언트를 반환한다."""
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True,
        )
    return _redis_client


async def close_redis() -> None:
    """Redis 연결을 종료한다. (앱 종료 시 호출)"""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
        logger.info("Redis 연결 종료")
