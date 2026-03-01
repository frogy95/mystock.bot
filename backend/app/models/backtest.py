"""
백테스트 ORM 모델 모듈
전략 백테스트 결과 정보를 정의한다.
Sprint 8: symbol, start_date, end_date 컬럼 추가, strategy_id nullable로 변경
"""
from datetime import date
from typing import Optional

from sqlalchemy import ForeignKey, Numeric, String, Date
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base import Base


class BacktestResult(Base):
    """백테스트 결과 테이블 - 전략 백테스트 수행 결과를 저장한다."""

    __tablename__ = "backtest_results"

    # 기본 키
    id: Mapped[int] = mapped_column(primary_key=True)
    # 전략 외래 키 (nullable: 커스텀 백테스트는 전략 없이도 실행 가능)
    strategy_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("strategies.id"), nullable=True
    )
    # 종목 코드 (단일 종목 백테스트용)
    symbol: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    # 백테스트 시작일
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    # 백테스트 종료일
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    # 대상 종목 코드 목록 (JSONB 배열, 선택값)
    stock_codes: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    # 총 수익률 (소수점 4자리, 선택값)
    total_return: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    # 최대 낙폭 MDD (소수점 4자리, 선택값)
    max_drawdown: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    # 샤프 지수 (소수점 4자리, 선택값)
    sharpe_ratio: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    # 승률 (소수점 4자리, 선택값)
    win_rate: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    # 결과 상세 데이터 (JSONB 형식, 선택값)
    result_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
