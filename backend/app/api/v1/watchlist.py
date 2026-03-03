"""
관심종목 API 엔드포인트
관심종목 그룹/항목 CRUD 및 전략 할당을 제공한다.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, is_demo_user
from app.core.database import get_db
from app.services.demo_data import get_demo_watchlist_groups
from app.models.user import User
from app.models.watchlist import WatchlistGroup, WatchlistItem
from app.schemas.watchlist import (
    WatchlistGroupCreate,
    WatchlistGroupResponse,
    WatchlistGroupUpdate,
    WatchlistItemCreate,
    WatchlistItemResponse,
    WatchlistItemStrategyAssign,
)

router = APIRouter()


@router.get("/groups", response_model=List[WatchlistGroupResponse], summary="관심종목 그룹 전체 조회")
async def list_groups(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """사용자의 모든 관심종목 그룹과 항목을 조회한다."""
    if is_demo_user(current_user.username):
        return get_demo_watchlist_groups()
    result = await db.execute(
        select(WatchlistGroup)
        .where(WatchlistGroup.user_id == current_user.id)
        .order_by(WatchlistGroup.sort_order, WatchlistGroup.id)
    )
    return result.scalars().all()


@router.post("/groups", response_model=WatchlistGroupResponse, status_code=201, summary="관심종목 그룹 생성")
async def create_group(
    body: WatchlistGroupCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """관심종목 그룹을 생성한다."""
    if is_demo_user(current_user.username):
        raise HTTPException(status_code=403, detail="데모 모드에서는 사용할 수 없습니다.")
    group = WatchlistGroup(user_id=current_user.id, name=body.name)
    db.add(group)
    await db.commit()
    await db.refresh(group)
    return group


@router.put("/groups/{group_id}", response_model=WatchlistGroupResponse, summary="관심종목 그룹 수정")
async def update_group(
    group_id: int,
    body: WatchlistGroupUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """관심종목 그룹명을 수정한다."""
    if is_demo_user(current_user.username):
        raise HTTPException(status_code=403, detail="데모 모드에서는 사용할 수 없습니다.")
    result = await db.execute(
        select(WatchlistGroup).where(
            WatchlistGroup.id == group_id, WatchlistGroup.user_id == current_user.id
        )
    )
    group = result.scalar_one_or_none()
    if group is None:
        raise HTTPException(status_code=404, detail="그룹을 찾을 수 없습니다.")
    group.name = body.name
    await db.commit()
    await db.refresh(group)
    return group


@router.delete("/groups/{group_id}", status_code=204, summary="관심종목 그룹 삭제")
async def delete_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """관심종목 그룹과 하위 항목을 모두 삭제한다. (cascade)"""
    if is_demo_user(current_user.username):
        raise HTTPException(status_code=403, detail="데모 모드에서는 사용할 수 없습니다.")
    result = await db.execute(
        select(WatchlistGroup).where(
            WatchlistGroup.id == group_id, WatchlistGroup.user_id == current_user.id
        )
    )
    group = result.scalar_one_or_none()
    if group is None:
        raise HTTPException(status_code=404, detail="그룹을 찾을 수 없습니다.")
    await db.delete(group)
    await db.commit()


@router.post("/groups/{group_id}/items", response_model=WatchlistItemResponse, status_code=201, summary="관심종목 추가")
async def add_item(
    group_id: int,
    body: WatchlistItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """관심종목 그룹에 종목을 추가한다."""
    if is_demo_user(current_user.username):
        raise HTTPException(status_code=403, detail="데모 모드에서는 사용할 수 없습니다.")
    # 그룹 소유권 확인
    result = await db.execute(
        select(WatchlistGroup).where(
            WatchlistGroup.id == group_id, WatchlistGroup.user_id == current_user.id
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="그룹을 찾을 수 없습니다.")

    item = WatchlistItem(
        group_id=group_id,
        stock_code=body.stock_code,
        stock_name=body.stock_name,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/groups/{group_id}/items/{item_id}", status_code=204, summary="관심종목 제거")
async def remove_item(
    group_id: int,
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """관심종목 그룹에서 종목을 제거한다."""
    if is_demo_user(current_user.username):
        raise HTTPException(status_code=403, detail="데모 모드에서는 사용할 수 없습니다.")
    result = await db.execute(
        select(WatchlistItem)
        .join(WatchlistGroup)
        .where(
            WatchlistItem.id == item_id,
            WatchlistItem.group_id == group_id,
            WatchlistGroup.user_id == current_user.id,
        )
    )
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=404, detail="항목을 찾을 수 없습니다.")
    await db.delete(item)
    await db.commit()


@router.put("/items/{item_id}/strategy", response_model=WatchlistItemResponse, summary="관심종목 전략 할당")
async def assign_strategy(
    item_id: int,
    body: WatchlistItemStrategyAssign,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """관심종목에 전략을 할당하거나 해제한다. (strategy_id=null이면 해제)"""
    if is_demo_user(current_user.username):
        raise HTTPException(status_code=403, detail="데모 모드에서는 사용할 수 없습니다.")
    result = await db.execute(
        select(WatchlistItem)
        .join(WatchlistGroup)
        .where(WatchlistItem.id == item_id, WatchlistGroup.user_id == current_user.id)
    )
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=404, detail="항목을 찾을 수 없습니다.")
    item.strategy_id = body.strategy_id
    await db.commit()
    await db.refresh(item)
    return item
