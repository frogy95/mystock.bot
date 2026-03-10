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

from sqlalchemy import select
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
        # 비밀번호는 환경변수 SEED_ADMIN_PASSWORD 또는 기본값 사용
        admin_email = settings.ADMIN_EMAIL
        admin_password = os.environ.get("SEED_ADMIN_PASSWORD", "change-me-in-production")
        admin = User(
            username="admin",
            email=admin_email,
            password_hash=hash_password(admin_password),
            role=ROLE_ADMIN,
            is_approved=True,
            is_active=True,
        )
        session.add(admin)
        await session.flush()
        print(f"유저 생성: {admin.username} (id={admin.id})")

        # 2~4. 프리셋 전략 생성 (중복 방지: 동일 이름의 프리셋이 이미 존재하면 건너뜀)
        preset_strategies = [
            {
                "name": "골든크로스+RSI",
                "strategy_type": "technical",
                "params": [
                    ("sma_short", "20", "int"),        # 단기 이동평균 기간
                    ("sma_long", "60", "int"),          # 장기 이동평균 기간
                    ("rsi_period", "14", "int"),         # RSI 계산 기간
                    ("rsi_buy_threshold", "30", "int"),  # RSI 매수 기준값
                    ("rsi_sell_threshold", "70", "int"), # RSI 매도 기준값
                ],
            },
            {
                "name": "가치+모멘텀",
                "strategy_type": "fundamental",
                "params": [
                    ("per_ratio", "0.7", "float"),  # PER 비율 기준 (업종 PER 대비)
                    ("pbr_max", "1.0", "float"),     # PBR 최대값
                    ("roe_min", "10.0", "float"),    # ROE 최솟값 (%)
                ],
            },
            {
                "name": "볼린저밴드반전",
                "strategy_type": "technical",
                "params": [
                    ("bb_period", "20", "int"),             # 볼린저밴드 계산 기간
                    ("bb_std", "2.0", "float"),             # 볼린저밴드 표준편차 배수
                    ("rsi_buy_threshold", "35", "int"),      # RSI 매수 기준값 (개선: 30→35)
                ],
            },
            {
                "name": "MACD추세추종",
                "strategy_type": "technical",
                "params": [
                    ("rsi_max", "65", "float"),  # RSI 매수 허용 최대값
                ],
            },
            {
                "name": "저베타모멘텀",
                "strategy_type": "quantitative",
                "params": [
                    ("beta_max", "0.8", "float"),    # 매수 허용 최대 베타
                    ("beta_period", "60", "int"),     # 베타 계산 기간 (일)
                    ("momentum_min", "0.0", "float"), # 최소 모멘텀 (%)
                    ("rsi_max", "60.0", "float"),     # RSI 매수 허용 최대값
                ],
            },
            {
                "name": "모멘텀리스크스위치",
                "strategy_type": "quantitative",
                "params": [
                    ("market_momentum_period", "60", "int"),   # KOSPI 모멘텀 계산 기간
                    ("stock_momentum_min", "5.0", "float"),    # 종목 최소 모멘텀 (%)
                    ("market_risk_off", "-3.0", "float"),      # 시장 리스크오프 임계값 (%)
                    ("rsi_max", "60.0", "float"),              # RSI 매수 허용 최대값
                ],
            },
        ]

        for preset in preset_strategies:
            # 동일 이름의 프리셋이 이미 존재하면 건너뜀
            existing = await session.execute(
                select(Strategy).where(
                    Strategy.name == preset["name"],
                    Strategy.is_preset.is_(True),
                )
            )
            if existing.scalars().first() is not None:
                print(f"전략 이미 존재 (건너뜀): {preset['name']}")
                continue

            strategy = Strategy(
                name=preset["name"],
                strategy_type=preset["strategy_type"],
                is_active=True,
                is_preset=True,
            )
            session.add(strategy)
            await session.flush()
            print(f"전략 생성: {strategy.name} (id={strategy.id})")

            for key, value, type_ in preset["params"]:
                session.add(
                    StrategyParam(
                        strategy_id=strategy.id,
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
