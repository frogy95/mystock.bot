"""
설정 관련 API 엔드포인트 (인증 필요)
"""
import logging

from fastapi import APIRouter, Depends

from app.core.auth import get_current_user, is_demo_user
from app.models.user import User
from app.services.demo_data import get_demo_kis_status
from app.services.kis_client import kis_client

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/kis-status", summary="KIS API 연결 상태 조회")
async def get_kis_status(current_user: User = Depends(get_current_user)):
    """KIS API 연결 상태와 토큰 유효성을 반환한다. (인증 필요)"""
    if is_demo_user(current_user.username):
        return get_demo_kis_status()

    available = kis_client.is_available()
    if not available:
        return {"available": False, "token_valid": False, "message": "KIS API 키 미설정"}

    # 실제 토큰 발급을 시도하여 유효성 확인 (캐시 사용으로 중복 HTTP 요청 없음)
    try:
        await kis_client._get_access_token("real")
        token_valid = True
        message = "KIS API 연결됨"
    except Exception as e:
        token_valid = False
        message = f"KIS 토큰 발급 실패: {e}"
        logger.warning("KIS 토큰 발급 실패: %s", e)

    return {"available": available, "token_valid": token_valid, "message": message}
