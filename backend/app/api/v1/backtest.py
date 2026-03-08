"""
백테스팅 API 엔드포인트
POST /backtest/run  - 백테스팅 실행 및 결과 저장
GET  /backtest/results      - 최근 결과 목록 조회 (최대 20건)
GET  /backtest/results/{id} - 특정 결과 상세 조회
"""
import asyncio
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, is_demo_user
from app.services.demo_data import get_demo_backtest_results, get_demo_backtest_result
from app.core.database import get_db
from app.models.backtest import BacktestResult
from app.models.holding import Holding
from app.models.strategy import Strategy
from app.models.user import User
from app.models.watchlist import WatchlistItem
from app.schemas.backtest import (
    BacktestMultiResponse,
    BacktestMultiResultItem,
    BacktestMultiRunRequest,
    BacktestRankingEntry,
    BacktestRunRequest,
    BacktestResultResponse,
    EquityPoint,
    BacktestTrade,
    StockStatusResponse,
    WatchlistStatusItem,
)
from app.services.backtest_engine import BacktestConfig, run_backtest
from app.services.backtest_metrics import calculate_metrics, calculate_ranking_score

logger = logging.getLogger("mystock.bot")
router = APIRouter(prefix="/backtest", tags=["백테스팅"])


def _to_response(record: BacktestResult) -> BacktestResultResponse:
    """BacktestResult 모델을 응답 스키마로 변환한다."""
    data = record.result_data or {}
    equity_raw = data.get("equity_curve", [])
    equity_curve = [
        EquityPoint(date=ep["date"], value=ep["value"], benchmark=ep.get("benchmark", 0.0), stock_buyhold=ep.get("stock_buyhold", 0.0))
        for ep in equity_raw
        if isinstance(ep, dict) and "date" in ep and "value" in ep
    ]
    trades_raw = data.get("trades", [])
    trades = [
        BacktestTrade(
            type=t["type"],
            date=t.get("date", ""),
            price=float(t["price"]),
            qty=int(t["qty"]),
            amount=float(t["amount"]),
            pnl=float(t["pnl"]) if t.get("pnl") is not None else None,
        )
        for t in trades_raw
        if isinstance(t, dict)
    ]
    return BacktestResultResponse(
        id=record.id,
        symbol=record.symbol or "",
        strategy_name=data.get("strategy_name", ""),
        start_date=str(record.start_date) if record.start_date else "",
        end_date=str(record.end_date) if record.end_date else "",
        total_return=float(data.get("total_return", 0.0)),
        cagr=float(data.get("cagr", 0.0)),
        mdd=float(data.get("mdd", 0.0)),
        sharpe_ratio=float(data.get("sharpe_ratio", 0.0)),
        total_trades=int(data.get("total_trades", 0)),
        win_rate=float(data.get("win_rate", 0.0)),
        benchmark_return=float(data.get("benchmark_return", 0.0)),
        equity_curve=equity_curve,
        trades=trades,
        created_at=str(record.created_at),
    )


@router.post("/run", response_model=BacktestResultResponse, summary="백테스팅 실행")
async def run_backtest_api(
    request: BacktestRunRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    백테스팅을 실행하고 결과를 DB에 저장한다.
    KIS API 차트 데이터를 조회하여 전략 신호를 생성한 후 포트폴리오를 시뮬레이션한다.
    """
    if is_demo_user(current_user.username):
        raise HTTPException(status_code=403, detail="데모 모드에서는 사용할 수 없습니다.")

    # 커스텀 전략인 경우 DB에서 조건 로드
    buy_conditions = None
    sell_conditions = None
    if request.strategy_id is not None:
        from sqlalchemy import or_
        strategy_result = await db.execute(
            select(Strategy).where(
                Strategy.id == request.strategy_id,
                or_(Strategy.user_id.is_(None), Strategy.user_id == current_user.id),
                Strategy.is_preset.is_(False),
            )
        )
        custom_strategy = strategy_result.scalar_one_or_none()
        if custom_strategy and custom_strategy.buy_conditions and custom_strategy.sell_conditions:
            buy_conditions = custom_strategy.buy_conditions
            sell_conditions = custom_strategy.sell_conditions

    try:
        config = BacktestConfig(
            symbol=request.symbol,
            strategy_name=request.strategy_name,
            params=request.params,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_cash=request.initial_cash,
            buy_conditions=buy_conditions,
            sell_conditions=sell_conditions,
        )
        result = await run_backtest(config)
        metrics = calculate_metrics(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"백테스팅 실행 오류 [{request.symbol}/{request.strategy_name}]: {e}")
        raise HTTPException(status_code=500, detail="백테스팅 실행 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")

    # DB에 결과 저장
    result_data = {
        "strategy_name": request.strategy_name,
        "params": request.params,
        "initial_cash": request.initial_cash,
        **metrics,
    }
    backtest_record = BacktestResult(
        user_id=current_user.id,         # 사용자별 결과 격리
        strategy_id=None,                # 커스텀 백테스트는 전략 레코드 없음
        symbol=request.symbol,
        start_date=request.start_date,
        end_date=request.end_date,
        total_return=metrics.get("total_return"),
        max_drawdown=metrics.get("mdd"),
        sharpe_ratio=metrics.get("sharpe_ratio"),
        win_rate=metrics.get("win_rate"),
        result_data=result_data,
    )
    db.add(backtest_record)
    await db.commit()
    await db.refresh(backtest_record)

    logger.info(
        f"백테스팅 완료 [{request.symbol}/{request.strategy_name}]: "
        f"수익률 {metrics.get('total_return')}%, 거래 {metrics.get('total_trades')}건"
    )
    return _to_response(backtest_record)


@router.get("/results", response_model=list[BacktestResultResponse], summary="백테스팅 결과 목록")
async def list_results(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """최근 백테스팅 결과 목록을 반환한다 (최대 20건, 최신순, 본인 결과만)."""
    if is_demo_user(current_user.username):
        return get_demo_backtest_results()

    # 본인 결과만 조회 (사용자별 데이터 격리)
    result = await db.execute(
        select(BacktestResult)
        .where(BacktestResult.user_id == current_user.id)
        .order_by(BacktestResult.created_at.desc())
        .limit(20)
    )
    records = result.scalars().all()
    return [_to_response(r) for r in records]


@router.get("/results/{result_id}", response_model=BacktestResultResponse, summary="백테스팅 결과 상세")
async def get_result(
    result_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """특정 백테스팅 결과를 반환한다. (본인 결과만 접근 허용)"""
    if is_demo_user(current_user.username):
        record = get_demo_backtest_result(result_id)
        if record is None:
            raise HTTPException(status_code=404, detail="백테스팅 결과를 찾을 수 없습니다.")
        return record

    # 소유권 확인: 본인 결과만 접근 허용
    result = await db.execute(
        select(BacktestResult).where(
            BacktestResult.id == result_id,
            BacktestResult.user_id == current_user.id,
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="백테스팅 결과를 찾을 수 없습니다.")
    return _to_response(record)


@router.post("/run-multi", response_model=BacktestMultiResponse, summary="다중 전략 백테스트 실행")
async def run_backtest_multi(
    request: BacktestMultiRunRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    여러 전략을 한 번에 백테스트하고 랭킹을 반환한다.
    차트 데이터는 1회만 조회하고, 전략별 신호 생성은 병렬 처리한다.
    """
    if is_demo_user(current_user.username):
        raise HTTPException(status_code=403, detail="데모 모드에서는 사용할 수 없습니다.")

    # 전략 목록 조회 (프리셋 + 본인 소유)
    strategy_result = await db.execute(
        select(Strategy).where(
            Strategy.id.in_(request.strategy_ids),
            or_(Strategy.user_id.is_(None), Strategy.user_id == current_user.id),
        )
    )
    strategies = {s.id: s for s in strategy_result.scalars().all()}

    if not strategies:
        raise HTTPException(status_code=404, detail="선택한 전략을 찾을 수 없습니다.")

    async def run_single(strategy: Strategy) -> dict | None:
        """단일 전략 백테스트를 실행하고 결과를 반환한다."""
        try:
            # 커스텀 전략 조건 파싱
            buy_cond = strategy.buy_conditions if strategy.buy_conditions else None
            sell_cond = strategy.sell_conditions if strategy.sell_conditions else None

            config = BacktestConfig(
                symbol=request.symbol,
                strategy_name=strategy.name,
                params={},
                start_date=request.start_date,
                end_date=request.end_date,
                initial_cash=request.initial_cash,
                buy_conditions=buy_cond,
                sell_conditions=sell_cond,
            )
            result = await run_backtest(config)
            metrics = calculate_metrics(result)
            return {
                "strategy_id": strategy.id,
                "strategy_name": strategy.name,
                **metrics,
            }
        except Exception as e:
            logger.warning(f"다중 백테스트 전략 오류 [{strategy.name}]: {e}")
            return None

    # 병렬 실행
    tasks = [run_single(s) for s in strategies.values()]
    raw_results = await asyncio.gather(*tasks)
    valid_results = [r for r in raw_results if r is not None]

    if not valid_results:
        raise HTTPException(status_code=400, detail="모든 전략 백테스트가 실패했습니다.")

    # 랭킹 계산
    ranked = calculate_ranking_score(valid_results)

    # 응답 구성
    result_items = []
    for r in valid_results:
        equity_curve = [
            EquityPoint(date=ep["date"], value=ep["value"], benchmark=ep.get("benchmark", 0.0), stock_buyhold=ep.get("stock_buyhold", 0.0))
            for ep in r.get("equity_curve", [])
            if isinstance(ep, dict) and "date" in ep and "value" in ep
        ]
        result_items.append(BacktestMultiResultItem(
            strategy_id=r["strategy_id"],
            strategy_name=r["strategy_name"],
            total_return=float(r.get("total_return", 0.0)),
            cagr=float(r.get("cagr", 0.0)),
            mdd=float(r.get("mdd", 0.0)),
            sharpe_ratio=float(r.get("sharpe_ratio", 0.0)),
            win_rate=float(r.get("win_rate", 0.0)),
            total_trades=int(r.get("total_trades", 0)),
            benchmark_return=float(r.get("benchmark_return", 0.0)),
            equity_curve=equity_curve,
        ))

    ranking_items = [
        BacktestRankingEntry(
            strategy_id=r["strategy_id"],
            strategy_name=r["strategy_name"],
            rank=r["rank"],
            score=r["score"],
            total_return=float(r.get("total_return", 0.0)),
            cagr=float(r.get("cagr", 0.0)),
            mdd=float(r.get("mdd", 0.0)),
            sharpe_ratio=float(r.get("sharpe_ratio", 0.0)),
            win_rate=float(r.get("win_rate", 0.0)),
            total_trades=int(r.get("total_trades", 0)),
        )
        for r in ranked
    ]

    return BacktestMultiResponse(
        symbol=request.symbol,
        results=result_items,
        ranking=ranking_items,
    )


@router.get("/stock-status/{symbol}", response_model=StockStatusResponse, summary="종목 보유/관심 상태 확인")
async def get_stock_status(
    symbol: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """종목의 보유 여부와 관심종목 등록 여부를 확인한다."""
    if is_demo_user(current_user.username):
        return StockStatusResponse(is_holding=False, is_watchlist=False)

    # 보유 여부 확인 (컬럼명: stock_code)
    holding_result = await db.execute(
        select(Holding).where(
            Holding.user_id == current_user.id,
            Holding.stock_code == symbol,
        )
    )
    holding = holding_result.scalar_one_or_none()

    # 관심종목 여부 확인 (그룹명 포함, 컬럼명: stock_code)
    from app.models.watchlist import WatchlistGroup
    watchlist_result = await db.execute(
        select(WatchlistItem, WatchlistGroup.name.label("group_name"), Strategy.name.label("strategy_name"))
        .join(WatchlistGroup, WatchlistItem.group_id == WatchlistGroup.id)
        .outerjoin(Strategy, WatchlistItem.strategy_id == Strategy.id)
        .where(
            WatchlistGroup.user_id == current_user.id,
            WatchlistItem.stock_code == symbol,
        )
    )
    watchlist_rows = watchlist_result.all()

    # 보유 중인 경우 매도 전략명 조회
    sell_strategy_name = None
    if holding and holding.sell_strategy_id:
        strat_result = await db.execute(select(Strategy).where(Strategy.id == holding.sell_strategy_id))
        sell_strategy = strat_result.scalar_one_or_none()
        sell_strategy_name = sell_strategy.name if sell_strategy else None

    watchlist_items = [
        WatchlistStatusItem(
            item_id=row.WatchlistItem.id,
            group_name=row.group_name,
            current_strategy=row.strategy_name,
        )
        for row in watchlist_rows
    ]

    return StockStatusResponse(
        is_holding=holding is not None,
        holding_id=holding.id if holding else None,
        current_sell_strategy=sell_strategy_name,
        is_watchlist=len(watchlist_rows) > 0,
        watchlist_items=watchlist_items,
    )
