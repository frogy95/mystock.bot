"""
Alembic 마이그레이션 환경 설정 모듈
데이터베이스 URL과 메타데이터를 동적으로 설정한다.
"""
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 프로젝트 루트(backend/)를 sys.path에 추가하여 app 모듈을 임포트할 수 있도록 설정
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 애플리케이션 설정 및 모델 임포트
from app.core.config import settings
from app.models.base import Base

# 모든 모델을 임포트하여 SQLAlchemy 메타데이터에 등록
from app.models import user, watchlist, strategy, order, portfolio, backtest, settings as settings_model  # noqa: F401

# Alembic Config 객체 - alembic.ini 파일의 값에 접근한다
config = context.config

# Python 로깅 설정 - alembic.ini의 로거 설정을 적용한다
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 비동기 드라이버(asyncpg)를 동기 드라이버(psycopg2)로 변환
# Alembic은 동기 드라이버를 사용하므로 +asyncpg를 제거한다
_db_url = settings.database_url.replace("+asyncpg", "")
config.set_main_option("sqlalchemy.url", _db_url)

# autogenerate 지원을 위한 모델 메타데이터 설정
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """오프라인 모드로 마이그레이션을 실행한다.

    URL만으로 컨텍스트를 설정하며, Engine 생성 없이 SQL을 출력한다.
    실제 DB 연결 없이 SQL 스크립트를 생성할 수 있다.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """온라인 모드로 마이그레이션을 실행한다.

    Engine을 생성하고 연결을 통해 실제 DB에 마이그레이션을 적용한다.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
