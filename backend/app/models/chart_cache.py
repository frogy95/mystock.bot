"""
차트 데이터 캐시 ORM 모델 모듈
KIS API 또는 yfinance에서 조회한 일별 OHLCV 데이터를 DB에 캐싱한다.
"""
from datetime import date

from sqlalchemy import BigInteger, Date, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ChartDataCache(Base):
    """차트 데이터 캐시 테이블 - 종목별 일별 OHLCV 데이터를 저장한다."""

    __tablename__ = "chart_data_cache"
    __table_args__ = (
        UniqueConstraint("symbol", "trade_date", name="uq_chart_symbol_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    # 종목 코드 (예: 229200)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    # 거래일
    trade_date: Mapped[date] = mapped_column(Date, nullable=False)
    # OHLCV
    open: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    high: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    low: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    close: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # 데이터 출처: 'kis' | 'yfinance'
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    # created_at, updated_at는 Base에서 자동 상속
