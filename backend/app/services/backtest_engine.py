"""
VectorBT 기반 백테스팅 엔진
과거 OHLCV 데이터에 전략을 적용하여 성과를 시뮬레이션한다.
vectorbt 미설치 시 기본 시뮬레이션 로직으로 대체한다.
"""
import logging
from dataclasses import dataclass
from datetime import date
import pandas as pd

from app.services.kis_client import kis_client
from app.services.indicators import _ohlcv_to_df, _calculate_indicators
from app.services.strategy_engine import get_strategy

logger = logging.getLogger("mystock.bot")

# vectorbt 임포트 시도 (선택적 의존성)
try:
    import vectorbt as vbt
    _VBT_AVAILABLE = True
    logger.info("vectorbt 로드 성공")
except ImportError:
    _VBT_AVAILABLE = False
    logger.warning("vectorbt 미설치. 기본 시뮬레이션 로직으로 대체한다.")


@dataclass
class BacktestConfig:
    """백테스팅 설정 데이터클래스"""
    symbol: str                          # 종목코드
    strategy_name: str                   # 전략명
    params: dict                         # 전략 파라미터
    start_date: date                     # 시작일
    end_date: date                       # 종료일
    initial_cash: float = 10_000_000     # 초기 자본 (기본 1천만원)
    commission: float = 0.00015          # 수수료 (기본 0.015%)


def _build_signals(
    df: pd.DataFrame,
    strategy_name: str,
    params: dict,
    signal_start_idx: int = 20,
) -> tuple[pd.Series, pd.Series]:
    """
    전략 엔진을 사용하여 매수/매도 신호 시리즈를 생성한다.
    각 시점(signal_start_idx번째 행부터)에서 누적 데이터를 전략에 입력하여 신호를 평가한다.
    signal_start_idx로 루프 시작점을 제한하여 성능을 최적화하되 df 전체를 받아 인덱스 정합성을 유지한다.
    """
    engine = get_strategy(strategy_name)
    if engine is None:
        raise ValueError(f"전략 없음: {strategy_name}")

    # 원본 컬럼명 확인 (소문자 또는 pandas_ta 표준명 처리)
    col_map = {c.lower(): c for c in df.columns}

    def _get_col(name: str):
        return col_map.get(name, name)

    entries = pd.Series(False, index=df.index, dtype=bool)
    exits = pd.Series(False, index=df.index, dtype=bool)

    for i in range(signal_start_idx, len(df)):
        slice_df = df.iloc[: i + 1]
        try:
            # KIS API 형식의 딕셔너리 리스트로 변환
            chart_list = [
                {
                    "date": idx.strftime("%Y%m%d") if hasattr(idx, 'strftime') else str(idx).replace("-", ""),
                    "open": float(row.get(_get_col("open"), row.get("Open", 0))),
                    "high": float(row.get(_get_col("high"), row.get("High", 0))),
                    "low": float(row.get(_get_col("low"), row.get("Low", 0))),
                    "close": float(row.get(_get_col("close"), row.get("Close", 0))),
                    "volume": int(row.get(_get_col("volume"), row.get("Volume", 0))),
                }
                for idx, row in slice_df.iterrows()
            ]
            signal = engine.evaluate_from_ohlcv(chart_list, params)
            if signal.signal_type == "BUY" and signal.confidence >= 0.5:
                entries.iloc[i] = True
            elif signal.signal_type == "SELL" and signal.confidence >= 0.5:
                exits.iloc[i] = True
        except Exception as e:
            logger.debug(f"신호 생성 오류 (인덱스 {i}): {e}")
            continue

    return entries, exits


def _simulate_portfolio_basic(
    close: pd.Series,
    entries: pd.Series,
    exits: pd.Series,
    initial_cash: float,
    commission: float,
) -> dict:
    """
    vectorbt 미설치 시 사용하는 기본 포트폴리오 시뮬레이션.
    단순 매수/매도 로직으로 수익률과 거래 내역을 계산한다.
    """
    cash = initial_cash
    shares = 0
    equity_values = []
    trades = []
    buy_price = 0.0

    for i, (dt, price) in enumerate(close.items()):
        # 매수 신호
        if entries.iloc[i] and shares == 0 and cash > 0:
            buy_qty = int(cash / price)
            if buy_qty > 0:
                cost = buy_qty * price * (1 + commission)
                if cost <= cash:
                    cash -= cost
                    shares = buy_qty
                    buy_price = price
                    trades.append({"type": "BUY", "date": str(dt.date()), "price": price, "qty": buy_qty, "pnl": None})

        # 매도 신호
        elif exits.iloc[i] and shares > 0:
            revenue = shares * price * (1 - commission)
            pnl = revenue - (shares * buy_price)
            cash += revenue
            trades.append({"type": "SELL", "date": str(dt.date()), "price": price, "qty": shares, "pnl": pnl})
            shares = 0
            buy_price = 0.0

        # 현재 포트폴리오 가치 계산
        portfolio_value = cash + (shares * price)
        equity_values.append(portfolio_value)

    # 미청산 포지션 강제 청산 (마지막 종가 기준)
    if shares > 0:
        last_price = close.iloc[-1]
        last_date = str(close.index[-1].date()) if hasattr(close.index[-1], 'date') else str(close.index[-1])
        revenue = shares * last_price * (1 - commission)
        pnl = revenue - (shares * buy_price)
        trades.append({"type": "SELL", "date": last_date, "price": last_price, "qty": shares, "pnl": pnl})
        equity_values[-1] = cash + revenue

    equity_series = pd.Series(equity_values, index=close.index)
    return {"equity": equity_series, "trades": trades}


async def run_backtest(config: BacktestConfig) -> dict:
    """
    백테스팅을 실행하고 결과를 반환한다.

    Returns:
        portfolio_data: 포트폴리오 시뮬레이션 결과 딕셔너리
        close: 종가 시리즈
        entries: 매수 신호 시리즈
        exits: 매도 신호 시리즈
        benchmark_return: 벤치마크 수익률 (연평균)
        df: OHLCV + 지표 DataFrame
        use_vbt: vectorbt 사용 여부
    """
    # 1. 차트 데이터 조회 (DB 캐시 → KIS API → yfinance 폴백)
    from app.services.chart_data_service import get_chart_data
    warmup_days = 80  # SMA(60) 계산을 위한 워밍업 + 여유분
    chart_data = await get_chart_data(config.symbol, config.start_date, config.end_date, warmup_days=warmup_days)
    if not chart_data or len(chart_data) < 30:
        raise ValueError(f"차트 데이터 부족: {config.symbol} (최소 30일 데이터 필요)")

    # 2. DataFrame 변환
    df = pd.DataFrame(chart_data)
    # KIS API는 날짜를 "YYYYMMDD" 형식으로 반환한다
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d", errors="coerce")
    df = df.dropna(subset=["date"])
    df = df.set_index("date").sort_index()

    start_ts = pd.Timestamp(config.start_date)
    end_ts = pd.Timestamp(config.end_date)
    # 날짜 필터링은 신호 생성 후 적용 (지표 계산에 과거 데이터 필요)

    if len(df) < 60:
        raise ValueError(f"차트 데이터 부족: {len(df)}일 (최소 60일 필요)")

    # 요청 기간에 데이터가 존재하는지 검증
    period_count = len(df[(df.index >= start_ts) & (df.index <= end_ts)])
    if period_count < 1:
        raise ValueError(
            f"요청 기간에 데이터 없음. 날짜 범위를 확인해주세요: {config.start_date} ~ {config.end_date}"
        )

    # 3. 지표 계산을 위해 컬럼명을 표준화(대문자)
    rename_map = {
        "open": "Open", "high": "High", "low": "Low",
        "close": "Close", "volume": "Volume",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    # pandas_ta 지표 계산
    _calculate_indicators(df)

    # 4. 전략 신호 생성
    # start_ts 근처부터 루프를 시작하여 성능을 최적화한다 (df 전체를 전달해 인덱스 정합성 유지)
    # SMA(60) 계산을 위한 최소 워밍업 보장 (60행 이상에서 신호 생성 시작)
    start_signal_idx = max(60, df.index.searchsorted(start_ts) - 5)
    entries, exits = _build_signals(df, config.strategy_name, config.params, signal_start_idx=start_signal_idx)

    # 요청 기간으로 결과 필터링 (신호 생성은 전체 데이터 기반)
    period_mask = (df.index >= start_ts) & (df.index <= end_ts)
    df = df[period_mask]
    entries = entries[period_mask]
    exits = exits[period_mask]

    # 5. 종가 시리즈 (소문자 'Close' 또는 'close' 처리)
    close_col = "Close" if "Close" in df.columns else "close"
    close = df[close_col].astype(float)

    # 6. 포트폴리오 시뮬레이션
    portfolio_data = None
    use_vbt = False

    if _VBT_AVAILABLE:
        try:
            portfolio = vbt.Portfolio.from_signals(
                close,
                entries=entries,
                exits=exits,
                init_cash=config.initial_cash,
                fees=config.commission,
                freq="D",
            )
            portfolio_data = {"vbt_portfolio": portfolio}
            use_vbt = True
            logger.info(f"vectorbt 시뮬레이션 완료: {config.symbol}")
        except Exception as e:
            logger.warning(f"vectorbt 시뮬레이션 오류, 기본 방식으로 대체: {e}")

    if not use_vbt:
        portfolio_data = _simulate_portfolio_basic(
            close, entries, exits, config.initial_cash, config.commission
        )
        logger.info(f"기본 시뮬레이션 완료: {config.symbol}")

    # KOSPI 벤치마크 (KIS API에서 지수 조회 불가 시 고정 수익률로 대체)
    benchmark_return = 0.08  # KOSPI 연평균 8% 가정

    return {
        "portfolio_data": portfolio_data,
        "close": close,
        "entries": entries,
        "exits": exits,
        "benchmark_return": benchmark_return,
        "df": df,
        "initial_cash": config.initial_cash,
        "use_vbt": use_vbt,
    }
