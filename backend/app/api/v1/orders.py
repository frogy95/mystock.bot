"""
주문 API 엔드포인트
주문 목록 조회를 제공한다.
"""
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.order import Order
from app.models.user import User
from datetime import datetime
from typing import Optional
from fastapi import HTTPException

router = APIRouter()


class OrderResponse(BaseModel):
    """주문 응답 스키마"""

    id: int
    stock_code: str
    order_type: str
    status: str
    strategy_id: Optional[int] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


async def _get_user_id(username: str, db: AsyncSession) -> int:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return user.id


@router.get("", response_model=List[OrderResponse], summary="주문 목록 조회")
async def list_orders(
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """사용자의 주문 목록을 최신순으로 반환한다."""
    user_id = await _get_user_id(current_user, db)
    result = await db.execute(
        select(Order)
        .where(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .limit(200)
    )
    return result.scalars().all()
