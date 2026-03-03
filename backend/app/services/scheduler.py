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
                        # 주문 수량: 설정값 조회 (기본 1주)
                        from app.models.settings import SystemSetting
                        qty_result = await db.execute(
                            select(SystemSetting).where(
                                SystemSetting.user_id == group.user_id,
                                SystemSetting.setting_key == "order_quantity",
                            )
                        )
                        qty_setting = qty_result.scalar_one_or_none()
                        order_quantity = int(qty_setting.setting_value) if qty_setting else 1

                        # 전략 신호 사전 알림 (fire-and-forget)
                        import asyncio as _asyncio
                        from app.services.telegram_notifier import notify_strategy_signal
                        _asyncio.create_task(notify_strategy_signal(
                            stock_code=item.stock_code,
                            signal_type=signal.signal_type,
                            strategy_name=strategy.name,
                            confidence=signal.confidence,
                            reason=signal.reason,
                            target_price=signal.target_price,
                        ))
                        await execute_signal(
                            user_id=group.user_id,
                            stock_code=item.stock_code,
                            signal=signal,
                            quantity=order_quantity,
                            strategy_id=strategy.id,
                            db=db,
                        )

                except Exception as e:
                    logger.warning(f"종목 {item.stock_code} 전략 평가 오류: {e}")

    except Exception as e:
        logger.error(f"전략 평가 스케줄 오류: {e}")


async def _run_risk_monitoring() -> None:
    """
    보유종목의 손절/익절 조건을 평가하고 자동 매도 주문을 실행한다.
    """
    from app.core.database import AsyncSessionLocal
    from app.models.holding import Holding
    from app.services.risk_manager import evaluate_holding_risk, to_signal
    from app.services.order_executor import execute_signal
    from app.services.kis_client import kis_client
    from sqlalchemy import select

    if not kis_client.is_available():
        return

    now = datetime.now()
    if not (9 <= now.hour < 15 or (now.hour == 15 and now.minute <= 30)):
        return

    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Holding).where(
                    Holding.quantity > 0,
                    (Holding.stop_loss_rate != None) | (Holding.take_profit_rate != None),
                )
            )
            holdings = result.scalars().all()

            for holding in holdings:
                try:
                    risk_signal = await evaluate_holding_risk(holding)
                    if risk_signal.action != "HOLD":
                        signal = to_signal(risk_signal)
                        await execute_signal(
                            user_id=holding.user_id,
                            stock_code=holding.stock_code,
                            signal=signal,
                            quantity=risk_signal.quantity,
                            strategy_id=None,
                            db=db,
                        )
                except Exception as e:
                    logger.warning(f"손절/익절 모니터링 오류 [{holding.stock_code}]: {e}")

    except Exception as e:
        logger.error(f"손절/익절 모니터링 스케줄 오류: {e}")


async def _run_holdings_sync() -> None:
    """
    KIS 잔고를 조회하여 DB holdings 테이블을 주기적으로 동기화한다.
    장중(09:00~15:30) 매 30분마다 실행된다.
    """
    from app.core.config import settings as env
    from app.core.database import AsyncSessionLocal
    from app.models.user import User
    from app.services.holding_service import sync_with_kis
    from app.services.kis_client import kis_client
    from sqlalchemy import select

    if not kis_client.is_available():
        logger.debug("KIS API 미설정. 잔고 동기화 스킵.")
        return

    now = datetime.now()
    if not (9 <= now.hour < 15 or (now.hour == 15 and now.minute <= 30)):
        return

    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(User).where(User.username == env.ADMIN_USERNAME)
            )
            user = result.scalar_one_or_none()
            if user is None:
                logger.warning("잔고 동기화: admin 사용자를 찾을 수 없음.")
                return
            holdings = await sync_with_kis(user.id, db)
            logger.info("KIS 잔고 자동 동기화 완료 (보유종목 %d개)", len(holdings))
    except Exception as e:
        logger.error(f"KIS 잔고 동기화 스케줄 오류: {e}")


async def _run_daily_summary() -> None:
    """
    장 마감 후 포트폴리오 일일 요약 알림을 전송한다. (평일 16:00 KST)
    """
    from app.core.database import AsyncSessionLocal
    from app.models.order import Order
    from app.services.holding_service import calculate_summary
    from app.services.telegram_notifier import notify_daily_portfolio_summary
    from sqlalchemy import select
    from datetime import date

    try:
        from app.models.user import User
        async with AsyncSessionLocal() as db:
            # 전체 사용자 조회 (하드코딩된 user_id=1 제거)
            user_result = await db.execute(select(User))
            users = user_result.scalars().all()

            today = date.today()
            from datetime import datetime
            start = datetime(today.year, today.month, today.day, 0, 0, 0)
            end = datetime(today.year, today.month, today.day, 23, 59, 59)

            for user in users:
                try:
                    # 포트폴리오 요약 계산
                    summary = await calculate_summary(user.id, db)

                    # 오늘 주문 건수 집계
                    result = await db.execute(
                        select(Order).where(
                            Order.user_id == user.id,
                            Order.created_at >= start,
                            Order.created_at <= end,
                        )
                    )
                    orders = result.scalars().all()
                    buy_count = sum(1 for o in orders if o.order_type == "buy")
                    sell_count = sum(1 for o in orders if o.order_type == "sell")

                    await notify_daily_portfolio_summary(
                        total_evaluation=summary["total_evaluation"],
                        total_profit_loss=summary["total_profit_loss"],
                        total_profit_loss_rate=summary["total_profit_loss_rate"],
                        buy_count=buy_count,
                        sell_count=sell_count,
                    )
                except Exception as e:
                    logger.error(f"사용자 {user.id} 일일 요약 알림 오류: {e}")

    except Exception as e:
        logger.error(f"일일 요약 알림 오류: {e}")


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

        # 장중 매 30분마다 KIS 잔고 동기화 (09:00~15:30)
        _scheduler.add_job(
            _run_holdings_sync,
            CronTrigger(
                day_of_week="mon-fri",
                hour="9-15",
                minute="*/30",
                timezone="Asia/Seoul",
            ),
            id="holdings_sync",
            replace_existing=True,
        )

        # 평일 16:00 KST 일일 포트폴리오 요약 알림
        _scheduler.add_job(
            _run_daily_summary,
            CronTrigger(
                day_of_week="mon-fri",
                hour=16,
                minute=0,
                timezone="Asia/Seoul",
            ),
            id="daily_summary",
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
