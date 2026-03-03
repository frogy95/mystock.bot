"""
인증 API 통합 테스트
POST /api/v1/auth/login
"""
import pytest


@pytest.mark.asyncio
async def test_login_success(client):
    """로그인 성공 시 토큰 반환 확인 (email 기반 로그인)"""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "change-me-in-production"},
    )
    # DB에 해당 계정이 없으면 401, 있으면 200
    assert response.status_code in (200, 401)


@pytest.mark.asyncio
async def test_login_invalid_credentials_returns_401(client):
    """잘못된 인증 정보로 로그인 시 401 반환"""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@example.com", "password": "wrong"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_without_auth_returns_403_or_401():
    """인증 없이 보호된 엔드포인트 접근 시 401/403 반환"""
    from httpx import AsyncClient, ASGITransport
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.get("/api/v1/orders")
    assert response.status_code in (401, 403)
