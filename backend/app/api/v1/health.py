"""
헬스체크 엔드포인트 모듈
DB, Redis, 스케줄러 실제 상태를 확인하여 반환한다.
unhealthy 시 HTTP 503 반환 (ALB 호환).
"""
import logging
from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config import settings

router = APIRouter()
logger = logging.getLogger("mystock.bot")


@router.get("/health")
async def health_check() -> JSONResponse:
    """
    서비스 상태 확인 엔드포인트
    DB, Redis, 스케줄러의 실제 상태를 확인하고 반환한다.
    unhealthy 시 HTTP 503 반환 (ALB 헬스체크 호환).
    """
    checks: dict[str, dict] = {}
    overall_healthy = True

    # --- DB 연결 상태 확인 ---
    try:
        from app.core.database import engine
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy", fromlist=["text"]).text("SELECT 1"))
        checks["database"] = {"status": "healthy"}
    except Exception as e:
        logger.warning(f"Health check - DB 연결 실패: {e}")
        error_detail = str(e) if settings.DEBUG else "연결 실패"
        checks["database"] = {"status": "unhealthy", "error": error_detail}
        overall_healthy = False

    # --- Redis 연결 상태 확인 ---
    try:
        from app.services.redis_client import get_redis
        redis = get_redis()
        await redis.ping()
        checks["redis"] = {"status": "healthy"}
    except Exception as e:
        logger.warning(f"Health check - Redis 연결 실패: {e}")
        error_detail = str(e) if settings.DEBUG else "연결 실패"
        checks["redis"] = {"status": "unhealthy", "error": error_detail}
        overall_healthy = False

    # --- 스케줄러 상태 확인 ---
    try:
        from app.services.scheduler import get_scheduler
        scheduler = get_scheduler()
        if scheduler is not None and scheduler.running:
            job_count = len(scheduler.get_jobs())
            checks["scheduler"] = {"status": "healthy", "jobs": job_count}
        else:
            checks["scheduler"] = {"status": "unhealthy", "error": "스케줄러가 실행 중이 아닙니다."}
            overall_healthy = False
    except Exception as e:
        logger.warning(f"Health check - 스케줄러 상태 확인 실패: {e}")
        checks["scheduler"] = {"status": "unknown", "error": str(e) if settings.DEBUG else "확인 실패"}

    body = {
        "status": "healthy" if overall_healthy else "unhealthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "0.1.0",
        "checks": checks,
    }
    status_code = 200 if overall_healthy else 503
    return JSONResponse(content=body, status_code=status_code)
