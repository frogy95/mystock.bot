"""
risk_manager 서비스 단위 테스트
Sprint 13 Task 2: 전량/분할 익절 순서 검증
"""
import pytest
from types import SimpleNamespace
from unittest.mock import patch

from app.services.risk_manager import evaluate_holding_risk


def _make_holding(avg_price: float, current_price: float, quantity: int,
                  stop_loss_rate=None, take_profit_rate=None):
    """테스트용 Holding-like 객체 생성 헬퍼 (SimpleNamespace 사용)"""
    return SimpleNamespace(
        user_id=1,
        stock_code="005930",
        avg_price=avg_price,
        current_price=current_price,
        quantity=quantity,
        stop_loss_rate=stop_loss_rate,
        take_profit_rate=take_profit_rate,
    )


@pytest.mark.asyncio
async def test_full_take_profit_triggered_before_partial():
    """
    전량 익절 조건이 분할 익절보다 먼저 체크되는지 검증
    수익률 10% (목표 10%) → 전량 익절(TAKE_PROFIT) 반환 (분할 아님)
    """
    holding = _make_holding(avg_price=10000, current_price=11000, quantity=10,
                            take_profit_rate=10.0)

    with patch("app.services.risk_manager.asyncio.create_task"):
        signal = await evaluate_holding_risk(holding)

    assert signal.action == "TAKE_PROFIT"
    assert signal.quantity == 10  # 전량


@pytest.mark.asyncio
async def test_partial_take_profit_at_half_target():
    """
    수익률이 목표의 50% 도달 시 분할 익절(PARTIAL_TAKE_PROFIT) 반환
    수익률 5% (목표 10%) → 분할 익절, 반량(5주)
    """
    holding = _make_holding(avg_price=10000, current_price=10500, quantity=10,
                            take_profit_rate=10.0)

    with patch("app.services.risk_manager.asyncio.create_task"):
        signal = await evaluate_holding_risk(holding)

    assert signal.action == "PARTIAL_TAKE_PROFIT"
    assert signal.quantity == 5  # 반량


@pytest.mark.asyncio
async def test_stop_loss_triggered():
    """
    손절 조건 검증: 손실률이 설정 비율 초과 시 STOP_LOSS 반환
    수익률 -6% (손절 5%) → STOP_LOSS 전량
    """
    holding = _make_holding(avg_price=10000, current_price=9400, quantity=5,
                            stop_loss_rate=5.0)

    with patch("app.services.risk_manager.asyncio.create_task"):
        signal = await evaluate_holding_risk(holding)

    assert signal.action == "STOP_LOSS"
    assert signal.quantity == 5
