# Sprint 7 코드 리뷰 보고서

- **리뷰 대상 브랜치:** sprint7
- **리뷰 일자:** 2026-03-01
- **리뷰 범위:** Sprint 7 신규 6개 파일 + 수정 3개 파일 (백엔드), 수정 2개 파일 (프론트엔드)

---

## 전체 평가

Sprint 7 구현 품질은 전반적으로 양호합니다. 핵심 기능(손절/익절, 안전장치, 분산 락)이 설계대로 구현되었으며 보안상 Critical/High 이슈는 없습니다. 아래 Medium 이슈는 기능 정확도에 영향을 줄 수 있으므로 Sprint 8 시작 전 수정을 권장합니다.

---

## 이슈 목록

### Medium 이슈

#### M1. 분할 익절 조건 논리 역전 (risk_manager.py L64-77)

**파일:** `backend/app/services/risk_manager.py`

**현상:** `change_rate >= take_profit * 0.5` 조건이 `change_rate >= take_profit` 조건보다 먼저 평가됩니다. 목표 수익률의 100%에 도달했을 때도 분할 익절(반량)만 실행되고 전량 익절이 실행되지 않습니다.

**예시:**
- `take_profit_rate = 10%`, `change_rate = 12%` (목표 초과)
- `change_rate >= 10% * 0.5` (즉 `12% >= 5%`) → True → 분할 익절만 실행됨 (의도와 다름)

**권장 수정:** 전량 익절 조건을 분할 익절 조건보다 먼저 평가하도록 순서를 변경.

---

#### M2. 분산 락 범위 문제 (order_executor.py L70-84)

**파일:** `backend/app/services/order_executor.py`

**현상:** `async with acquire_order_lock` 컨텍스트 매니저 블록을 빠져나온 뒤 중복 주문 체크 및 DB 주문 생성이 수행됩니다. 락이 해제된 상태에서 작업이 진행되므로 동시 접근 시 중복 주문이 발생할 수 있습니다.

**권장 수정:** 중복 주문 체크, DB 주문 생성, KIS 주문 실행을 `async with acquire_order_lock` 블록 내부로 이동.

---

#### M3. 미사용 임포트 (safety_guard.py L134)

**파일:** `backend/app/services/safety_guard.py`

**현상:** `from sqlalchemy import cast, Date` 임포트가 있으나 실제로는 사용되지 않습니다. `func.date()`로 날짜 비교를 수행하고 있어 `cast`, `Date`는 불필요합니다.

**권장 수정:** 미사용 임포트 제거.

---

#### M4. 타입 힌트 누락 (system_monitor.py L70)

**파일:** `backend/app/services/system_monitor.py`

**현상:** `check_error_threshold` 함수의 `db` 파라미터에 `AsyncSession` 타입 힌트가 없습니다.

```python
async def check_error_threshold(user_id: int, db) -> tuple[bool, str]:
```

**권장 수정:**
```python
from sqlalchemy.ext.asyncio import AsyncSession

async def check_error_threshold(user_id: int, db: AsyncSession) -> tuple[bool, str]:
```

---

### Low 이슈

#### L1. avg_price None 체크 누락 (risk_manager.py L142)

**파일:** `backend/app/services/risk_manager.py`

**현상:** `evaluate_atr_stop` 함수에서 `holding.avg_price`를 None 체크 없이 `float()` 변환합니다. `holding.current_price`는 L130에서 체크하지만 `avg_price`는 체크하지 않아 None 시 `TypeError` 발생 가능.

**권장 수정:** `avg_price is None` 체크 추가 후 `HOLD` 반환.

---

## 긍정 사항

- Redis 분산 락을 `asynccontextmanager`로 구현하여 예외 발생 시에도 자동 해제되는 안전한 구조
- 안전장치 체크를 매수 주문에만 적용하고 매도(손절/익절)는 즉시 실행 — 설계 의도에 맞는 올바른 구현
- `emergency_sell_all` 실행 후 자동매매를 비활성화하는 연계 처리가 잘 구현됨
- 프론트엔드 훅이 명확한 타입 정의와 함께 TanStack Query 패턴을 일관되게 사용
- `useSafetyStatus`의 `refetchInterval: 60_000` 설정으로 상태 자동 갱신 구현

---

## 요약

| 심각도 | 건수 | 비고 |
|--------|------|------|
| Critical | 0 | |
| High | 0 | |
| Medium | 4 | Sprint 8 전 수정 권장 |
| Low | 1 | 추후 개선 |
| 합계 | 5 | |
