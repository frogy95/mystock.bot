"""
차트 데이터 서비스 모듈
DB 캐시에서 OHLCV 데이터를 조회하고, 부족분을 KIS API 또는 yfinance로 보충한다.
"""
import logging
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.database import AsyncSessionLocal
from app.models.chart_cache import ChartDataCache

logger = logging.getLogger(__name__)


async def get_chart_data(
    symbol: str,
    start_date: date,
    end_date: date,
    warmup_days: int = 80,
) -> list[dict]:
    """
    종목의 일별 OHLCV 데이터를 반환한다.
    DB 캐시를 먼저 조회하고, 미스 시 KIS API(→ 실패 시 yfinance)로 조회 후 DB에 저장한다.

    Returns:
        KIS API 형식의 dict 리스트 (date: "YYYYMMDD", open/high/low/close: float, volume: int)
    """
    # 워밍업 포함 조회 시작일 (캘린더 기준으로 여유있게 계산)
    calendar_buffer = int(warmup_days * 7 / 5) + 10
    fetch_start = start_date - timedelta(days=calendar_buffer)

    async with AsyncSessionLocal() as session:
        # 1. DB 캐시 조회
        stmt = (
            select(ChartDataCache)
            .where(
                ChartDataCache.symbol == symbol,
                ChartDataCache.trade_date >= fetch_start,
                ChartDataCache.trade_date <= end_date,
            )
            .order_by(ChartDataCache.trade_date)
        )
        result = await session.execute(stmt)
        cached = result.scalars().all()

        # 캐시 히트 판단: 예상 거래일의 90% 이상이면 충분하다고 판단
        expected_trading_days = (end_date - fetch_start).days * 5 // 7
        if len(cached) >= max(30, int(expected_trading_days * 0.9)):
            logger.info(
                "차트 캐시 히트 [%s]: DB %d건 반환 (예상 %d건)",
                symbol, len(cached), expected_trading_days,
            )
            return _to_kis_format(cached)

        # 2. 캐시 미스 → 외부 API 조회
        logger.info("차트 캐시 미스 [%s]: 외부 API 조회 시작 (DB %d건)", symbol, len(cached))
        expected = (end_date - fetch_start).days * 5 // 7
        raw_data = await _fetch_from_kis(symbol, fetch_start, end_date)

        # KIS 데이터가 없거나 기대 건수의 70% 미만이면 yfinance로 보충
        if raw_data is None or len(raw_data) < expected * 0.7:
            if raw_data:
                logger.warning(
                    "KIS 데이터 부족 [%s]: %d건/%d건 — yfinance 보충 시도",
                    symbol, len(raw_data), expected,
                )
            else:
                logger.warning("KIS 실패 [%s]: yfinance 폴백 시도", symbol)
            yf_data = _fetch_chart_yfinance(symbol, fetch_start, end_date)
            if yf_data and len(yf_data) > len(raw_data or []):
                raw_data = yf_data

        if not raw_data:
            # 외부 API 모두 실패 시 캐시 데이터라도 반환
            logger.warning("외부 API 전부 실패 [%s]: 캐시 데이터 %d건 반환", symbol, len(cached))
            return _to_kis_format(cached)

        # 3. DB UPSERT
        await _upsert_chart_data(session, symbol, raw_data)
        await session.commit()

        # 4. DB에서 최종 조회하여 반환
        result = await session.execute(stmt)
        final = result.scalars().all()
        logger.info("차트 데이터 저장 완료 [%s]: %d건", symbol, len(final))
        return _to_kis_format(final)


async def _fetch_from_kis(symbol: str, start_date: date, end_date: date) -> list[dict] | None:
    """KIS API로 차트 데이터를 조회한다. 실패 시 None 반환."""
    from app.services.kis_client import kis_client

    if not kis_client.is_available():
        logger.info("KIS API 미설정 [%s]: yfinance 폴백", symbol)
        return None

    trading_days = (end_date - start_date).days * 5 // 7 + 10
    warmup_extra = 100  # 워밍업 여유분
    count = trading_days + warmup_extra

    return await kis_client.get_chart(symbol, period="day", count=count)


def _fetch_chart_yfinance(symbol: str, start_date: date, end_date: date) -> list[dict] | None:
    """yfinance로 차트 데이터를 조회한다. 실패 시 None 반환."""
    try:
        import yfinance as yf
        import pandas as pd
    except ImportError:
        logger.error("yfinance가 설치되지 않았습니다")
        return None

    # .KS(코스피) → .KQ(코스닥) 순서로 시도
    tickers_to_try = [f"{symbol}.KS", f"{symbol}.KQ"]

    for ticker_symbol in tickers_to_try:
        try:
            ticker = yf.Ticker(ticker_symbol)
            df = ticker.history(
                start=start_date.strftime("%Y-%m-%d"),
                end=(end_date + timedelta(days=1)).strftime("%Y-%m-%d"),
                auto_adjust=True,
            )

            if df is None or df.empty:
                continue

            # MultiIndex 컬럼 처리
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # KIS API 형식으로 변환
            result = []
            for idx, row in df.iterrows():
                trade_date = idx.date() if hasattr(idx, "date") else idx
                result.append({
                    "date": trade_date.strftime("%Y%m%d"),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]),
                    "_source": "yfinance",
                })

            logger.info("yfinance 조회 완료 [%s → %s]: %d건", symbol, ticker_symbol, len(result))
            return result

        except Exception as exc:
            logger.warning("yfinance 조회 실패 [%s]: %s", ticker_symbol, exc)
            continue

    logger.error("yfinance 전체 실패 [%s]", symbol)
    return None


async def _upsert_chart_data(session, symbol: str, raw_data: list[dict]) -> None:
    """차트 데이터를 DB에 UPSERT한다."""
    if not raw_data:
        return

    rows = []
    for item in raw_data:
        date_str = item["date"]
        if len(date_str) == 8:
            trade_date = date(int(date_str[:4]), int(date_str[4:6]), int(date_str[6:8]))
        else:
            continue

        source = item.get("_source", "kis")
        rows.append({
            "symbol": symbol,
            "trade_date": trade_date,
            "open": float(item["open"]),
            "high": float(item["high"]),
            "low": float(item["low"]),
            "close": float(item["close"]),
            "volume": int(item["volume"]),
            "source": source,
        })

    if not rows:
        return

    stmt = pg_insert(ChartDataCache).values(rows)
    stmt = stmt.on_conflict_do_update(
        constraint="uq_chart_symbol_date",
        set_={col: stmt.excluded[col] for col in ["open", "high", "low", "close", "volume", "source"]},
    )
    await session.execute(stmt)


def _to_kis_format(cached: list[ChartDataCache]) -> list[dict]:
    """DB 캐시 레코드를 KIS API 형식의 dict 리스트로 변환한다."""
    return [
        {
            "date": row.trade_date.strftime("%Y%m%d"),
            "open": float(row.open),
            "high": float(row.high),
            "low": float(row.low),
            "close": float(row.close),
            "volume": int(row.volume),
        }
        for row in cached
    ]
