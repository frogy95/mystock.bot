"""
보유종목 서비스 모듈
KIS API에서 보유종목을 동기화하고 포트폴리오 요약을 계산한다.
"""
import logging
from datetime import datetime, timezone
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.holding import Holding
from app.services.kis_client import kis_client

logger = logging.getLogger("mystock.bot")


async def sync_with_kis(user_id: int, db: AsyncSession) -> List[Holding]:
    """
    KIS 잔고를 조회하여 DB holdings 테이블에 upsert한다.
    기존의 stop_loss_rate, take_profit_rate, sell_strategy_id는 보존한다.
    """
    if not kis_client.is_available():
        raise ValueError("KIS API가 설정되지 않았습니다.")

    balance = await kis_client.get_balance()
    if balance is None:
        raise ValueError("KIS 잔고 조회에 실패했습니다.")

    now = datetime.now(timezone.utc)
    stocks = balance.get("stocks", [])

    # 기존 보유종목 조회 (종목코드 → Holding 매핑)
    result = await db.execute(
        select(Holding).where(Holding.user_id == user_id)
    )
    existing: dict[str, Holding] = {h.stock_code: h for h in result.scalars().all()}

    updated_holdings = []

    for stock in stocks:
        code = stock["symbol"]
        holding = existing.get(code)

        if holding:
            # 기존 레코드 업데이트 (손절/익절/전략은 보존)
            holding.stock_name = stock["name"]
            holding.quantity = stock["quantity"]
            holding.avg_price = stock["avg_price"]
            holding.current_price = stock["current_price"]
            holding.synced_at = now
        else:
            # 신규 레코드 생성
            holding = Holding(
                user_id=user_id,
                stock_code=code,
                stock_name=stock["name"],
                quantity=stock["quantity"],
                avg_price=stock["avg_price"],
                current_price=stock["current_price"],
                synced_at=now,
            )
            db.add(holding)

        updated_holdings.append(holding)

    # KIS에 더 이상 없는 종목 (전량 매도 처리) → quantity=0으로 업데이트
    kis_codes = {s["symbol"] for s in stocks}
    for code, holding in existing.items():
        if code not in kis_codes:
            holding.quantity = 0
            holding.current_price = None
            holding.synced_at = now

    await db.commit()

    # 최신 상태로 재조회
    result = await db.execute(
        select(Holding).where(Holding.user_id == user_id)
    )
    return result.scalars().all()


async def calculate_summary(user_id: int, db: AsyncSession) -> dict:
    """
    포트폴리오 요약을 계산한다.
    KIS 연결 시 KIS 잔고를 단일 소스로 사용하고, 미연결 시 DB 폴백.
    """
    result = await db.execute(
        select(Holding).where(Holding.user_id == user_id, Holding.quantity > 0)
    )
    holdings = result.scalars().all()

    # KIS 사용 가능 시: KIS 요약 데이터 우선 사용
    if kis_client.is_available():
        try:
            balance = await kis_client.get_balance()
            if balance:
                total_eval = balance.get("total_evaluation", 0)
                total_purch = balance.get("total_purchase", 0)
                total_pl = balance.get("total_profit_loss", 0)
                deposit = float(balance.get("cash", 0))
                prev_total = balance.get("prev_total_asset", 0)

                # 일일 손익 계산: 현재 총자산 - 전일 총자산
                current_total = total_eval + deposit
                daily_pl = (current_total - prev_total) if prev_total > 0 else 0.0
                daily_rate = (daily_pl / prev_total * 100) if prev_total > 0 else 0.0

                return {
                    "total_evaluation": round(total_eval, 2),
                    "total_purchase": round(total_purch, 2),
                    "total_profit_loss": round(total_pl, 2),
                    "total_profit_loss_rate": round(
                        (total_pl / total_purch * 100) if total_purch > 0 else 0.0, 2
                    ),
                    "deposit": deposit,
                    "holdings_count": len(balance.get("stocks", [])),
                    "daily_profit_loss": round(daily_pl, 2),
                    "daily_profit_rate": round(daily_rate, 2),
                }
        except Exception as e:
            logger.warning(f"KIS 요약 조회 실패, DB 폴백: {e}")

    # KIS 미연결 시: DB 기반 폴백 계산
    total_evaluation = 0.0
    total_purchase = 0.0

    for h in holdings:
        if h.current_price and h.quantity > 0:
            total_evaluation += float(h.current_price) * h.quantity
            total_purchase += float(h.avg_price) * h.quantity

    total_profit_loss = total_evaluation - total_purchase
    total_profit_loss_rate = (
        (total_profit_loss / total_purchase * 100) if total_purchase > 0 else 0.0
    )

    return {
        "total_evaluation": round(total_evaluation, 2),
        "total_purchase": round(total_purchase, 2),
        "total_profit_loss": round(total_profit_loss, 2),
        "total_profit_loss_rate": round(total_profit_loss_rate, 2),
        "deposit": 0.0,
        "holdings_count": len(holdings),
        "daily_profit_loss": 0.0,
        "daily_profit_rate": 0.0,
    }
