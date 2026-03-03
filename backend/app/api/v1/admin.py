"""
관리자 전용 API 엔드포인트
초대 코드 발급, 사용자 관리 기능을 제공한다.
"""
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.invitation import InvitationCode
from app.models.user import ROLE_ADMIN, User

router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """관리자 권한을 요구하는 의존성 함수."""
    if current_user.role != ROLE_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다.",
        )
    return current_user


class InvitationCreateRequest(BaseModel):
    """초대 코드 생성 요청 스키마"""

    expires_days: int = 7  # 기본 7일 유효


class InvitationResponse(BaseModel):
    """초대 코드 응답 스키마"""

    id: int
    code: str
    created_by: int
    used_by: int | None
    expires_at: datetime
    is_used: bool

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    """사용자 목록 응답 스키마"""

    id: int
    username: str
    email: str | None
    role: str
    is_approved: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("/invitations", response_model=list[InvitationResponse], summary="초대 코드 목록")
async def list_invitations(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """관리자가 생성한 모든 초대 코드를 반환한다."""
    result = await db.execute(select(InvitationCode).order_by(InvitationCode.id.desc()))
    return result.scalars().all()


@router.post("/invitations", response_model=InvitationResponse, summary="초대 코드 생성")
async def create_invitation(
    body: InvitationCreateRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """새 초대 코드를 생성한다."""
    invitation = InvitationCode(
        code=secrets.token_urlsafe(16),
        created_by=admin.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=body.expires_days),
        is_used=False,
    )
    db.add(invitation)
    await db.commit()
    await db.refresh(invitation)
    return invitation


@router.get("/users", response_model=list[UserResponse], summary="사용자 목록")
async def list_users(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """전체 사용자 목록을 반환한다."""
    result = await db.execute(select(User).order_by(User.id.asc()))
    return result.scalars().all()


@router.put("/users/{user_id}/approve", response_model=UserResponse, summary="사용자 승인")
async def approve_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """사용자를 승인하여 로그인 가능 상태로 변경한다."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    user.is_approved = True
    await db.commit()
    await db.refresh(user)
    return user


@router.put("/users/{user_id}/deactivate", response_model=UserResponse, summary="사용자 비활성화")
async def deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """사용자를 비활성화하여 로그인 불가 상태로 변경한다."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="자기 자신은 비활성화할 수 없습니다.")
    user.is_active = False
    await db.commit()
    await db.refresh(user)
    return user
