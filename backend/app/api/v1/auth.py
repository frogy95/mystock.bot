"""
인증 API 엔드포인트
환경변수에 설정된 단일 유저 로그인을 처리한다.
"""
from fastapi import APIRouter, HTTPException, status

from app.core.auth import create_token
from app.core.config import settings
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter()


@router.post("/login", response_model=TokenResponse, summary="로그인")
async def login(body: LoginRequest):
    """유저명/비밀번호를 검증하고 Bearer 토큰을 발급한다."""
    if (
        body.username != settings.ADMIN_USERNAME
        or body.password != settings.ADMIN_PASSWORD
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유저명 또는 비밀번호가 올바르지 않습니다.",
        )

    token = create_token(body.username)
    return TokenResponse(access_token=token)
