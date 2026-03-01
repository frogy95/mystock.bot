"""
보유종목 ORM 모델 모듈
사용자의 보유 종목 정보와 손절/익절 설정을 정의한다.
"""
from datetime import datetime

from sqlalchemy import String, Integer, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Holding(Base):
    """보유종목 테이블 - KIS에서 동기화된 보유 종목 정보를 저장한다."""

    __tablename__ = "holdings"

    # 기본 키
    id: Mapped[int] = mapped_column(primary_key=True)
    # 사용자 외래 키
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    # 종목 코드 (예: 005930)
    stock_code: Mapped[str] = mapped_column(String(20), nullable=False)
    # 종목명 (예: 삼성전자)
    stock_name: Mapped[str] = mapped_column(String(100), nullable=False)
    # 보유 수량
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # 평균 매수가
    avg_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    # 현재가 (마지막 동기화 시점 기준)
    current_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    # 손절 비율 (예: 5.0 → -5% 하락 시 매도)
    stop_loss_rate: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    # 익절 비율 (예: 10.0 → +10% 상승 시 매도)
    take_profit_rate: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    # 매도 전략 외래 키 (선택값)
    sell_strategy_id: Mapped[int | None] = mapped_column(
        ForeignKey("strategies.id"), nullable=True
    )
    # 마지막 KIS 동기화 시각
    synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
