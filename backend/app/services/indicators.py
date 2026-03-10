"""
기술적 분석 지표 엔진
pandas-ta를 사용하여 OHLCV 데이터에 기술적 지표를 계산한다.
Redis를 통한 5분 TTL 캐싱을 적용한다.
"""
import json
import logging
from typing import Any, Optional

import pandas as pd

from app.services.kis_client import kis_client
from app.services.redis_client import get_redis

# 시장 데이터 캐시 TTL (24시간)
_MARKET_TTL = 86400

logger = logging.getLogger("mystock.bot")

# 지표 캐시 TTL (5분)
_INDICATOR_TTL = 300


def _ohlcv_to_df(chart_data: list[dict]) -> pd.DataFrame:
    """KIS 차트 데이터 리스트를 pandas DataFrame으로 변환한다."""
    df = pd.DataFrame(chart_data)
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
    df = df.sort_values("date").reset_index(drop=True)
    df = df.rename(columns={
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume",
    })
    return df


def _calculate_indicators(df: pd.DataFrame) -> dict[str, Any]:
    """
    DataFrame에 기술적 지표를 계산하여 반환한다.
    최신 행(마지막 행) 기준의 지표값을 딕셔너리로 반환한다.
    """
    try:
        import pandas_ta as ta
    except ImportError:
        logger.warning("pandas_ta 미설치. 지표 계산 불가.")
        return {}

    if len(df) < 5:
        return {}

    # SMA (이동평균선)
    df.ta.sma(length=20, append=True)
    df.ta.sma(length=60, append=True)

    # EMA (지수이동평균)
    df.ta.ema(length=12, append=True)
    df.ta.ema(length=26, append=True)

    # RSI (상대강도지수)
    df.ta.rsi(length=14, append=True)

    # MACD
    df.ta.macd(fast=12, slow=26, signal=9, append=True)

    # 볼린저밴드
    df.ta.bbands(length=20, std=2, append=True)

    # ATR (평균진폭)
    df.ta.atr(length=14, append=True)

    # 거래량 비율 (현재 거래량 / 20일 평균 거래량)
    df["VOL_RATIO_20"] = df["Volume"] / df["Volume"].rolling(20).mean()

    # 모멘텀 (20일, 60일 수익률 %)
    df["MOMENTUM_20"] = df["Close"].pct_change(20) * 100
    df["MOMENTUM_60"] = df["Close"].pct_change(60) * 100

    # SMA(60) 5일 기울기 (상승/하락 추세 판단용)
    df["SMA60_SLOPE"] = df["SMA_60"].diff(5)

    last = df.iloc[-1]

    def safe_float(val) -> Optional[float]:
        """NaN을 None으로 변환한다."""
        if pd.isna(val):
            return None
        return round(float(val), 4)

    return {
        "sma_20": safe_float(last.get("SMA_20")),
        "sma_60": safe_float(last.get("SMA_60")),
        "ema_12": safe_float(last.get("EMA_12")),
        "ema_26": safe_float(last.get("EMA_26")),
        "rsi_14": safe_float(last.get("RSI_14")),
        "macd": safe_float(last.get("MACD_12_26_9")),
        "macd_signal": safe_float(last.get("MACDs_12_26_9")),
        "macd_hist": safe_float(last.get("MACDh_12_26_9")),
        "bb_upper": safe_float(last.get("BBU_20_2.0")),
        "bb_mid": safe_float(last.get("BBM_20_2.0")),
        "bb_lower": safe_float(last.get("BBL_20_2.0")),
        "atr_14": safe_float(last.get("ATRr_14")),
        "vol_ratio_20": safe_float(last.get("VOL_RATIO_20")),
        "momentum_20": safe_float(last.get("MOMENTUM_20")),
        "momentum_60": safe_float(last.get("MOMENTUM_60")),
        "sma60_slope": safe_float(last.get("SMA60_SLOPE")),
        "close": safe_float(last.get("Close")),
        "volume": int(last.get("Volume", 0)),
    }


async def get_indicators(symbol: str, period: str = "day", count: int = 90) -> dict[str, Any]:
    """
    종목의 기술적 지표를 계산하여 반환한다.
    Redis 캐시(5분 TTL)를 우선 조회한다.
    """
    cache_key = f"indicators:{symbol}:{period}"
    redis = get_redis()

    # 캐시 조회
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # KIS API에서 차트 데이터 조회
    if not kis_client.is_available():
        logger.warning(f"KIS API 미설정. 종목 {symbol} 지표 계산 불가.")
        return {}

    chart_data = await kis_client.get_chart(symbol, period=period, count=count)
    if not chart_data:
        return {}

    # DataFrame 변환 및 지표 계산
    df = _ohlcv_to_df(chart_data)
    result = _calculate_indicators(df)
    result["symbol"] = symbol

    # 캐시 저장
    if result:
        await redis.setex(cache_key, _INDICATOR_TTL, json.dumps(result))

    return result


def get_indicators_from_df(df: pd.DataFrame) -> dict[str, Any]:
    """
    이미 로드된 DataFrame에서 지표를 계산한다. (백테스팅용 동기 버전)
    """
    return _calculate_indicators(df.copy())


def calculate_beta(
    stock_returns: pd.Series,
    market_returns: pd.Series,
    shrinkage_w: float = 0.5,
) -> float:
    """
    Vasicek 수축 기법으로 베타를 추정한다.
    raw_beta를 시장 베타(1.0) 방향으로 shrinkage_w 비율만큼 수축한다.
    """
    if len(stock_returns) < 5 or len(market_returns) < 5:
        return 1.0
    market_var = market_returns.var()
    if market_var == 0:
        return 1.0
    raw_beta = float(stock_returns.cov(market_returns) / market_var)
    # Vasicek 수축: w * raw_beta + (1-w) * 1.0
    return shrinkage_w * raw_beta + (1 - shrinkage_w) * 1.0


async def get_market_returns(period_days: int = 120) -> Optional[pd.Series]:
    """
    KOSPI(^KS11) 일별 수익률 Series를 반환한다.
    Redis 24시간 캐싱을 적용한다. 실패 시 None 반환.
    """
    cache_key = f"market_returns:kospi:{period_days}"
    redis = get_redis()

    cached = await redis.get(cache_key)
    if cached:
        data = json.loads(cached)
        series = pd.Series(data["returns"], index=pd.to_datetime(data["index"]))
        return series

    try:
        import yfinance as yf
        import asyncio
        from datetime import date, timedelta

        end_date = date.today()
        start_date = end_date - timedelta(days=period_days + 30)
        loop = asyncio.get_event_loop()
        raw = await loop.run_in_executor(
            None,
            lambda: yf.download(
                "^KS11",
                start=str(start_date),
                end=str(end_date),
                progress=False,
                auto_adjust=True,
            ),
        )
        if raw is None or len(raw) < 5:
            return None
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
        prices = raw["Close"].dropna()
        returns = prices.pct_change().dropna()
        # Redis에 저장
        payload = json.dumps({
            "index": [str(d.date()) for d in returns.index],
            "returns": returns.tolist(),
        })
        await redis.setex(cache_key, _MARKET_TTL, payload)
        return returns
    except Exception as e:
        logger.warning(f"KOSPI 수익률 조회 실패: {e}")
        return None
