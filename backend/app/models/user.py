"""
사용자 ORM 모델 모듈
시스템 사용자 정보를 정의한다.
"""
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class User(Base):
    """사용자 테이블 - 시스템에 등록된 사용자 정보를 저장한다."""

    __tablename__ = "users"

    # 기본 키
    id: Mapped[int] = mapped_column(primary_key=True)
    # 사용자명 (고유값, 최대 50자)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    # 활성화 여부 (기본값: True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
