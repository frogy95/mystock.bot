"""
APScheduler 기반 스케줄러 모듈
장중(09:00-15:30) 전략 평가 및 매매 신호 스케줄을 관리한다.
"""
import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger("mystock.bot")

# 전역 스케줄러 인스턴스
_scheduler: AsyncIOScheduler | None = None


async def _run_strategy_evaluation() -> None:
    """
    장중 전략 평가 작업
    모든 활성 관심종목에 대해 전략 신호를 평가하고 자동 주문을 실행한다.
    """
    from app.core.database import AsyncSessionLocal
    from app.models.watchlist import WatchlistItem, WatchlistGroup
    from app.models.strategy import Strategy, StrategyParam
    from app.services.strategy_engine import get_strategy
    from app.services.order_executor import execute_signal
    from app.services.kis_client import kis_client
    from sqlalchemy import select

    # KIS API 미설정 시 스킵
    if not kis_client.is_available():
        logger.debug("KIS API 미설정. 전략 평가 스킵.")
        return

    # 장중 시간 확인 (09:00 ~ 15:30 KST, UTC+9)
    now = datetime.now()
    if not (9 <= now.hour < 15 or (now.hour == 15 and now.minute <= 30)):
        return

    try:
        async with AsyncSessionLocal() as db:
            # 전략이 할당된 관심종목 조회
            result = await db.execute(
                select(WatchlistItem, WatchlistGroup, Strategy)
                .join(WatchlistGroup, WatchlistItem.group_id == WatchlistGroup.id)
                .join(Strategy, WatchlistItem.strategy_id == Strategy.id)
                .where(Strategy.is_active == True)
            )
            rows = result.all()

            for item, group, strategy in rows:
                try:
                    # 전략 파라미터 조회
                    param_result = await db.execute(
                        select(StrategyParam).where(
                            StrategyParam.strategy_id == strategy.id
                        )
                    )
                    params = {
                        p.param_key: (
                            float(p.param_value)
                            if p.param_type == "float"
                            else int(p.param_value)
                            if p.param_type == "int"
                            else p.param_value
                        )
                        for p in param_result.scalars().all()
                    }

                    # 전략 엔진 조회
                    engine = get_strategy(strategy.name)
                    if engine is None:
                        continue

                    # 차트 데이터 조회
                    chart_data = await kis_client.get_chart(
                        item.stock_code, period="day", count=90
                    )
                    if not chart_data:
                        continue

                    # 신호 평가
                    signal = engine.evaluate_from_ohlcv(chart_data, params)

                    if signal.signal_type in ("BUY", "SELL") and signal.confidence >= 0.5:
                        await execute_signal(
                            user_id=group.user_id,
                            stock_code=item.stock_code,
                            signal=signal,
                            quantity=1,  # 기본 1주 (향후 수량 계산 로직 추가)
                            strategy_id=strategy.id,
                            db=db,
                        )

                except Exception as e:
                    logger.warning(f"종목 {item.stock_code} 전략 평가 오류: {e}")

    except Exception as e:
        logger.error(f"전략 평가 스케줄 오류: {e}")


async def _run_risk_monitoring() -> None:
    """손절/익절 모니터링 (Sprint 7에서 risk_manager 통합 예정)"""
    logger.debug("손절/익절 모니터링 실행 (Sprint 7에서 구현)")


def get_scheduler() -> AsyncIOScheduler:
    """스케줄러 싱글턴을 반환한다."""
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler(timezone="Asia/Seoul")

        # 장중 매 5분마다 전략 평가 (09:00~15:30)
        _scheduler.add_job(
            _run_strategy_evaluation,
            CronTrigger(
                day_of_week="mon-fri",
                hour="9-15",
                minute="*/5",
                timezone="Asia/Seoul",
            ),
            id="strategy_evaluation",
            replace_existing=True,
        )

        # 장중 매 1분마다 손절/익절 모니터링
        _scheduler.add_job(
            _run_risk_monitoring,
            CronTrigger(
                day_of_week="mon-fri",
                hour="9-15",
                minute="*",
                timezone="Asia/Seoul",
            ),
            id="risk_monitoring",
            replace_existing=True,
        )

    return _scheduler


async def start_scheduler() -> None:
    """스케줄러를 시작한다."""
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()
        logger.info("APScheduler 시작 (전략 평가: 장중 매 5분)")


async def stop_scheduler() -> None:
    """스케줄러를 종료한다."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("APScheduler 종료")
