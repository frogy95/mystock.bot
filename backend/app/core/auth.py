"""
단일 유저 인증 모듈
환경변수(ADMIN_USERNAME, ADMIN_PASSWORD)를 기반으로 Bearer 토큰을 발급/검증한다.
JWT 대신 단순 서명 토큰을 사용하여 의존성을 최소화한다.
"""
from __future__ import annotations

import hashlib
import hmac
import time

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

_bearer_scheme = HTTPBearer()

# 토큰 유효 기간: 24시간
_TOKEN_TTL = 86400

# 데모 유저 상수
DEMO_USERNAME = "__demo__"


def is_demo_user(username: str) -> bool:
    """데모 유저인지 확인한다."""
    return username == DEMO_USERNAME


def _sign(payload: str) -> str:
    """SECRET_KEY로 HMAC-SHA256 서명을 생성한다."""
    return hmac.new(
        settings.SECRET_KEY.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()


def create_token(username: str) -> str:
    """유저명과 만료시각을 포함한 Bearer 토큰을 생성한다."""
    expires_at = int(time.time()) + _TOKEN_TTL
    payload = f"{username}:{expires_at}"
    signature = _sign(payload)
    # 토큰 형식: {payload}:{signature}
    return f"{payload}:{signature}"


def verify_token(token: str) -> str:
    """토큰을 검증하고 유저명을 반환한다. 유효하지 않으면 예외를 발생시킨다."""
    try:
        # 형식: username:expires_at:signature
        parts = token.split(":")
        if len(parts) != 3:
            raise ValueError("잘못된 토큰 형식")

        username, expires_at_str, received_sig = parts
        expires_at = int(expires_at_str)
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 만료 시간 검사
    if time.time() > expires_at:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="만료된 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 서명 검증
    payload = f"{username}:{expires_at_str}"
    expected_sig = _sign(payload)
    if not hmac.compare_digest(expected_sig, received_sig):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return username


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> str:
    """FastAPI 의존성: Bearer 토큰을 검증하고 유저명을 반환한다."""
    return verify_token(credentials.credentials)
