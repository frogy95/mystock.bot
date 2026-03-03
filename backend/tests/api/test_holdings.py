"""
보유종목 API 통합 테스트
GET  /api/v1/holdings
GET  /api/v1/holdings/summary
"""
import pytest

from app.models.holding import Holding


@pytest.mark.asyncio
async def test_list_holdings_empty(client_with_user):
    """보유종목 목록 조회 - 빈 결과"""
    response = await client_with_user.get("/api/v1/holdings")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_holdings_returns_holding(client_with_user, db_session):
    """보유종목 목록 조회 - 보유종목 존재 시 반환"""
    from app.models.user import User
    from sqlalchemy import select

    result = await db_session.execute(select(User).where(User.username == "testuser"))
    user = result.scalar_one()

    holding = Holding(
        user_id=user.id,
        stock_code="005930",
        stock_name="삼성전자",
        quantity=10,
        avg_price=70000,
    )
    db_session.add(holding)
    await db_session.commit()

    response = await client_with_user.get("/api/v1/holdings")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["stock_code"] == "005930"


@pytest.mark.asyncio
async def test_portfolio_summary_returns_structure(client_with_user):
    """포트폴리오 요약 조회 - 응답 구조 확인"""
    response = await client_with_user.get("/api/v1/holdings/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_evaluation" in data
    assert "total_profit_loss" in data
    assert "total_profit_loss_rate" in data
