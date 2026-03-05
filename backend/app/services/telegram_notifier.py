"""
텔레그램 알림 모듈
매매 신호, 주문 체결, 손절/익절, 시스템 오류를 텔레그램으로 알린다.
TELEGRAM_BOT_TOKEN은 DB(system_settings)에서 읽는다. 미설정 시 gracefully skip한다.
"""
import logging
from typing import Optional

logger = logging.getLogger("mystock.bot")


async def _get_telegram_token() -> str:
    """DB에서 텔레그램 봇 토큰을 조회한다."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.settings import SystemSetting
        from sqlalchemy import select

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(SystemSetting).where(
                    SystemSetting.setting_key == "telegram_bot_token",
                    SystemSetting.user_id == None,
                )
            )
            setting = result.scalar_one_or_none()
            return setting.setting_value if setting else ""
    except Exception as e:
        logger.debug(f"텔레그램 토큰 조회 실패: {e}")
        return ""


async def _get_telegram_chat_id() -> str:
    """DB에서 텔레그램 chat ID를 조회한다."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.settings import SystemSetting
        from sqlalchemy import select

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(SystemSetting).where(
                    SystemSetting.setting_key == "telegram_chat_id",
                    SystemSetting.user_id == None,
                )
            )
            setting = result.scalar_one_or_none()
            return setting.setting_value if setting else ""
    except Exception as e:
        logger.debug(f"텔레그램 chat_id 조회 실패: {e}")
        return ""


async def _is_notification_enabled(setting_key: str) -> bool:
    """system_settings 테이블에서 알림 ON/OFF 설정을 조회한다. 미설정 시 True 반환."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.settings import SystemSetting
        from sqlalchemy import select

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(SystemSetting).where(
                    SystemSetting.setting_key == setting_key,
                    SystemSetting.user_id == None,
                )
            )
            setting = result.scalar_one_or_none()
            if setting is None:
                return True
            return setting.setting_value.lower() not in ("false", "0", "off")
    except Exception as e:
        logger.debug(f"알림 설정 조회 실패 ({setting_key}): {e}")
        return True


async def send_message(text: str, chat_id: Optional[str] = None) -> bool:
    """텔레그램 메시지를 전송한다."""
    token = await _get_telegram_token()
    if not token:
        logger.debug(f"텔레그램 미설정. 메시지 스킵: {text[:50]}")
        return False

    target_chat_id = chat_id or await _get_telegram_chat_id()
    if not target_chat_id:
        return False

    try:
        from telegram import Bot
        bot = Bot(token=token)
        await bot.send_message(
            chat_id=target_chat_id,
            text=text,
            parse_mode="Markdown",
        )
        return True
    except Exception as e:
        logger.warning(f"텔레그램 전송 실패: {e}")
        return False


async def notify_order_executed(
    stock_code: str,
    order_type: str,
    quantity: int,
    price: float,
    reason: str = "",
) -> None:
    """주문 체결 알림을 전송한다."""
    if not await _is_notification_enabled("notify_order_executed"):
        return
    emoji = "📈" if order_type == "buy" else "📉"
    action = "매수" if order_type == "buy" else "매도"
    text = (
        f"{emoji} *{action} 체결*\n"
        f"종목: `{stock_code}`\n"
        f"수량: {quantity}주\n"
        f"가격: {price:,.0f}원\n"
    )
    if reason:
        text += f"사유: {reason}"
    await send_message(text)


async def notify_risk_triggered(
    stock_code: str,
    action: str,
    current_price: float,
    avg_price: float,
    reason: str,
) -> None:
    """손절/익절 알림을 전송한다."""
    if not await _is_notification_enabled("notify_risk_triggered"):
        return
    pnl_pct = (current_price - avg_price) / avg_price * 100
    emoji = "🛑" if "손절" in reason else "✅"
    text = (
        f"{emoji} *리스크 관리 발동*\n"
        f"종목: `{stock_code}`\n"
        f"조치: {action}\n"
        f"현재가: {current_price:,.0f}원\n"
        f"평균단가: {avg_price:,.0f}원\n"
        f"수익률: {pnl_pct:+.2f}%\n"
        f"사유: {reason}"
    )
    await send_message(text)


async def notify_system_error(error_msg: str, user_id: Optional[int] = None) -> None:
    """시스템 오류 알림을 전송한다."""
    if not await _is_notification_enabled("notify_system_error"):
        return
    user_info = f"(사용자 {user_id})" if user_id else ""
    text = f"⚠️ *시스템 오류* {user_info}\n```\n{error_msg[:500]}\n```"
    await send_message(text)


async def notify_auto_trade_disabled(user_id: int, reason: str) -> None:
    """자동매매 중단 알림을 전송한다."""
    if not await _is_notification_enabled("notify_auto_trade_disabled"):
        return
    text = (
        f"🚫 *자동매매 중단* (사용자 {user_id})\n"
        f"사유: {reason}"
    )
    await send_message(text)


async def notify_strategy_signal(
    stock_code: str,
    signal_type: str,
    strategy_name: str,
    confidence: float,
    reason: str,
    target_price: Optional[float] = None,
) -> None:
    """전략 신호 발생 사전 알림을 전송한다."""
    if not await _is_notification_enabled("notify_strategy_signal"):
        return
    emoji = "🟢" if signal_type == "BUY" else "🔴"
    action = "매수" if signal_type == "BUY" else "매도"
    text = (
        f"{emoji} *{action} 신호 발생*\n"
        f"종목: `{stock_code}`\n"
        f"전략: {strategy_name}\n"
        f"신뢰도: {confidence * 100:.0f}%\n"
        f"근거: {reason}"
    )
    if target_price:
        text += f"\n목표가: {target_price:,.0f}원"
    await send_message(text)


async def notify_daily_portfolio_summary(
    total_evaluation: float,
    total_profit_loss: float,
    total_profit_loss_rate: float,
    buy_count: int,
    sell_count: int,
) -> None:
    """일일 포트폴리오 요약 알림을 전송한다."""
    if not await _is_notification_enabled("notify_daily_summary"):
        return
    pnl_emoji = "📈" if total_profit_loss >= 0 else "📉"
    text = (
        f"{pnl_emoji} *일일 포트폴리오 요약*\n"
        f"총 평가금액: {total_evaluation:,.0f}원\n"
        f"평가손익: {total_profit_loss:+,.0f}원 ({total_profit_loss_rate:+.2f}%)\n"
        f"오늘 매수: {buy_count}건 / 매도: {sell_count}건"
    )
    await send_message(text)
