"""
백테스팅 요청/응답 Pydantic 스키마
"""
from datetime import date
from typing import Any, Dict, List, Optional
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


# ── Sprint 24: 다중 백테스트 스키마 ──────────────────────────────────

class BacktestMultiRunRequest(BaseModel):
    """다중 백테스트 실행 요청 스키마"""
    symbol: str
    strategy_ids: List[int]
    start_date: date
    end_date: date
    initial_cash: float = 10_000_000

    @field_validator("symbol")
    @classmethod
    def symbol_must_be_valid(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("종목코드는 비어있을 수 없습니다.")
        return v

    @field_validator("strategy_ids")
    @classmethod
    def strategy_ids_must_not_be_empty(cls, v: List[int]) -> List[int]:
        if not v:
            raise ValueError("최소 1개 이상의 전략을 선택해야 합니다.")
        if len(v) > 10:
            raise ValueError("한 번에 최대 10개 전략까지 선택할 수 있습니다.")
        return v

    @field_validator("end_date")
    @classmethod
    def end_date_must_be_after_start(cls, v: date, info) -> date:
        start = info.data.get("start_date")
        if start and v <= start:
            raise ValueError("종료일은 시작일보다 이후여야 합니다.")
        return v


class BacktestRankingEntry(BaseModel):
    """랭킹 항목 스키마"""
    strategy_id: int
    strategy_name: str
    rank: int
    score: float              # 가중 종합 스코어 (0~100)
    total_return: float       # 총 수익률 (%)
    cagr: float               # 연환산 수익률 (%)
    mdd: float                # 최대 낙폭 (%)
    sharpe_ratio: float       # 샤프 지수
    win_rate: float           # 승률 (%)
    total_trades: int         # 총 거래 횟수


class BacktestMultiResultItem(BaseModel):
    """다중 백테스트 개별 결과"""
    strategy_id: int
    strategy_name: str
    total_return: float
    cagr: float
    mdd: float
    sharpe_ratio: float
    win_rate: float
    total_trades: int
    benchmark_return: float
    equity_curve: List[EquityPoint]


class BacktestMultiResponse(BaseModel):
    """다중 백테스트 전체 응답"""
    symbol: str
    results: List[BacktestMultiResultItem]
    ranking: List[BacktestRankingEntry]


class WatchlistStatusItem(BaseModel):
    """관심종목 상태 개별 항목"""
    item_id: int
    group_name: str
    current_strategy: Optional[str] = None


class StockStatusResponse(BaseModel):
    """종목 보유/관심 상태 응답"""
    is_holding: bool
    holding_id: Optional[int] = None
    current_sell_strategy: Optional[str] = None
    is_watchlist: bool
    watchlist_items: List[WatchlistStatusItem] = []


# ── Sprint 25: AI 추천 스키마 ──────────────────────────────────────────

class AIRecommendResultSummary(BaseModel):
    """AI 추천 요청 내 전략 성과 요약"""
    strategy_name: str
    total_return: float
    mdd: float
    sharpe_ratio: float
    win_rate: float
    total_trades: int


class AIRecommendRequest(BaseModel):
    """AI 전략 추천 요청 스키마"""
    symbol: str
    stock_name: str = ""
    results_summary: List[AIRecommendResultSummary]
    is_holding: bool = False
    is_watchlist: bool = False


class AIRecommendationResponse(BaseModel):
    """AI 전략 추천 응답 스키마"""
    recommended_strategy: str
    confidence: str          # "높음" | "보통" | "낮음"
    analysis: str
    risk_warning: str
    position_advice: str
