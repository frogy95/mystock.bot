"""
주식 관련 API 엔드포인트
종목 검색, 현재가, 차트, 잔고 조회를 제공한다.
"""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import get_current_user, is_demo_user
from app.models.user import User
from app.services.demo_data import (
    get_demo_balance,
    get_demo_market_index,
    get_demo_stock_chart,
    get_demo_stock_quote,
    get_demo_stock_search,
)
from app.schemas.search import StockSearchResult
from app.schemas.stock import BalanceResponse, StockChartResponse, StockQuoteResponse
from app.services.kis_client import kis_client
from app.services.stock_search import search_stocks

router = APIRouter()


@router.get("/search", response_model=List[StockSearchResult], summary="종목 검색")
async def search(
    q: str = Query(..., min_length=1, description="검색어 (종목코드 또는 종목명)"),
    current_user: User = Depends(get_current_user),
):
    """종목코드 또는 종목명으로 KRX 종목을 검색한다. (Redis 캐시 기반)"""
    if is_demo_user(current_user.username):
        return get_demo_stock_search(q)
    results = await search_stocks(q)
    return results


@router.get("/balance", response_model=BalanceResponse, summary="계좌 잔고 조회")
async def get_balance(current_user: User = Depends(get_current_user)):
    """계좌 잔고(현금 + 보유종목)를 조회한다. (인증 필요)"""
    if is_demo_user(current_user.username):
        return get_demo_balance()
    if not kis_client.is_available():
        raise HTTPException(status_code=503, detail="KIS API가 설정되지 않았습니다.")

    result = await kis_client.get_balance()
    if result is None:
        raise HTTPException(status_code=503, detail="잔고 조회에 실패했습니다.")
    return result


@router.get("/market-index", summary="시장 지수 조회")
async def get_market_index(current_user: User = Depends(get_current_user)):
    """KOSPI, KOSDAQ 지수 현재가를 반환한다. KIS 미설정 시 빈 배열 반환."""
    if is_demo_user(current_user.username):
        return get_demo_market_index()
    if not kis_client.is_available():
        return []

    results = []
    for code in ("0001", "1001"):
        index = await kis_client.get_market_index(code)
        if index:
            results.append(index)
    return results


@router.get("/{symbol}/quote", response_model=StockQuoteResponse, summary="현재가 조회")
async def get_stock_quote(symbol: str, current_user: User = Depends(get_current_user)):
    """주식 심볼의 현재가를 조회한다. (인증 필요)"""
    if is_demo_user(current_user.username):
        return get_demo_stock_quote(symbol)
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
    current_user: User = Depends(get_current_user),
):
    """주식 심볼의 OHLCV 차트 데이터를 조회한다. (인증 필요)"""
    if is_demo_user(current_user.username):
        return get_demo_stock_chart(symbol, period=period, count=count)
    if not kis_client.is_available():
        raise HTTPException(status_code=503, detail="KIS API가 설정되지 않았습니다.")

    data = await kis_client.get_chart(symbol, period=period, count=count)
    if data is None:
        raise HTTPException(status_code=404, detail=f"종목 {symbol}의 차트 데이터를 찾을 수 없습니다.")
    return {"symbol": symbol, "period": period, "data": data}
