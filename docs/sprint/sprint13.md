# Sprint 13: MVP 안정화 - 핵심 버그 수정 및 코드 품질 개선

**기간:** 2026-03-03
**브랜치:** sprint-13
**상태:** ✅ 완료

---

## 개요

Sprint 0~12 완료 후 전체 코드 리뷰를 통해 발견된 **긴급 버그 2건** + **중요 이슈 8건** + **권장 개선 2건**을 수정하여 MVP 안정성을 확보한다.

---

## 수행 작업

### [긴급] Task 1: order_executor.py 분산 락 경합 조건 수정

**파일:** `backend/app/services/order_executor.py`

**문제:** `async with acquire_order_lock()` 블록이 락 획득 확인만 하고 즉시 빠져나감. 중복 체크 + DB 주문 생성 + KIS 주문 실행이 락 해제 후 실행되어 경합 조건 발생.

**수정:** 80행 이후의 중복 체크/주문 생성/KIS 실행 로직 전체를 `async with` 블록 안으로 이동 (들여쓰기 1단계 추가).

---

### [긴급] Task 2: risk_manager.py 분할/전량 익절 순서 수정

**파일:** `backend/app/services/risk_manager.py`

**문제:** 분할 익절(50% 도달) 체크가 전량 익절(100% 도달) 체크보다 먼저 실행. 수익률 100% 도달 시에도 50% 조건에 걸려 반량만 매도됨.

**수정:** 전량 익절 체크를 분할 익절보다 먼저 실행하도록 순서 변경.

```
변경 순서:
1. 고정비율 손절 (기존 유지)
2. 전량 익절 (change_rate >= take_profit) ← 먼저 체크
3. 분할 익절 (change_rate >= take_profit * 0.5) ← 후순위
```

---

### [중요] Task 3: strategies.py N+1 쿼리 최적화

**파일:** `backend/app/api/v1/strategies.py`

**문제:**
- `list_strategies()`: 각 전략마다 `StrategyParam` 별도 SELECT (N+1)
- `get_strategy_performance()`: 각 전략별로 Order 전체 SELECT + Python 집계

**수정:**
- StrategyParam을 단일 IN 쿼리로 묶어서 조회 + dict 매핑
- Order GROUP BY + WatchlistItem GROUP BY SQL 집계 2개로 변환

---

### [중요] Task 4: `_get_user_id` 중복 함수 추출

**파일 (신규):** `backend/app/core/deps.py`

**문제:** 5개 라우터(holdings, orders, safety, system_settings, watchlist)에 동일한 `_get_user_id()` 함수가 복사-붙여넣기됨.

**수정:** `core/deps.py`에 `get_user_id()` 한 번 정의 후 5곳에서 import.

---

### [중요] Task 5: kis_client.py httpx 연결 풀 공유

**파일:** `backend/app/services/kis_client.py`, `backend/app/main.py`

**문제:** 모든 API 호출마다 `async with httpx.AsyncClient()` 로 새 TCP 연결 생성 (연결 재사용 없음).

**수정:** KISClient에 실전/모의 서버별 `httpx.AsyncClient` 인스턴스를 lazy 초기화로 유지. 앱 종료 시 `close()` 메서드로 정리.

---

### [중요] Task 6: stocks.py 데모 모드 누락 보완

**파일:** `backend/app/api/v1/stocks.py`, `backend/app/services/demo_data.py`

**문제:** `get_balance()`, `get_stock_quote()`, `get_stock_chart()`에 데모 유저 분기 없음. 데모 유저 호출 시 KIS 503 에러 발생.

**수정:** 각 엔드포인트에 `if is_demo_user(current_user): return get_demo_*()` 분기 추가. demo_data.py에 3개 더미 함수 추가.

---

### [중요] Task 7: safety_guard.py 손실 계산 네이밍 수정

**파일:** `backend/app/services/safety_guard.py`

**문제:** 전체 보유기간 누적 손익을 "일일 손실"로 잘못 명명.

**수정:** `daily_loss_pct` → `unrealized_loss_pct` 로 변수명/메시지 변경하여 의미 명확화.

---

### [중요] Task 8: 프론트엔드 Mock Zustand 스토어 정리

**삭제된 파일:**
- `frontend/src/stores/orders-store.ts` (실제 페이지는 TanStack Query로 대체)
- `frontend/src/stores/settings-store.ts` (실제 페이지는 TanStack Query로 대체)

**수정:** `frontend/src/stores/index.ts` — 삭제된 스토어 export 제거.

---

### [중요] Task 9: API 타입 중복 해소

**파일 (신규):** `frontend/src/lib/api/types.ts`

**문제:** `OrderAPI` 인터페이스가 `use-orders.ts`, `use-dashboard.ts` 2곳에 중복 정의.

**수정:** 공통 타입 파일로 추출 후 import.

---

### [중요] Task 10: 주문 취소 기능 구현

**파일:**
- `backend/app/api/v1/orders.py` — `PUT /{order_id}/cancel` 엔드포인트 추가
- `frontend/src/hooks/use-orders.ts` — `useCancelOrder` mutation 훅 추가
- `frontend/src/app/orders/page.tsx` — `onCancel` 연결 (기존 noop 대체)

**동작:**
- `pending` 상태 주문만 `cancelled`로 변경
- 데모 모드에서 호출 시 403 반환

---

### [권장] Task 11: scheduler.py 하드코딩 개선

**파일:** `backend/app/services/scheduler.py`

**문제:**
- `_run_daily_summary()`: `user_id = 1` 하드코딩
- `_run_strategy_evaluation()`: `quantity = 1` 하드코딩

**수정:**
- users 테이블에서 전체 사용자 조회 후 순회
- SystemSetting `order_quantity` 설정값에서 수량 조회

---

### [권장] Task 12: 미사용 코드 정리

**파일:** `backend/app/models/portfolio.py`

**수정:** `PortfolioSnapshot`이 현재 미사용임을 주석으로 명시 (Sprint 14+ 장 시작가 스냅샷 기능 구현 시 활용 예정).

---

## 테스트 결과

### 백엔드 통합 테스트 (Task 13)

새로 추가된 테스트 파일:
- `backend/tests/api/test_strategies.py` — 전략 목록/상세/성과 (4건)
- `backend/tests/api/test_holdings.py` — 보유종목 목록/요약 (3건)
- `backend/tests/api/test_watchlist.py` — 관심종목 그룹 CRUD (3건)
- `backend/tests/api/test_stocks.py` — 종목 검색/시세/잔고 (3건)
- `backend/tests/services/test_risk_manager.py` — 전량/분할 익절 순서 (3건)

`test_orders.py`에 주문 취소 3건 추가.

**결과: 33개 테스트 전부 PASSED** (기존 14개 → 33개)

```
======================== 33 passed, 1 warning in 0.72s =========================
```

### E2E API 검증 (Task 14)

**데모 모드 API 검증 (9개 엔드포인트 전부 200):**
- ✅ `/api/v1/watchlist/groups` → 200 (3그룹)
- ✅ `/api/v1/strategies` → 200 (3전략)
- ✅ `/api/v1/orders` → 200 (6주문)
- ✅ `/api/v1/holdings` → 200 (5보유종목)
- ✅ `/api/v1/holdings/summary` → 200
- ✅ `/api/v1/orders/daily-summary` → 200
- ✅ `/api/v1/stocks/balance` → 200 (데모 더미 데이터)
- ✅ `/api/v1/stocks/005930/quote` → 200 (데모 더미 데이터)
- ✅ `/api/v1/safety/status` → 200

**데모 모드 쓰기 제한 검증:**
- ✅ `/api/v1/orders/{id}/cancel` → 403 (데모 모드 쓰기 차단)

**헬스체크:**
- ✅ 상태: healthy, DB: healthy

---

## 완료 기준 (Definition of Done)

- ✅ 분산 락 경합 조건 수정 완료
- ✅ 익절 순서 버그 수정 완료
- ✅ 데모 유저 접속 시 503 에러 없음 확인
- ✅ 주문 취소 기능 동작 확인 (pending → cancelled)
- ✅ 33개 테스트 전부 PASSED
- ✅ TypeScript 빌드 에러 없음 (`npm run build` 성공)

---

## Out of Scope (Sprint 14+)

- WebSocket 인증 (프로토콜 변경 필요)
- 종목 마스터 Redis 구조 최적화
- backtest_engine O(n^2) 성능 개선
- 프론트엔드 단위 테스트 프레임워크 도입
- AuthGuard hydration 로딩 표시
- CORS origin 제한 (운영 배포 시)
- 진정한 일일 손실 계산 (장 시작가 스냅샷 - PortfolioSnapshot 활용)
