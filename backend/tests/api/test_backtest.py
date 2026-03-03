"""
백테스팅 API 통합 테스트 - 사용자별 데이터 격리 검증
GET  /api/v1/backtest/results          - 결과 목록 (본인 결과만)
GET  /api/v1/backtest/results/{id}     - 결과 상세 (본인 결과만, 타인 → 404)
"""
import pytest

from app.models.backtest import BacktestResult
from app.models.user import User


@pytest.mark.asyncio
async def test_backtest_results_isolated_by_user(client_with_user, db_session):
    """백테스팅 결과 목록 조회 - 다른 사용자의 결과는 반환되지 않음"""
    from sqlalchemy import select

    # 현재 인증된 사용자(testuser) 조회
    result = await db_session.execute(select(User).where(User.username == "testuser"))
    testuser = result.scalar_one()

    # 다른 사용자 생성
    other_user = User(
        username="other",
        is_active=True,
        is_approved=True,
        role="user",
    )
    db_session.add(other_user)
    await db_session.commit()

    # testuser의 백테스트 결과 생성
    own_record = BacktestResult(
        user_id=testuser.id,
        strategy_id=None,
        symbol="005930",
        result_data={
            "strategy_name": "TestStrategy",
            "total_return": 10.0,
            "cagr": 5.0,
            "mdd": -3.0,
            "sharpe_ratio": 1.2,
            "total_trades": 5,
            "win_rate": 60.0,
            "benchmark_return": 8.0,
            "equity_curve": [],
        },
    )

    # 다른 사용자의 백테스트 결과 생성
    other_record = BacktestResult(
        user_id=other_user.id,
        strategy_id=None,
        symbol="000660",
        result_data={
            "strategy_name": "OtherStrategy",
            "total_return": 20.0,
            "cagr": 10.0,
            "mdd": -5.0,
            "sharpe_ratio": 1.5,
            "total_trades": 10,
            "win_rate": 70.0,
            "benchmark_return": 12.0,
            "equity_curve": [],
        },
    )
    db_session.add(own_record)
    db_session.add(other_record)
    await db_session.commit()

    response = await client_with_user.get("/api/v1/backtest/results")
    assert response.status_code == 200
    data = response.json()

    # testuser의 결과만 반환됨
    assert len(data) == 1
    assert data[0]["symbol"] == "005930"

    # 다른 사용자(000660)의 결과는 포함되지 않음
    symbols = [d["symbol"] for d in data]
    assert "000660" not in symbols


@pytest.mark.asyncio
async def test_get_backtest_result_other_user_returns_404(client_with_user, db_session):
    """백테스팅 결과 상세 조회 - 다른 사용자의 결과 ID로 조회 시 404 반환"""
    from sqlalchemy import select

    # 다른 사용자 생성
    other_user = User(
        username="other2",
        is_active=True,
        is_approved=True,
        role="user",
    )
    db_session.add(other_user)
    await db_session.commit()

    # 다른 사용자의 백테스트 결과 생성
    other_record = BacktestResult(
        user_id=other_user.id,
        strategy_id=None,
        symbol="035420",
        result_data={
            "strategy_name": "OtherStrategy2",
            "total_return": 15.0,
            "cagr": 7.5,
            "mdd": -4.0,
            "sharpe_ratio": 1.1,
            "total_trades": 8,
            "win_rate": 62.5,
            "benchmark_return": 9.0,
            "equity_curve": [],
        },
    )
    db_session.add(other_record)
    await db_session.commit()

    # 현재 사용자(testuser)가 다른 사용자의 결과 id로 조회 시 404
    response = await client_with_user.get(f"/api/v1/backtest/results/{other_record.id}")
    assert response.status_code == 404
