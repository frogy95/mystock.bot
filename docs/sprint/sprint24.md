# Sprint 24: 다중 백테스트 + 랭킹 + 전략 매칭

## 개요

- **기간**: 2026-03-08
- **브랜치**: `sprint24`
- **PR**: `develop` 브랜치로 PR 생성
- **상태**: 계획

---

## 목표

단일 종목에 대해 여러 전략을 동시에 백테스트하고, 랭킹 스코어로 최적 전략을 추천하며, 해당 종목의 보유/관심 상태를 함께 확인할 수 있는 기능을 구현한다. 프론트엔드는 체크박스 다중 선택 폼, 랭킹 테이블, 다중 라인 에쿼티 차트로 완전히 개편한다.

---

## 배경 및 현황

### 현재 상태

- `backend/app/schemas/backtest.py`에 `BacktestMultiRunRequest`, `BacktestMultiResponse`, `BacktestRankingEntry`, `WatchlistStatusItem`, `StockStatusResponse` 스키마가 **이미 정의**되어 있음
- `backend/app/api/v1/backtest.py`에는 단일 실행 엔드포인트(`POST /backtest/run`)만 존재 (다중 실행 없음)
- `backend/app/services/backtest_metrics.py`에 랭킹 스코어 계산 함수 없음
- `frontend/src/hooks/use-backtest.ts`에 `useBacktestRunMulti`, `useStockStatus` 훅 없음
- `frontend/src/components/backtest/backtest-config-form.tsx`가 단일 전략 Select 방식 (체크박스 다중 선택 없음)
- `frontend/src/components/backtest/backtest-equity-chart.tsx`가 단일 결과 기준 3-라인 차트 (다중 전략 라인 없음)
- `backtest-ranking-table.tsx` 컴포넌트 미존재

### 구현 목표

| 항목 | Before | After |
|------|--------|-------|
| 백테스트 대상 | 전략 1개 + 종목 1개 | 전략 N개 + 종목 1개 (최대 10개) |
| 전략 선택 UI | Select 드롭다운 (단일) | 체크박스 목록 (다중 선택) |
| 결과 표시 | 단일 결과 카드 + 차트 | 랭킹 테이블 + 다중 라인 에쿼티 차트 |
| 랭킹 스코어 | 없음 | 가중 복합 스코어 (CAGR, MDD, 샤프, 승률) |
| 종목 상태 확인 | 없음 | GET /backtest/stock-status/{symbol} |

---

## 구현 범위

### 포함 항목 (Must Have)

1. **백엔드 다중 백테스트 API**: `POST /api/v1/backtest/run-multi` — 단일 종목, 복수 전략 순차 실행
2. **랭킹 스코어 계산 함수**: `backtest_metrics.py`에 `calculate_ranking_score()` 추가
3. **종목 상태 확인 API**: `GET /api/v1/backtest/stock-status/{symbol}` — 보유/관심 상태 반환
4. **프론트엔드 훅 추가**: `useBacktestRunMulti`, `useStockStatus`
5. **백테스트 설정 폼 개편**: 전략 체크박스 다중 선택으로 교체
6. **랭킹 테이블 컴포넌트**: `backtest-ranking-table.tsx` 신규 생성
7. **다중 라인 에쿼티 차트**: `backtest-equity-chart.tsx`를 다중 전략 라인 지원으로 확장
8. **페이지 레이아웃 개편**: `backtest/page.tsx`에 다중 백테스트 결과 표시 흐름 추가

### 제외 항목 (Out of Scope)

- 전략 간 상관관계 분석 (별도 스프린트)
- 다중 종목 × 다중 전략 조합 (10×10 등, 성능 이슈 예상)
- 랭킹 기준 커스터마이징 UI (가중치 직접 조정)
- 데모 모드 다중 백테스트 지원
- DB 스키마 변경 없음 (기존 `backtest_results` 테이블 재활용, 다중 결과를 복수 레코드로 저장)

---

## Task 목록

### Task 0: 브랜치 확인 및 현황 파악

**목적**: 작업 환경을 확인하고 기존 스키마 파일이 올바른지 검증한다.

**Files**:
- `backend/app/schemas/backtest.py` (검증)
- `backend/app/api/v1/backtest.py` (검증)

**Step 1: 브랜치 및 스키마 확인**

```bash
git branch --show-current
# 예상 출력: sprint24
```

**Step 2: 기존 스키마 확인**

`backend/app/schemas/backtest.py`에 `BacktestMultiRunRequest`, `BacktestMultiResponse`, `BacktestRankingEntry`, `StockStatusResponse`가 모두 존재하는지 확인한다.

**완료 기준**: 브랜치가 `sprint24`이고, 4개 스키마 클래스가 모두 정의되어 있음

---

### Task 1: 랭킹 스코어 계산 함수 추가

**목적**: 다중 백테스트 결과를 비교할 수 있는 복합 스코어를 계산한다.

**Files**:
- Modify: `backend/app/services/backtest_metrics.py`
- Test: `backend/tests/test_backtest_metrics.py`

**알고리즘 설계**:
- 스코어는 0~100 범위의 가중 복합 점수
- CAGR(40%), MDD(30%), 샤프비율(20%), 승률(10%) 가중합
- 각 지표는 후보 집합 내에서 정규화(min-max) 후 가중치 적용
- MDD는 낮을수록 좋으므로 역순 정규화

**가중치 상수**:
```python
_RANKING_WEIGHTS = {
    "cagr": 0.40,
    "mdd": 0.30,    # 역순: 낮을수록 좋음
    "sharpe": 0.20,
    "win_rate": 0.10,
}
```

**Step 1: 실패하는 테스트 작성**

`backend/tests/test_backtest_metrics.py`에 추가:

```python
def test_calculate_ranking_score_single():
    """전략이 1개인 경우 스코어는 100.0 (단독 1위)"""
    from app.services.backtest_metrics import calculate_ranking_score
    metrics_list = [
        {"strategy_id": 1, "strategy_name": "A", "total_return": 30.0, "cagr": 12.0, "mdd": -10.0, "sharpe_ratio": 1.2, "win_rate": 60.0, "total_trades": 20, "benchmark_return": 5.0, "equity_curve": []},
    ]
    result = calculate_ranking_score(metrics_list)
    assert len(result) == 1
    assert result[0]["rank"] == 1
    assert result[0]["score"] == 100.0


def test_calculate_ranking_score_ordering():
    """더 높은 CAGR, 낮은 MDD를 가진 전략이 더 높은 순위를 가진다"""
    from app.services.backtest_metrics import calculate_ranking_score
    metrics_list = [
        {"strategy_id": 1, "strategy_name": "A", "total_return": 10.0, "cagr": 5.0, "mdd": -20.0, "sharpe_ratio": 0.5, "win_rate": 40.0, "total_trades": 10, "benchmark_return": 5.0, "equity_curve": []},
        {"strategy_id": 2, "strategy_name": "B", "total_return": 50.0, "cagr": 20.0, "mdd": -8.0, "sharpe_ratio": 1.8, "win_rate": 65.0, "total_trades": 15, "benchmark_return": 5.0, "equity_curve": []},
    ]
    result = calculate_ranking_score(metrics_list)
    ranked = sorted(result, key=lambda x: x["rank"])
    assert ranked[0]["strategy_id"] == 2
    assert ranked[1]["strategy_id"] == 1
```

**Step 2: 테스트 실패 확인**

```bash
docker compose exec backend pytest tests/test_backtest_metrics.py::test_calculate_ranking_score_single -v
# 예상: FAILED (ImportError: cannot import name 'calculate_ranking_score')
```

**Step 3: `calculate_ranking_score` 함수 구현**

`backend/app/services/backtest_metrics.py` 하단에 추가:

```python
# ── Sprint 24: 랭킹 스코어 계산 ────────────────────────────────────────
_RANKING_WEIGHTS = {
    "cagr": 0.40,
    "mdd": 0.30,     # 역순: 낮을수록 좋음 (절댓값 기준)
    "sharpe": 0.20,
    "win_rate": 0.10,
}


def calculate_ranking_score(metrics_list: list[dict]) -> list[dict]:
    """
    다중 백테스트 결과 목록을 받아 랭킹 스코어를 계산하여 반환한다.

    Args:
        metrics_list: 각 항목이 strategy_id, strategy_name, cagr, mdd,
                      sharpe_ratio, win_rate, total_trades, benchmark_return,
                      equity_curve를 포함하는 딕셔너리 목록

    Returns:
        score, rank 필드가 추가된 BacktestRankingEntry 형태의 딕셔너리 목록
        (score 내림차순 정렬)
    """
    if not metrics_list:
        return []

    n = len(metrics_list)

    # 정규화에 사용할 지표 추출
    cagrs = [m["cagr"] for m in metrics_list]
    mdds = [abs(m["mdd"]) for m in metrics_list]   # MDD: 절댓값 (낮을수록 좋음)
    sharpes = [m["sharpe_ratio"] for m in metrics_list]
    win_rates = [m["win_rate"] for m in metrics_list]

    def _normalize(values: list[float], invert: bool = False) -> list[float]:
        """min-max 정규화. invert=True이면 낮을수록 높은 점수."""
        min_v, max_v = min(values), max(values)
        if max_v == min_v:
            # 모든 값이 동일한 경우 최대 점수
            return [1.0] * len(values)
        normalized = [(v - min_v) / (max_v - min_v) for v in values]
        if invert:
            normalized = [1.0 - v for v in normalized]
        return normalized

    norm_cagr = _normalize(cagrs)
    norm_mdd = _normalize(mdds, invert=True)   # MDD는 낮을수록 좋음
    norm_sharpe = _normalize(sharpes)
    norm_win_rate = _normalize(win_rates)

    scored = []
    for i, m in enumerate(metrics_list):
        score = (
            norm_cagr[i] * _RANKING_WEIGHTS["cagr"]
            + norm_mdd[i] * _RANKING_WEIGHTS["mdd"]
            + norm_sharpe[i] * _RANKING_WEIGHTS["sharpe"]
            + norm_win_rate[i] * _RANKING_WEIGHTS["win_rate"]
        ) * 100
        scored.append({
            "strategy_id": m["strategy_id"],
            "strategy_name": m["strategy_name"],
            "score": round(score, 2),
            "total_return": m["total_return"],
            "cagr": m["cagr"],
            "mdd": m["mdd"],
            "sharpe_ratio": m["sharpe_ratio"],
            "win_rate": m["win_rate"],
            "total_trades": m["total_trades"],
        })

    # 스코어 내림차순 정렬 후 rank 부여
    scored.sort(key=lambda x: x["score"], reverse=True)
    for rank, item in enumerate(scored, start=1):
        item["rank"] = rank

    return scored
```

**Step 4: 테스트 통과 확인**

```bash
docker compose exec backend pytest tests/test_backtest_metrics.py -v
# 예상: 기존 테스트 + 신규 2개 PASSED
```

**Step 5: 커밋**

```bash
git add backend/app/services/backtest_metrics.py backend/tests/test_backtest_metrics.py
git commit -m "feat: 다중 백테스트 랭킹 스코어 계산 함수 추가 (Sprint 24 Task 1)"
```

**완료 기준**: `calculate_ranking_score` 함수가 정상 작동하고 테스트 2개 이상 통과

---

### Task 2: 종목 상태 확인 API 추가

**목적**: 특정 종목이 현재 보유 중인지, 관심종목에 등록되어 있는지 확인하는 API를 제공한다.

**Files**:
- Modify: `backend/app/api/v1/backtest.py`
- Test: `backend/tests/test_backtest_api.py`

**엔드포인트 설계**:
- `GET /api/v1/backtest/stock-status/{symbol}`
- 응답: `StockStatusResponse` (schemas/backtest.py에 이미 정의됨)
- 쿼리 대상: `holdings` 테이블 (Holding 모델), `watchlist_groups` + `watchlist_items` 테이블

**Step 1: 테스트 작성**

`backend/tests/test_backtest_api.py`에 추가:

```python
@pytest.mark.asyncio
async def test_stock_status_not_found(client, auth_headers):
    """보유하지도 않고 관심종목에도 없는 종목은 모두 False"""
    resp = await client.get(
        "/api/v1/backtest/stock-status/XXXNOTEXIST",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_holding"] is False
    assert data["is_watchlist"] is False
    assert data["watchlist_items"] == []
```

**Step 2: 테스트 실패 확인**

```bash
docker compose exec backend pytest tests/test_backtest_api.py::test_stock_status_not_found -v
# 예상: FAILED (404 또는 엔드포인트 없음)
```

**Step 3: 엔드포인트 구현**

`backend/app/api/v1/backtest.py`에 추가 (기존 `get_result` 엔드포인트 이후):

```python
from app.models.holding import Holding
from app.models.watchlist import WatchlistGroup, WatchlistItem
from app.schemas.backtest import StockStatusResponse, WatchlistStatusItem


@router.get(
    "/stock-status/{symbol}",
    response_model=StockStatusResponse,
    summary="종목 보유/관심 상태 확인",
)
async def get_stock_status(
    symbol: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    지정 종목의 보유 여부와 관심종목 등록 여부를 반환한다.
    - is_holding: 해당 종목을 현재 보유 중인지
    - is_watchlist: 관심종목 그룹 중 하나에라도 등록되어 있는지
    - watchlist_items: 등록된 관심종목 항목 목록 (그룹명 포함)
    """
    # 보유 종목 조회
    holding_result = await db.execute(
        select(Holding).where(
            Holding.user_id == current_user.id,
            Holding.stock_code == symbol,
        )
    )
    holding = holding_result.scalar_one_or_none()

    # 관심종목 조회: user_id를 통해 watchlist_groups 경유
    wl_result = await db.execute(
        select(WatchlistItem, WatchlistGroup.name.label("group_name"))
        .join(WatchlistGroup, WatchlistItem.group_id == WatchlistGroup.id)
        .where(
            WatchlistGroup.user_id == current_user.id,
            WatchlistItem.stock_code == symbol,
        )
    )
    wl_rows = wl_result.all()

    watchlist_items = [
        WatchlistStatusItem(
            item_id=row.WatchlistItem.id,
            group_name=row.group_name,
            current_strategy=None,  # 전략 이름 조회는 생략 (성능)
        )
        for row in wl_rows
    ]

    # 현재 매도 전략명 조회 (보유 종목에 매도 전략이 설정된 경우)
    sell_strategy_name = None
    if holding and holding.sell_strategy_id:
        from app.models.strategy import Strategy
        strategy_result = await db.execute(
            select(Strategy).where(Strategy.id == holding.sell_strategy_id)
        )
        strategy = strategy_result.scalar_one_or_none()
        if strategy:
            sell_strategy_name = strategy.name

    return StockStatusResponse(
        is_holding=holding is not None,
        holding_id=holding.id if holding else None,
        current_sell_strategy=sell_strategy_name,
        is_watchlist=len(watchlist_items) > 0,
        watchlist_items=watchlist_items,
    )
```

**Step 4: 테스트 통과 확인**

```bash
docker compose exec backend pytest tests/test_backtest_api.py -v
```

**Step 5: 커밋**

```bash
git add backend/app/api/v1/backtest.py backend/tests/test_backtest_api.py
git commit -m "feat: 종목 보유/관심 상태 확인 API 추가 (Sprint 24 Task 2)"
```

**완료 기준**: `GET /backtest/stock-status/{symbol}` 200 응답, 미보유/미등록 종목에 `is_holding=false, is_watchlist=false` 반환

---

### Task 3: 다중 백테스트 실행 API 추가

**목적**: 단일 종목에 대해 여러 전략을 순차 실행하고, 랭킹 스코어를 포함한 통합 결과를 반환한다.

**Files**:
- Modify: `backend/app/api/v1/backtest.py`
- Test: `backend/tests/test_backtest_api.py`

**엔드포인트 설계**:
- `POST /api/v1/backtest/run-multi`
- 요청: `BacktestMultiRunRequest` (symbol, strategy_ids, start_date, end_date, initial_cash)
- 응답: `BacktestMultiResponse` (symbol, results, ranking)
- 각 전략 결과는 `backtest_results` 테이블에 개별 레코드로 저장
- 전략 조회: `strategy_ids`로 `strategies` 테이블 조회 (프리셋 + 커스텀 모두 포함)
- 데모 사용자: 403 반환

**주의사항**:
- FastAPI 라우터는 경로 매칭 순서가 중요하다. `POST /run-multi`를 `POST /run` 앞에 등록하거나 별도로 구분되도록 prefix를 확인한다. 실제로는 `/run`과 `/run-multi`는 다른 경로이므로 충돌하지 않는다.
- 전략 ID로 strategies 테이블 조회 시 사용자 소유 또는 프리셋(user_id=None) 전략만 허용한다.

**Step 1: 테스트 작성**

```python
@pytest.mark.asyncio
async def test_run_multi_invalid_empty_strategies(client, auth_headers):
    """전략 ID 목록이 비어있으면 422"""
    resp = await client.post(
        "/api/v1/backtest/run-multi",
        json={
            "symbol": "005930",
            "strategy_ids": [],
            "start_date": "2022-01-01",
            "end_date": "2023-01-01",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 422
```

**Step 2: 테스트 실패 확인**

```bash
docker compose exec backend pytest tests/test_backtest_api.py::test_run_multi_invalid_empty_strategies -v
# 예상: FAILED (404, 엔드포인트 없음)
```

**Step 3: 엔드포인트 구현**

`backend/app/api/v1/backtest.py`에 추가:

```python
from app.schemas.backtest import (
    BacktestMultiRunRequest,
    BacktestMultiResponse,
    BacktestMultiResultItem,
    BacktestRankingEntry,
)
from app.services.backtest_metrics import calculate_ranking_score


@router.post(
    "/run-multi",
    response_model=BacktestMultiResponse,
    summary="다중 전략 백테스팅 실행",
)
async def run_backtest_multi(
    request: BacktestMultiRunRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    단일 종목에 대해 여러 전략을 순차 백테스트하고 랭킹 스코어를 반환한다.
    각 전략 결과는 backtest_results 테이블에 개별 저장된다.
    최대 10개 전략 선택 가능 (스키마 validator에서 제한).
    """
    if is_demo_user(current_user.username):
        raise HTTPException(status_code=403, detail="데모 모드에서는 사용할 수 없습니다.")

    from sqlalchemy import or_

    # 허용된 전략 조회: 프리셋 또는 본인 소유
    strategies_result = await db.execute(
        select(Strategy).where(
            Strategy.id.in_(request.strategy_ids),
            or_(Strategy.user_id.is_(None), Strategy.user_id == current_user.id),
        )
    )
    strategies = strategies_result.scalars().all()

    if not strategies:
        raise HTTPException(status_code=404, detail="선택한 전략을 찾을 수 없습니다.")

    results = []
    metrics_for_ranking = []

    for strategy in strategies:
        # 커스텀 전략 조건 로드
        buy_conditions = strategy.buy_conditions if not strategy.is_preset else None
        sell_conditions = strategy.sell_conditions if not strategy.is_preset else None

        try:
            config = BacktestConfig(
                symbol=request.symbol,
                strategy_name=strategy.name,
                params={},
                start_date=request.start_date,
                end_date=request.end_date,
                initial_cash=request.initial_cash,
                buy_conditions=buy_conditions,
                sell_conditions=sell_conditions,
            )
            raw_result = await run_backtest(config)
            metrics = calculate_metrics(raw_result)
        except Exception as e:
            logger.warning(f"다중 백테스트 전략 [{strategy.name}] 실행 실패: {e}")
            continue

        # DB 저장
        result_data = {
            "strategy_name": strategy.name,
            "params": {},
            "initial_cash": request.initial_cash,
            **metrics,
        }
        record = BacktestResult(
            user_id=current_user.id,
            strategy_id=strategy.id,
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            total_return=metrics.get("total_return"),
            max_drawdown=metrics.get("mdd"),
            sharpe_ratio=metrics.get("sharpe_ratio"),
            win_rate=metrics.get("win_rate"),
            result_data=result_data,
        )
        db.add(record)

        equity_raw = metrics.get("equity_curve", [])
        equity_curve = [
            EquityPoint(
                date=ep["date"],
                value=ep["value"],
                benchmark=ep.get("benchmark", 0.0),
                stock_buyhold=ep.get("stock_buyhold", 0.0),
            )
            for ep in equity_raw
            if isinstance(ep, dict)
        ]

        results.append({
            "strategy_id": strategy.id,
            "strategy_name": strategy.name,
            "total_return": float(metrics.get("total_return", 0.0)),
            "cagr": float(metrics.get("cagr", 0.0)),
            "mdd": float(metrics.get("mdd", 0.0)),
            "sharpe_ratio": float(metrics.get("sharpe_ratio", 0.0)),
            "win_rate": float(metrics.get("win_rate", 0.0)),
            "total_trades": int(metrics.get("total_trades", 0)),
            "benchmark_return": float(metrics.get("benchmark_return", 0.0)),
            "equity_curve": equity_curve,
        })

        metrics_for_ranking.append({
            "strategy_id": strategy.id,
            "strategy_name": strategy.name,
            "total_return": float(metrics.get("total_return", 0.0)),
            "cagr": float(metrics.get("cagr", 0.0)),
            "mdd": float(metrics.get("mdd", 0.0)),
            "sharpe_ratio": float(metrics.get("sharpe_ratio", 0.0)),
            "win_rate": float(metrics.get("win_rate", 0.0)),
            "total_trades": int(metrics.get("total_trades", 0)),
            "benchmark_return": float(metrics.get("benchmark_return", 0.0)),
            "equity_curve": [],
        })

    await db.commit()

    if not results:
        raise HTTPException(status_code=500, detail="실행된 백테스트 결과가 없습니다. 전략 설정을 확인해주세요.")

    # 랭킹 계산
    ranking_data = calculate_ranking_score(metrics_for_ranking)
    ranking = [BacktestRankingEntry(**r) for r in ranking_data]

    result_items = [
        BacktestMultiResultItem(
            strategy_id=r["strategy_id"],
            strategy_name=r["strategy_name"],
            total_return=r["total_return"],
            cagr=r["cagr"],
            mdd=r["mdd"],
            sharpe_ratio=r["sharpe_ratio"],
            win_rate=r["win_rate"],
            total_trades=r["total_trades"],
            benchmark_return=r["benchmark_return"],
            equity_curve=r["equity_curve"],
        )
        for r in results
    ]

    logger.info(
        f"다중 백테스팅 완료 [{request.symbol}]: {len(results)}개 전략, "
        f"1위: {ranking[0].strategy_name if ranking else 'N/A'}"
    )

    return BacktestMultiResponse(
        symbol=request.symbol,
        results=result_items,
        ranking=ranking,
    )
```

**Step 4: 테스트 통과 확인**

```bash
docker compose exec backend pytest tests/test_backtest_api.py -v
```

**Step 5: 커밋**

```bash
git add backend/app/api/v1/backtest.py backend/tests/test_backtest_api.py
git commit -m "feat: 다중 전략 백테스팅 실행 API 추가 (Sprint 24 Task 3)"
```

**완료 기준**: `POST /backtest/run-multi` 422(빈 전략 목록), 404(전략 없음) 정상 반환; 기존 단일 실행 API 영향 없음

---

### Task 4: 프론트엔드 훅 추가

**목적**: 다중 백테스트 실행과 종목 상태 확인을 위한 TanStack Query 훅을 추가한다.

**Files**:
- Modify: `frontend/src/hooks/use-backtest.ts`

**Step 1: 타입 정의 추가**

`use-backtest.ts` 기존 타입 정의 아래에 추가:

```typescript
/** 다중 백테스트 실행 요청 타입 */
export interface BacktestMultiRunRequest {
  symbol: string;
  strategy_ids: number[];
  start_date: string;   // "YYYY-MM-DD"
  end_date: string;     // "YYYY-MM-DD"
  initial_cash?: number;
}

/** 랭킹 항목 타입 */
export interface BacktestRankingEntry {
  strategy_id: number;
  strategy_name: string;
  rank: number;
  score: number;
  total_return: number;
  cagr: number;
  mdd: number;
  sharpe_ratio: number;
  win_rate: number;
  total_trades: number;
}

/** 다중 백테스트 개별 결과 타입 */
export interface BacktestMultiResultItem {
  strategy_id: number;
  strategy_name: string;
  total_return: number;
  cagr: number;
  mdd: number;
  sharpe_ratio: number;
  win_rate: number;
  total_trades: number;
  benchmark_return: number;
  equity_curve: EquityPoint[];
}

/** 다중 백테스트 전체 응답 타입 */
export interface BacktestMultiResponse {
  symbol: string;
  results: BacktestMultiResultItem[];
  ranking: BacktestRankingEntry[];
}

/** 관심종목 항목 상태 타입 */
export interface WatchlistStatusItem {
  item_id: number;
  group_name: string;
  current_strategy: string | null;
}

/** 종목 보유/관심 상태 응답 타입 */
export interface StockStatusResponse {
  is_holding: boolean;
  holding_id: number | null;
  current_sell_strategy: string | null;
  is_watchlist: boolean;
  watchlist_items: WatchlistStatusItem[];
}
```

**Step 2: 훅 구현 추가**

```typescript
/**
 * 다중 전략 백테스팅 실행 뮤테이션 훅
 * POST /api/v1/backtest/run-multi
 */
export function useBacktestRunMulti() {
  const queryClient = useQueryClient();
  return useMutation<BacktestMultiResponse, Error, BacktestMultiRunRequest>({
    mutationFn: (request) =>
      apiClient.post<BacktestMultiResponse>("/api/v1/backtest/run-multi", request),
    onSuccess: () => {
      // 결과 목록 캐시 무효화
      queryClient.invalidateQueries({ queryKey: ["backtest", "results"] });
    },
    onError: (error) => {
      console.error("[useBacktestRunMulti] 다중 백테스팅 실행 실패:", error);
    },
  });
}

/**
 * 종목 보유/관심 상태 조회 훅
 * GET /api/v1/backtest/stock-status/{symbol}
 */
export function useStockStatus(symbol: string) {
  return useQuery<StockStatusResponse>({
    queryKey: ["backtest", "stock-status", symbol],
    queryFn: () =>
      apiClient.get<StockStatusResponse>(`/api/v1/backtest/stock-status/${symbol}`),
    enabled: symbol.trim().length > 0,
    staleTime: 30_000,
  });
}
```

**Step 3: TypeScript 컴파일 확인**

```bash
cd /Users/choijiseon/Documents/Sources/mystock.bot/frontend && npx tsc --noEmit 2>&1 | head -30
# 예상: 에러 없음 또는 기존 에러만 출력
```

**Step 4: 커밋**

```bash
git add frontend/src/hooks/use-backtest.ts
git commit -m "feat: 다중 백테스트 및 종목 상태 확인 훅 추가 (Sprint 24 Task 4)"
```

**완료 기준**: `useBacktestRunMulti`, `useStockStatus` 훅이 타입 에러 없이 추가됨

---

### Task 5: 백테스트 설정 폼 개편 (체크박스 다중 선택)

**목적**: 단일 전략 Select를 체크박스 목록으로 교체하여 여러 전략을 동시에 선택할 수 있도록 한다.

**Files**:
- Modify: `frontend/src/components/backtest/backtest-config-form.tsx`

**UI 설계**:
- 전략 선택 영역: 스크롤 가능한 체크박스 목록 (shadcn/ui `Checkbox` 사용)
- 최소 1개, 최대 10개 선택 제한
- 선택된 전략 수 표시 (`N개 선택됨`)
- 폼 제출 시 선택된 `strategy.id` 배열을 `onRunMulti` 콜백으로 전달
- `onRun` 기존 콜백 유지 (단일 실행 경로는 삭제하거나 다중으로 통합)

**Step 1: shadcn/ui Checkbox 설치 확인**

```bash
ls /Users/choijiseon/Documents/Sources/mystock.bot/frontend/src/components/ui/checkbox.tsx 2>/dev/null && echo "존재" || echo "없음"
```

없으면 설치:
```bash
cd /Users/choijiseon/Documents/Sources/mystock.bot/frontend && npx shadcn@latest add checkbox --yes
```

**Step 2: 컴포넌트 Props 인터페이스 변경**

```typescript
interface BacktestConfigFormProps {
  onRunMulti: (config: {
    strategyIds: number[];
    symbol: string;
    startDate: string;
    endDate: string;
  }) => void;
  isRunning: boolean;
}
```

**Step 3: 전략 선택 UI를 체크박스로 교체**

기존 `<Select>` 전략 선택 부분을 아래로 교체:

```tsx
{/* 전략 다중 선택 (체크박스) */}
<div className="space-y-1.5">
  <Label>전략 선택 ({selectedStrategyIds.length}개 선택됨, 최대 10개)</Label>
  <div className="rounded-md border p-3 space-y-2 max-h-48 overflow-y-auto">
    {strategiesLoading ? (
      <p className="text-sm text-muted-foreground">로딩 중...</p>
    ) : (
      strategies?.map((strategy) => (
        <div key={strategy.id} className="flex items-center gap-2">
          <Checkbox
            id={`strategy-${strategy.id}`}
            checked={selectedStrategyIds.includes(strategy.id)}
            onCheckedChange={(checked) => {
              if (checked) {
                if (selectedStrategyIds.length >= 10) return;
                setSelectedStrategyIds((prev) => [...prev, strategy.id]);
              } else {
                setSelectedStrategyIds((prev) =>
                  prev.filter((id) => id !== strategy.id)
                );
              }
            }}
          />
          <label
            htmlFor={`strategy-${strategy.id}`}
            className="text-sm cursor-pointer"
          >
            {strategy.name}
          </label>
        </div>
      ))
    )}
  </div>
</div>
```

**Step 4: 폼 유효성 및 제출 로직 변경**

```typescript
const isFormValid =
  selectedStrategyIds.length > 0 &&
  symbol.trim() !== "" &&
  startDate !== "" &&
  endDate !== "";

function handleSubmit(e: React.FormEvent) {
  e.preventDefault();
  if (!isFormValid) return;
  const match = symbol.match(/\((\w+)\)\s*$/);
  const resolvedSymbol = match ? match[1] : symbol.trim();
  onRunMulti({ strategyIds: selectedStrategyIds, symbol: resolvedSymbol, startDate, endDate });
}
```

**Step 5: TypeScript 컴파일 확인**

```bash
cd /Users/choijiseon/Documents/Sources/mystock.bot/frontend && npx tsc --noEmit 2>&1 | head -30
```

**Step 6: 커밋**

```bash
git add frontend/src/components/backtest/backtest-config-form.tsx
git commit -m "feat: 백테스트 설정 폼 전략 선택 체크박스로 개편 (Sprint 24 Task 5)"
```

**완료 기준**: 전략 체크박스 목록 렌더링, 다중 선택 가능, 10개 초과 시 추가 선택 불가

---

### Task 6: 랭킹 테이블 컴포넌트 신규 생성

**목적**: 다중 백테스트 결과를 랭킹 스코어 기준으로 테이블로 표시한다.

**Files**:
- Create: `frontend/src/components/backtest/backtest-ranking-table.tsx`

**UI 설계**:
- shadcn/ui `Table` 컴포넌트 사용
- 컬럼: 순위, 전략명, 종합 스코어, 수익률, CAGR, MDD, 샤프, 승률, 거래수
- 1위 행 강조 (배경색 또는 Badge)
- MDD는 음수이므로 색상 표시 (높은 MDD → 빨간색)
- 스코어는 소수점 1자리, 나머지 퍼센트 지표는 소수점 2자리

**Step 1: shadcn/ui Table 설치 확인**

```bash
ls /Users/choijiseon/Documents/Sources/mystock.bot/frontend/src/components/ui/table.tsx 2>/dev/null && echo "존재" || echo "없음"
```

없으면:
```bash
cd /Users/choijiseon/Documents/Sources/mystock.bot/frontend && npx shadcn@latest add table --yes
```

**Step 2: 컴포넌트 구현**

`frontend/src/components/backtest/backtest-ranking-table.tsx`:

```tsx
"use client";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { BacktestRankingEntry } from "@/hooks/use-backtest";

interface BacktestRankingTableProps {
  ranking: BacktestRankingEntry[];
  symbol: string;
}

export function BacktestRankingTable({ ranking, symbol }: BacktestRankingTableProps) {
  if (ranking.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>전략 랭킹 — {symbol}</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-12 text-center">순위</TableHead>
              <TableHead>전략명</TableHead>
              <TableHead className="text-right">스코어</TableHead>
              <TableHead className="text-right">수익률</TableHead>
              <TableHead className="text-right">CAGR</TableHead>
              <TableHead className="text-right">MDD</TableHead>
              <TableHead className="text-right">샤프</TableHead>
              <TableHead className="text-right">승률</TableHead>
              <TableHead className="text-right">거래수</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {ranking.map((entry) => (
              <TableRow
                key={entry.strategy_id}
                className={entry.rank === 1 ? "bg-primary/5" : undefined}
              >
                <TableCell className="text-center font-semibold">
                  {entry.rank === 1 ? (
                    <Badge variant="default">1위</Badge>
                  ) : (
                    entry.rank
                  )}
                </TableCell>
                <TableCell className="font-medium">{entry.strategy_name}</TableCell>
                <TableCell className="text-right font-semibold">
                  {entry.score.toFixed(1)}
                </TableCell>
                <TableCell
                  className={`text-right ${entry.total_return >= 0 ? "text-red-500" : "text-blue-500"}`}
                >
                  {entry.total_return >= 0 ? "+" : ""}
                  {entry.total_return.toFixed(2)}%
                </TableCell>
                <TableCell
                  className={`text-right ${entry.cagr >= 0 ? "text-red-500" : "text-blue-500"}`}
                >
                  {entry.cagr >= 0 ? "+" : ""}
                  {entry.cagr.toFixed(2)}%
                </TableCell>
                <TableCell className="text-right text-orange-500">
                  {entry.mdd.toFixed(2)}%
                </TableCell>
                <TableCell className="text-right">{entry.sharpe_ratio.toFixed(2)}</TableCell>
                <TableCell className="text-right">{entry.win_rate.toFixed(2)}%</TableCell>
                <TableCell className="text-right">{entry.total_trades}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
```

**Step 3: TypeScript 컴파일 확인**

```bash
cd /Users/choijiseon/Documents/Sources/mystock.bot/frontend && npx tsc --noEmit 2>&1 | head -30
```

**Step 4: 커밋**

```bash
git add frontend/src/components/backtest/backtest-ranking-table.tsx
git commit -m "feat: 다중 백테스트 랭킹 테이블 컴포넌트 추가 (Sprint 24 Task 6)"
```

**완료 기준**: `BacktestRankingTable` 컴포넌트가 타입 에러 없이 생성됨; 1위 행 강조 확인

---

### Task 7: 다중 라인 에쿼티 차트 확장

**목적**: 단일 전략 결과를 표시하던 에쿼티 차트를 여러 전략의 수익 곡선을 동시에 표시하도록 확장한다.

**Files**:
- Modify: `frontend/src/components/backtest/backtest-equity-chart.tsx`

**UI 설계**:
- 기존 단일 모드 Props(`equityCurve`) 유지 (하위 호환)
- 다중 모드 Props 추가(`multiResults: BacktestMultiResultItem[]`)
- 다중 모드에서는 전략별로 서로 다른 색상의 Line 렌더링
- 전략 수에 따라 색상 팔레트 자동 배분 (최대 10개)
- 벤치마크 라인은 첫 번째 결과의 benchmark 값 사용

**색상 팔레트** (10색):
```typescript
const STRATEGY_COLORS = [
  "#ef4444", "#3b82f6", "#22c55e", "#f59e0b",
  "#8b5cf6", "#ec4899", "#06b6d4", "#84cc16",
  "#f97316", "#6366f1",
];
```

**Step 1: Props 인터페이스 확장**

```typescript
import type { BacktestMultiResultItem } from "@/hooks/use-backtest";

interface BacktestEquityChartProps {
  /** 단일 백테스트 결과용 (기존 호환) */
  equityCurve?: { date: string; value: number; benchmark: number; stockBuyhold: number }[];
  /** 다중 백테스트 결과용 */
  multiResults?: BacktestMultiResultItem[];
}
```

**Step 2: 다중 모드 데이터 변환 로직**

```typescript
// 다중 모드: 날짜를 기준으로 전략별 value 병합
function buildMultiChartData(multiResults: BacktestMultiResultItem[]) {
  if (multiResults.length === 0) return [];

  // 기준 날짜는 첫 번째 결과의 equity_curve 날짜 사용
  const baseCurve = multiResults[0].equity_curve;
  return baseCurve.map((point, idx) => {
    const entry: Record<string, string | number> = {
      date: point.date,
      benchmark: point.benchmark,
    };
    multiResults.forEach((result) => {
      const p = result.equity_curve[idx];
      if (p) {
        // 전략명을 key로 사용 (공백 제거)
        entry[`strategy_${result.strategy_id}`] = p.value;
      }
    });
    return entry;
  });
}
```

**Step 3: 렌더링 로직 분기**

```tsx
export function BacktestEquityChart({ equityCurve, multiResults }: BacktestEquityChartProps) {
  const isMultiMode = multiResults && multiResults.length > 0;
  const chartData = isMultiMode
    ? buildMultiChartData(multiResults)
    : (equityCurve ?? []);

  return (
    <Card>
      <CardHeader>
        <CardTitle>수익 곡선{isMultiMode ? ` — ${multiResults.length}개 전략 비교` : ""}</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={chartData} margin={{ top: 8, right: 16, left: 0, bottom: 4 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} tickLine={false} interval="preserveStartEnd" />
            <YAxis
              tick={{ fontSize: 11 }}
              tickLine={false}
              tickFormatter={(v: number) => `${(v / 10000).toLocaleString("ko-KR")}만`}
              domain={["auto", "auto"]}
            />
            <Tooltip
              formatter={(value: number | string | undefined, name: string | undefined) => {
                const formatted = typeof value === "number"
                  ? `${(value / 10000).toFixed(1)}만원`
                  : String(value ?? "");
                // 전략 key 형식: "strategy_{id}" → 전략명으로 치환
                let label = name ?? "";
                if (isMultiMode && name?.startsWith("strategy_")) {
                  const id = Number(name.replace("strategy_", ""));
                  const found = multiResults?.find((r) => r.strategy_id === id);
                  label = found?.strategy_name ?? name;
                } else if (name === "value") {
                  label = "전략 수익";
                } else if (name === "benchmark") {
                  label = "KOSPI 벤치마크";
                } else if (name === "stockBuyhold") {
                  label = "종목 바이앤홀드";
                }
                return [formatted, label];
              }}
            />
            <Legend />

            {/* 벤치마크 라인 (항상 표시) */}
            <Line type="monotone" dataKey="benchmark" stroke="#94a3b8" dot={false} strokeWidth={1.5} strokeDasharray="4 2" name="benchmark" />

            {isMultiMode ? (
              // 다중 모드: 전략별 라인
              multiResults.map((result, idx) => (
                <Line
                  key={result.strategy_id}
                  type="monotone"
                  dataKey={`strategy_${result.strategy_id}`}
                  stroke={STRATEGY_COLORS[idx % STRATEGY_COLORS.length]}
                  dot={false}
                  strokeWidth={2}
                  name={`strategy_${result.strategy_id}`}
                />
              ))
            ) : (
              // 단일 모드: 기존 3라인
              <>
                <Line type="monotone" dataKey="value" stroke="#ef4444" dot={false} strokeWidth={2} name="value" />
                <Line type="monotone" dataKey="stockBuyhold" stroke="#22c55e" dot={false} strokeWidth={2} name="stockBuyhold" />
              </>
            )}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
```

**Step 4: TypeScript 컴파일 확인**

```bash
cd /Users/choijiseon/Documents/Sources/mystock.bot/frontend && npx tsc --noEmit 2>&1 | head -30
```

**Step 5: 커밋**

```bash
git add frontend/src/components/backtest/backtest-equity-chart.tsx
git commit -m "feat: 에쿼티 차트 다중 전략 라인 지원으로 확장 (Sprint 24 Task 7)"
```

**완료 기준**: 단일 모드(기존 Props)와 다중 모드(multiResults) 모두 타입 에러 없이 렌더링 가능

---

### Task 8: 백테스트 페이지 레이아웃 개편

**목적**: `backtest/page.tsx`를 다중 백테스트 결과 표시 흐름으로 재구성한다.

**Files**:
- Modify: `frontend/src/app/backtest/page.tsx`

**레이아웃 구성**:
1. `BacktestConfigForm` (체크박스 다중 선택 폼)
2. 로딩 중 스피너 또는 텍스트
3. 에러 메시지
4. 종목 상태 배지 (보유/관심 여부)
5. 랭킹 테이블 (`BacktestRankingTable`)
6. 다중 라인 에쿼티 차트 (`BacktestEquityChart` with `multiResults`)
7. 초기 안내 메시지

**종목 상태 배지 설계**:
- 보유 중: `Badge variant="destructive"` (빨간색) — "보유 중"
- 관심종목 등록: `Badge variant="outline"` — "관심종목 N개"
- 둘 다 아님: 표시 안 함

**Step 1: 페이지 컴포넌트 재구성**

```tsx
"use client";

import { useState } from "react";
import { BacktestConfigForm } from "@/components/backtest/backtest-config-form";
import { BacktestRankingTable } from "@/components/backtest/backtest-ranking-table";
import { BacktestEquityChart } from "@/components/backtest/backtest-equity-chart";
import { Badge } from "@/components/ui/badge";
import {
  useBacktestRunMulti,
  useStockStatus,
  type BacktestMultiResponse,
} from "@/hooks/use-backtest";

export default function BacktestPage() {
  const backtestRunMulti = useBacktestRunMulti();
  const [multiResult, setMultiResult] = useState<BacktestMultiResponse | null>(null);
  const [resolvedSymbol, setResolvedSymbol] = useState("");

  const { data: stockStatus } = useStockStatus(resolvedSymbol);

  const handleRunMulti = (config: {
    strategyIds: number[];
    symbol: string;
    startDate: string;
    endDate: string;
  }) => {
    setResolvedSymbol(config.symbol);
    backtestRunMulti.mutate(
      {
        strategy_ids: config.strategyIds,
        symbol: config.symbol,
        start_date: config.startDate,
        end_date: config.endDate,
      },
      {
        onSuccess: (result) => {
          setMultiResult(result);
        },
      }
    );
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">백테스팅</h2>

      {/* 백테스트 설정 폼 */}
      <BacktestConfigForm onRunMulti={handleRunMulti} isRunning={backtestRunMulti.isPending} />

      {/* 에러 메시지 */}
      {backtestRunMulti.isError && (
        <p className="text-destructive text-sm">
          백테스트 실행 중 오류가 발생했습니다.
        </p>
      )}

      {/* 종목 상태 배지 */}
      {resolvedSymbol && stockStatus && (
        <div className="flex gap-2 flex-wrap">
          {stockStatus.is_holding && (
            <Badge variant="destructive">보유 중</Badge>
          )}
          {stockStatus.is_watchlist && (
            <Badge variant="outline">
              관심종목 {stockStatus.watchlist_items.length}개
            </Badge>
          )}
        </div>
      )}

      {/* 면책 고지 */}
      {multiResult && (
        <div className="rounded-lg bg-muted/50 px-4 py-3 text-sm text-muted-foreground">
          선택한 전략들의 과거 데이터 기반 시뮬레이션 결과입니다. 실제 투자 성과와 다를 수 있습니다.
        </div>
      )}

      {/* 랭킹 테이블 */}
      {multiResult && (
        <BacktestRankingTable
          ranking={multiResult.ranking}
          symbol={multiResult.symbol}
        />
      )}

      {/* 다중 에쿼티 차트 */}
      {multiResult && multiResult.results.length > 0 && (
        <BacktestEquityChart multiResults={multiResult.results} />
      )}

      {/* 초기 안내 메시지 */}
      {!multiResult && !backtestRunMulti.isPending && (
        <div className="text-center text-muted-foreground py-12">
          전략을 하나 이상 선택하고 백테스트를 실행하면 결과가 여기에 표시됩니다.
        </div>
      )}

      {/* 로딩 */}
      {backtestRunMulti.isPending && (
        <div className="text-center text-muted-foreground py-12">
          백테스트 실행 중... 전략 수에 따라 수십 초가 소요될 수 있습니다.
        </div>
      )}
    </div>
  );
}
```

**Step 2: TypeScript 컴파일 확인**

```bash
cd /Users/choijiseon/Documents/Sources/mystock.bot/frontend && npx tsc --noEmit 2>&1 | head -30
```

**Step 3: 커밋**

```bash
git add frontend/src/app/backtest/page.tsx
git commit -m "feat: 백테스트 페이지 다중 전략 실행 흐름으로 개편 (Sprint 24 Task 8)"
```

**완료 기준**: 페이지가 타입 에러 없이 로드되고, 랭킹 테이블과 다중 라인 차트가 렌더링됨

---

## 의존성 및 리스크

| 리스크 | 영향도 | 대응 방안 |
|--------|--------|-----------|
| 다중 백테스트 실행 시간 초과 (전략 10개 × 3년 데이터) | 중 | 30초 타임아웃 설정; yfinance 캐시 활용; 실패한 전략은 건너뛰고 성공한 결과만 반환 |
| 랭킹 스코어 정규화: 전략이 1개일 때 전략 값 동일 | 낮 | 단일 전략 시 score=100.0 처리 (이미 설계에 포함) |
| `backtest-equity-chart.tsx` 다중 모드에서 날짜 길이 불일치 | 중 | 첫 번째 결과를 기준 날짜로 사용; 인덱스 기반 접근으로 안전 처리 |
| shadcn/ui `Table`, `Checkbox` 미설치 | 낮 | Task 5, 6에서 설치 확인 단계 포함 |
| 기존 `backtest/page.tsx` 단일 모드 경로 제거 | 중 | `BacktestResultCards`, `BacktestTradesTable` 컴포넌트는 제거하지 않고 그대로 유지 (추후 재활용 가능) |

---

## 완료 기준 (Definition of Done)

- [ ] `POST /api/v1/backtest/run-multi` 엔드포인트 응답 200, 다중 결과 + 랭킹 포함
- [ ] `GET /api/v1/backtest/stock-status/{symbol}` 엔드포인트 응답 200, 보유/관심 상태 반환
- [ ] `calculate_ranking_score()` 함수 테스트 2개 이상 통과
- [ ] `useBacktestRunMulti`, `useStockStatus` 훅 타입 에러 없이 추가
- [ ] 백테스트 설정 폼에서 체크박스로 여러 전략 선택 가능 (1~10개)
- [ ] 랭킹 테이블에서 1위 전략 강조 표시 확인
- [ ] 다중 라인 에쿼티 차트에서 전략별 색상 구분 라인 렌더링
- [ ] 기존 단일 백테스트 API(`POST /backtest/run`) 동작 영향 없음
- [ ] `docker compose exec backend pytest -v` 기존 테스트 포함 모두 통과
- [ ] 콘솔 에러 없이 백테스트 페이지 정상 렌더링

---

## Playwright 검증 시나리오

서버 실행 중(`docker compose up`) 상태에서 sprint-close agent가 자동 실행한다.

**TC-1: 백테스트 설정 폼 다중 선택 UI 확인**
```
1. browser_navigate -> http://localhost:3001/backtest 접속
2. browser_snapshot -> 전략 체크박스 목록 렌더링 확인
3. browser_click -> 전략 체크박스 2개 이상 클릭
4. browser_snapshot -> "N개 선택됨" 표시 확인
5. browser_console_messages(level: "error") -> 에러 없음 확인
```

**TC-2: 다중 백테스트 실행 및 결과 확인**
```
1. browser_navigate -> http://localhost:3001/backtest 접속
2. 전략 체크박스 2개 선택
3. 종목 입력 (예: 005930)
4. 기간 입력
5. browser_click -> "백테스트 실행" 버튼
6. browser_wait_for -> 로딩 완료 (결과 테이블 표시)
7. browser_snapshot -> 랭킹 테이블 + 다중 라인 차트 확인
8. browser_network_requests -> /api/v1/backtest/run-multi 200 응답 확인
```

**TC-3: 종목 상태 배지 표시 확인**
```
1. 백테스트 실행 완료 후
2. browser_snapshot -> 종목 상태 배지 영역 확인 (보유/관심 여부에 따라 조건부 표시)
3. browser_network_requests -> /api/v1/backtest/stock-status/{symbol} 200 응답 확인
```

---

## 수동 검증 항목 (사용자 직접 수행)

- `docker compose up --build` — 신규 코드 반영 빌드
- 실제 KIS API 연동 상태에서 다중 백테스트 실행 시간 체감 확인
- 랭킹 스코어의 직관성 검토 (1위 전략이 실제로 가장 나은 전략인지 육안 판단)
- 다중 라인 차트의 색상 가독성 확인 (10개 전략 동시 표시 시 구분 가능한지)

---

## 예상 산출물

1. `backend/app/services/backtest_metrics.py` — `calculate_ranking_score()` 함수 추가
2. `backend/app/api/v1/backtest.py` — `run-multi`, `stock-status` 엔드포인트 추가
3. `backend/tests/test_backtest_metrics.py` — 랭킹 스코어 테스트 추가
4. `backend/tests/test_backtest_api.py` — 다중 실행 및 종목 상태 API 테스트 추가
5. `frontend/src/hooks/use-backtest.ts` — `useBacktestRunMulti`, `useStockStatus` 훅 추가
6. `frontend/src/components/backtest/backtest-config-form.tsx` — 체크박스 다중 선택으로 개편
7. `frontend/src/components/backtest/backtest-ranking-table.tsx` — 신규 생성
8. `frontend/src/components/backtest/backtest-equity-chart.tsx` — 다중 라인 지원 확장
9. `frontend/src/app/backtest/page.tsx` — 다중 백테스트 흐름으로 개편
