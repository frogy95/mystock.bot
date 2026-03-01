"""
KIS API Rate Limit 유틸리티 및 재시도 로직
- 슬라이딩 윈도우 방식 RateLimiter (모의투자 5건/초, 실전 20건/초)
- 지수 백오프 retry (최대 3회)
"""
from __future__ import annotations

import asyncio
import logging
import time
from collections import deque
from functools import wraps
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class RateLimiter:
    """슬라이딩 윈도우 방식 Rate Limiter"""

    def __init__(self, max_calls: int, window_seconds: float = 1.0) -> None:
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self._calls: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Rate Limit을 적용하여 호출을 허용한다."""
        async with self._lock:
            now = time.monotonic()

            # 윈도우 범위를 벗어난 오래된 호출 제거
            cutoff = now - self.window_seconds
            while self._calls and self._calls[0] < cutoff:
                self._calls.popleft()

            # 한도 초과 시 대기
            if len(self._calls) >= self.max_calls:
                wait_time = self._calls[0] + self.window_seconds - now
                if wait_time > 0:
                    logger.debug("Rate limit 도달. %.3f초 대기", wait_time)
                    await asyncio.sleep(wait_time)

                # 대기 후 다시 정리
                now = time.monotonic()
                cutoff = now - self.window_seconds
                while self._calls and self._calls[0] < cutoff:
                    self._calls.popleft()

            self._calls.append(now)


# 모의투자: 5건/초, 실전: 20건/초
_vts_limiter = RateLimiter(max_calls=5, window_seconds=1.0)
_prod_limiter = RateLimiter(max_calls=20, window_seconds=1.0)


def get_rate_limiter(is_virtual: bool = True) -> RateLimiter:
    """환경에 맞는 RateLimiter를 반환한다."""
    return _vts_limiter if is_virtual else _prod_limiter


async def retry_with_backoff(
    func: Callable[..., Any],
    *args: Any,
    max_retries: int = 3,
    base_delay: float = 1.0,
    **kwargs: Any,
) -> Any:
    """지수 백오프로 비동기 함수를 재시도한다.

    Args:
        func: 실행할 함수
        max_retries: 최대 재시도 횟수 (기본 3회)
        base_delay: 초기 대기 시간 초 (기본 1.0)
    """
    last_exc: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)
        except Exception as exc:
            last_exc = exc
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                logger.warning(
                    "호출 실패 (시도 %d/%d), %.1f초 후 재시도: %s",
                    attempt + 1,
                    max_retries,
                    delay,
                    exc,
                )
                await asyncio.sleep(delay)

    raise last_exc  # type: ignore[misc]
