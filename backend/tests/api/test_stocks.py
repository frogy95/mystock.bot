"""
종목 API 통합 테스트
GET /api/v1/stocks/search - 종목 검색
GET /api/v1/stocks/balance - 계좌 잔고 (KIS 미설정 → 503)
GET /api/v1/stocks/quote/{symbol} - 시세 (KIS 미설정 → 503)
"""
import pytest


@pytest.mark.asyncio
async def test_search_requires_query(client_with_user):
    """종목 검색 - q 파라미터 없으면 422"""
    response = await client_with_user.get("/api/v1/stocks/search")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_balance_without_kis_returns_503(client_with_user):
    """계좌 잔고 - KIS API 미설정 시 503"""
    response = await client_with_user.get("/api/v1/stocks/balance")
    # KIS 미설정 테스트 환경에서는 503 반환
    assert response.status_code == 503


@pytest.mark.asyncio
async def test_quote_without_kis_returns_503(client_with_user):
    """시세 조회 - KIS API 미설정 시 503"""
    response = await client_with_user.get("/api/v1/stocks/005930/quote")
    assert response.status_code == 503
