"""
KIS 설정 캐시 모듈
DB의 system_settings 테이블에서 KIS 자격증명을 읽어 메모리에 캐싱한다.
환경변수(config.settings)는 폴백으로만 사용된다.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

from sqlalchemy import select

logger = logging.getLogger(__name__)


@dataclass
class KISSettings:
    """KIS API 자격증명 모음"""

    vts_app_key: str = ""
    vts_app_secret: str = ""
    vts_account_number: str = ""
    real_app_key: str = ""
    real_app_secret: str = ""
    real_account_number: str = ""
    hts_id: str = ""
    environment: str = "vts"


# 모듈 레벨 캐시 (None이면 아직 미로드)
_cached_settings: KISSettings | None = None


def _build_from_env() -> KISSettings:
    """환경변수(config.settings)에서 KISSettings를 구성한다."""
    from app.core.config import settings as env

    return KISSettings(
        vts_app_key=env.KIS_VTS_APP_KEY,
        vts_app_secret=env.KIS_VTS_APP_SECRET,
        vts_account_number=env.KIS_VTS_ACCOUNT_NUMBER,
        real_app_key=env.KIS_REAL_APP_KEY,
        real_app_secret=env.KIS_REAL_APP_SECRET,
        real_account_number=env.KIS_REAL_ACCOUNT_NUMBER,
        hts_id=env.KIS_HTS_ID,
        environment=env.KIS_ENVIRONMENT,
    )


async def load_kis_settings() -> None:
    """DB에서 admin 사용자의 KIS 설정을 읽어 캐시를 갱신한다.
    DB 조회 실패 또는 값이 없으면 환경변수로 폴백한다.
    """
    global _cached_settings

    from app.core.config import settings as env
    from app.core.database import AsyncSessionLocal
    from app.models.user import User
    from app.models.settings import SystemSetting

    # DB에서 키 이름 → KISSettings 필드 매핑
    _KEY_MAP = {
        "kis_vts_app_key": "vts_app_key",
        "kis_vts_app_secret": "vts_app_secret",
        "kis_vts_account_number": "vts_account_number",
        "kis_real_app_key": "real_app_key",
        "kis_real_app_secret": "real_app_secret",
        "kis_real_account_number": "real_account_number",
        "kis_hts_id": "hts_id",
        "kis_mode": "environment",
    }

    try:
        async with AsyncSessionLocal() as db:
            # admin 사용자 ID 조회
            result = await db.execute(
                select(User).where(User.username == env.ADMIN_USERNAME)
            )
            user = result.scalar_one_or_none()
            if user is None:
                logger.warning("KIS 설정 로드: admin 사용자(%s)를 찾을 수 없음 → 환경변수 사용", env.ADMIN_USERNAME)
                _cached_settings = _build_from_env()
                return

            # 해당 사용자의 KIS 관련 설정값 조회
            result = await db.execute(
                select(SystemSetting).where(
                    SystemSetting.user_id == user.id,
                    SystemSetting.setting_key.in_(list(_KEY_MAP.keys())),
                )
            )
            rows = result.scalars().all()

        # DB값을 딕셔너리로 변환
        db_values: dict[str, str] = {row.setting_key: row.setting_value for row in rows}

        # 환경변수를 기본값으로 먼저 채운 뒤 DB값으로 덮어쓴다
        cfg = _build_from_env()
        for db_key, field_name in _KEY_MAP.items():
            val = db_values.get(db_key, "")
            if val:  # DB에 값이 있을 때만 덮어씀
                setattr(cfg, field_name, val)

        _cached_settings = cfg
        logger.info("KIS 설정 DB 로드 완료 (environment=%s)", cfg.environment)

    except Exception as exc:
        logger.warning("KIS 설정 DB 로드 실패: %s → 환경변수 사용", exc)
        _cached_settings = _build_from_env()


def get_kis_settings() -> KISSettings:
    """캐시된 KISSettings를 반환한다.
    캐시가 비어 있으면 환경변수 기반 기본값을 반환한다 (비동기 불가 컨텍스트 안전).
    """
    if _cached_settings is None:
        return _build_from_env()
    return _cached_settings


async def invalidate_kis_settings() -> None:
    """캐시를 무효화하고 DB에서 재로드한다.
    토큰 캐시도 함께 초기화하여 새 자격증명으로 토큰을 재발급받도록 한다.
    """
    from app.services.kis_client import _token_cache

    _token_cache.clear()
    logger.info("KIS 토큰 캐시 초기화")
    await load_kis_settings()
