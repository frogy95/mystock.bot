"""
보유종목 API 엔드포인트
보유종목 조회, KIS 동기화, 손절/익절/전략 설정을 제공한다.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, is_demo_user
from app.core.database import get_db
from app.services.demo_data import (
    get_demo_holdings,
    get_demo_portfolio_summary,
)
from app.models.holding import Holding
from app.models.user import User
from app.schemas.holding import (
    HoldingResponse,
    HoldingSellStrategyUpdate,
    HoldingStopLossUpdate,
    PortfolioSummaryResponse,
    PortfolioSyncResponse,
)
from app.services.holding_service import calculate_summary, sync_with_kis

router = APIRouter()


async def _get_user_id(username: str, db: AsyncSession) -> int:
    """사용자명으로 user_id를 조회한다."""
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return user.id


@router.get("", response_model=List[HoldingResponse], summary="보유종목 목록 조회")
async def list_holdings(
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """DB에 저장된 보유종목 목록을 조회한다."""
    if is_demo_user(current_user):
        return get_demo_holdings()
    user_id = await _get_user_id(current_user, db)
    result = await db.execute(
        select(Holding)
        .where(Holding.user_id == user_id, Holding.quantity > 0)
        .order_by(Holding.id)
    )
    return result.scalars().all()


@router.post("/sync", response_model=PortfolioSyncResponse, summary="KIS 잔고 동기화")
async def sync_holdings(
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if is_demo_user(current_user):
        raise HTTPException(status_code=403, detail="데모 모드에서는 사용할 수 없습니다.")
    """KIS 실제 잔고를 조회하여 DB를 동기화한다."""
    user_id = await _get_user_id(current_user, db)
    try:
        holdings = await sync_with_kis(user_id, db)
        active = [h for h in holdings if h.quantity > 0]
        return PortfolioSyncResponse(
            synced_count=len(active),
            holdings=active,
        )
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.put("/{holding_id}/stop-loss", response_model=HoldingResponse, summary="손절/익절 설정")
async def update_stop_loss(
    holding_id: int,
    body: HoldingStopLossUpdate,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """보유종목의 손절/익절 비율을 설정한다."""
    if is_demo_user(current_user):
        raise HTTPException(status_code=403, detail="데모 모드에서는 사용할 수 없습니다.")
    user_id = await _get_user_id(current_user, db)
    result = await db.execute(
        select(Holding).where(Holding.id == holding_id, Holding.user_id == user_id)
    )
    holding = result.scalar_one_or_none()
    if holding is None:
        raise HTTPException(status_code=404, detail="보유종목을 찾을 수 없습니다.")
    holding.stop_loss_rate = body.stop_loss_rate
    holding.take_profit_rate = body.take_profit_rate
    await db.commit()
    await db.refresh(holding)
    return holding


@router.put("/{holding_id}/sell-strategy", response_model=HoldingResponse, summary="매도 전략 설정")
async def update_sell_strategy(
    holding_id: int,
    body: HoldingSellStrategyUpdate,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """보유종목의 매도 전략을 설정한다."""
    if is_demo_user(current_user):
        raise HTTPException(status_code=403, detail="데모 모드에서는 사용할 수 없습니다.")
    user_id = await _get_user_id(current_user, db)
    result = await db.execute(
        select(Holding).where(Holding.id == holding_id, Holding.user_id == user_id)
    )
    holding = result.scalar_one_or_none()
    if holding is None:
        raise HTTPException(status_code=404, detail="보유종목을 찾을 수 없습니다.")
    holding.sell_strategy_id = body.sell_strategy_id
    await db.commit()
    await db.refresh(holding)
    return holding


@router.get("/summary", response_model=PortfolioSummaryResponse, summary="포트폴리오 요약")
async def get_summary(
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """포트폴리오 전체 요약 (총평가/손익/예수금 등)을 반환한다."""
    if is_demo_user(current_user):
        return get_demo_portfolio_summary()
    user_id = await _get_user_id(current_user, db)
    summary = await calculate_summary(user_id, db)
    return summary
