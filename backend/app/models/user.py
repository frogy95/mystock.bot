"""
사용자 ORM 모델 모듈
시스템 사용자 정보를 정의한다.
"""
from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

# 사용자 역할 상수
ROLE_ADMIN = "admin"
ROLE_USER = "user"


class User(Base):
    """사용자 테이블 - 시스템에 등록된 사용자 정보를 저장한다."""

    __tablename__ = "users"

    # 기본 키
    id: Mapped[int] = mapped_column(primary_key=True)
    # 사용자명 (고유값, 최대 50자)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    # 이메일 (고유값, 최대 255자)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=True)
    # 비밀번호 해시 (bcrypt, 최대 255자)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=True)
    # 역할 (admin/user)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default=ROLE_USER)
    # 초대자 ID (자기 참조 FK, nullable)
    invited_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    # 관리자 승인 여부 (기본값: False, 관리자는 True)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # 활성화 여부 (기본값: True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # 관계: 초대한 사용자들
    invitees: Mapped[list[User]] = relationship(
        "User", foreign_keys=[invited_by], back_populates="inviter"
    )
    inviter: Mapped[User | None] = relationship(
        "User", foreign_keys=[invited_by], remote_side=[id], back_populates="invitees"
    )
