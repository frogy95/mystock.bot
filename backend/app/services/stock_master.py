"""
종목 마스터 서비스 모듈
KRX 전체 종목 목록을 pykrx로 조회하여 Redis에 캐싱하고 검색 기능을 제공한다.
"""
import json
import logging
from typing import List

from app.services.redis_client import get_redis

logger = logging.getLogger("mystock.bot")

# Redis 캐시 키 및 TTL 설정
STOCK_MASTER_KEY = "stock_master:all"
STOCK_MASTER_TTL = 60 * 60 * 24  # 24시간


async def load_stock_master() -> None:
    """
    pykrx로 KRX 종목 목록을 조회하여 Redis에 캐싱한다.
    앱 시작(lifespan)에서 호출된다.
    """
    redis = get_redis()

    # 캐시가 이미 존재하면 스킵
    if await redis.exists(STOCK_MASTER_KEY):
        count = await redis.llen(STOCK_MASTER_KEY)
        logger.info(f"종목 마스터 캐시 존재 (종목 수: {count}), 로드 스킵")
        return

    try:
        from pykrx import stock as krx_stock

        logger.info("pykrx로 KRX 종목 목록 조회 시작")

        # KOSPI + KOSDAQ 종목 조회 (최근 영업일 기준)
        from datetime import date, timedelta
        today = date.today().strftime("%Y%m%d")

        # KOSPI 종목
        kospi_tickers = krx_stock.get_market_ticker_list(today, market="KOSPI")
        # KOSDAQ 종목
        kosdaq_tickers = krx_stock.get_market_ticker_list(today, market="KOSDAQ")

        stocks = []
        for ticker in kospi_tickers:
            name = krx_stock.get_market_ticker_name(ticker)
            stocks.append({"symbol": ticker, "name": name, "market": "KOSPI"})

        for ticker in kosdaq_tickers:
            name = krx_stock.get_market_ticker_name(ticker)
            stocks.append({"symbol": ticker, "name": name, "market": "KOSDAQ"})

        # Redis List에 저장 (JSON 직렬화)
        serialized = [json.dumps(s, ensure_ascii=False) for s in stocks]
        if serialized:
            pipe = redis.pipeline()
            pipe.delete(STOCK_MASTER_KEY)
            pipe.rpush(STOCK_MASTER_KEY, *serialized)
            pipe.expire(STOCK_MASTER_KEY, STOCK_MASTER_TTL)
            await pipe.execute()

        logger.info(f"종목 마스터 캐싱 완료 (KOSPI {len(kospi_tickers)}종목 + KOSDAQ {len(kosdaq_tickers)}종목)")

    except Exception as e:
        logger.warning(f"종목 마스터 로드 실패 (pykrx 오류): {e} - 검색 기능 제한될 수 있음")


async def search_stocks(query: str, limit: int = 20) -> List[dict]:
    """
    종목코드 또는 종목명으로 종목을 검색한다.
    Redis 캐시에서 prefix/contains 방식으로 검색한다.
    """
    if not query.strip():
        return []

    redis = get_redis()
    q = query.strip().lower()

    # 캐시가 없으면 빈 결과 반환
    total = await redis.llen(STOCK_MASTER_KEY)
    if total == 0:
        logger.warning("종목 마스터 캐시 없음, 빈 결과 반환")
        return []

    results = []
    # Redis List에서 전체 조회 후 필터링
    raw_list = await redis.lrange(STOCK_MASTER_KEY, 0, -1)
    for raw in raw_list:
        item = json.loads(raw)
        if q in item["symbol"].lower() or q in item["name"].lower():
            results.append(item)
            if len(results) >= limit:
                break

    return results
