"""
안전장치 API 엔드포인트
긴급 전체 매도, 자동매매 제어, 안전장치 상태 조회를 제공한다.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, is_demo_user
from app.core.database import get_db
from app.services.demo_data import get_demo_safety_status
from app.models.user import User
from app.services.safety_guard import (
    emergency_sell_all,
    is_auto_trade_enabled,
    set_auto_trade,
    check_daily_loss_limit,
    check_max_daily_orders,
)
from app.services.system_monitor import get_system_status

router = APIRouter()


class AutoTradeRequest(BaseModel):
    enabled: bool


@router.get("/status", summary="안전장치 전체 상태 조회")
async def get_safety_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """자동매매 상태, 손실 한도, 에러 카운트 등 전체 안전장치 상태를 반환한다."""
    if is_demo_user(current_user.username):
        return get_demo_safety_status()

    auto_enabled = await is_auto_trade_enabled(current_user.id, db)
    loss_ok, loss_msg = await check_daily_loss_limit(current_user.id, db)
    order_ok, order_msg = await check_max_daily_orders(current_user.id, db)
    sys_status = await get_system_status(current_user.id)

    return {
        "auto_trade_enabled": auto_enabled,
        "daily_loss_check": {"ok": loss_ok, "message": loss_msg},
        "daily_order_check": {"ok": order_ok, "message": order_msg},
        "system": sys_status,
    }


@router.post("/auto-trade", summary="자동매매 활성화/비활성화")
async def toggle_auto_trade(
    body: AutoTradeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """자동매매를 활성화하거나 비활성화한다."""
    if is_demo_user(current_user.username):
        raise HTTPException(status_code=403, detail="데모 모드에서는 사용할 수 없습니다.")
    await set_auto_trade(current_user.id, body.enabled, db)
    return {"auto_trade_enabled": body.enabled}


@router.post("/emergency-sell", summary="긴급 전체 매도")
async def trigger_emergency_sell(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """모든 보유종목을 즉시 시장가로 매도하고 자동매매를 비활성화한다."""
    if is_demo_user(current_user.username):
        raise HTTPException(status_code=403, detail="데모 모드에서는 사용할 수 없습니다.")
    result = await emergency_sell_all(current_user.id, db)
    return result
