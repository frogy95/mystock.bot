"""
주문 실행 서비스 모듈
전략 신호를 받아 KIS API로 주문을 실행하고 DB에 저장한다.
중복 주문 방지 및 주문 로그 기록을 담당한다.
주문 체결 시 텔레그램 알림을 fire-and-forget 방식으로 전송한다.
"""
import asyncio
import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderLog
from app.services.kis_client import kis_client
from app.services.strategy_engine import Signal
from app.services.telegram_notifier import notify_order_executed

logger = logging.getLogger("mystock.bot")


async def _has_pending_order(
    user_id: int,
    stock_code: str,
    order_type: str,
    db: AsyncSession,
) -> bool:
    """동일 종목+방향의 미체결 주문이 있는지 확인한다."""
    result = await db.execute(
        select(Order).where(
            Order.user_id == user_id,
            Order.stock_code == stock_code,
            Order.order_type == order_type,
            Order.status == "pending",
        )
    )
    return result.scalar_one_or_none() is not None


async def execute_signal(
    user_id: int,
    stock_code: str,
    signal: Signal,
    quantity: int,
    strategy_id: Optional[int],
    db: AsyncSession,
    price: int = 0,
) -> Optional[Order]:
    """
    매매 신호를 받아 KIS 주문을 실행하고 DB에 기록한다.
    - 중복 주문 방지 (동일 종목+방향 미체결 주문 확인)
    - 주문 실패 시 OrderLog에 에러 기록
    Returns: 생성된 Order 또는 None (중복/실패)
    """
    if signal.signal_type not in ("BUY", "SELL"):
        return None

    order_type = signal.signal_type.lower()

    # 안전장치 검사 (매도 주문은 손절/익절이므로 안전장치 일부 면제)
    if order_type == "buy":
        from app.services.safety_guard import run_all_checks
        from app.services.system_monitor import check_error_threshold, acquire_order_lock
        ok, msg = await check_error_threshold(user_id, db)
        if not ok:
            logger.warning(f"시스템 에러 임계값 초과로 주문 차단: {msg}")
            return None
        ok, msg = await run_all_checks(user_id, stock_code, quantity, float(price), db)
        if not ok:
            logger.info(f"안전장치 차단: {msg}")
            return None

    # Redis 분산 락 (동시 주문 방지)
    from app.services.system_monitor import acquire_order_lock
    async with acquire_order_lock(user_id, stock_code) as acquired:
        if not acquired:
            logger.info(f"주문 락 획득 실패: {stock_code} - 이미 처리 중")
            return None

    # 중복 주문 방지
    if await _has_pending_order(user_id, stock_code, order_type, db):
        logger.info(f"중복 주문 방지: {stock_code} {order_type} 미체결 주문 존재")
        return None

    # DB에 pending 주문 생성
    order = Order(
        user_id=user_id,
        stock_code=stock_code,
        order_type=order_type,
        status="pending",
        strategy_id=strategy_id,
        quantity=quantity,
        price=float(price) if price > 0 else None,
    )
    db.add(order)
    await db.flush()  # id 생성을 위해 flush

    try:
        if not kis_client.is_available():
            # KIS API 미설정 시 시뮬레이션 모드로 처리
            order.status = "simulated"
            log = OrderLog(
                order_id=order.id,
                log_type="info",
                message=f"시뮬레이션 주문: {order_type.upper()} {stock_code} {quantity}주",
                detail={"signal_reason": signal.reason, "confidence": signal.confidence},
            )
            db.add(log)
            await db.commit()
            logger.info(f"시뮬레이션 주문 생성: {stock_code} {order_type}")
            # 텔레그램 알림 (fire-and-forget 방식)
            asyncio.create_task(
                notify_order_executed(
                    stock_code=stock_code,
                    order_type=order_type,
                    quantity=quantity,
                    price=float(price),
                    reason=f"[시뮬레이션] {signal.reason}",
                )
            )
            # WebSocket 브로드캐스트 (실시간 체결 알림)
            from app.services.websocket_manager import ws_manager
            asyncio.create_task(ws_manager.broadcast({
                "type": "notification",
                "order_type": order_type,
                "stock_code": stock_code,
                "quantity": quantity,
                "price": float(price),
                "reason": f"[시뮬레이션] {signal.reason}",
            }))
            return order

        # KIS 주문 실행
        result = await kis_client.place_order(
            symbol=stock_code,
            order_type=order_type,
            quantity=quantity,
            price=price,
        )

        if result:
            order.status = "pending"  # KIS에서 체결 대기
            log = OrderLog(
                order_id=order.id,
                log_type="info",
                message=f"KIS 주문 전송: {order_type.upper()} {stock_code} {quantity}주",
                detail={
                    "order_no": result.get("order_no"),
                    "signal_reason": signal.reason,
                    "confidence": signal.confidence,
                },
            )
            # 텔레그램 알림 (fire-and-forget 방식)
            asyncio.create_task(
                notify_order_executed(
                    stock_code=stock_code,
                    order_type=order_type,
                    quantity=quantity,
                    price=float(price),
                    reason=signal.reason,
                )
            )
            # WebSocket 브로드캐스트 (실시간 체결 알림)
            from app.services.websocket_manager import ws_manager
            asyncio.create_task(ws_manager.broadcast({
                "type": "notification",
                "order_type": order_type,
                "stock_code": stock_code,
                "quantity": quantity,
                "price": float(price),
                "reason": signal.reason,
            }))
        else:
            order.status = "failed"
            log = OrderLog(
                order_id=order.id,
                log_type="error",
                message="KIS 주문 응답 없음",
                detail=None,
            )

        db.add(log)
        await db.commit()
        return order

    except Exception as e:
        order.status = "failed"
        error_log = OrderLog(
            order_id=order.id,
            log_type="error",
            message=f"주문 실행 오류: {str(e)[:400]}",
            detail=None,
        )
        db.add(error_log)
        await db.commit()
        logger.error(f"주문 실행 실패 [{stock_code} {order_type}]: {e}")
        return order
