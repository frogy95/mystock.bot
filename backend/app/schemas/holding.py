"""
보유종목 관련 Pydantic 스키마
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, computed_field


class HoldingResponse(BaseModel):
    """보유종목 응답 스키마 (수익률 계산 포함)"""

    id: int
    stock_code: str
    stock_name: str
    quantity: int
    avg_price: float
    current_price: Optional[float] = None
    stop_loss_rate: Optional[float] = None
    take_profit_rate: Optional[float] = None
    sell_strategy_id: Optional[int] = None
    synced_at: Optional[datetime] = None

    @computed_field
    @property
    def profit_loss(self) -> Optional[float]:
        """평가손익 (현재가 - 평균가) × 수량"""
        if self.current_price is None:
            return None
        return (self.current_price - self.avg_price) * self.quantity

    @computed_field
    @property
    def profit_loss_rate(self) -> Optional[float]:
        """수익률 (%) = (현재가 - 평균가) / 평균가 × 100"""
        if self.current_price is None or self.avg_price == 0:
            return None
        return round((self.current_price - self.avg_price) / self.avg_price * 100, 2)

    @computed_field
    @property
    def total_value(self) -> Optional[float]:
        """평가금액 = 현재가 × 수량"""
        if self.current_price is None:
            return None
        return self.current_price * self.quantity

    model_config = {"from_attributes": True}


class HoldingStopLossUpdate(BaseModel):
    """손절/익절 설정 요청 스키마"""

    stop_loss_rate: Optional[float] = None
    take_profit_rate: Optional[float] = None


class HoldingSellStrategyUpdate(BaseModel):
    """매도 전략 설정 요청 스키마"""

    sell_strategy_id: Optional[int] = None


class PortfolioSyncResponse(BaseModel):
    """KIS 잔고 동기화 응답 스키마"""

    synced_count: int
    holdings: List[HoldingResponse]


class PortfolioSummaryResponse(BaseModel):
    """포트폴리오 요약 응답 스키마"""

    total_evaluation: float  # 총 평가금액
    total_purchase: float    # 총 매입금액
    total_profit_loss: float  # 총 평가손익
    total_profit_loss_rate: float  # 총 수익률 (%)
    deposit: float           # 예수금
    holdings_count: int      # 보유 종목 수
