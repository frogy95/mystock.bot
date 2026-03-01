"""
관심종목 ORM 모델 모듈
관심종목 그룹과 종목 항목 정보를 정의한다.
"""
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class WatchlistGroup(Base):
    """관심종목 그룹 테이블 - 관심종목을 묶는 그룹 정보를 저장한다."""

    __tablename__ = "watchlist_groups"

    # 기본 키
    id: Mapped[int] = mapped_column(primary_key=True)
    # 사용자 외래 키
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    # 그룹명 (최대 100자)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # 정렬 순서 (기본값: 0)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class WatchlistItem(Base):
    """관심종목 항목 테이블 - 그룹에 속하는 개별 종목 정보를 저장한다."""

    __tablename__ = "watchlist_items"

    # 기본 키
    id: Mapped[int] = mapped_column(primary_key=True)
    # 관심종목 그룹 외래 키
    group_id: Mapped[int] = mapped_column(
        ForeignKey("watchlist_groups.id"), nullable=False
    )
    # 종목 코드 (예: 005930)
    stock_code: Mapped[str] = mapped_column(String(20), nullable=False)
    # 종목명 (예: 삼성전자)
    stock_name: Mapped[str] = mapped_column(String(100), nullable=False)
    # 적용 전략 외래 키 (선택값)
    strategy_id: Mapped[int | None] = mapped_column(
        ForeignKey("strategies.id"), nullable=True
    )
