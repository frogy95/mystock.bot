"""
KIS (한국투자증권) API 클라이언트 서비스
httpx를 사용하여 KIS REST API를 직접 호출하는 싱글턴 클래스.
KIS API 키 미설정 시 경고만 출력하고 동작한다.
"""
from __future__ import annotations

import logging
from typing import Any

import httpx

from app.services.rate_limiter import get_rate_limiter, retry_with_backoff

logger = logging.getLogger(__name__)

# KIS API 엔드포인트
_KIS_REAL_BASE = "https://openapi.koreainvestment.com:9443"
_KIS_VTS_BASE = "https://openapivts.koreainvestment.com:29443"

# 메모리 토큰 캐시 (프로세스 내)
_token_cache: dict[str, Any] = {}


class KISClient:
    """KIS API 싱글턴 클라이언트 (httpx 직접 호출 방식)"""

    _instance: "KISClient | None" = None

    def __new__(cls) -> "KISClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def is_available(self) -> bool:
        """KIS API 클라이언트 사용 가능 여부를 반환한다."""
        from app.core.config import settings
        return all([
            settings.KIS_APP_KEY,
            settings.KIS_APP_SECRET,
            settings.KIS_ACCOUNT_NUMBER,
            settings.KIS_HTS_ID,
        ])

    async def _get_access_token(self) -> str:
        """KIS OAuth 액세스 토큰을 발급/캐싱한다."""
        import time
        from app.core.config import settings

        cache_key = settings.KIS_APP_KEY
        cached = _token_cache.get(cache_key)
        if cached and cached["expires_at"] > time.time() + 60:
            return cached["token"]

        is_virtual = settings.KIS_ENVIRONMENT == "vts"
        base_url = _KIS_VTS_BASE if is_virtual else _KIS_REAL_BASE

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{base_url}/oauth2/tokenP",
                json={
                    "grant_type": "client_credentials",
                    "appkey": settings.KIS_APP_KEY,
                    "appsecret": settings.KIS_APP_SECRET,
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()

        token = data["access_token"]
        expires_in = int(data.get("expires_in", 86400))
        _token_cache[cache_key] = {"token": token, "expires_at": time.time() + expires_in}
        logger.info("KIS 액세스 토큰 발급 완료 (유효기간: %d초)", expires_in)
        return token

    async def get_quote(self, symbol: str) -> dict[str, Any] | None:
        """주식 현재가를 조회한다 (KIS REST API 직접 호출, rate limit + retry 적용).
        시세 데이터는 모의투자 여부와 무관하게 실전 서버에서만 제공된다.
        """
        if not self.is_available():
            return None

        from app.core.config import settings
        limiter = get_rate_limiter(settings.KIS_ENVIRONMENT == "vts")
        await limiter.acquire()

        async def _fetch() -> dict[str, Any]:
            token = await self._get_access_token()
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{_KIS_REAL_BASE}/uapi/domestic-stock/v1/quotations/inquire-price",
                    headers={
                        "tr_id": "FHKST01010100",
                        "appkey": settings.KIS_APP_KEY,
                        "appsecret": settings.KIS_APP_SECRET,
                        "Authorization": f"Bearer {token}",
                    },
                    params={"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": symbol},
                    timeout=10,
                )
                resp.raise_for_status()
                data = resp.json()

            if data.get("rt_cd") != "0":
                raise ValueError(f"KIS API 오류: {data.get('msg1')}")
            d = data["output"]
            return {
                "symbol": symbol,
                "price": float(d["stck_prpr"]),
                "change": float(d["prdy_vrss"]),
                "change_rate": float(d["prdy_ctrt"]),
                "volume": int(d["acml_vol"]),
                "high": float(d["stck_hgpr"]),
                "low": float(d["stck_lwpr"]),
                "open": float(d["stck_oprc"]),
            }

        try:
            return await retry_with_backoff(_fetch)
        except Exception as exc:
            logger.error("현재가 조회 실패 [%s]: %s", symbol, exc)
            raise

    async def get_chart(self, symbol: str, period: str = "day", count: int = 30) -> list[dict[str, Any]] | None:
        """주식 차트 데이터(OHLCV)를 조회한다 (KIS REST API 직접 호출).
        시세 데이터는 실전 서버에서만 제공된다.
        period: "day" → "D", "week" → "W", "month" → "M"
        """
        if not self.is_available():
            return None

        from app.core.config import settings
        import datetime
        _PERIOD_MAP = {"day": "D", "week": "W", "month": "M"}
        period_code = _PERIOD_MAP.get(period, "D")
        limiter = get_rate_limiter(settings.KIS_ENVIRONMENT == "vts")
        await limiter.acquire()

        async def _fetch() -> list[dict[str, Any]]:
            today = datetime.date.today().strftime("%Y%m%d")
            token = await self._get_access_token()
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{_KIS_REAL_BASE}/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice",
                    headers={
                        "tr_id": "FHKST03010100",
                        "appkey": settings.KIS_APP_KEY,
                        "appsecret": settings.KIS_APP_SECRET,
                        "Authorization": f"Bearer {token}",
                    },
                    params={
                        "FID_COND_MRKT_DIV_CODE": "J",
                        "FID_INPUT_ISCD": symbol,
                        "FID_INPUT_DATE_1": "19000101",
                        "FID_INPUT_DATE_2": today,
                        "FID_PERIOD_DIV_CODE": period_code,
                        "FID_ORG_ADJ_PRC": "0",
                    },
                    timeout=10,
                )
                resp.raise_for_status()
                data = resp.json()

            if data.get("rt_cd") != "0":
                raise ValueError(f"KIS API 오류: {data.get('msg1')}")
            items = data.get("output2", [])
            return [
                {
                    "date": item["stck_bsop_date"],
                    "open": float(item["stck_oprc"]),
                    "high": float(item["stck_hgpr"]),
                    "low": float(item["stck_lwpr"]),
                    "close": float(item["stck_clpr"]),
                    "volume": int(item["acml_vol"]),
                }
                for item in items[:count]
                if item.get("stck_clpr")
            ]

        try:
            return await retry_with_backoff(_fetch)
        except Exception as exc:
            logger.error("차트 조회 실패 [%s]: %s", symbol, exc)
            raise

    async def get_balance(self) -> dict[str, Any] | None:
        """계좌 잔고를 조회한다 (KIS REST API 직접 호출, rate limit + retry 적용).
        모의투자: VTTC8434R (VTS 서버), 실전투자: TTTC8434R (실전 서버).
        """
        if not self.is_available():
            return None

        from app.core.config import settings
        is_virtual = settings.KIS_ENVIRONMENT == "vts"
        base_url = _KIS_VTS_BASE if is_virtual else _KIS_REAL_BASE
        tr_id = "VTTC8434R" if is_virtual else "TTTC8434R"

        # KIS 계좌번호는 8자리 본계좌 + 상품코드 2자리 (기본 "01")
        account_no = settings.KIS_ACCOUNT_NUMBER
        cano = account_no[:8] if len(account_no) >= 8 else account_no
        acnt_prdt_cd = account_no[8:] if len(account_no) > 8 else "01"

        limiter = get_rate_limiter(is_virtual)
        await limiter.acquire()

        async def _fetch() -> dict[str, Any]:
            token = await self._get_access_token()
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{base_url}/uapi/domestic-stock/v1/trading/inquire-balance",
                    headers={
                        "tr_id": tr_id,
                        "appkey": settings.KIS_APP_KEY,
                        "appsecret": settings.KIS_APP_SECRET,
                        "Authorization": f"Bearer {token}",
                    },
                    params={
                        "CANO": cano,
                        "ACNT_PRDT_CD": acnt_prdt_cd,
                        "AFHR_FLPR_YN": "N",
                        "OFL_YN": "",
                        "INQR_DVSN": "02",
                        "UNPR_DVSN": "01",
                        "FUND_STTL_ICLD_YN": "N",
                        "FNCG_AMT_AUTO_RDPT_YN": "N",
                        "PRCS_DVSN": "00",
                        "CTX_AREA_FK100": "",
                        "CTX_AREA_NK100": "",
                    },
                    timeout=10,
                )
                resp.raise_for_status()
                data = resp.json()

            if data.get("rt_cd") != "0":
                raise ValueError(f"KIS API 오류: {data.get('msg1')}")

            output1 = data.get("output1", [])  # 보유 종목 목록
            output2 = data.get("output2", [{}])  # 계좌 요약
            summary = output2[0] if output2 else {}

            return {
                "cash": float(summary.get("dnca_tot_amt", 0)),  # 예수금 총금액
                "stocks": [
                    {
                        "symbol": item["pdno"],
                        "name": item["prdt_name"],
                        "quantity": int(item["hldg_qty"]),
                        "current_price": float(item["prpr"]),
                        "profit_loss_rate": float(item["evlu_pfls_rt"]),
                    }
                    for item in output1
                    if int(item.get("hldg_qty", 0)) > 0
                ],
            }

        try:
            return await retry_with_backoff(_fetch)
        except Exception as exc:
            logger.error("잔고 조회 실패: %s", exc)
            raise


# 싱글턴 인스턴스
kis_client = KISClient()
