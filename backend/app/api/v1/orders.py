"""
주문 API 엔드포인트
주문 목록 조회를 제공한다.
"""
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, is_demo_user
from app.core.database import get_db
from app.services.demo_data import get_demo_orders, get_demo_daily_summary
from app.models.order import Order
from app.models.user import User

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


class DailySummaryResponse(BaseModel):
    """일일 매매 요약 응답 스키마"""

    date: str
    total_buy_count: int
    total_sell_count: int
    total_buy_amount: float
    total_sell_amount: float
    orders: List[OrderResponse]


@router.get("/daily-summary", response_model=DailySummaryResponse, summary="일일 매매 요약 조회")
async def get_daily_summary(
    date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """특정 날짜의 매매 요약(매수/매도 건수 및 금액)을 반환한다. date 미입력 시 오늘 날짜."""
    if is_demo_user(current_user.username):
        return get_demo_daily_summary()
    from datetime import date as date_type

    # date 파라미터가 있으면 ISO 형식(YYYY-MM-DD)으로 파싱 시도
    if date:
        try:
            target_date = date_type.fromisoformat(date)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식으로 입력해주세요.",
            )
    else:
        target_date = date_type.today()

    start = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0)
    end = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59)

    result = await db.execute(
        select(Order)
        .where(
            Order.user_id == current_user.id,
            Order.created_at >= start,
            Order.created_at <= end,
        )
        .order_by(Order.created_at.desc())
    )
    orders = result.scalars().all()

    buy_orders = [o for o in orders if o.order_type == "buy"]
    sell_orders = [o for o in orders if o.order_type == "sell"]

    total_buy_amount = sum((o.price or 0) * (o.quantity or 0) for o in buy_orders)
    total_sell_amount = sum((o.price or 0) * (o.quantity or 0) for o in sell_orders)

    return DailySummaryResponse(
        date=target_date.isoformat(),
        total_buy_count=len(buy_orders),
        total_sell_count=len(sell_orders),
        total_buy_amount=total_buy_amount,
        total_sell_amount=total_sell_amount,
        orders=orders,
    )


@router.put("/{order_id}/cancel", response_model=OrderResponse, summary="주문 취소")
async def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """pending 상태의 주문을 cancelled로 변경한다. 데모 모드에서는 403 반환."""
    if is_demo_user(current_user.username):
        raise HTTPException(status_code=403, detail="데모 모드에서는 사용할 수 없습니다.")
    result = await db.execute(
        select(Order).where(Order.id == order_id, Order.user_id == current_user.id)
    )
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다.")
    if order.status != "pending":
        raise HTTPException(status_code=400, detail=f"취소할 수 없는 주문 상태입니다: {order.status}")
    order.status = "cancelled"
    await db.commit()
    await db.refresh(order)
    return order


@router.get("", response_model=List[OrderResponse], summary="주문 목록 조회")
async def list_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """사용자의 주문 목록을 최신순으로 반환한다."""
    if is_demo_user(current_user.username):
        return get_demo_orders()
    result = await db.execute(
        select(Order)
        .where(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
        .limit(200)
    )
    return result.scalars().all()
