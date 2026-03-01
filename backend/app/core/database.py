"""
데이터베이스 연결 설정 모듈
SQLAlchemy 2.x 비동기 엔진 및 세션을 설정한다.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# 비동기 데이터베이스 엔진 생성
engine = create_async_engine(
    settings.database_url,
    echo=settings.DEBUG,  # DEBUG 모드에서 SQL 쿼리 출력
)

# 비동기 세션 팩토리 생성
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,  # 커밋 후 객체를 만료시키지 않음
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    데이터베이스 세션 의존성 함수
    FastAPI의 Depends와 함께 사용한다.
    """
    async with AsyncSessionLocal() as session:
        yield session
