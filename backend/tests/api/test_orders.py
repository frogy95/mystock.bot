"""
주문 API 통합 테스트
GET /api/v1/orders
GET /api/v1/orders/daily-summary
"""
import pytest


@pytest.mark.asyncio
async def test_list_orders_empty(client_with_user):
    """주문 목록 조회 - 빈 결과"""
    response = await client_with_user.get("/api/v1/orders")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_daily_summary_default_date(client_with_user):
    """일일 매매 요약 조회 - 기본(오늘) 날짜"""
    response = await client_with_user.get("/api/v1/orders/daily-summary")
    assert response.status_code == 200
    data = response.json()
    assert "date" in data
    assert "total_buy_count" in data
    assert "total_sell_count" in data
    assert "total_buy_amount" in data
    assert "total_sell_amount" in data
    assert "orders" in data


@pytest.mark.asyncio
async def test_daily_summary_with_valid_date(client_with_user):
    """일일 매매 요약 조회 - 유효한 날짜 파라미터"""
    response = await client_with_user.get("/api/v1/orders/daily-summary?date=2026-01-01")
    assert response.status_code == 200
    data = response.json()
    assert data["date"] == "2026-01-01"


@pytest.mark.asyncio
async def test_daily_summary_invalid_date_returns_400(client):
    """일일 매매 요약 조회 - 잘못된 날짜 형식 → 400 반환 (에러 핸들링 검증)"""
    response = await client.get("/api/v1/orders/daily-summary?date=not-a-date")
    assert response.status_code == 400
