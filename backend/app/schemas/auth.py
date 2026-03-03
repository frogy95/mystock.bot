"""
인증 관련 Pydantic 스키마
"""
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """로그인 요청 스키마 (이메일 + 비밀번호)"""

    email: str
    password: str


class RegisterRequest(BaseModel):
    """회원가입 요청 스키마"""

    username: str
    email: EmailStr
    password: str
    invitation_code: str


class RefreshRequest(BaseModel):
    """리프레시 토큰 요청 스키마"""

    refresh_token: str


class TokenResponse(BaseModel):
    """토큰 응답 스키마"""

    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
