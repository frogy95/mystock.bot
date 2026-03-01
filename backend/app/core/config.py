"""
환경변수 설정 모듈
pydantic-settings를 사용하여 .env 파일에서 설정값을 로드한다.
"""
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정 클래스"""

    # PostgreSQL 데이터베이스 설정
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "mystock"
    POSTGRES_USER: str = "mystock_user"
    POSTGRES_PASSWORD: str = ""

    # Redis 캐시 설정
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # 백엔드 서버 설정
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    # 보안 및 환경 설정
    SECRET_KEY: str = "change-me-in-production"
    DEBUG: bool = False

    @property
    def database_url(self) -> str:
        """비동기 PostgreSQL 연결 URL을 반환한다. (비밀번호 특수문자 URL 인코딩 적용)"""
        password = quote_plus(self.POSTGRES_PASSWORD)
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{password}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = {"env_file": ".env", "extra": "ignore"}


# 싱글턴 설정 인스턴스
settings = Settings()
