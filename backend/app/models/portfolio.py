"""
포트폴리오 ORM 모델 모듈
포트폴리오 스냅샷 정보를 정의한다.
"""
import datetime

from sqlalchemy import Integer, ForeignKey, Numeric, Date
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base import Base


class PortfolioSnapshot(Base):
    """포트폴리오 스냅샷 테이블 - 특정 날짜의 포트폴리오 상태를 저장한다."""

    __tablename__ = "portfolio_snapshots"

    # 기본 키
    id: Mapped[int] = mapped_column(primary_key=True)
    # 사용자 외래 키
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    # 스냅샷 날짜
    snapshot_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    # 총 평가금액 (소수점 2자리)
    total_value: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    # 스냅샷 상세 데이터 (JSONB 형식, 선택값)
    snapshot_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
