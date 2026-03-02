"""
전략 관련 API 엔드포인트
전략 목록/파라미터 조회, 활성화/비활성화, 신호 평가를 제공한다.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, is_demo_user
from app.core.database import get_db
from app.services.demo_data import (
    get_demo_strategies,
    get_demo_strategy,
    get_demo_strategy_performance,
)
from app.models.order import Order
from app.models.strategy import Strategy, StrategyParam
from app.models.watchlist import WatchlistItem
from app.schemas.strategy import (
    StrategyActivateRequest,
    StrategyParamBulkUpdate,
    StrategyResponse,
    StrategySignalResponse,
)
from app.services.kis_client import kis_client
from app.services.strategy_engine import get_strategy

router = APIRouter()


async def _get_strategy_with_params(
    strategy_id: int, db: AsyncSession
) -> Strategy | None:
    """전략과 파라미터를 함께 조회한다."""
    result = await db.execute(
        select(Strategy).where(Strategy.id == strategy_id)
    )
    strategy = result.scalar_one_or_none()
    if strategy is None:
        return None

    # 파라미터 로드
    param_result = await db.execute(
        select(StrategyParam).where(StrategyParam.strategy_id == strategy_id)
    )
    strategy.params = param_result.scalars().all()
    return strategy


class StrategyPerformanceResponse(BaseModel):
    """전략 성과 응답 스키마"""

    id: int
    name: str
    trade_count: int
    buy_count: int
    sell_count: int
    win_rate: float
    active_stocks: int
    is_active: bool


@router.get("/performance", response_model=List[StrategyPerformanceResponse], summary="전략별 성과 집계")
async def get_strategy_performance(
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """각 전략의 매매 횟수, 승률, 적용 종목 수를 집계하여 반환한다."""
    if is_demo_user(current_user):
        return get_demo_strategy_performance()
    result = await db.execute(select(Strategy).order_by(Strategy.id))
    strategies = result.scalars().all()

    performance_list = []
    for strategy in strategies:
        # 해당 전략으로 실행된 주문 집계
        order_result = await db.execute(
            select(Order).where(Order.strategy_id == strategy.id)
        )
        orders = order_result.scalars().all()

        buy_count = sum(1 for o in orders if o.order_type == "buy")
        sell_count = sum(1 for o in orders if o.order_type == "sell")
        trade_count = len(orders)
        # 승률: 매도 주문 수 / 전체 주문 수 (매도 = 수익 실현 가정)
        win_rate = round((sell_count / trade_count * 100) if trade_count > 0 else 0.0, 2)

        # 적용 종목 수 (관심종목에 전략이 할당된 종목 수)
        stock_result = await db.execute(
            select(func.count(WatchlistItem.id)).where(
                WatchlistItem.strategy_id == strategy.id
            )
        )
        active_stocks = stock_result.scalar() or 0

        performance_list.append(
            StrategyPerformanceResponse(
                id=strategy.id,
                name=strategy.name,
                trade_count=trade_count,
                buy_count=buy_count,
                sell_count=sell_count,
                win_rate=win_rate,
                active_stocks=active_stocks,
                is_active=strategy.is_active,
            )
        )

    return performance_list


@router.get("", response_model=List[StrategyResponse], summary="전략 목록 조회")
async def list_strategies(
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """전체 전략 목록과 파라미터를 반환한다."""
    if is_demo_user(current_user):
        return get_demo_strategies()
    result = await db.execute(select(Strategy).order_by(Strategy.id))
    strategies = result.scalars().all()

    # 각 전략의 파라미터 로드
    response = []
    for s in strategies:
        param_result = await db.execute(
            select(StrategyParam).where(StrategyParam.strategy_id == s.id)
        )
        s.params = param_result.scalars().all()
        response.append(s)

    return response


@router.get("/{strategy_id}", response_model=StrategyResponse, summary="전략 상세 조회")
async def get_strategy_detail(
    strategy_id: int,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """단일 전략 상세 정보와 파라미터를 반환한다."""
    if is_demo_user(current_user):
        strategy = get_demo_strategy(strategy_id)
        if strategy is None:
            raise HTTPException(status_code=404, detail="전략을 찾을 수 없습니다.")
        return strategy
    strategy = await _get_strategy_with_params(strategy_id, db)
    if strategy is None:
        raise HTTPException(status_code=404, detail="전략을 찾을 수 없습니다.")
    return strategy


@router.put("/{strategy_id}/activate", response_model=StrategyResponse, summary="전략 활성화/비활성화")
async def toggle_strategy(
    strategy_id: int,
    body: StrategyActivateRequest,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """전략의 활성화 상태를 변경한다."""
    if is_demo_user(current_user):
        raise HTTPException(status_code=403, detail="데모 모드에서는 사용할 수 없습니다.")
    result = await db.execute(select(Strategy).where(Strategy.id == strategy_id))
    strategy = result.scalar_one_or_none()
    if strategy is None:
        raise HTTPException(status_code=404, detail="전략을 찾을 수 없습니다.")

    strategy.is_active = body.is_active
    await db.commit()
    return await _get_strategy_with_params(strategy_id, db)


@router.put("/{strategy_id}/params", response_model=StrategyResponse, summary="전략 파라미터 업데이트")
async def update_strategy_params(
    strategy_id: int,
    body: StrategyParamBulkUpdate,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """전략 파라미터를 일괄 업데이트한다. (기존 파라미터 삭제 후 재생성)"""
    if is_demo_user(current_user):
        raise HTTPException(status_code=403, detail="데모 모드에서는 사용할 수 없습니다.")
    result = await db.execute(select(Strategy).where(Strategy.id == strategy_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="전략을 찾을 수 없습니다.")

    # 기존 파라미터 삭제
    await db.execute(
        delete(StrategyParam).where(StrategyParam.strategy_id == strategy_id)
    )

    # 신규 파라미터 생성
    for p in body.params:
        db.add(
            StrategyParam(
                strategy_id=strategy_id,
                param_key=p.param_key,
                param_value=p.param_value,
                param_type=p.param_type,
            )
        )

    await db.commit()
    return await _get_strategy_with_params(strategy_id, db)


@router.post("/{strategy_id}/evaluate/{symbol}", response_model=StrategySignalResponse, summary="전략 신호 평가")
async def evaluate_strategy_signal(
    strategy_id: int,
    symbol: str,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """특정 전략으로 종목의 현재 신호를 평가한다."""
    if is_demo_user(current_user):
        raise HTTPException(status_code=403, detail="데모 모드에서는 사용할 수 없습니다.")
    strategy = await _get_strategy_with_params(strategy_id, db)
    if strategy is None:
        raise HTTPException(status_code=404, detail="전략을 찾을 수 없습니다.")

    engine = get_strategy(strategy.name)
    if engine is None:
        raise HTTPException(status_code=400, detail=f"전략 엔진 '{strategy.name}'을 찾을 수 없습니다.")

    if not kis_client.is_available():
        raise HTTPException(status_code=503, detail="KIS API가 설정되지 않았습니다.")

    chart_data = await kis_client.get_chart(symbol, period="day", count=90)
    if not chart_data:
        raise HTTPException(status_code=404, detail=f"종목 {symbol}의 차트 데이터를 가져올 수 없습니다.")

    params = {p.param_key: float(p.param_value) if p.param_type == "float" else p.param_value
               for p in strategy.params}

    signal = engine.evaluate_from_ohlcv(chart_data, params)
    return StrategySignalResponse(
        symbol=symbol,
        signal_type=signal.signal_type,
        confidence=signal.confidence,
        reason=signal.reason,
        target_price=signal.target_price,
    )
