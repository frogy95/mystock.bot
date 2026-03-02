"""
안전장치 API 통합 테스트
GET  /api/v1/safety/status
POST /api/v1/safety/auto-trade
POST /api/v1/safety/emergency-sell
"""
import pytest


@pytest.mark.asyncio
async def test_safety_status_returns_200(client_with_user):
    """안전장치 상태 조회 - 200 반환 및 응답 구조 확인"""
    response = await client_with_user.get("/api/v1/safety/status")
    assert response.status_code == 200
    data = response.json()
    assert "auto_trade_enabled" in data
    assert "daily_loss_check" in data
    assert "daily_order_check" in data


@pytest.mark.asyncio
async def test_toggle_auto_trade_enable(client_with_user):
    """자동매매 활성화 - 200 반환 및 상태 반영 확인"""
    response = await client_with_user.post(
        "/api/v1/safety/auto-trade",
        json={"enabled": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["auto_trade_enabled"] is True


@pytest.mark.asyncio
async def test_toggle_auto_trade_disable(client_with_user):
    """자동매매 비활성화 - 200 반환 및 상태 반영 확인"""
    response = await client_with_user.post(
        "/api/v1/safety/auto-trade",
        json={"enabled": False},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["auto_trade_enabled"] is False


@pytest.mark.asyncio
async def test_safety_status_no_user_returns_404(client):
    """사용자 미존재 시 404 반환 (DB에 사용자 없음)"""
    response = await client.get("/api/v1/safety/status")
    assert response.status_code == 404
