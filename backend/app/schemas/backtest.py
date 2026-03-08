"""
백테스팅 요청/응답 Pydantic 스키마
"""
from datetime import date
from typing import Optional
from pydantic import BaseModel, field_validator


class BacktestRunRequest(BaseModel):
    """백테스팅 실행 요청 스키마"""
    symbol: str                          # 종목코드 (예: "005930")
    strategy_name: str                   # 전략명 (예: "GoldenCrossRSI")
    params: dict = {}                    # 전략 파라미터
    start_date: date                     # 백테스트 시작일
    end_date: date                       # 백테스트 종료일
    initial_cash: float = 10_000_000     # 초기 자본 (기본 1천만원)
    strategy_id: Optional[int] = None   # 커스텀 전략 DB ID (커스텀 전략인 경우)

    @field_validator("symbol")
    @classmethod
    def symbol_must_be_valid(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("종목코드는 비어있을 수 없습니다.")
        return v

    @field_validator("end_date")
    @classmethod
    def end_date_must_be_after_start(cls, v: date, info) -> date:
        start = info.data.get("start_date")
        if start and v <= start:
            raise ValueError("종료일은 시작일보다 이후여야 합니다.")
        return v


class EquityPoint(BaseModel):
    """Equity Curve 개별 포인트"""
    date: str       # "YYYY-MM-DD"
    value: float    # 포트폴리오 가치 (원)
    benchmark: float = 0.0      # 벤치마크 가치 (원)
    stock_buyhold: float = 0.0  # 종목 바이앤홀드 가치 (원)


class BacktestTrade(BaseModel):
    """시뮬레이션 개별 거래 내역"""
    type: str           # "BUY" | "SELL"
    date: str           # "YYYY-MM-DD"
    price: float        # 거래 가격
    qty: int            # 거래 수량
    amount: float       # 거래 금액 (price * qty)
    pnl: Optional[float] = None  # 손익 (SELL 시), BUY는 None


class BacktestResultResponse(BaseModel):
    """백테스팅 결과 응답 스키마"""
    id: int
    symbol: str
    strategy_name: str
    start_date: str
    end_date: str
    total_return: float       # 총 수익률 (%)
    cagr: float               # 연환산 수익률 (%)
    mdd: float                # 최대 낙폭 (%)
    sharpe_ratio: float       # 샤프 지수
    total_trades: int         # 총 거래 횟수
    win_rate: float           # 승률 (%)
    benchmark_return: float   # 벤치마크 수익률 (%)
    equity_curve: list[EquityPoint]  # 자산 가치 곡선
    trades: list[BacktestTrade] = []  # 시뮬레이션 거래 내역
    created_at: str
