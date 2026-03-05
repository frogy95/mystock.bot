"""
KIS 설정 캐시 모듈
DB의 system_settings 테이블에서 KIS 자격증명을 읽어 메모리에 캐싱한다.
KIS/Telegram 설정은 DB(system_settings)에서만 관리하며 환경변수 폴백은 사용하지 않는다.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

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


async def load_kis_settings() -> None:
    """DB에서 admin 사용자의 KIS 설정을 읽어 캐시를 갱신한다.
    DB 조회 실패 또는 admin 사용자가 없으면 빈 설정을 사용한다.
    """
    global _cached_settings

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
            # role=admin 사용자 ID 조회
            result = await db.execute(
                select(User).where(User.role == "admin")
            )
            user = result.scalar_one_or_none()
            if user is None:
                logger.warning("KIS 설정 로드: admin 사용자를 찾을 수 없음 → 빈 설정 사용")
                _cached_settings = KISSettings()
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

        # 기본값(빈 문자열)에서 시작해 DB값으로 채운다
        cfg = KISSettings()
        for db_key, field_name in _KEY_MAP.items():
            val = db_values.get(db_key, "")
            if val:  # DB에 값이 있을 때만 덮어씀
                setattr(cfg, field_name, val)

        _cached_settings = cfg
        logger.info("KIS 설정 DB 로드 완료 (environment=%s)", cfg.environment)

    except Exception as exc:
        logger.warning("KIS 설정 DB 로드 실패: %s → 빈 설정 사용", exc)
        _cached_settings = KISSettings()


def get_kis_settings() -> KISSettings:
    """캐시된 KISSettings를 반환한다.
    캐시가 비어 있으면 빈 기본값을 반환한다 (비동기 불가 컨텍스트 안전).
    """
    if _cached_settings is None:
        return KISSettings()
    return _cached_settings


async def invalidate_kis_settings() -> None:
    """캐시를 무효화하고 DB에서 재로드한다.
    토큰 캐시도 함께 초기화하여 새 자격증명으로 토큰을 재발급받도록 한다.
    """
    from app.services.kis_client import _token_cache

    _token_cache.clear()
    logger.info("KIS 토큰 캐시 초기화")
    await load_kis_settings()
