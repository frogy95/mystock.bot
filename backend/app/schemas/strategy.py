"""
전략 관련 Pydantic 스키마
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class StrategyParamResponse(BaseModel):
    """전략 파라미터 응답 스키마"""

    id: int
    param_key: str
    param_value: str
    param_type: str

    model_config = {"from_attributes": True}


class StrategyParamUpdate(BaseModel):
    """전략 파라미터 업데이트 스키마"""

    param_key: str
    param_value: str
    param_type: str = "float"


class StrategyResponse(BaseModel):
    """전략 응답 스키마"""

    id: int
    name: str
    strategy_type: str
    is_active: bool
    is_preset: bool
    user_id: int | None = None
    params: List[StrategyParamResponse] = []
    created_at: datetime
    buy_conditions: Optional[Dict[str, Any]] = None
    sell_conditions: Optional[Dict[str, Any]] = None
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class StrategyActivateRequest(BaseModel):
    """전략 활성화/비활성화 요청 스키마"""

    is_active: bool


class StrategyParamBulkUpdate(BaseModel):
    """전략 파라미터 일괄 업데이트 요청 스키마"""

    params: List[StrategyParamUpdate]


class StrategyRenameRequest(BaseModel):
    """전략 이름 변경 요청 스키마"""

    name: str


class CustomStrategyCreateRequest(BaseModel):
    """커스텀 전략 생성 요청 스키마"""

    name: str
    description: Optional[str] = None
    buy_conditions: Dict[str, Any]
    sell_conditions: Dict[str, Any]


class CustomStrategyUpdateRequest(BaseModel):
    """커스텀 전략 조건 수정 요청 스키마"""

    buy_conditions: Dict[str, Any]
    sell_conditions: Dict[str, Any]
    description: Optional[str] = None


class StrategySignalResponse(BaseModel):
    """전략 신호 응답 스키마"""

    symbol: str
    signal_type: str       # BUY | SELL | HOLD
    confidence: float
    reason: str
    target_price: Optional[float] = None
