"""
KIS (한국투자증권) API 클라이언트 서비스
python-kis(pykis) 라이브러리를 래핑한 싱글턴 클래스.
KIS API 키 미설정 시 경고만 출력하고 동작한다 (lazy 초기화).
"""
from __future__ import annotations

import logging
from typing import Any

from app.services.rate_limiter import get_rate_limiter, retry_with_backoff

logger = logging.getLogger(__name__)


class KISClient:
    """KIS API 싱글턴 클라이언트"""

    _instance: "KISClient | None" = None
    _kis: Any = None  # pykis.PyKis 인스턴스

    def __new__(cls) -> "KISClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _get_kis(self) -> Any:
        """PyKis 인스턴스를 lazy 초기화하여 반환한다."""
        if self._kis is not None:
            return self._kis

        from app.core.config import settings

        # KIS API 키가 설정되어 있는지 확인
        if not all([settings.KIS_APP_KEY, settings.KIS_APP_SECRET, settings.KIS_ACCOUNT_NUMBER]):
            logger.warning(
                "KIS API 키가 설정되지 않았습니다. "
                "KIS_APP_KEY, KIS_APP_SECRET, KIS_ACCOUNT_NUMBER 환경변수를 설정하세요."
            )
            return None

        try:
            from pykis import PyKis

            is_virtual = settings.KIS_ENVIRONMENT == "vts"

            self._kis = PyKis(
                id=None,  # HTS ID 없이 동작
                account=settings.KIS_ACCOUNT_NUMBER,
                appkey=settings.KIS_APP_KEY,
                secretkey=settings.KIS_APP_SECRET,
                virtual=is_virtual,
            )
            logger.info(
                "KIS API 클라이언트 초기화 완료 (환경: %s)",
                "모의투자" if is_virtual else "실전투자",
            )
        except Exception as exc:
            logger.error("KIS API 클라이언트 초기화 실패: %s", exc)
            return None

        return self._kis

    def is_available(self) -> bool:
        """KIS API 클라이언트 사용 가능 여부를 반환한다."""
        from app.core.config import settings
        is_virtual = settings.KIS_ENVIRONMENT == "vts"
        self._limiter = get_rate_limiter(is_virtual)
        return self._get_kis() is not None

    async def get_quote(self, symbol: str) -> dict[str, Any] | None:
        """주식 현재가를 조회한다 (rate limit + retry 적용)."""
        kis = self._get_kis()
        if kis is None:
            return None

        from app.core.config import settings
        limiter = get_rate_limiter(settings.KIS_ENVIRONMENT == "vts")
        await limiter.acquire()

        def _fetch() -> dict[str, Any]:
            stock = kis.stock(symbol)
            quote = stock.quote()
            return {
                "symbol": symbol,
                "price": float(quote.price),
                "change": float(quote.change),
                "change_rate": float(quote.change_rate),
                "volume": int(quote.volume),
                "high": float(quote.high),
                "low": float(quote.low),
                "open": float(quote.open),
            }

        try:
            return await retry_with_backoff(_fetch)
        except Exception as exc:
            logger.error("현재가 조회 실패 [%s]: %s", symbol, exc)
            raise

    async def get_chart(self, symbol: str, period: str = "day", count: int = 30) -> list[dict[str, Any]] | None:
        """주식 차트 데이터(OHLCV)를 조회한다 (rate limit + retry 적용)."""
        kis = self._get_kis()
        if kis is None:
            return None

        from app.core.config import settings
        limiter = get_rate_limiter(settings.KIS_ENVIRONMENT == "vts")
        await limiter.acquire()

        def _fetch() -> list[dict[str, Any]]:
            stock = kis.stock(symbol)
            chart = stock.chart(period=period, count=count)
            return [
                {
                    "date": str(item.time),
                    "open": float(item.open),
                    "high": float(item.high),
                    "low": float(item.low),
                    "close": float(item.close),
                    "volume": int(item.volume),
                }
                for item in chart
            ]

        try:
            return await retry_with_backoff(_fetch)
        except Exception as exc:
            logger.error("차트 조회 실패 [%s]: %s", symbol, exc)
            raise

    async def get_balance(self) -> dict[str, Any] | None:
        """계좌 잔고를 조회한다 (rate limit + retry 적용)."""
        kis = self._get_kis()
        if kis is None:
            return None

        from app.core.config import settings
        limiter = get_rate_limiter(settings.KIS_ENVIRONMENT == "vts")
        await limiter.acquire()

        def _fetch() -> dict[str, Any]:
            account = kis.account()
            balance = account.balance()
            return {
                "cash": float(balance.amount.amount),
                "stocks": [
                    {
                        "symbol": stock.symbol,
                        "name": stock.name,
                        "quantity": int(stock.qty),
                        "current_price": float(stock.price),
                        "profit_loss_rate": float(stock.profit_loss_rate),
                    }
                    for stock in balance.stocks
                ],
            }

        try:
            return await retry_with_backoff(_fetch)
        except Exception as exc:
            logger.error("잔고 조회 실패: %s", exc)
            raise


# 싱글턴 인스턴스
kis_client = KISClient()
