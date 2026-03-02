"""
pytest 전역 fixture 설정
테스트용 DB 세션, 인증 오버라이드, TestClient를 제공한다.
"""
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db
from app.core.auth import get_current_user, create_token
from app.models.base import Base  # noqa: F401 - 모든 모델 임포트 트리거용
from app.models.user import User


# 인메모리 SQLite (테스트용)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """테스트용 인메모리 SQLite 엔진 픽스처"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine):
    """테스트용 DB 세션 픽스처"""
    session_factory = async_sessionmaker(db_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):
    """
    테스트용 AsyncClient 픽스처
    - DB 의존성: 테스트 DB로 오버라이드
    - 인증 의존성: 테스트 유저("testuser")로 오버라이드
    """
    async def override_get_db():
        yield db_session

    async def override_get_current_user():
        return "testuser"

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def client_with_user(db_session: AsyncSession):
    """
    테스트용 AsyncClient 픽스처 (DB에 testuser 생성 포함)
    - 안전장치, 보유종목 등 User 레코드가 필요한 엔드포인트 테스트용
    """
    # testuser DB 레코드 생성
    user = User(username="testuser", is_active=True)
    db_session.add(user)
    await db_session.commit()

    async def override_get_db():
        yield db_session

    async def override_get_current_user():
        return "testuser"

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def auth_token() -> str:
    """테스트용 Bearer 토큰"""
    return create_token("testuser")


@pytest.fixture
def auth_headers(auth_token: str) -> dict:
    """테스트 요청에 사용할 Authorization 헤더"""
    return {"Authorization": f"Bearer {auth_token}"}
