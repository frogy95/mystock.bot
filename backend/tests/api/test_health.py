"""
헬스체크 엔드포인트 통합 테스트
GET /api/v1/health
"""
import pytest


@pytest.mark.asyncio
async def test_health_check_returns_200(client):
    """헬스체크 엔드포인트가 200을 반환하는지 확인"""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_check_response_structure(client):
    """헬스체크 응답에 필수 필드가 포함되어 있는지 확인"""
    response = await client.get("/api/v1/health")
    data = response.json()

    assert "status" in data
    assert "timestamp" in data
    assert "version" in data
    assert "checks" in data
    assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_health_check_has_database_check(client):
    """헬스체크 응답에 database 체크 항목이 있는지 확인"""
    response = await client.get("/api/v1/health")
    data = response.json()
    checks = data.get("checks", {})
    assert "database" in checks
