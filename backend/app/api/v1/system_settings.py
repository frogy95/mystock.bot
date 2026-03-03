"""
시스템 설정 API 엔드포인트
KIS/텔레그램/매매시간/안전장치 전체 설정을 관리한다.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, is_demo_user
from app.core.database import get_db
from app.services.demo_data import get_demo_system_settings
from app.models.settings import SystemSetting
from app.models.user import User

router = APIRouter()


class SettingItem(BaseModel):
    """개별 설정 항목"""

    setting_key: str
    setting_value: str
    setting_type: str = "str"


class SettingsUpdateRequest(BaseModel):
    """설정 일괄 업데이트 요청"""

    settings: List[SettingItem]


class SettingResponse(BaseModel):
    """설정 응답"""

    setting_key: str
    setting_value: str
    setting_type: str

    model_config = {"from_attributes": True}


@router.get("", response_model=List[SettingResponse], summary="전체 설정 조회")
async def get_all_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """사용자의 모든 시스템 설정을 반환한다."""
    if is_demo_user(current_user.username):
        return get_demo_system_settings()
    result = await db.execute(
        select(SystemSetting).where(SystemSetting.user_id == current_user.id)
        .order_by(SystemSetting.setting_key)
    )
    return result.scalars().all()


@router.put("", response_model=List[SettingResponse], summary="설정 일괄 업데이트")
async def update_settings(
    body: SettingsUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """설정을 일괄 업데이트한다. (upsert)"""
    if is_demo_user(current_user.username):
        raise HTTPException(status_code=403, detail="데모 모드에서는 사용할 수 없습니다.")

    for item in body.settings:
        result = await db.execute(
            select(SystemSetting).where(
                SystemSetting.user_id == current_user.id,
                SystemSetting.setting_key == item.setting_key,
            )
        )
        setting = result.scalar_one_or_none()
        if setting:
            setting.setting_value = item.setting_value
            setting.setting_type = item.setting_type
        else:
            db.add(SystemSetting(
                user_id=current_user.id,
                setting_key=item.setting_key,
                setting_value=item.setting_value,
                setting_type=item.setting_type,
            ))

    await db.commit()

    # KIS 관련 키 변경 시 설정 캐시 무효화 (새 자격증명으로 즉시 반영)
    _KIS_KEYS = {
        "kis_vts_app_key", "kis_vts_app_secret", "kis_vts_account_number",
        "kis_real_app_key", "kis_real_app_secret", "kis_real_account_number",
        "kis_hts_id", "kis_mode",
    }
    updated_keys = {item.setting_key for item in body.settings}
    if updated_keys & _KIS_KEYS:
        from app.services.kis_settings_cache import invalidate_kis_settings
        await invalidate_kis_settings()

    result = await db.execute(
        select(SystemSetting).where(SystemSetting.user_id == current_user.id)
        .order_by(SystemSetting.setting_key)
    )
    return result.scalars().all()


@router.get("/{key}", response_model=SettingResponse, summary="단일 설정 조회")
async def get_setting(
    key: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """특정 키의 설정값을 반환한다."""
    if is_demo_user(current_user.username):
        settings_list = get_demo_system_settings()
        setting = next((s for s in settings_list if s["setting_key"] == key), None)
        if setting is None:
            raise HTTPException(status_code=404, detail=f"설정 키 '{key}'를 찾을 수 없습니다.")
        return setting
    result = await db.execute(
        select(SystemSetting).where(
            SystemSetting.user_id == current_user.id,
            SystemSetting.setting_key == key,
        )
    )
    setting = result.scalar_one_or_none()
    if setting is None:
        raise HTTPException(status_code=404, detail=f"설정 키 '{key}'를 찾을 수 없습니다.")
    return setting
