"""
종목 API 통합 테스트
GET /api/v1/stocks/search - 종목 검색
GET /api/v1/stocks/balance - 계좌 잔고
GET /api/v1/stocks/quote/{symbol} - 시세
"""
import pytest


@pytest.mark.asyncio
async def test_search_requires_query(client_with_user):
    """종목 검색 - q 파라미터 없으면 422"""
    response = await client_with_user.get("/api/v1/stocks/search")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_balance_returns_valid_status(client_with_user):
    """계좌 잔고 - KIS 설정 여부에 따라 200 또는 503 반환"""
    response = await client_with_user.get("/api/v1/stocks/balance")
    assert response.status_code in (200, 503)


@pytest.mark.asyncio
async def test_quote_returns_valid_status(client_with_user):
    """시세 조회 - KIS 설정 여부에 따라 200 또는 503 반환"""
    response = await client_with_user.get("/api/v1/stocks/005930/quote")
    assert response.status_code in (200, 503)
