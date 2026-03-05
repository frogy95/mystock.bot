"""
FastAPI 애플리케이션 엔트리포인트
앱 생성, 미들웨어 설정, 라우터 등록을 담당한다.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError, OperationalError

import app.core.logging as _logging_setup  # 로깅 설정 초기화
from app.api.v1 import router as v1_router
from app.core.config import settings
from app.core.exceptions import (
    AppError,
    handle_app_error,
    handle_general_error,
    handle_integrity_error,
    handle_operational_error,
    handle_validation_error,
)
from app.core.middleware import RequestIdMiddleware
from app.services.kis_client import kis_client
from app.services.redis_client import close_redis
from app.services.stock_master import load_stock_master
from app.services.scheduler import start_scheduler, stop_scheduler
from app.services.websocket_manager import ws_manager

import logging

logger = logging.getLogger("mystock.bot")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 이벤트 핸들러"""
    logger.info("mystock.bot API 서버 시작")
    # 프로덕션 환경에서 기본 시크릿 키 사용 시 경고
    if not settings.DEBUG:
        _defaults = {"change-me-in-production", "change-me-in-production-jwt"}
        if settings.SECRET_KEY in _defaults or settings.JWT_SECRET in _defaults:
            logger.warning(
                "⚠️ 프로덕션 환경에서 기본 시크릿 키가 사용 중입니다. "
                "SECRET_KEY와 JWT_SECRET을 안전한 값으로 변경하세요."
            )
    # KIS 설정 DB 초기 로드
    try:
        from app.services.kis_settings_cache import load_kis_settings
        await load_kis_settings()
    except Exception as e:
        logger.warning(f"KIS 설정 DB 초기 로드 실패: {e}")
    # 종목 마스터 데이터 Redis 캐싱
    try:
        await load_stock_master()
    except Exception as e:
        logger.warning(f"종목 마스터 초기 로드 실패: {e}")
    # APScheduler 시작
    try:
        await start_scheduler()
    except Exception as e:
        logger.warning(f"스케줄러 시작 실패: {e}")
    # WebSocket 시세 폴링 시작
    try:
        await ws_manager.start_polling()
    except Exception as e:
        logger.warning(f"WebSocket 폴링 시작 실패: {e}")
    yield
    # 종료 시 WebSocket 폴링 + 스케줄러 + Redis + httpx 연결 풀 정리
    await ws_manager.stop_polling()
    await stop_scheduler()
    await close_redis()
    await kis_client.close()
    logger.info("mystock.bot API 서버 종료")


# FastAPI 애플리케이션 생성
app = FastAPI(
    title="mystock.bot API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 미들웨어 설정 (CORS_ORIGINS 환경변수로 제어)
_cors_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request ID 미들웨어 등록 (요청 추적)
app.add_middleware(RequestIdMiddleware)

# 글로벌 예외 핸들러 등록
app.add_exception_handler(AppError, handle_app_error)
app.add_exception_handler(RequestValidationError, handle_validation_error)
app.add_exception_handler(IntegrityError, handle_integrity_error)
app.add_exception_handler(OperationalError, handle_operational_error)
app.add_exception_handler(Exception, handle_general_error)

# v1 API 라우터 등록
app.include_router(v1_router.router, prefix="/api/v1")
