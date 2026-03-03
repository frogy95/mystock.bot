"""
초대 코드 ORM 모델 모듈
관리자가 발급하는 초대 코드를 관리한다.
"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class InvitationCode(Base):
    """초대 코드 테이블 - 회원가입에 필요한 초대 코드를 저장한다."""

    __tablename__ = "invitation_codes"

    # 기본 키
    id: Mapped[int] = mapped_column(primary_key=True)
    # 초대 코드 (고유값, 최대 64자)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    # 생성자 (관리자 user_id)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    # 사용자 (회원가입한 user_id, nullable)
    used_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    # 만료 시각
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    # 사용 여부
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
