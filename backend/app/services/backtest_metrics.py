"""
백테스팅 성과 지표 계산 모듈
VectorBT 포트폴리오 또는 기본 시뮬레이션 결과에서 주요 지표를 추출한다.
"""
import math
import logging
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger("mystock.bot")


def _calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.03) -> float:
    """
    샤프 지수를 계산한다.
    returns: 일별 수익률 시리즈
    risk_free_rate: 무위험 수익률 (연간, 기본 3%)
    """
    if len(returns) < 2:
        return 0.0
    daily_rf = risk_free_rate / 252
    excess_returns = returns - daily_rf
    mean_excess = excess_returns.mean()
    std_excess = excess_returns.std()
    if std_excess == 0 or math.isnan(std_excess):
        return 0.0
    sharpe = (mean_excess / std_excess) * math.sqrt(252)
    if math.isnan(sharpe) or math.isinf(sharpe):
        return 0.0
    return round(sharpe, 3)


def _calculate_max_drawdown(equity: pd.Series) -> float:
    """
    최대 낙폭(MDD)을 계산한다.
    equity: 포트폴리오 가치 시리즈
    """
    if len(equity) < 2:
        return 0.0
    rolling_max = equity.cummax()
    drawdown = (equity - rolling_max) / rolling_max
    mdd = drawdown.min()
    return float(mdd) if not math.isnan(mdd) else 0.0


def _extract_vbt_trades(trades_df: Any) -> list:
    """VBT records_readable DataFrame에서 BUY/SELL 거래 내역을 추출한다."""
    if trades_df is None:
        return []
    result = []
    try:
        for _, row in trades_df.iterrows():
            qty = max(1, int(round(float(row["Size"]))))
            entry_price = float(row["Avg Entry Price"])
            exit_price = float(row["Avg Exit Price"])
            entry_date = str(row["Entry Timestamp"].date()) if hasattr(row["Entry Timestamp"], "date") else str(row["Entry Timestamp"])[:10]
            exit_date = str(row["Exit Timestamp"].date()) if hasattr(row["Exit Timestamp"], "date") else str(row["Exit Timestamp"])[:10]
            result.append({
                "type": "BUY",
                "date": entry_date,
                "price": entry_price,
                "qty": qty,
                "amount": round(entry_price * qty, 2),
                "pnl": None,
            })
            result.append({
                "type": "SELL",
                "date": exit_date,
                "price": exit_price,
                "qty": qty,
                "amount": round(exit_price * qty, 2),
                "pnl": round(float(row["PnL"]), 2),
            })
    except Exception as e:
        logger.warning(f"VBT 거래 내역 추출 실패: {e}")
    return result


def _build_stock_buyhold_values(dates: list, initial_cash: float, close: Any) -> list:
    """
    종목 바이앤홀드 가치 시계열을 생성한다.
    초기 자본으로 첫날 종가에 전량 매수했을 때의 포트폴리오 가치.
    """
    try:
        bm_index = pd.to_datetime(dates)
        close_aligned = close.reindex(bm_index, method="ffill").bfill()
        if close_aligned.isna().any() or len(close_aligned) == 0:
            raise ValueError("종가 날짜 정렬 실패")
        start_price = float(close_aligned.iloc[0])
        if start_price == 0:
            raise ValueError("시작 종가가 0")
        return [initial_cash * float(v) / start_price for v in close_aligned]
    except Exception as e:
        logger.warning(f"종목 바이앤홀드 시계열 생성 실패: {e}")
        return [initial_cash] * len(dates)


def _build_benchmark_values(dates: list, initial_cash: float, benchmark_return: float, benchmark_prices: Any = None) -> list:
    """
    벤치마크 가치 시계열을 생성한다.
    benchmark_prices(KOSPI 일별 종가 Series)가 있으면 실제 수익률을 사용하고,
    없으면 연 benchmark_return% 복리 성장 근사값을 사용한다.
    """
    if benchmark_prices is not None and len(benchmark_prices) >= 2:
        try:
            # dates와 동일한 날짜 인덱스에 맞게 리샘플링 (전진 채움)
            bm_index = pd.to_datetime(dates)
            bm_aligned = benchmark_prices.reindex(bm_index, method="ffill")
            # 여전히 NaN인 첫 번째 날짜는 역방향 채움
            bm_aligned = bm_aligned.bfill()
            if bm_aligned.isna().any():
                raise ValueError("KOSPI 날짜 정렬 실패")
            start_val = float(bm_aligned.iloc[0])
            return [initial_cash * float(v) / start_val for v in bm_aligned]
        except Exception as e:
            logger.warning(f"KOSPI 시계열 정렬 실패, 복리 근사 사용: {e}")
    # 복리 근사
    daily_bm_rate = (1 + benchmark_return) ** (1 / 252) - 1
    return [initial_cash * (1 + daily_bm_rate) ** i for i in range(len(dates))]


def _calculate_metrics_from_vbt(portfolio: Any, benchmark_return: float, initial_cash: float = 10_000_000, benchmark_prices: Any = None, close: Any = None) -> dict:
    """vectorbt 포트폴리오 객체에서 성과 지표를 계산한다."""
    try:
        total_return = float(portfolio.total_return())
        if math.isnan(total_return):
            total_return = 0.0

        # 샤프 지수
        try:
            sharpe = float(portfolio.sharpe_ratio())
            if math.isnan(sharpe) or math.isinf(sharpe):
                sharpe = 0.0
        except Exception:
            sharpe = 0.0

        # 최대 낙폭
        try:
            max_dd = float(portfolio.max_drawdown())
            if math.isnan(max_dd):
                max_dd = 0.0
        except Exception:
            max_dd = 0.0

        # 거래 통계
        trades = None
        try:
            trades = portfolio.trades.records_readable
            total_trades = len(trades)
            if total_trades > 0:
                winning_trades = len(trades[trades["PnL"] > 0])
                win_rate = winning_trades / total_trades
            else:
                win_rate = 0.0
        except Exception:
            total_trades = 0
            win_rate = 0.0

        # CAGR 계산
        try:
            equity = portfolio.value()
            days = (equity.index[-1] - equity.index[0]).days
            years = days / 365.25 if days > 0 else 1.0
            cagr = ((1 + total_return) ** (1 / years) - 1) if years > 0 else total_return
        except Exception:
            cagr = total_return

        # Equity Curve 생성
        try:
            equity_values = portfolio.value().tolist()
            dates = [str(d.date()) if hasattr(d, 'date') else str(d) for d in portfolio.value().index]
        except Exception:
            equity_values = []
            dates = []

        # 벤치마크 시계열: 실제 KOSPI 데이터 또는 복리 근사
        bm_values = _build_benchmark_values(dates, initial_cash, benchmark_return, benchmark_prices)

        # 종목 바이앤홀드 시계열
        sh_values = _build_stock_buyhold_values(dates, initial_cash, close) if close is not None else [initial_cash] * len(dates)

        return {
            "total_return": round(total_return * 100, 2),
            "cagr": round(cagr * 100, 2),
            "mdd": round(max_dd * 100, 2),
            "sharpe_ratio": round(sharpe, 3),
            "total_trades": total_trades,
            "win_rate": round(win_rate * 100, 2),
            "benchmark_return": round(benchmark_return * 100, 2),
            "equity_curve": [
                {"date": d, "value": round(v, 2), "benchmark": round(b, 2), "stock_buyhold": round(sh, 2)}
                for d, v, b, sh in zip(dates, equity_values, bm_values, sh_values)
            ],
            "trades": _extract_vbt_trades(trades),
        }
    except Exception as e:
        logger.error(f"VectorBT 지표 계산 오류: {e}")
        return _empty_metrics(benchmark_return, str(e))


def _calculate_metrics_from_basic(
    portfolio_data: dict,
    close: pd.Series,
    initial_cash: float,
    benchmark_return: float,
    benchmark_prices: Any = None,
) -> dict:
    """기본 시뮬레이션 결과에서 성과 지표를 계산한다."""
    try:
        equity = portfolio_data["equity"]
        trades_list = portfolio_data["trades"]

        # 총 수익률
        final_value = equity.iloc[-1]
        total_return = (final_value - initial_cash) / initial_cash

        # 일별 수익률로 샤프 지수 계산
        daily_returns = equity.pct_change().dropna()
        sharpe = _calculate_sharpe_ratio(daily_returns)

        # 최대 낙폭
        max_dd = _calculate_max_drawdown(equity)

        # 거래 통계
        sell_trades = [t for t in trades_list if t["type"] == "SELL"]
        total_trades = len(sell_trades)
        if total_trades > 0:
            winning_trades = sum(1 for t in sell_trades if t.get("pnl", 0) and t["pnl"] > 0)
            win_rate = winning_trades / total_trades
        else:
            win_rate = 0.0

        # CAGR 계산
        days = (close.index[-1] - close.index[0]).days
        years = days / 365.25 if days > 0 else 1.0
        cagr = ((1 + total_return) ** (1 / years) - 1) if years > 0 else total_return

        # Equity Curve 생성
        dates = [str(d.date()) if hasattr(d, 'date') else str(d) for d in equity.index]
        equity_values = equity.tolist()

        # 벤치마크 시계열: 실제 KOSPI 데이터 또는 복리 근사
        bm_values = _build_benchmark_values(dates, initial_cash, benchmark_return, benchmark_prices)

        # 종목 바이앤홀드 시계열
        sh_values = _build_stock_buyhold_values(dates, initial_cash, close)

        return {
            "total_return": round(total_return * 100, 2),
            "cagr": round(cagr * 100, 2),
            "mdd": round(max_dd * 100, 2),
            "sharpe_ratio": sharpe,
            "total_trades": total_trades,
            "win_rate": round(win_rate * 100, 2),
            "benchmark_return": round(benchmark_return * 100, 2),
            "equity_curve": [
                {"date": d, "value": round(v, 2), "benchmark": round(b, 2), "stock_buyhold": round(sh, 2)}
                for d, v, b, sh in zip(dates, equity_values, bm_values, sh_values)
            ],
            "trades": [
                {
                    "type": t["type"],
                    "date": t.get("date", ""),
                    "price": t["price"],
                    "qty": t["qty"],
                    "amount": round(t["price"] * t["qty"], 2),
                    "pnl": round(t["pnl"], 2) if t["pnl"] is not None else None,
                }
                for t in trades_list
            ],
        }
    except Exception as e:
        logger.error(f"기본 시뮬레이션 지표 계산 오류: {e}")
        return _empty_metrics(benchmark_return, str(e))


def _empty_metrics(benchmark_return: float, error: str = "") -> dict:
    """오류 발생 시 반환할 빈 지표 딕셔너리"""
    result = {
        "total_return": 0.0,
        "cagr": 0.0,
        "mdd": 0.0,
        "sharpe_ratio": 0.0,
        "total_trades": 0,
        "win_rate": 0.0,
        "benchmark_return": round(benchmark_return * 100, 2),
        "equity_curve": [],
    }
    if error:
        result["error"] = error
    return result


def calculate_metrics(result: dict) -> dict:
    """
    백테스팅 엔진 결과에서 성과 지표를 계산한다.

    Args:
        result: run_backtest()가 반환한 딕셔너리
            - portfolio_data: 포트폴리오 시뮬레이션 결과
            - close: 종가 시리즈
            - benchmark_return: 벤치마크 수익률
            - initial_cash: 초기 자본
            - use_vbt: vectorbt 사용 여부

    Returns:
        총수익률, CAGR, MDD, 샤프지수, 거래수, 승률, 벤치마크수익률, equity_curve 포함 딕셔너리
    """
    portfolio_data = result["portfolio_data"]
    close = result["close"]
    benchmark_return = result["benchmark_return"]
    benchmark_prices = result.get("benchmark_prices")  # 실제 KOSPI 일별 종가 (선택)
    initial_cash = result.get("initial_cash", 10_000_000)
    use_vbt = result.get("use_vbt", False)

    if use_vbt and "vbt_portfolio" in portfolio_data:
        return _calculate_metrics_from_vbt(portfolio_data["vbt_portfolio"], benchmark_return, initial_cash, benchmark_prices, close)
    else:
        return _calculate_metrics_from_basic(portfolio_data, close, initial_cash, benchmark_return, benchmark_prices)
