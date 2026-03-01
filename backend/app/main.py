"""
FastAPI 애플리케이션 엔트리포인트
앱 생성, 미들웨어 설정, 라우터 등록을 담당한다.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import router as v1_router

logger = logging.getLogger("mystock.bot")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 이벤트 핸들러"""
    # 시작 시 로깅
    logger.info("mystock.bot API 서버 시작")
    yield
    # 종료 시 로깅
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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# v1 API 라우터 등록
app.include_router(v1_router.router, prefix="/api/v1")
