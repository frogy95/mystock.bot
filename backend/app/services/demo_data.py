"""
데모 모드 더미 데이터 모듈
프론트엔드 mock 데이터를 백엔드 스키마에 맞게 Python dict로 제공한다.
날짜는 오늘 기준으로 상대적으로 계산한다.
"""
from datetime import datetime, timedelta, date


def _dt(days_ago: int, hour: int = 9, minute: int = 0) -> str:
    """오늘 기준 N일 전 ISO 날짜 문자열을 반환한다."""
    d = datetime.now() - timedelta(days=days_ago)
    return d.replace(hour=hour, minute=minute, second=0, microsecond=0).isoformat()


def _date(days_ago: int) -> str:
    """오늘 기준 N일 전 날짜 문자열 (YYYY-MM-DD)을 반환한다."""
    return (date.today() - timedelta(days=days_ago)).isoformat()


def get_demo_holdings() -> list:
    """보유종목 더미 데이터 (HoldingResponse 형식)"""
    return [
        {
            "id": 1,
            "stock_code": "005930",
            "stock_name": "삼성전자",
            "quantity": 100,
            "avg_price": 72000.0,
            "current_price": 74500.0,
            "stop_loss_rate": -5.0,
            "take_profit_rate": 15.0,
            "sell_strategy_id": 1,
            "synced_at": _dt(1),
        },
        {
            "id": 2,
            "stock_code": "000660",
            "stock_name": "SK하이닉스",
            "quantity": 30,
            "avg_price": 178000.0,
            "current_price": 185500.0,
            "stop_loss_rate": -7.0,
            "take_profit_rate": 20.0,
            "sell_strategy_id": 2,
            "synced_at": _dt(1),
        },
        {
            "id": 3,
            "stock_code": "035720",
            "stock_name": "카카오",
            "quantity": 50,
            "avg_price": 52000.0,
            "current_price": 48300.0,
            "stop_loss_rate": -10.0,
            "take_profit_rate": 15.0,
            "sell_strategy_id": 3,
            "synced_at": _dt(1),
        },
        {
            "id": 4,
            "stock_code": "051910",
            "stock_name": "LG화학",
            "quantity": 10,
            "avg_price": 380000.0,
            "current_price": 395000.0,
            "stop_loss_rate": -5.0,
            "take_profit_rate": 12.0,
            "sell_strategy_id": 1,
            "synced_at": _dt(1),
        },
        {
            "id": 5,
            "stock_code": "006400",
            "stock_name": "삼성SDI",
            "quantity": 15,
            "avg_price": 420000.0,
            "current_price": 432000.0,
            "stop_loss_rate": -5.0,
            "take_profit_rate": 15.0,
            "sell_strategy_id": None,
            "synced_at": _dt(1),
        },
    ]


def get_demo_portfolio_summary() -> dict:
    """포트폴리오 요약 더미 데이터 (PortfolioSummaryResponse 형식)"""
    return {
        "total_evaluation": 52340000.0,
        "total_purchase": 50000000.0,
        "total_profit_loss": 2340000.0,
        "total_profit_loss_rate": 4.68,
        "deposit": 12500000.0,
        "holdings_count": 5,
        "daily_profit_loss": 156000.0,
        "daily_profit_rate": 0.30,
    }


def get_demo_orders() -> list:
    """주문 목록 더미 데이터 (OrderResponse 형식)"""
    return [
        {
            "id": 1,
            "stock_code": "005930",
            "order_type": "buy",
            "status": "filled",
            "strategy_id": 1,
            "quantity": 100,
            "price": 72000.0,
            "created_at": _dt(2, 9, 10),
            "updated_at": _dt(2, 9, 15),
        },
        {
            "id": 2,
            "stock_code": "000660",
            "order_type": "buy",
            "status": "filled",
            "strategy_id": 2,
            "quantity": 30,
            "price": 183000.0,
            "created_at": _dt(3, 10, 5),
            "updated_at": _dt(3, 10, 7),
        },
        {
            "id": 3,
            "stock_code": "051910",
            "order_type": "sell",
            "status": "filled",
            "strategy_id": 1,
            "quantity": 10,
            "price": 398000.0,
            "created_at": _dt(4, 13, 20),
            "updated_at": _dt(4, 13, 24),
        },
        {
            "id": 4,
            "stock_code": "035720",
            "order_type": "sell",
            "status": "pending",
            "strategy_id": 2,
            "quantity": 20,
            "price": 49000.0,
            "created_at": _dt(1, 13, 45),
            "updated_at": _dt(1, 13, 45),
        },
        {
            "id": 5,
            "stock_code": "006400",
            "order_type": "buy",
            "status": "pending",
            "strategy_id": 1,
            "quantity": 15,
            "price": 428000.0,
            "created_at": _dt(1, 10, 20),
            "updated_at": _dt(1, 10, 20),
        },
        {
            "id": 6,
            "stock_code": "051910",
            "order_type": "buy",
            "status": "cancelled",
            "strategy_id": 3,
            "quantity": 5,
            "price": 388000.0,
            "created_at": _dt(2, 14, 20),
            "updated_at": _dt(2, 14, 20),
        },
    ]


def get_demo_daily_summary() -> dict:
    """일일 매매 요약 더미 데이터 (DailySummaryResponse 형식)"""
    orders = [
        o for o in get_demo_orders()
        if o["created_at"].startswith(_date(1))
    ]
    buy_orders = [o for o in orders if o["order_type"] == "buy"]
    sell_orders = [o for o in orders if o["order_type"] == "sell"]
    return {
        "date": _date(0),
        "total_buy_count": len(buy_orders),
        "total_sell_count": len(sell_orders),
        "total_buy_amount": sum((o["price"] or 0) * (o["quantity"] or 0) for o in buy_orders),
        "total_sell_amount": sum((o["price"] or 0) * (o["quantity"] or 0) for o in sell_orders),
        "orders": orders,
    }


def get_demo_strategies() -> list:
    """전략 목록 더미 데이터 (StrategyResponse 형식)"""
    return [
        {
            "id": 1,
            "name": "골든크로스 + RSI",
            "strategy_type": "GoldenCrossRSI",
            "is_active": True,
            "is_preset": True,
            "params": [
                {"id": 1, "param_key": "shortPeriod", "param_value": "20", "param_type": "float"},
                {"id": 2, "param_key": "longPeriod", "param_value": "60", "param_type": "float"},
                {"id": 3, "param_key": "rsiPeriod", "param_value": "14", "param_type": "float"},
                {"id": 4, "param_key": "rsiOversold", "param_value": "35", "param_type": "float"},
            ],
            "created_at": _dt(30),
        },
        {
            "id": 2,
            "name": "볼린저 밴드 반전",
            "strategy_type": "BollingerReversal",
            "is_active": False,
            "is_preset": True,
            "params": [
                {"id": 5, "param_key": "bbPeriod", "param_value": "20", "param_type": "float"},
                {"id": 6, "param_key": "bbStdDev", "param_value": "2.0", "param_type": "str"},
                {"id": 7, "param_key": "rsiOverbought", "param_value": "70", "param_type": "float"},
            ],
            "created_at": _dt(30),
        },
        {
            "id": 3,
            "name": "가치 + 모멘텀",
            "strategy_type": "ValueMomentum",
            "is_active": True,
            "is_preset": True,
            "params": [
                {"id": 8, "param_key": "perRatio", "param_value": "0.7", "param_type": "float"},
                {"id": 9, "param_key": "momentumPeriod", "param_value": "3m", "param_type": "str"},
                {"id": 10, "param_key": "minMarketCap", "param_value": "5000", "param_type": "float"},
            ],
            "created_at": _dt(30),
        },
    ]


def get_demo_strategy(strategy_id: int) -> dict | None:
    """전략 상세 더미 데이터 (StrategyResponse 형식)"""
    strategies = get_demo_strategies()
    return next((s for s in strategies if s["id"] == strategy_id), None)


def get_demo_strategy_performance() -> list:
    """전략 성과 더미 데이터 (StrategyPerformanceResponse 형식)"""
    return [
        {
            "id": 1,
            "name": "골든크로스 + RSI",
            "trade_count": 23,
            "buy_count": 12,
            "sell_count": 11,
            "win_rate": 65.0,
            "active_stocks": 3,
            "is_active": True,
        },
        {
            "id": 2,
            "name": "볼린저 밴드 반전",
            "trade_count": 18,
            "buy_count": 9,
            "sell_count": 9,
            "win_rate": 72.0,
            "active_stocks": 2,
            "is_active": False,
        },
        {
            "id": 3,
            "name": "가치 + 모멘텀",
            "trade_count": 12,
            "buy_count": 7,
            "sell_count": 5,
            "win_rate": 58.0,
            "active_stocks": 2,
            "is_active": True,
        },
    ]


def get_demo_watchlist_groups() -> list:
    """관심종목 그룹 더미 데이터 (WatchlistGroupResponse 형식)"""
    return [
        {
            "id": 1,
            "name": "반도체",
            "sort_order": 0,
            "created_at": _dt(20),
            "items": [
                {"id": 1, "group_id": 1, "stock_code": "005930", "stock_name": "삼성전자", "strategy_id": 1, "created_at": _dt(20)},
                {"id": 2, "group_id": 1, "stock_code": "000660", "stock_name": "SK하이닉스", "strategy_id": 2, "created_at": _dt(20)},
                {"id": 3, "group_id": 1, "stock_code": "042700", "stock_name": "한미반도체", "strategy_id": None, "created_at": _dt(20)},
            ],
        },
        {
            "id": 2,
            "name": "2차전지",
            "sort_order": 1,
            "created_at": _dt(20),
            "items": [
                {"id": 4, "group_id": 2, "stock_code": "051910", "stock_name": "LG화학", "strategy_id": 3, "created_at": _dt(20)},
                {"id": 5, "group_id": 2, "stock_code": "006400", "stock_name": "삼성SDI", "strategy_id": None, "created_at": _dt(20)},
                {"id": 6, "group_id": 2, "stock_code": "247540", "stock_name": "에코프로비엠", "strategy_id": 1, "created_at": _dt(20)},
            ],
        },
        {
            "id": 3,
            "name": "바이오",
            "sort_order": 2,
            "created_at": _dt(20),
            "items": [
                {"id": 7, "group_id": 3, "stock_code": "207940", "stock_name": "삼성바이오로직스", "strategy_id": None, "created_at": _dt(20)},
            ],
        },
    ]


def get_demo_system_settings() -> list:
    """시스템 설정 더미 데이터 (SettingResponse 형식)"""
    return [
        {"setting_key": "auto_trade_enabled", "setting_value": "false", "setting_type": "bool"},
        {"setting_key": "daily_loss_limit", "setting_value": "3", "setting_type": "float"},
        {"setting_key": "exclude_last_minutes", "setting_value": "30", "setting_type": "int"},
        {"setting_key": "kis_mode", "setting_value": "paper", "setting_type": "str"},
        {"setting_key": "max_orders_per_day", "setting_value": "10", "setting_type": "int"},
        {"setting_key": "max_position_ratio", "setting_value": "20", "setting_type": "float"},
        {"setting_key": "stop_loss_rate", "setting_value": "5", "setting_type": "float"},
        {"setting_key": "telegram_enabled", "setting_value": "true", "setting_type": "bool"},
        {"setting_key": "trading_end_time", "setting_value": "15:00", "setting_type": "str"},
        {"setting_key": "trading_start_time", "setting_value": "09:30", "setting_type": "str"},
    ]


def get_demo_safety_status() -> dict:
    """안전장치 상태 더미 데이터"""
    return {
        "auto_trade_enabled": False,
        "daily_loss_check": {"ok": True, "message": "일일 손실 한도 내 (0.35% / 3.00%)"},
        "daily_order_check": {"ok": True, "message": "일일 주문 한도 내 (2건 / 10건)"},
        "system": {
            "error_count": 0,
            "last_error": None,
            "is_healthy": True,
            "message": "정상 동작 중",
        },
    }


def get_demo_market_index() -> list:
    """시장 지수 더미 데이터"""
    return [
        {
            "name": "KOSPI",
            "current_value": 2645.32,
            "change_value": 12.45,
            "change_rate": 0.47,
        },
        {
            "name": "KOSDAQ",
            "current_value": 842.15,
            "change_value": -3.21,
            "change_rate": -0.38,
        },
    ]


def get_demo_backtest_results() -> list:
    """백테스팅 결과 목록 더미 데이터 (BacktestResultResponse 형식)"""
    return [
        {
            "id": 1,
            "symbol": "005930",
            "strategy_name": "골든크로스 + RSI",
            "start_date": _date(245),
            "end_date": _date(2),
            "total_return": 15.32,
            "cagr": 22.48,
            "mdd": -8.14,
            "sharpe_ratio": 1.42,
            "total_trades": 23,
            "win_rate": 65.2,
            "benchmark_return": 7.85,
            "equity_curve": _generate_equity_curve(),
            "created_at": _dt(2),
        }
    ]


def get_demo_backtest_result(result_id: int) -> dict | None:
    """백테스팅 결과 상세 더미 데이터"""
    results = get_demo_backtest_results()
    return next((r for r in results if r["id"] == result_id), None)


def _generate_equity_curve() -> list:
    """간단한 equity curve 더미 데이터 생성 (10포인트)"""
    values = [100.0, 101.2, 100.8, 102.5, 103.1, 101.9, 104.2, 105.8, 107.3, 115.3]
    base = date.today() - timedelta(days=240)
    result = []
    for i, v in enumerate(values):
        d = base + timedelta(days=i * 24)
        result.append({"date": d.isoformat(), "value": v})
    return result


def get_demo_kis_status() -> dict:
    """KIS API 연결 상태 더미 데이터"""
    return {
        "available": False,
        "message": "데모 모드 — KIS API 미연결",
    }


def get_demo_balance() -> dict:
    """잔고 더미 데이터 (BalanceResponse 형식)"""
    return {
        "cash": 12500000.0,
        "stocks": [
            {"symbol": "005930", "name": "삼성전자", "quantity": 100, "current_price": 74500.0, "profit_loss_rate": 3.47},
            {"symbol": "000660", "name": "SK하이닉스", "quantity": 30, "current_price": 185500.0, "profit_loss_rate": 4.21},
            {"symbol": "035720", "name": "카카오", "quantity": 50, "current_price": 48300.0, "profit_loss_rate": -7.12},
        ],
    }


def get_demo_stock_quote(symbol: str) -> dict:
    """현재가 더미 데이터 (StockQuoteResponse 형식)"""
    _prices = {
        "005930": (74500.0, 500.0, 0.67, 12345678, 75200.0, 73800.0, 74100.0),
        "000660": (185500.0, 2500.0, 1.37, 3456789, 186500.0, 184000.0, 184500.0),
        "035720": (48300.0, -700.0, -1.43, 5678901, 49200.0, 48100.0, 48800.0),
    }
    price, change, change_rate, volume, high, low, open_ = _prices.get(
        symbol, (50000.0, 0.0, 0.0, 1000000, 51000.0, 49000.0, 50000.0)
    )
    return {
        "symbol": symbol,
        "price": price,
        "change": change,
        "change_rate": change_rate,
        "volume": volume,
        "high": high,
        "low": low,
        "open": open_,
    }


def get_demo_stock_chart(symbol: str, period: str = "day", count: int = 30) -> dict:
    """차트 더미 데이터 (StockChartResponse 형식)"""
    base_price = {"005930": 74500.0, "000660": 185500.0, "035720": 48300.0}.get(symbol, 50000.0)
    data = []
    for i in range(min(count, 30)):
        d = date.today() - timedelta(days=i)
        factor = 1 + (i % 5 - 2) * 0.005
        p = round(base_price * factor)
        data.append({
            "date": d.strftime("%Y%m%d"),
            "open": p - 200,
            "high": p + 400,
            "low": p - 400,
            "close": p,
            "volume": 1000000 + i * 50000,
        })
    return {"symbol": symbol, "period": period, "data": data}


def get_demo_stock_search(q: str) -> list:
    """종목 검색 더미 데이터 (StockSearchResult 형식)"""
    stocks = [
        {"symbol": "005930", "name": "삼성전자", "market": "KOSPI"},
        {"symbol": "000660", "name": "SK하이닉스", "market": "KOSPI"},
        {"symbol": "035720", "name": "카카오", "market": "KOSPI"},
        {"symbol": "051910", "name": "LG화학", "market": "KOSPI"},
        {"symbol": "006400", "name": "삼성SDI", "market": "KOSPI"},
        {"symbol": "247540", "name": "에코프로비엠", "market": "KOSDAQ"},
        {"symbol": "207940", "name": "삼성바이오로직스", "market": "KOSPI"},
        {"symbol": "042700", "name": "한미반도체", "market": "KOSPI"},
        {"symbol": "035420", "name": "NAVER", "market": "KOSPI"},
        {"symbol": "055550", "name": "신한지주", "market": "KOSPI"},
    ]
    q_lower = q.lower()
    return [s for s in stocks if q_lower in s["symbol"] or q_lower in s["name"].lower()]
