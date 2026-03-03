"""
전략 ORM 모델 모듈
매매 전략과 전략 파라미터 정보를 정의한다.
"""
from typing import Optional

from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Strategy(Base):
    """전략 테이블 - 매매 전략 정보를 저장한다."""

    __tablename__ = "strategies"

    # 기본 키
    id: Mapped[int] = mapped_column(primary_key=True)
    # 전략 이름 (최대 100자)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # 전략 유형 (예: technical, fundamental)
    strategy_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # 활성화 여부 (기본값: True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # 프리셋 여부 - 시스템 기본 제공 전략인지 여부
    is_preset: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # 소유 사용자 FK - NULL이면 시스템 프리셋, 값이 있으면 사용자 소유
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)


class StrategyParam(Base):
    """전략 파라미터 테이블 - 전략별 설정 파라미터를 키-값 형식으로 저장한다."""

    __tablename__ = "strategy_params"

    # 기본 키
    id: Mapped[int] = mapped_column(primary_key=True)
    # 전략 외래 키
    strategy_id: Mapped[int] = mapped_column(
        ForeignKey("strategies.id"), nullable=False
    )
    # 파라미터 키 (최대 50자)
    param_key: Mapped[str] = mapped_column(String(50), nullable=False)
    # 파라미터 값 (최대 200자, 문자열로 저장)
    param_value: Mapped[str] = mapped_column(String(200), nullable=False)
    # 파라미터 타입 (int, float, str 등)
    param_type: Mapped[str] = mapped_column(String(20), nullable=False)
