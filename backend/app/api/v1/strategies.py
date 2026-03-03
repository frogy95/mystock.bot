"""
전략 관련 API 엔드포인트
전략 목록/파라미터 조회, 활성화/비활성화, 신호 평가, 전략 복사를 제공한다.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, delete, update, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, is_demo_user
from app.core.database import get_db
from app.services.demo_data import (
    get_demo_strategies,
    get_demo_strategy,
    get_demo_strategy_performance,
)
from app.models.backtest import BacktestResult
from app.models.holding import Holding
from app.models.order import Order
from app.models.strategy import Strategy, StrategyParam
from app.models.user import User
from app.models.watchlist import WatchlistItem
from app.schemas.strategy import (
    StrategyActivateRequest,
    StrategyParamBulkUpdate,
    StrategyRenameRequest,
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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """각 전략의 매매 횟수, 승률, 적용 종목 수를 집계하여 반환한다."""
    if is_demo_user(current_user.username):
        return get_demo_strategy_performance()

    # 현재 사용자가 접근 가능한 전략만 조회 (프리셋 + 본인 소유)
    result = await db.execute(
        select(Strategy)
        .where(or_(Strategy.user_id.is_(None), Strategy.user_id == current_user.id))
        .order_by(Strategy.id)
    )
    strategies = result.scalars().all()

    # 주문 통계를 SQL 집계 쿼리 1번으로 처리 (N+1 → 1), 현재 사용자 주문만 필터
    from sqlalchemy import case as sql_case
    order_result = await db.execute(
        select(
            Order.strategy_id,
            func.count(Order.id).label("trade_count"),
            func.sum(sql_case((Order.order_type == "buy", 1), else_=0)).label("buy_count"),
            func.sum(sql_case((Order.order_type == "sell", 1), else_=0)).label("sell_count"),
        )
        .where(Order.strategy_id.isnot(None))
        .where(Order.user_id == current_user.id)
        .group_by(Order.strategy_id)
    )
    order_stats = {row.strategy_id: row for row in order_result}

    # 관심종목 적용 수를 SQL 집계 쿼리 1번으로 처리 (N+1 → 1)
    stock_result = await db.execute(
        select(WatchlistItem.strategy_id, func.count(WatchlistItem.id).label("count"))
        .where(WatchlistItem.strategy_id.isnot(None))
        .group_by(WatchlistItem.strategy_id)
    )
    stock_stats = {row.strategy_id: row.count for row in stock_result}

    performance_list = []
    for strategy in strategies:
        stats = order_stats.get(strategy.id)
        trade_count = stats.trade_count if stats else 0
        buy_count = stats.buy_count if stats else 0
        sell_count = stats.sell_count if stats else 0
        win_rate = round((sell_count / trade_count * 100) if trade_count > 0 else 0.0, 2)
        active_stocks = stock_stats.get(strategy.id, 0)
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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """프리셋 전략과 본인 소유 전략 목록을 파라미터와 함께 반환한다."""
    if is_demo_user(current_user.username):
        return get_demo_strategies()

    # 프리셋(user_id IS NULL) 또는 본인 소유(user_id == current_user.id) 전략만 조회
    result = await db.execute(
        select(Strategy)
        .where(or_(Strategy.user_id.is_(None), Strategy.user_id == current_user.id))
        .order_by(Strategy.id)
    )
    strategies = result.scalars().all()

    # 모든 전략 파라미터를 쿼리 1번으로 로드 (N+1 → 1)
    strategy_ids = [s.id for s in strategies]
    param_result = await db.execute(
        select(StrategyParam).where(StrategyParam.strategy_id.in_(strategy_ids))
    )
    params_by_strategy: dict[int, list] = {}
    for p in param_result.scalars().all():
        params_by_strategy.setdefault(p.strategy_id, []).append(p)

    for s in strategies:
        s.params = params_by_strategy.get(s.id, [])

    return strategies


@router.get("/{strategy_id}", response_model=StrategyResponse, summary="전략 상세 조회")
async def get_strategy_detail(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """프리셋 또는 본인 소유 전략의 상세 정보와 파라미터를 반환한다."""
    if is_demo_user(current_user.username):
        strategy = get_demo_strategy(strategy_id)
        if strategy is None:
            raise HTTPException(status_code=404, detail="전략을 찾을 수 없습니다.")
        return strategy

    # 프리셋(user_id IS NULL) 또는 본인 소유(user_id == current_user.id) 전략만 접근 허용
    result = await db.execute(
        select(Strategy).where(
            Strategy.id == strategy_id,
            or_(Strategy.user_id.is_(None), Strategy.user_id == current_user.id),
        )
    )
    strategy = result.scalar_one_or_none()
    if strategy is None:
        raise HTTPException(status_code=404, detail="전략을 찾을 수 없습니다.")

    # 파라미터 로드
    param_result = await db.execute(
        select(StrategyParam).where(StrategyParam.strategy_id == strategy_id)
    )
    strategy.params = param_result.scalars().all()
    return strategy


@router.put("/{strategy_id}/activate", response_model=StrategyResponse, summary="전략 활성화/비활성화")
async def toggle_strategy(
    strategy_id: int,
    body: StrategyActivateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """본인 소유 전략의 활성화 상태를 변경한다. (프리셋 전략은 변경 불가)"""
    if is_demo_user(current_user.username):
        raise HTTPException(status_code=403, detail="데모 모드에서는 사용할 수 없습니다.")

    # 본인 소유 전략만 활성화/비활성화 가능 (프리셋은 차단)
    result = await db.execute(
        select(Strategy).where(
            Strategy.id == strategy_id,
            Strategy.user_id == current_user.id,
        )
    )
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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """본인 소유 전략 파라미터를 일괄 업데이트한다. (기존 파라미터 삭제 후 재생성, 프리셋은 변경 불가)"""
    if is_demo_user(current_user.username):
        raise HTTPException(status_code=403, detail="데모 모드에서는 사용할 수 없습니다.")

    # 본인 소유 전략만 파라미터 변경 가능 (프리셋은 차단)
    result = await db.execute(
        select(Strategy).where(
            Strategy.id == strategy_id,
            Strategy.user_id == current_user.id,
        )
    )
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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """프리셋 또는 본인 소유 전략으로 종목의 현재 신호를 평가한다."""
    if is_demo_user(current_user.username):
        raise HTTPException(status_code=403, detail="데모 모드에서는 사용할 수 없습니다.")

    # 프리셋(user_id IS NULL) 또는 본인 소유(user_id == current_user.id) 전략만 평가 허용
    result = await db.execute(
        select(Strategy).where(
            Strategy.id == strategy_id,
            or_(Strategy.user_id.is_(None), Strategy.user_id == current_user.id),
        )
    )
    strategy = result.scalar_one_or_none()
    if strategy is None:
        raise HTTPException(status_code=404, detail="전략을 찾을 수 없습니다.")

    # 파라미터 로드
    param_result = await db.execute(
        select(StrategyParam).where(StrategyParam.strategy_id == strategy_id)
    )
    strategy.params = param_result.scalars().all()

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


@router.post("/{strategy_id}/clone", response_model=StrategyResponse, summary="전략 복사")
async def clone_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """프리셋 또는 본인 소유 전략을 복사하여 새 전략을 생성한다. 복사된 전략은 본인 소유로 설정된다."""
    if is_demo_user(current_user.username):
        raise HTTPException(status_code=403, detail="데모 모드에서는 사용할 수 없습니다.")

    # 프리셋(user_id IS NULL) 또는 본인 소유(user_id == current_user.id) 전략만 복사 허용
    result = await db.execute(
        select(Strategy).where(
            Strategy.id == strategy_id,
            or_(Strategy.user_id.is_(None), Strategy.user_id == current_user.id),
        )
    )
    original = result.scalar_one_or_none()
    if original is None:
        raise HTTPException(status_code=404, detail="전략을 찾을 수 없습니다.")

    # 원본 파라미터 로드
    param_result = await db.execute(
        select(StrategyParam).where(StrategyParam.strategy_id == strategy_id)
    )
    original_params = param_result.scalars().all()

    # 새 전략 생성 (복사본은 본인 소유, 프리셋 아님)
    cloned = Strategy(
        name=f"{original.name} (복사본)",
        strategy_type=original.strategy_type,
        is_active=original.is_active,
        is_preset=False,
        user_id=current_user.id,
    )
    db.add(cloned)
    await db.flush()  # cloned.id를 얻기 위해 flush

    # 파라미터 복사
    for p in original_params:
        db.add(
            StrategyParam(
                strategy_id=cloned.id,
                param_key=p.param_key,
                param_value=p.param_value,
                param_type=p.param_type,
            )
        )

    await db.commit()
    return await _get_strategy_with_params(cloned.id, db)


@router.put("/{strategy_id}/name", response_model=StrategyResponse, summary="전략 이름 변경")
async def rename_strategy(
    strategy_id: int,
    body: StrategyRenameRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """본인 소유 전략의 이름을 변경한다. (프리셋 전략은 변경 불가)"""
    if is_demo_user(current_user.username):
        raise HTTPException(status_code=403, detail="데모 모드에서는 사용할 수 없습니다.")

    # 본인 소유이며 프리셋이 아닌 전략만 이름 변경 가능
    result = await db.execute(
        select(Strategy).where(
            Strategy.id == strategy_id,
            Strategy.user_id == current_user.id,
            Strategy.is_preset.is_(False),
        )
    )
    strategy = result.scalar_one_or_none()
    if strategy is None:
        raise HTTPException(status_code=404, detail="전략을 찾을 수 없습니다.")

    strategy.name = body.name
    await db.commit()
    return await _get_strategy_with_params(strategy_id, db)


@router.delete("/{strategy_id}", status_code=204, summary="전략 삭제")
async def delete_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """본인 소유 전략을 삭제한다. (프리셋 전략은 삭제 불가)"""
    if is_demo_user(current_user.username):
        raise HTTPException(status_code=403, detail="데모 모드에서는 사용할 수 없습니다.")

    # 본인 소유이며 프리셋이 아닌 전략만 삭제 가능
    result = await db.execute(
        select(Strategy).where(
            Strategy.id == strategy_id,
            Strategy.user_id == current_user.id,
            Strategy.is_preset.is_(False),
        )
    )
    strategy = result.scalar_one_or_none()
    if strategy is None:
        raise HTTPException(status_code=404, detail="전략을 찾을 수 없습니다.")

    # FK 참조 NULL 처리 후 삭제 (NO ACTION 제약 해제)
    await db.execute(
        update(WatchlistItem).where(WatchlistItem.strategy_id == strategy_id).values(strategy_id=None)
    )
    await db.execute(
        update(Holding).where(Holding.sell_strategy_id == strategy_id).values(sell_strategy_id=None)
    )
    await db.execute(
        update(Order).where(Order.strategy_id == strategy_id).values(strategy_id=None)
    )
    await db.execute(
        update(BacktestResult).where(BacktestResult.strategy_id == strategy_id).values(strategy_id=None)
    )
    await db.execute(
        delete(StrategyParam).where(StrategyParam.strategy_id == strategy_id)
    )
    await db.delete(strategy)
    await db.commit()
