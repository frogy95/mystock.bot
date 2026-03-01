"""
주식 관련 API 엔드포인트
현재가, 차트, 잔고 조회를 제공한다.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.schemas.stock import BalanceResponse, StockChartResponse, StockQuoteResponse
from app.services.kis_client import kis_client

router = APIRouter()


@router.get("/{symbol}/quote", response_model=StockQuoteResponse, summary="현재가 조회")
async def get_stock_quote(symbol: str):
    """주식 심볼의 현재가를 조회한다."""
    if not kis_client.is_available():
        raise HTTPException(status_code=503, detail="KIS API가 설정되지 않았습니다.")

    result = await kis_client.get_quote(symbol)
    if result is None:
        raise HTTPException(status_code=404, detail=f"종목 {symbol}을 찾을 수 없습니다.")
    return result


@router.get("/{symbol}/chart", response_model=StockChartResponse, summary="차트 데이터 조회")
async def get_stock_chart(
    symbol: str,
    period: str = Query(default="day", description="조회 주기 (day/week/month)"),
    count: int = Query(default=30, ge=1, le=200, description="조회 건수"),
):
    """주식 심볼의 OHLCV 차트 데이터를 조회한다."""
    if not kis_client.is_available():
        raise HTTPException(status_code=503, detail="KIS API가 설정되지 않았습니다.")

    data = await kis_client.get_chart(symbol, period=period, count=count)
    if data is None:
        raise HTTPException(status_code=404, detail=f"종목 {symbol}의 차트 데이터를 찾을 수 없습니다.")
    return {"symbol": symbol, "period": period, "data": data}


@router.get("/balance", response_model=BalanceResponse, summary="계좌 잔고 조회")
async def get_balance():
    """계좌 잔고(현금 + 보유종목)를 조회한다."""
    if not kis_client.is_available():
        raise HTTPException(status_code=503, detail="KIS API가 설정되지 않았습니다.")

    result = await kis_client.get_balance()
    if result is None:
        raise HTTPException(status_code=503, detail="잔고 조회에 실패했습니다.")
    return result
