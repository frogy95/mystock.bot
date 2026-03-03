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

    # 한국투자증권 (KIS) API 설정
    # 모의투자 전용 키 (주문/잔고에 사용, KIS_ENVIRONMENT=vts 시)
    KIS_VTS_APP_KEY: str = ""
    KIS_VTS_APP_SECRET: str = ""
    KIS_VTS_ACCOUNT_NUMBER: str = ""

    # 실전 전용 키 (시세 조회 항상 사용 + KIS_ENVIRONMENT=real 시 주문/잔고에도 사용)
    KIS_REAL_APP_KEY: str = ""
    KIS_REAL_APP_SECRET: str = ""
    KIS_REAL_ACCOUNT_NUMBER: str = ""

    KIS_HTS_ID: str = ""  # eFriend Plus (HTS) 로그인 ID
    KIS_ENVIRONMENT: str = "vts"  # vts: 모의투자, real: 실전투자

    # 단일 유저 인증 설정 (레거시 - 초기 관리자 계정 생성용)
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "change-me-in-production"
    ADMIN_EMAIL: str = "admin@mystock.bot"

    # JWT 설정
    JWT_SECRET: str = "change-me-in-production-jwt"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1시간
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30    # 30일

    # 텔레그램 봇 설정
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""

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
