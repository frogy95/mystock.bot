"""
로깅 설정 모듈
JSON 구조화 로그 포맷을 사용하여 로그를 출력한다.
python-json-logger가 없을 경우 평문 포맷으로 폴백한다.
"""
import logging

from app.core.config import settings

log_level = logging.DEBUG if settings.DEBUG else logging.INFO


def _setup_logging() -> None:
    """JSON 구조화 로그 포맷 설정 (python-json-logger 사용)"""
    try:
        from pythonjsonlogger import jsonlogger  # type: ignore

        formatter = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        # 기존 핸들러 교체
        root_logger.handlers.clear()
        root_logger.addHandler(handler)
    except ImportError:
        # python-json-logger 미설치 시 평문 포맷으로 폴백
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )


_setup_logging()

# 모듈용 로거
logger = logging.getLogger("mystock.bot")
