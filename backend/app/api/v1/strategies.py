"""
전략 관련 API 엔드포인트
전략 목록/파라미터 조회, 활성화/비활성화, 신호 평가를 제공한다.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.strategy import Strategy, StrategyParam
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


@router.get("", response_model=List[StrategyResponse], summary="전략 목록 조회")
async def list_strategies(
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """전체 전략 목록과 파라미터를 반환한다."""
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
