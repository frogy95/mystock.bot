"""
주식 관련 Pydantic 스키마
"""
from __future__ import annotations

from pydantic import BaseModel


class StockQuoteResponse(BaseModel):
    """현재가 응답 스키마"""

    symbol: str
    price: float
    change: float
    change_rate: float
    volume: int
    high: float
    low: float
    open: float


class OHLCVItem(BaseModel):
    """OHLCV 차트 데이터 항목"""

    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class StockChartResponse(BaseModel):
    """차트 응답 스키마"""

    symbol: str
    period: str
    data: list[OHLCVItem]


class StockHolding(BaseModel):
    """보유 종목 항목"""

    symbol: str
    name: str
    quantity: int
    current_price: float
    profit_loss_rate: float


class BalanceResponse(BaseModel):
    """잔고 응답 스키마"""

    cash: float
    stocks: list[StockHolding]
