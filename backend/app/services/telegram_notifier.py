"""
텔레그램 알림 모듈
매매 신호, 주문 체결, 손절/익절, 시스템 오류를 텔레그램으로 알린다.
TELEGRAM_BOT_TOKEN이 미설정된 경우 gracefully skip한다.
"""
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger("mystock.bot")

_bot = None


def _get_bot():
    """텔레그램 봇 싱글턴을 반환한다."""
    global _bot
    if _bot is None and settings.TELEGRAM_BOT_TOKEN:
        try:
            from telegram import Bot
            _bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        except Exception as e:
            logger.warning(f"텔레그램 봇 초기화 실패: {e}")
    return _bot


async def send_message(text: str, chat_id: Optional[str] = None) -> bool:
    """텔레그램 메시지를 전송한다."""
    bot = _get_bot()
    if not bot:
        logger.debug(f"텔레그램 미설정. 메시지 스킵: {text[:50]}")
        return False

    target_chat_id = chat_id or settings.TELEGRAM_CHAT_ID
    if not target_chat_id:
        return False

    try:
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
    user_info = f"(사용자 {user_id})" if user_id else ""
    text = f"⚠️ *시스템 오류* {user_info}\n```\n{error_msg[:500]}\n```"
    await send_message(text)


async def notify_auto_trade_disabled(user_id: int, reason: str) -> None:
    """자동매매 중단 알림을 전송한다."""
    text = (
        f"🚫 *자동매매 중단* (사용자 {user_id})\n"
        f"사유: {reason}"
    )
    await send_message(text)
