"""
FastAPI 애플리케이션 엔트리포인트
앱 생성, 미들웨어 설정, 라우터 등록을 담당한다.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.core.logging as _logging_setup  # 로깅 설정 초기화
from app.api.v1 import router as v1_router
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
    # 종료 시 WebSocket 폴링 + 스케줄러 + Redis 정리
    await ws_manager.stop_polling()
    await stop_scheduler()
    await close_redis()
    logger.info("mystock.bot API 서버 종료")


# FastAPI 애플리케이션 생성
app = FastAPI(
    title="mystock.bot API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 미들웨어 설정 (개발용: 모든 origin 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# v1 API 라우터 등록
app.include_router(v1_router.router, prefix="/api/v1")
