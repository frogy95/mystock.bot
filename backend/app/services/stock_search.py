"""
글로벌 종목 검색 서비스
- 한글 쿼리: KRX 인메모리 dict 직접 검색 (yfinance가 한글 미지원)
- 영문/숫자 쿼리: yfinance Search API → 전세계 시장 검색 + KRX 한국어 이름 매핑
"""
import asyncio
import json
import logging
import re
from typing import List, Optional

from app.services.redis_client import get_redis
from app.services.krx_names import get_korean_name, get_market, search_krx_by_name

# 한글 유니코드 범위: 한글 자모(ㄱ~ㅣ) + 한글 음절(가~힣)
_KOREAN_RE = re.compile(r"[\uAC00-\uD7A3\u3131-\u3163\u3165-\u318E]")

logger = logging.getLogger("mystock.bot")

_CACHE_PREFIX = "stock_search:"
_CACHE_TTL = 60 * 5  # 5분


def _yfinance_search(query: str, limit: int) -> list:
    """yfinance Search를 동기 방식으로 실행한다 (to_thread에서 호출)."""
    try:
        import yfinance as yf

        search = yf.Search(query, max_results=limit)
        return getattr(search, "quotes", None) or []
    except Exception as e:
        logger.warning(f"yfinance 검색 실패 (query={query!r}): {e}")
        return []


def _normalize_quote(quote: dict) -> Optional[dict]:
    """
    yfinance 검색 결과 항목을 {symbol, name, market} 형태로 정규화한다.
    KRX 종목(.KS/.KQ)은 한국어 이름과 시장 정보를 적용한다.
    """
    symbol: str = quote.get("symbol", "")
    if not symbol:
        return None

    name: str = quote.get("longname") or quote.get("shortname") or symbol
    exchange: str = quote.get("exchange", "")

    if symbol.endswith(".KS"):
        # KOSPI 종목: 접미사 제거 후 한국어 이름 매핑
        code = symbol[:-3]
        korean_name = get_korean_name(code)
        market = get_market(code) or "KOSPI"
        return {"symbol": code, "name": korean_name or name, "market": market}

    if symbol.endswith(".KQ"):
        # KOSDAQ 종목: 접미사 제거 후 한국어 이름 매핑
        code = symbol[:-3]
        korean_name = get_korean_name(code)
        market = get_market(code) or "KOSDAQ"
        return {"symbol": code, "name": korean_name or name, "market": market}

    # 글로벌 종목: exchange를 market으로 사용
    return {"symbol": symbol, "name": name, "market": exchange}


async def search_stocks(query: str, limit: int = 20) -> List[dict]:
    """
    종목코드 또는 종목명으로 글로벌 종목을 검색한다.
    - 한글 포함 쿼리: KRX 인메모리 dict 직접 검색
    - 영문/숫자 쿼리: yfinance Search → KRX 한국어 이름 매핑
    - Redis 5분 TTL 캐시 적용
    """
    query = query.strip()
    if not query:
        return []

    # Redis 캐시 확인
    redis = get_redis()
    cache_key = f"{_CACHE_PREFIX}{query.lower()}"
    try:
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception:
        pass

    # 한글 포함 여부에 따라 검색 경로 분기
    if _KOREAN_RE.search(query):
        # 한글 쿼리: yfinance가 한글 미지원 → KRX 인메모리 dict 직접 검색
        results = search_krx_by_name(query, limit)
    else:
        # 영문/숫자 쿼리: yfinance Search (블로킹 동기 → 스레드풀)
        raw_quotes: list = await asyncio.to_thread(_yfinance_search, query, limit)
        results = []
        seen: set[str] = set()
        for quote in raw_quotes:
            item = _normalize_quote(quote)
            if item and item["symbol"] not in seen:
                seen.add(item["symbol"])
                results.append(item)

    # Redis 캐시 저장
    try:
        await redis.setex(
            cache_key, _CACHE_TTL, json.dumps(results, ensure_ascii=False)
        )
    except Exception:
        pass

    return results
