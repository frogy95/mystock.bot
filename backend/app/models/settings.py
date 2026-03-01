"""
시스템 설정 ORM 모델 모듈
애플리케이션 전역 설정을 키-값 형식으로 정의한다.
"""
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SystemSetting(Base):
    """시스템 설정 테이블 - 전역 또는 사용자별 설정값을 저장한다."""

    __tablename__ = "system_settings"

    # 기본 키
    id: Mapped[int] = mapped_column(primary_key=True)
    # 사용자 외래 키 (None이면 전역 설정)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    # 설정 키 (최대 100자)
    setting_key: Mapped[str] = mapped_column(String(100), nullable=False)
    # 설정 값 (최대 500자, 문자열로 저장)
    setting_value: Mapped[str] = mapped_column(String(500), nullable=False)
    # 설정 타입 (int, float, str, bool)
    setting_type: Mapped[str] = mapped_column(String(20), nullable=False)
