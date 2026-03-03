"""
공통 의존성 함수 모듈
여러 라우터에서 공유하는 의존성 헬퍼 함수를 정의한다.
"""
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def get_user_id(username: str, db: AsyncSession) -> int:
    """username으로 user_id를 조회한다. 없으면 404 예외를 발생시킨다."""
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return user.id
