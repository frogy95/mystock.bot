"""
전략 API 통합 테스트
GET    /api/v1/strategies
GET    /api/v1/strategies/{id}
GET    /api/v1/strategies/performance
PUT    /api/v1/strategies/{id}/activate
POST   /api/v1/strategies/{id}/clone
PUT    /api/v1/strategies/{id}/name
DELETE /api/v1/strategies/{id}
"""
import pytest

from app.models.strategy import Strategy, StrategyParam
from app.models.user import User


@pytest.mark.asyncio
async def test_list_strategies_empty(client_with_user):
    """전략 목록 조회 - 빈 결과"""
    response = await client_with_user.get("/api/v1/strategies")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_strategies_returns_strategy(client_with_user, db_session):
    """전략 목록 조회 - 프리셋 전략 존재 시 반환"""
    # user_id=None인 프리셋 전략 생성
    strategy = Strategy(
        name="GoldenCross",
        strategy_type="technical",
        is_active=True,
        is_preset=True,
        user_id=None,
    )
    db_session.add(strategy)
    await db_session.commit()

    response = await client_with_user.get("/api/v1/strategies")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "GoldenCross"


@pytest.mark.asyncio
async def test_get_strategy_not_found(client_with_user):
    """전략 상세 조회 - 없는 ID → 404"""
    response = await client_with_user.get("/api/v1/strategies/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_strategy_performance_empty(client_with_user):
    """전략 성과 집계 - 전략 없을 때 빈 배열"""
    response = await client_with_user.get("/api/v1/strategies/performance")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_strategies_returns_preset_and_own(client_with_user, db_session):
    """전략 목록 조회 - 프리셋 전략과 본인 소유 전략 모두 반환"""
    # conftest.py에서 생성한 testuser의 id를 가져오기 위해 쿼리
    from sqlalchemy import select
    result = await db_session.execute(select(User).where(User.username == "testuser"))
    testuser = result.scalar_one()

    # 프리셋 전략 생성 (user_id=None)
    preset = Strategy(
        name="PresetStrategy",
        strategy_type="technical",
        is_active=True,
        is_preset=True,
        user_id=None,
    )
    # 본인 소유 전략 생성 (user_id=testuser.id)
    own = Strategy(
        name="MyStrategy",
        strategy_type="fundamental",
        is_active=True,
        is_preset=False,
        user_id=testuser.id,
    )
    db_session.add(preset)
    db_session.add(own)
    await db_session.commit()

    response = await client_with_user.get("/api/v1/strategies")
    assert response.status_code == 200
    data = response.json()
    names = [d["name"] for d in data]
    # 프리셋과 본인 소유 전략 모두 목록에 포함됨
    assert "PresetStrategy" in names
    assert "MyStrategy" in names
    assert len(data) == 2


@pytest.mark.asyncio
async def test_list_strategies_excludes_other_user_strategy(client_with_user, db_session):
    """전략 목록 조회 - 다른 사용자 소유 전략은 목록에서 제외"""
    # 다른 사용자 생성
    other_user = User(
        username="other",
        is_active=True,
        is_approved=True,
        role="user",
    )
    db_session.add(other_user)
    await db_session.commit()

    # 다른 사용자 소유 전략 생성
    other_strategy = Strategy(
        name="OtherUserStrategy",
        strategy_type="technical",
        is_active=True,
        is_preset=False,
        user_id=other_user.id,
    )
    db_session.add(other_strategy)
    await db_session.commit()

    response = await client_with_user.get("/api/v1/strategies")
    assert response.status_code == 200
    data = response.json()
    names = [d["name"] for d in data]
    # 다른 사용자의 전략은 목록에 포함되지 않음
    assert "OtherUserStrategy" not in names


@pytest.mark.asyncio
async def test_toggle_preset_strategy_returns_404(client_with_user, db_session):
    """전략 활성화 토글 - 프리셋 전략 토글 시 404 반환"""
    # 프리셋 전략 생성 (user_id=None)
    preset = Strategy(
        name="PresetOnly",
        strategy_type="technical",
        is_active=True,
        is_preset=True,
        user_id=None,
    )
    db_session.add(preset)
    await db_session.commit()

    # 프리셋 전략은 본인 소유가 아니므로 토글 불가 → 404
    response = await client_with_user.put(
        f"/api/v1/strategies/{preset.id}/activate",
        json={"is_active": False},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_toggle_own_strategy_succeeds(client_with_user, db_session):
    """전략 활성화 토글 - 본인 소유 전략 토글 성공"""
    from sqlalchemy import select
    result = await db_session.execute(select(User).where(User.username == "testuser"))
    testuser = result.scalar_one()

    # 본인 소유 전략 생성 (is_active=True)
    own = Strategy(
        name="MyToggleStrategy",
        strategy_type="fundamental",
        is_active=True,
        is_preset=False,
        user_id=testuser.id,
    )
    db_session.add(own)
    await db_session.commit()

    # 비활성화로 토글
    response = await client_with_user.put(
        f"/api/v1/strategies/{own.id}/activate",
        json={"is_active": False},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False
    assert data["name"] == "MyToggleStrategy"


@pytest.mark.asyncio
async def test_clone_preset_strategy(client_with_user, db_session):
    """전략 복사 - 프리셋 전략 복사 성공, 복사본은 본인 소유"""
    from sqlalchemy import select
    result = await db_session.execute(select(User).where(User.username == "testuser"))
    testuser = result.scalar_one()

    # 프리셋 전략 생성
    preset = Strategy(
        name="CloneablePreset",
        strategy_type="technical",
        is_active=True,
        is_preset=True,
        user_id=None,
    )
    db_session.add(preset)
    await db_session.commit()

    # 프리셋 전략 복사
    response = await client_with_user.post(f"/api/v1/strategies/{preset.id}/clone")
    assert response.status_code == 200
    data = response.json()
    # 복사본 이름에 원본 이름이 포함됨
    assert "CloneablePreset" in data["name"]
    # 복사본은 본인 소유
    assert data["user_id"] == testuser.id
    # 복사본은 프리셋이 아님
    assert data["is_preset"] is False


@pytest.mark.asyncio
async def test_clone_creates_new_strategy_with_params(client_with_user, db_session):
    """전략 복사 - 파라미터도 함께 복사됨"""
    from sqlalchemy import select
    result = await db_session.execute(select(User).where(User.username == "testuser"))
    testuser = result.scalar_one()

    # 파라미터가 있는 프리셋 전략 생성
    preset = Strategy(
        name="ParamPreset",
        strategy_type="technical",
        is_active=True,
        is_preset=True,
        user_id=None,
    )
    db_session.add(preset)
    await db_session.flush()  # preset.id 확보

    # 파라미터 추가
    param1 = StrategyParam(
        strategy_id=preset.id,
        param_key="short_window",
        param_value="5",
        param_type="int",
    )
    param2 = StrategyParam(
        strategy_id=preset.id,
        param_key="long_window",
        param_value="20",
        param_type="int",
    )
    db_session.add(param1)
    db_session.add(param2)
    await db_session.commit()

    # 전략 복사
    response = await client_with_user.post(f"/api/v1/strategies/{preset.id}/clone")
    assert response.status_code == 200
    data = response.json()
    # 복사본 파라미터가 원본과 동일하게 복사됨
    assert len(data["params"]) == 2
    param_keys = {p["param_key"] for p in data["params"]}
    assert "short_window" in param_keys
    assert "long_window" in param_keys
    # 복사본은 본인 소유이고 새로운 id를 가짐
    assert data["user_id"] == testuser.id
    assert data["id"] != preset.id


@pytest.mark.asyncio
async def test_rename_own_strategy(client_with_user, db_session):
    """전략 이름 변경 - 본인 소유 전략 이름 변경 성공"""
    from sqlalchemy import select
    result = await db_session.execute(select(User).where(User.username == "testuser"))
    testuser = result.scalar_one()

    # 본인 소유 전략 생성
    own = Strategy(
        name="OriginalName",
        strategy_type="technical",
        is_active=True,
        is_preset=False,
        user_id=testuser.id,
    )
    db_session.add(own)
    await db_session.commit()

    # 이름 변경 요청
    response = await client_with_user.put(
        f"/api/v1/strategies/{own.id}/name",
        json={"name": "NewName"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "NewName"


@pytest.mark.asyncio
async def test_rename_preset_strategy_returns_404(client_with_user, db_session):
    """전략 이름 변경 - 프리셋 전략 이름 변경 시 404 반환"""
    # 프리셋 전략 생성 (user_id=None)
    preset = Strategy(
        name="PresetName",
        strategy_type="technical",
        is_active=True,
        is_preset=True,
        user_id=None,
    )
    db_session.add(preset)
    await db_session.commit()

    # 프리셋은 user_id가 None이므로 본인 소유가 아님 → 404
    response = await client_with_user.put(
        f"/api/v1/strategies/{preset.id}/name",
        json={"name": "NewName"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_own_strategy(client_with_user, db_session):
    """전략 삭제 - 본인 소유 전략 삭제 성공"""
    from sqlalchemy import select
    result = await db_session.execute(select(User).where(User.username == "testuser"))
    testuser = result.scalar_one()

    # 본인 소유 전략 생성
    own = Strategy(
        name="ToBeDeleted",
        strategy_type="technical",
        is_active=True,
        is_preset=False,
        user_id=testuser.id,
    )
    db_session.add(own)
    await db_session.commit()

    strategy_id = own.id

    # 전략 삭제 요청
    response = await client_with_user.delete(f"/api/v1/strategies/{strategy_id}")
    assert response.status_code == 204

    # 삭제 후 조회 시 404
    get_response = await client_with_user.get(f"/api/v1/strategies/{strategy_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_preset_strategy_returns_404(client_with_user, db_session):
    """전략 삭제 - 프리셋 전략 삭제 시 404 반환"""
    # 프리셋 전략 생성 (user_id=None)
    preset = Strategy(
        name="PresetsAreUndeletable",
        strategy_type="technical",
        is_active=True,
        is_preset=True,
        user_id=None,
    )
    db_session.add(preset)
    await db_session.commit()

    # 프리셋은 user_id가 None이므로 본인 소유가 아님 → 404
    response = await client_with_user.delete(f"/api/v1/strategies/{preset.id}")
    assert response.status_code == 404
