# Sprint 15 pytest 검증 보고서

- **검증 일시**: 2026-03-03
- **검증 환경**: Docker 컨테이너 (mystockbot-backend-1)
- **실행 명령**: `docker compose exec backend pytest -v --tb=short`
- **결과**: 41 passed, 0 failed, 1 warning

---

## 테스트 결과 요약

| 구분 | 수량 |
|------|------|
| 전체 테스트 | 41 |
| 통과 | 41 |
| 실패 | 0 |
| 경고 | 1 (coroutine never awaited — Sprint 15 이전부터 존재하는 기존 경고) |

---

## 테스트 상세 (41개 전부 PASSED)

### test_auth.py (3개)
- `test_login_success` PASSED
- `test_login_invalid_credentials_returns_401` PASSED
- `test_protected_endpoint_without_auth_returns_403_or_401` PASSED

### test_backtest.py (2개) — Sprint 15 신규
- `test_backtest_results_isolated_by_user` PASSED
- `test_get_backtest_result_other_user_returns_404` PASSED

### test_health.py (3개)
- `test_health_check_returns_200` PASSED
- `test_health_check_response_structure` PASSED
- `test_health_check_has_database_check` PASSED

### test_holdings.py (3개)
- `test_list_holdings_empty` PASSED
- `test_list_holdings_returns_holding` PASSED
- `test_portfolio_summary_returns_structure` PASSED

### test_orders.py (7개)
- `test_list_orders_empty` PASSED
- `test_daily_summary_default_date` PASSED
- `test_daily_summary_with_valid_date` PASSED
- `test_daily_summary_invalid_date_returns_400` PASSED
- `test_cancel_pending_order_success` PASSED
- `test_cancel_filled_order_returns_400` PASSED
- `test_cancel_nonexistent_order_returns_404` PASSED

### test_safety.py (4개)
- `test_safety_status_returns_200` PASSED
- `test_toggle_auto_trade_enable` PASSED
- `test_toggle_auto_trade_disable` PASSED
- `test_safety_status_with_auth_returns_200` PASSED

### test_stocks.py (3개)
- `test_search_requires_query` PASSED
- `test_balance_returns_valid_status` PASSED
- `test_quote_returns_valid_status` PASSED

### test_strategies.py (10개) — Sprint 15 신규 6개 포함
- `test_list_strategies_empty` PASSED
- `test_list_strategies_returns_strategy` PASSED
- `test_get_strategy_not_found` PASSED
- `test_get_strategy_performance_empty` PASSED
- `test_list_strategies_returns_preset_and_own` PASSED (Sprint 15 신규)
- `test_list_strategies_excludes_other_user_strategy` PASSED (Sprint 15 신규)
- `test_toggle_preset_strategy_returns_404` PASSED (Sprint 15 신규)
- `test_toggle_own_strategy_succeeds` PASSED (Sprint 15 신규)
- `test_clone_preset_strategy` PASSED (Sprint 15 신규)
- `test_clone_creates_new_strategy_with_params` PASSED (Sprint 15 신규)

### test_watchlist.py (3개)
- `test_list_groups_empty` PASSED
- `test_create_group_success` PASSED
- `test_create_group_then_list` PASSED

### test_risk_manager.py (3개)
- `test_full_take_profit_triggered_before_partial` PASSED
- `test_partial_take_profit_at_half_target` PASSED
- `test_stop_loss_triggered` PASSED

---

## 경고 내용

```
RuntimeWarning: coroutine 'notify_risk_triggered' was never awaited
```

- Sprint 15 이전부터 존재하는 기존 경고
- `test_risk_manager.py`에서 mock 처리되지 않은 비동기 함수 호출로 발생
- 기능 동작에는 영향 없음

---

## 결론

Sprint 15 신규 테스트 8개 (전략 격리 6개 + 백테스트 격리 2개) 포함 전체 41개 통과.
Sprint 15 구현의 사용자별 데이터 격리가 테스트 레벨에서 완전히 검증됨.
