"""
로깅 설정 모듈
DEBUG 환경변수에 따라 로그 레벨을 설정한다.
"""
import logging

from app.core.config import settings

# 로그 레벨: DEBUG=True이면 DEBUG, 아니면 INFO
log_level = logging.DEBUG if settings.DEBUG else logging.INFO

logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# 모듈용 로거
logger = logging.getLogger("mystock.bot")
