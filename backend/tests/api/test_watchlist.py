"""
관심종목 API 통합 테스트
GET  /api/v1/watchlist/groups
POST /api/v1/watchlist/groups
POST /api/v1/watchlist/groups/{id}/items
"""
import pytest


@pytest.mark.asyncio
async def test_list_groups_empty(client_with_user):
    """관심종목 그룹 조회 - 빈 결과"""
    response = await client_with_user.get("/api/v1/watchlist/groups")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_group_success(client_with_user):
    """관심종목 그룹 생성 - 성공"""
    response = await client_with_user.post(
        "/api/v1/watchlist/groups",
        json={"name": "테스트 그룹"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "테스트 그룹"


@pytest.mark.asyncio
async def test_create_group_then_list(client_with_user):
    """관심종목 그룹 생성 후 목록 조회 - 생성된 그룹 반환"""
    await client_with_user.post(
        "/api/v1/watchlist/groups",
        json={"name": "내 관심종목"},
    )
    response = await client_with_user.get("/api/v1/watchlist/groups")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "내 관심종목"
