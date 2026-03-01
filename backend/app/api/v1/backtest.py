"""
백테스팅 API 엔드포인트
POST /backtest/run  - 백테스팅 실행 및 결과 저장
GET  /backtest/results      - 최근 결과 목록 조회 (최대 20건)
GET  /backtest/results/{id} - 특정 결과 상세 조회
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.backtest import BacktestResult
from app.schemas.backtest import BacktestRunRequest, BacktestResultResponse, EquityPoint
from app.services.backtest_engine import BacktestConfig, run_backtest
from app.services.backtest_metrics import calculate_metrics

logger = logging.getLogger("mystock.bot")
router = APIRouter(prefix="/backtest", tags=["백테스팅"])


def _to_response(record: BacktestResult) -> BacktestResultResponse:
    """BacktestResult 모델을 응답 스키마로 변환한다."""
    data = record.result_data or {}
    equity_raw = data.get("equity_curve", [])
    equity_curve = [
        EquityPoint(date=ep["date"], value=ep["value"])
        for ep in equity_raw
        if isinstance(ep, dict) and "date" in ep and "value" in ep
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
        created_at=str(record.created_at),
    )


@router.post("/run", response_model=BacktestResultResponse, summary="백테스팅 실행")
async def run_backtest_api(
    request: BacktestRunRequest,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """
    백테스팅을 실행하고 결과를 DB에 저장한다.
    KIS API 차트 데이터를 조회하여 전략 신호를 생성한 후 포트폴리오를 시뮬레이션한다.
    """
    try:
        config = BacktestConfig(
            symbol=request.symbol,
            strategy_name=request.strategy_name,
            params=request.params,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_cash=request.initial_cash,
        )
        result = await run_backtest(config)
        metrics = calculate_metrics(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"백테스팅 실행 오류 [{request.symbol}/{request.strategy_name}]: {e}")
        raise HTTPException(status_code=500, detail=f"백테스팅 실행 오류: {e}")

    # DB에 결과 저장
    result_data = {
        "strategy_name": request.strategy_name,
        "params": request.params,
        "initial_cash": request.initial_cash,
        **metrics,
    }
    backtest_record = BacktestResult(
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
    current_user: str = Depends(get_current_user),
):
    """최근 백테스팅 결과 목록을 반환한다 (최대 20건, 최신순)."""
    result = await db.execute(
        select(BacktestResult)
        .order_by(BacktestResult.created_at.desc())
        .limit(20)
    )
    records = result.scalars().all()
    return [_to_response(r) for r in records]


@router.get("/results/{result_id}", response_model=BacktestResultResponse, summary="백테스팅 결과 상세")
async def get_result(
    result_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """특정 백테스팅 결과를 반환한다."""
    result = await db.execute(
        select(BacktestResult).where(BacktestResult.id == result_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="백테스팅 결과를 찾을 수 없습니다.")
    return _to_response(record)
