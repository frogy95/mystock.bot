"""
JWT 기반 인증 모듈
python-jose + bcrypt를 사용하여 JWT 토큰을 발급/검증한다.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

_bearer_scheme = HTTPBearer()

# 데모 유저 상수
DEMO_USERNAME = "__demo__"
DEMO_USER_ID = -1  # 데모 유저는 DB에 없으므로 가상 ID 사용


def is_demo_user(username: str) -> bool:
    """데모 유저인지 확인한다."""
    return username == DEMO_USERNAME


def hash_password(plain: str) -> str:
    """비밀번호를 bcrypt 해시로 변환한다."""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """비밀번호와 해시를 검증한다."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(user_id: int, username: str) -> str:
    """액세스 토큰(JWT)을 생성한다. 유효 기간: ACCESS_TOKEN_EXPIRE_MINUTES."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    """리프레시 토큰(JWT)을 생성한다. 유효 기간: REFRESH_TOKEN_EXPIRE_DAYS."""
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """JWT 토큰을 디코딩하여 페이로드를 반환한다. 유효하지 않으면 예외를 발생시킨다."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """FastAPI 의존성: Bearer 토큰을 검증하고 User 객체를 반환한다.
    데모 유저의 경우 가상 User 객체를 반환한다.
    """
    token = credentials.credentials
    payload = decode_token(token)

    # 데모 토큰 처리: username이 DEMO_USERNAME이면 가상 User 반환
    username = payload.get("username", "")
    if username == DEMO_USERNAME:
        demo_user = User()
        demo_user.id = DEMO_USER_ID
        demo_user.username = DEMO_USERNAME
        demo_user.role = "user"
        demo_user.is_active = True
        demo_user.is_approved = True
        return demo_user

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).where(User.id == int(user_id_str)))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없거나 비활성화된 계정입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 승인 대기 중입니다.",
        )
    return user


# 레거시 호환: 데모 로그인을 위한 토큰 생성 (DEMO_USERNAME 전용)
def create_demo_token() -> str:
    """데모 유저 전용 액세스 토큰을 생성한다."""
    return create_access_token(user_id=DEMO_USER_ID, username=DEMO_USERNAME)
