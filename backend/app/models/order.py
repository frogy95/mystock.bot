"""
주문 ORM 모델 모듈
매매 주문과 주문 로그 정보를 정의한다.
"""
from sqlalchemy import String, Integer, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base import Base


class Order(Base):
    """주문 테이블 - 매매 주문 정보를 저장한다."""

    __tablename__ = "orders"

    # 기본 키
    id: Mapped[int] = mapped_column(primary_key=True)
    # 사용자 외래 키
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    # 종목 코드 (예: 005930)
    stock_code: Mapped[str] = mapped_column(String(20), nullable=False)
    # 주문 유형 (buy: 매수, sell: 매도)
    order_type: Mapped[str] = mapped_column(String(10), nullable=False)
    # 주문 상태 (pending, filled, cancelled 등)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )
    # 적용 전략 외래 키 (선택값)
    strategy_id: Mapped[int | None] = mapped_column(
        ForeignKey("strategies.id"), nullable=True
    )
    # 주문 수량 (선택값)
    quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # 주문 단가 (선택값, 소수점 2자리)
    price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)


class OrderLog(Base):
    """주문 로그 테이블 - 주문 처리 과정의 로그를 저장한다."""

    __tablename__ = "order_logs"

    # 기본 키
    id: Mapped[int] = mapped_column(primary_key=True)
    # 주문 외래 키
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    # 로그 유형 (info, warning, error 등)
    log_type: Mapped[str] = mapped_column(String(20), nullable=False)
    # 로그 메시지 (최대 500자)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    # 상세 정보 (JSONB 형식, 선택값)
    detail: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
