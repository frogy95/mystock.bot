"""
헬스체크 엔드포인트 모듈
서비스 상태를 확인하는 API를 제공한다.
"""
from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """
    서비스 상태 확인 엔드포인트
    현재 시각과 버전 정보를 반환한다.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "0.1.0",
    }
