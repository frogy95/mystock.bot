"""
SQLAlchemy 베이스 모델 모듈
모든 모델이 상속할 Base 클래스와 공통 컬럼을 정의한다.
"""
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    """모든 SQLAlchemy 모델의 기반 클래스"""

    # 생성 시각 (DB 서버 기본값: 현재 UTC 시각)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # 수정 시각 (DB 서버 기본값: 현재 UTC 시각, 업데이트 시 DB 서버 시각으로 자동 갱신)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
