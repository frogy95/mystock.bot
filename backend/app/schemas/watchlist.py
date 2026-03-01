"""
관심종목 관련 Pydantic 스키마
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class WatchlistItemResponse(BaseModel):
    """관심종목 항목 응답 스키마"""

    id: int
    group_id: int
    stock_code: str
    stock_name: str
    strategy_id: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class WatchlistItemCreate(BaseModel):
    """관심종목 항목 생성 요청 스키마"""

    stock_code: str
    stock_name: str


class WatchlistItemStrategyAssign(BaseModel):
    """관심종목 전략 할당 요청 스키마 (strategy_id=None 이면 해제)"""

    strategy_id: Optional[int] = None


class WatchlistGroupResponse(BaseModel):
    """관심종목 그룹 응답 스키마 (항목 목록 포함)"""

    id: int
    name: str
    sort_order: int
    items: List[WatchlistItemResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class WatchlistGroupCreate(BaseModel):
    """관심종목 그룹 생성 요청 스키마"""

    name: str


class WatchlistGroupUpdate(BaseModel):
    """관심종목 그룹 수정 요청 스키마"""

    name: str
