"""
주문 API 통합 테스트
GET  /api/v1/orders
GET  /api/v1/orders/daily-summary
PUT  /api/v1/orders/{id}/cancel
"""
import pytest

from app.models.order import Order


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


@pytest.mark.asyncio
async def test_cancel_pending_order_success(client_with_user, db_session):
    """주문 취소 - pending 주문 → cancelled로 변경"""
    from app.models.user import User
    from sqlalchemy import select

    result = await db_session.execute(select(User).where(User.username == "testuser"))
    user = result.scalar_one()

    order = Order(user_id=user.id, stock_code="005930", order_type="buy", status="pending")
    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)

    response = await client_with_user.put(f"/api/v1/orders/{order.id}/cancel")
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


@pytest.mark.asyncio
async def test_cancel_filled_order_returns_400(client_with_user, db_session):
    """주문 취소 - filled 주문 취소 시도 → 400"""
    from app.models.user import User
    from sqlalchemy import select

    result = await db_session.execute(select(User).where(User.username == "testuser"))
    user = result.scalar_one()

    order = Order(user_id=user.id, stock_code="005930", order_type="buy", status="filled")
    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)

    response = await client_with_user.put(f"/api/v1/orders/{order.id}/cancel")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_cancel_nonexistent_order_returns_404(client_with_user):
    """주문 취소 - 존재하지 않는 주문 ID → 404"""
    response = await client_with_user.put("/api/v1/orders/99999/cancel")
    assert response.status_code == 404
