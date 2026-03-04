"""
인증 API 엔드포인트
JWT 기반 회원가입/로그인/리프레시/데모를 처리한다.
"""
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import (
    create_access_token,
    create_demo_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.core.database import get_db
from app.models.invitation import InvitationCode
from app.models.user import ROLE_ADMIN, ROLE_USER, User
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse

router = APIRouter()


class MeResponse(BaseModel):
    """현재 사용자 정보 응답"""

    id: int
    username: str
    email: str | None
    role: str
    is_approved: bool

    model_config = {"from_attributes": True}


@router.get("/me", response_model=MeResponse, summary="현재 사용자 정보")
async def get_me(current_user: User = Depends(get_current_user)):
    """현재 로그인한 사용자의 정보를 반환한다."""
    return current_user


@router.post("/register", response_model=TokenResponse, summary="회원가입")
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """초대 코드를 검증하고 새 사용자를 생성한다. 관리자 승인 후 로그인 가능."""
    # 초대 코드 검증
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(InvitationCode).where(
            InvitationCode.code == body.invitation_code,
            InvitationCode.is_used == False,  # noqa: E712
            InvitationCode.expires_at > now,
        )
    )
    invitation = result.scalar_one_or_none()
    if invitation is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효하지 않거나 만료된 초대 코드입니다.",
        )

    # 이메일 중복 확인
    email_result = await db.execute(select(User).where(User.email == body.email))
    if email_result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용 중인 이메일입니다.",
        )

    # 사용자명 중복 확인
    username_result = await db.execute(
        select(User).where(User.username == body.username)
    )
    if username_result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용 중인 사용자명입니다.",
        )

    # 사용자 생성
    user = User(
        username=body.username,
        email=body.email,
        password_hash=hash_password(body.password),
        role=ROLE_USER,
        invited_by=invitation.created_by,
        is_approved=False,
        is_active=True,
    )
    db.add(user)

    # 초대 코드 사용 처리 (flush 후 user.id 할당됨)
    await db.flush()
    invitation.is_used = True
    invitation.used_by = user.id
    await db.commit()
    await db.refresh(user)

    return TokenResponse(
        access_token="",
        refresh_token=None,
        token_type="bearer",
    )


@router.post("/login", response_model=TokenResponse, summary="로그인")
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """이메일/비밀번호를 검증하고 JWT 토큰을 발급한다."""
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if user is None or user.password_hash is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
        )
    if not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="비활성화된 계정입니다.",
        )
    if not user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 승인 대기 중입니다.",
        )

    access_token = create_access_token(user_id=user.id, username=user.username)
    refresh_token = create_refresh_token(user_id=user.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse, summary="토큰 갱신")
async def refresh_token(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """리프레시 토큰으로 새 액세스 토큰을 발급한다."""
    payload = decode_token(body.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="리프레시 토큰이 아닙니다.",
        )

    user_id = int(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active or not user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 사용자입니다.",
        )

    access_token = create_access_token(user_id=user.id, username=user.username)
    return TokenResponse(access_token=access_token)


@router.post("/demo", response_model=TokenResponse, summary="데모 로그인")
async def demo_login():
    """비밀번호 없이 데모 유저 토큰을 즉시 발급한다."""
    token = create_demo_token()
    return TokenResponse(access_token=token)
