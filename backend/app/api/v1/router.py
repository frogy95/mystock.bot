"""
v1 API 라우터 통합 모듈
v1 하위의 모든 라우터를 통합한다.
"""
from fastapi import APIRouter

from app.api.v1 import auth, health, holdings, settings, stocks, watchlist

# v1 통합 라우터
router = APIRouter()

# 헬스체크 라우터 포함
router.include_router(health.router, tags=["헬스체크"])

# 인증 라우터 포함
router.include_router(auth.router, prefix="/auth", tags=["인증"])

# 주식 조회 라우터 포함
router.include_router(stocks.router, prefix="/stocks", tags=["주식"])

# 설정 라우터 포함
router.include_router(settings.router, prefix="/settings", tags=["설정"])

# 관심종목 라우터 포함
router.include_router(watchlist.router, prefix="/watchlist", tags=["관심종목"])

# 보유종목 라우터 포함
router.include_router(holdings.router, prefix="/holdings", tags=["보유종목"])
