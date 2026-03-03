"""
시드 데이터 스크립트
개발 환경 초기 데이터를 DB에 삽입한다.

실행 방법:
    cd backend
    python3 scripts/seed.py
"""
import asyncio
import os
import sys

# backend/ 디렉토리를 sys.path에 추가하여 app 모듈을 임포트할 수 있도록 설정
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings
from app.core.auth import hash_password
from app.models.user import User, ROLE_ADMIN
from app.models.strategy import Strategy, StrategyParam
from app.models.settings import SystemSetting


async def seed() -> None:
    """초기 시드 데이터를 DB에 삽입한다."""
    # 비동기 엔진 생성 (asyncpg 드라이버 사용)
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        # 1. 기본 관리자 유저 생성 (Sprint 14: JWT 인증 필드 포함)
        admin = User(
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            password_hash=hash_password(settings.ADMIN_PASSWORD),
            role=ROLE_ADMIN,
            is_approved=True,
            is_active=True,
        )
        session.add(admin)
        await session.flush()
        print(f"유저 생성: {admin.username} (id={admin.id})")

        # 2. 프리셋 전략 1 - 골든크로스+RSI (기술적 분석)
        strategy1 = Strategy(
            name="골든크로스+RSI",
            strategy_type="technical",
            is_active=True,
            is_preset=True,
        )
        session.add(strategy1)
        await session.flush()
        print(f"전략 생성: {strategy1.name} (id={strategy1.id})")

        # 골든크로스+RSI 파라미터 설정
        strategy1_params = [
            ("sma_short", "20", "int"),       # 단기 이동평균 기간
            ("sma_long", "60", "int"),         # 장기 이동평균 기간
            ("rsi_period", "14", "int"),        # RSI 계산 기간
            ("rsi_buy_threshold", "30", "int"), # RSI 매수 기준값
            ("rsi_sell_threshold", "70", "int"), # RSI 매도 기준값
        ]
        for key, value, type_ in strategy1_params:
            session.add(
                StrategyParam(
                    strategy_id=strategy1.id,
                    param_key=key,
                    param_value=value,
                    param_type=type_,
                )
            )

        # 3. 프리셋 전략 2 - 가치+모멘텀 (기본적 분석)
        strategy2 = Strategy(
            name="가치+모멘텀",
            strategy_type="fundamental",
            is_active=True,
            is_preset=True,
        )
        session.add(strategy2)
        await session.flush()
        print(f"전략 생성: {strategy2.name} (id={strategy2.id})")

        # 가치+모멘텀 파라미터 설정
        strategy2_params = [
            ("per_ratio", "0.7", "float"),  # PER 비율 기준 (업종 PER 대비)
            ("pbr_max", "1.0", "float"),    # PBR 최대값
            ("roe_min", "10.0", "float"),   # ROE 최솟값 (%)
        ]
        for key, value, type_ in strategy2_params:
            session.add(
                StrategyParam(
                    strategy_id=strategy2.id,
                    param_key=key,
                    param_value=value,
                    param_type=type_,
                )
            )

        # 4. 프리셋 전략 3 - 볼린저밴드반전 (기술적 분석)
        strategy3 = Strategy(
            name="볼린저밴드반전",
            strategy_type="technical",
            is_active=True,
            is_preset=True,
        )
        session.add(strategy3)
        await session.flush()
        print(f"전략 생성: {strategy3.name} (id={strategy3.id})")

        # 볼린저밴드반전 파라미터 설정
        strategy3_params = [
            ("bb_period", "20", "int"),              # 볼린저밴드 계산 기간
            ("bb_std", "2.0", "float"),              # 볼린저밴드 표준편차 배수
            ("rsi_buy_threshold", "30", "int"),       # RSI 매수 기준값
        ]
        for key, value, type_ in strategy3_params:
            session.add(
                StrategyParam(
                    strategy_id=strategy3.id,
                    param_key=key,
                    param_value=value,
                    param_type=type_,
                )
            )

        # 5. 시스템 기본 설정값 삽입 (전역 설정: user_id=None)
        system_settings = [
            ("max_daily_loss", "500000", "int"),   # 일일 최대 손실 한도 (원)
            ("max_daily_orders", "20", "int"),      # 일일 최대 주문 횟수
        ]
        for key, value, type_ in system_settings:
            session.add(
                SystemSetting(
                    setting_key=key,
                    setting_value=value,
                    setting_type=type_,
                )
            )
            print(f"시스템 설정 추가: {key}={value}")

        # 모든 변경사항 커밋
        await session.commit()

    # 엔진 자원 해제
    await engine.dispose()
    print("\n시드 데이터 삽입 완료")


if __name__ == "__main__":
    asyncio.run(seed())
