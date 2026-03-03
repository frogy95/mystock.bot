"""
전략 API 통합 테스트
GET  /api/v1/strategies
GET  /api/v1/strategies/{id}
GET  /api/v1/strategies/performance
"""
import pytest

from app.models.strategy import Strategy


@pytest.mark.asyncio
async def test_list_strategies_empty(client_with_user):
    """전략 목록 조회 - 빈 결과"""
    response = await client_with_user.get("/api/v1/strategies")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_strategies_returns_strategy(client_with_user, db_session):
    """전략 목록 조회 - 전략 존재 시 반환"""
    strategy = Strategy(name="GoldenCross", strategy_type="technical", is_active=True)
    db_session.add(strategy)
    await db_session.commit()

    response = await client_with_user.get("/api/v1/strategies")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "GoldenCross"


@pytest.mark.asyncio
async def test_get_strategy_not_found(client_with_user):
    """전략 상세 조회 - 없는 ID → 404"""
    response = await client_with_user.get("/api/v1/strategies/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_strategy_performance_empty(client_with_user):
    """전략 성과 집계 - 전략 없을 때 빈 배열"""
    response = await client_with_user.get("/api/v1/strategies/performance")
    assert response.status_code == 200
    assert response.json() == []
