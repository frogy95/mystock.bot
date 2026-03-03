"""
KIS (한국투자증권) API 클라이언트 서비스
httpx를 사용하여 KIS REST API를 직접 호출하는 싱글턴 클래스.

듀얼 환경 설계:
- 시세 API (get_quote, get_chart, get_market_index): 항상 실전 키 + 실전 서버
- 주문/잔고 API (get_balance, place_order, get_order_status): KIS_ENVIRONMENT에 따라 선택
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

# 메모리 토큰 캐시 (앱 키별로 분리 관리)
_token_cache: dict[str, Any] = {}


class KISClient:
    """KIS API 싱글턴 클라이언트 (httpx 직접 호출 방식)"""

    _instance: "KISClient | None" = None

    def __new__(cls) -> "KISClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # 실전/모의 서버별 공유 httpx 클라이언트 (lazy 초기화)
            cls._instance._real_client: httpx.AsyncClient | None = None
            cls._instance._vts_client: httpx.AsyncClient | None = None
        return cls._instance

    def _get_http_client(self, base_url: str) -> httpx.AsyncClient:
        """기본 URL에 맞는 공유 httpx 클라이언트를 반환한다 (lazy 초기화)."""
        if base_url == _KIS_REAL_BASE:
            if self._real_client is None or self._real_client.is_closed:
                self._real_client = httpx.AsyncClient()
            return self._real_client
        else:
            if self._vts_client is None or self._vts_client.is_closed:
                self._vts_client = httpx.AsyncClient()
            return self._vts_client

    async def close(self) -> None:
        """연결 풀을 닫는다. 앱 종료 시 호출."""
        if self._real_client and not self._real_client.is_closed:
            await self._real_client.aclose()
        if self._vts_client and not self._vts_client.is_closed:
            await self._vts_client.aclose()

    def is_available(self) -> bool:
        """KIS API 클라이언트 사용 가능 여부를 반환한다.
        시세 API용 실전 키와 주문/잔고용 키(환경에 따라)가 모두 설정되어야 한다.
        """
        from app.core.config import settings
        is_virtual = settings.KIS_ENVIRONMENT == "vts"

        # 시세 API용 실전 키는 항상 필요
        real_keys_ok = bool(settings.KIS_REAL_APP_KEY and settings.KIS_REAL_APP_SECRET)

        # 주문/잔고용 키: 환경에 따라 확인
        if is_virtual:
            trade_keys_ok = bool(
                settings.KIS_VTS_APP_KEY
                and settings.KIS_VTS_APP_SECRET
                and settings.KIS_VTS_ACCOUNT_NUMBER
            )
        else:
            trade_keys_ok = bool(
                settings.KIS_REAL_APP_KEY
                and settings.KIS_REAL_APP_SECRET
                and settings.KIS_REAL_ACCOUNT_NUMBER
            )

        return real_keys_ok and trade_keys_ok

    def is_quote_available(self) -> bool:
        """시세 조회 가능 여부 (실전 키만 필요)."""
        from app.core.config import settings
        return bool(settings.KIS_REAL_APP_KEY and settings.KIS_REAL_APP_SECRET)

    async def _get_access_token(self, env: str = "real") -> str:
        """지정된 환경의 KIS OAuth 액세스 토큰을 발급/캐싱한다.
        env: "vts" → 모의투자 키 사용, "real" → 실전 키 사용
        토큰은 앱 키별로 분리 캐싱된다.
        """
        import time
        from app.core.config import settings

        if env == "vts":
            app_key = settings.KIS_VTS_APP_KEY
            app_secret = settings.KIS_VTS_APP_SECRET
            base_url = _KIS_VTS_BASE
        else:
            app_key = settings.KIS_REAL_APP_KEY
            app_secret = settings.KIS_REAL_APP_SECRET
            base_url = _KIS_REAL_BASE

        cache_key = app_key
        cached = _token_cache.get(cache_key)
        if cached and cached["expires_at"] > time.time() + 60:
            return cached["token"]

        client = self._get_http_client(base_url)
        resp = await client.post(
            f"{base_url}/oauth2/tokenP",
            json={
                "grant_type": "client_credentials",
                "appkey": app_key,
                "appsecret": app_secret,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        token = data["access_token"]
        expires_in = int(data.get("expires_in", 86400))
        _token_cache[cache_key] = {"token": token, "expires_at": time.time() + expires_in}
        logger.info("KIS 액세스 토큰 발급 완료 [%s] (유효기간: %d초)", env, expires_in)
        return token

    def _get_trade_env(self) -> str:
        """주문/잔고 API에 사용할 환경 코드를 반환한다."""
        from app.core.config import settings
        return "vts" if settings.KIS_ENVIRONMENT == "vts" else "real"

    def _get_trade_credentials(self) -> tuple[str, str, str, str, str, str]:
        """주문/잔고 API용 자격증명과 서버 URL, TR-ID 접두사를 반환한다.
        Returns: (app_key, app_secret, cano, acnt_prdt_cd, base_url, tr_prefix)
        """
        from app.core.config import settings
        is_virtual = settings.KIS_ENVIRONMENT == "vts"

        if is_virtual:
            account_no = settings.KIS_VTS_ACCOUNT_NUMBER
            cano = account_no[:8] if len(account_no) >= 8 else account_no
            acnt_prdt_cd = account_no[8:] if len(account_no) > 8 else "01"
            return (
                settings.KIS_VTS_APP_KEY,
                settings.KIS_VTS_APP_SECRET,
                cano,
                acnt_prdt_cd,
                _KIS_VTS_BASE,
                "V",  # 모의: VTTC...
            )
        else:
            account_no = settings.KIS_REAL_ACCOUNT_NUMBER
            cano = account_no[:8] if len(account_no) >= 8 else account_no
            acnt_prdt_cd = account_no[8:] if len(account_no) > 8 else "01"
            return (
                settings.KIS_REAL_APP_KEY,
                settings.KIS_REAL_APP_SECRET,
                cano,
                acnt_prdt_cd,
                _KIS_REAL_BASE,
                "T",  # 실전: TTTC...
            )

    async def get_quote(self, symbol: str) -> dict[str, Any] | None:
        """주식 현재가를 조회한다 (항상 실전 서버 + 실전 키 사용).
        시세 데이터는 모의투자 환경과 무관하게 실전 서버에서만 제공된다.
        """
        if not self.is_quote_available():
            return None

        from app.core.config import settings
        limiter = get_rate_limiter(is_virtual=False)  # 시세 = 항상 실전 Rate Limiter
        await limiter.acquire()

        async def _fetch() -> dict[str, Any]:
            token = await self._get_access_token("real")
            client = self._get_http_client(_KIS_REAL_BASE)
            resp = await client.get(
                f"{_KIS_REAL_BASE}/uapi/domestic-stock/v1/quotations/inquire-price",
                headers={
                    "tr_id": "FHKST01010100",
                    "appkey": settings.KIS_REAL_APP_KEY,
                    "appsecret": settings.KIS_REAL_APP_SECRET,
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
        """주식 차트 데이터(OHLCV)를 조회한다 (항상 실전 서버 + 실전 키 사용).
        period: "day" → "D", "week" → "W", "month" → "M"
        """
        if not self.is_quote_available():
            return None

        from app.core.config import settings
        import datetime
        _PERIOD_MAP = {"day": "D", "week": "W", "month": "M"}
        period_code = _PERIOD_MAP.get(period, "D")
        limiter = get_rate_limiter(is_virtual=False)  # 시세 = 항상 실전 Rate Limiter
        await limiter.acquire()

        async def _fetch() -> list[dict[str, Any]]:
            today = datetime.date.today().strftime("%Y%m%d")
            token = await self._get_access_token("real")
            client = self._get_http_client(_KIS_REAL_BASE)
            resp = await client.get(
                f"{_KIS_REAL_BASE}/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice",
                headers={
                    "tr_id": "FHKST03010100",
                    "appkey": settings.KIS_REAL_APP_KEY,
                    "appsecret": settings.KIS_REAL_APP_SECRET,
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
        """계좌 잔고를 조회한다.
        KIS_ENVIRONMENT에 따라 모의(VTTC8434R) 또는 실전(TTTC8434R) 서버 사용.
        """
        if not self.is_available():
            return None

        trade_env = self._get_trade_env()
        app_key, app_secret, cano, acnt_prdt_cd, base_url, tr_prefix = self._get_trade_credentials()
        tr_id = f"{tr_prefix}TTC8434R"
        is_virtual = trade_env == "vts"

        limiter = get_rate_limiter(is_virtual=is_virtual)
        await limiter.acquire()

        async def _fetch() -> dict[str, Any]:
            token = await self._get_access_token(trade_env)
            client = self._get_http_client(base_url)
            resp = await client.get(
                f"{base_url}/uapi/domestic-stock/v1/trading/inquire-balance",
                headers={
                    "tr_id": tr_id,
                    "appkey": app_key,
                    "appsecret": app_secret,
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
                        "avg_price": float(item.get("pchs_avg_pric", 0)),  # 매입평균가
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

    async def place_order(
        self,
        symbol: str,
        order_type: str,
        quantity: int,
        price: int = 0,
    ) -> dict[str, Any] | None:
        """KIS API로 매수/매도 주문을 실행한다.
        order_type: "buy" | "sell"
        price: 0 이면 시장가 주문
        KIS_ENVIRONMENT에 따라 모의(VTTC0802U/VTTC0801U) 또는 실전(TTTC0802U/TTTC0801U) 사용.
        """
        if not self.is_available():
            return None

        trade_env = self._get_trade_env()
        app_key, app_secret, cano, acnt_prdt_cd, base_url, tr_prefix = self._get_trade_credentials()
        is_virtual = trade_env == "vts"

        if order_type == "buy":
            tr_id = f"{tr_prefix}TTC0802U"
        else:
            tr_id = f"{tr_prefix}TTC0801U"

        # 지정가: "00", 시장가: "01"
        ord_dvsn = "01" if price == 0 else "00"
        ord_price = "0" if price == 0 else str(price)

        limiter = get_rate_limiter(is_virtual=is_virtual)
        await limiter.acquire()

        async def _fetch() -> dict[str, Any]:
            token = await self._get_access_token(trade_env)
            client = self._get_http_client(base_url)
            resp = await client.post(
                f"{base_url}/uapi/domestic-stock/v1/trading/order-cash",
                headers={
                    "tr_id": tr_id,
                    "appkey": app_key,
                    "appsecret": app_secret,
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json={
                    "CANO": cano,
                    "ACNT_PRDT_CD": acnt_prdt_cd,
                    "PDNO": symbol,
                    "ORD_DVSN": ord_dvsn,
                    "ORD_QTY": str(quantity),
                    "ORD_UNPR": ord_price,
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()

            if data.get("rt_cd") != "0":
                raise ValueError(f"KIS 주문 오류: {data.get('msg1')}")

            output = data.get("output", {})
            return {
                "order_no": output.get("ODNO", ""),
                "order_time": output.get("ORD_TMD", ""),
                "symbol": symbol,
                "order_type": order_type,
                "quantity": quantity,
                "price": price,
            }

        try:
            return await retry_with_backoff(_fetch)
        except Exception as exc:
            logger.error("주문 실행 실패 [%s %s]: %s", order_type, symbol, exc)
            raise

    async def get_market_index(self, index_code: str) -> dict[str, Any] | None:
        """업종 현재가(시장 지수)를 조회한다 (항상 실전 서버 + 실전 키 사용).
        index_code: '0001'=KOSPI, '1001'=KOSDAQ
        """
        if not self.is_quote_available():
            return None

        from app.core.config import settings
        limiter = get_rate_limiter(is_virtual=False)  # 시세 = 항상 실전 Rate Limiter
        await limiter.acquire()

        async def _fetch() -> dict[str, Any]:
            token = await self._get_access_token("real")
            client = self._get_http_client(_KIS_REAL_BASE)
            resp = await client.get(
                f"{_KIS_REAL_BASE}/uapi/domestic-stock/v1/quotations/inquire-index-price",
                headers={
                    "tr_id": "FHPUP02100000",
                    "appkey": settings.KIS_REAL_APP_KEY,
                    "appsecret": settings.KIS_REAL_APP_SECRET,
                    "Authorization": f"Bearer {token}",
                },
                params={
                    "FID_COND_MRKT_DIV_CODE": "U",
                    "FID_INPUT_ISCD": index_code,
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()

            if data.get("rt_cd") != "0":
                raise ValueError(f"KIS API 오류: {data.get('msg1')}")
            d = data["output"]
            name_map = {"0001": "KOSPI", "1001": "KOSDAQ"}
            return {
                "index_code": index_code,
                "name": name_map.get(index_code, index_code),
                "current_value": float(d.get("bstp_nmix_prpr", 0)),
                "change_value": float(d.get("bstp_nmix_prdy_vrss", 0)),
                "change_rate": float(d.get("bstp_nmix_prdy_ctrt", 0)),
            }

        try:
            return await retry_with_backoff(_fetch)
        except Exception as exc:
            logger.error("시장 지수 조회 실패 [%s]: %s", index_code, exc)
            return None

    async def get_order_status(self, order_no: str) -> dict[str, Any] | None:
        """주문 체결 상태를 조회한다.
        KIS_ENVIRONMENT에 따라 모의(VTTC8001R) 또는 실전(TTTC8001R) 서버 사용.
        """
        if not self.is_available():
            return None

        trade_env = self._get_trade_env()
        app_key, app_secret, cano, acnt_prdt_cd, base_url, tr_prefix = self._get_trade_credentials()
        tr_id = f"{tr_prefix}TTC8001R"
        is_virtual = trade_env == "vts"

        limiter = get_rate_limiter(is_virtual=is_virtual)
        await limiter.acquire()

        async def _fetch() -> dict[str, Any]:
            token = await self._get_access_token(trade_env)
            client = self._get_http_client(base_url)
            resp = await client.get(
                f"{base_url}/uapi/domestic-stock/v1/trading/inquire-daily-ccld",
                headers={
                    "tr_id": tr_id,
                    "appkey": app_key,
                    "appsecret": app_secret,
                    "Authorization": f"Bearer {token}",
                },
                params={
                    "CANO": cano,
                    "ACNT_PRDT_CD": acnt_prdt_cd,
                    "INQR_STRT_DT": "19000101",
                    "INQR_END_DT": "99991231",
                    "SLL_BUY_DVSN_CD": "00",
                    "INQR_DVSN": "01",
                    "PDNO": "",
                    "CCLD_DVSN": "00",
                    "ORD_GNO_BRNO": "",
                    "ODNO": order_no,
                    "INQR_DVSN_3": "00",
                    "INQR_DVSN_1": "",
                    "CTX_AREA_FK100": "",
                    "CTX_AREA_NK100": "",
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()

            if data.get("rt_cd") != "0":
                raise ValueError(f"KIS API 오류: {data.get('msg1')}")

            items = data.get("output1", [])
            if not items:
                return {"order_no": order_no, "status": "unknown"}

            item = items[0]
            return {
                "order_no": order_no,
                "status": "filled" if item.get("rmn_qty", "0") == "0" else "pending",
                "filled_qty": int(item.get("tot_ccld_qty", 0)),
                "filled_price": float(item.get("avg_prvs", 0)),
            }

        try:
            return await retry_with_backoff(_fetch)
        except Exception as exc:
            logger.error("주문 조회 실패 [%s]: %s", order_no, exc)
            raise


# 싱글턴 인스턴스
kis_client = KISClient()
