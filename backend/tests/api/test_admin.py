"""
관리자 API 통합 테스트
GET    /api/v1/admin/invitations
POST   /api/v1/admin/invitations
GET    /api/v1/admin/users
PUT    /api/v1/admin/users/{id}/approve
PUT    /api/v1/admin/users/{id}/deactivate
"""
import pytest

from app.models.invitation import InvitationCode
from app.models.user import ROLE_ADMIN, ROLE_USER, User


@pytest.mark.asyncio
async def test_non_admin_cannot_list_invitations(client_with_user):
    """일반 사용자는 초대코드 목록 조회 불가 (403)"""
    response = await client_with_user.get("/api/v1/admin/invitations")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_list_invitations(client_with_admin):
    """관리자는 초대코드 목록 조회 가능"""
    response = await client_with_admin.get("/api/v1/admin/invitations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_admin_can_create_invitation(client_with_admin):
    """관리자가 초대코드 생성"""
    response = await client_with_admin.post(
        "/api/v1/admin/invitations",
        json={"expires_days": 7},
    )
    assert response.status_code == 200
    data = response.json()
    assert "code" in data
    assert data["is_used"] is False
    assert len(data["code"]) > 10


@pytest.mark.asyncio
async def test_admin_can_list_users(client_with_admin):
    """관리자는 사용자 목록 조회 가능"""
    response = await client_with_admin.get("/api/v1/admin/users")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) >= 1  # 관리자 자신 포함


@pytest.mark.asyncio
async def test_admin_can_approve_user(client_with_admin, db_session):
    """관리자가 일반 사용자 승인"""
    import bcrypt
    pw_hash = bcrypt.hashpw(b"testpass", bcrypt.gensalt()).decode()
    new_user = User(
        username="pending_user",
        email="pending@example.com",
        password_hash=pw_hash,
        role=ROLE_USER,
        is_approved=False,
        is_active=True,
    )
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)

    response = await client_with_admin.put(
        f"/api/v1/admin/users/{new_user.id}/approve"
    )
    assert response.status_code == 200
    assert response.json()["is_approved"] is True


@pytest.mark.asyncio
async def test_admin_cannot_deactivate_self(client_with_admin, admin_user):
    """관리자는 자기 자신을 비활성화할 수 없음 (400)"""
    response = await client_with_admin.put(
        f"/api/v1/admin/users/{admin_user.id}/deactivate"
    )
    assert response.status_code == 400
