"""
설정 관련 API 엔드포인트 (인증 필요)
"""
from fastapi import APIRouter, Depends

from app.core.auth import get_current_user, is_demo_user
from app.models.user import User
from app.services.demo_data import get_demo_kis_status
from app.services.kis_client import kis_client

router = APIRouter()


@router.get("/kis-status", summary="KIS API 연결 상태 조회")
async def get_kis_status(current_user: User = Depends(get_current_user)):
    """KIS API 연결 상태를 반환한다. (인증 필요)"""
    if is_demo_user(current_user.username):
        return get_demo_kis_status()
    return {
        "available": kis_client.is_available(),
        "message": "KIS API 연결됨" if kis_client.is_available() else "KIS API 키 미설정",
    }
