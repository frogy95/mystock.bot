# Sprint 23: 커스텀 전략 백엔드 연동

## 개요

- **기간**: 2026-03-08
- **브랜치**: `sprint23`
- **PR**: develop 브랜치로 PR 생성
- **상태**: 진행 중

## 목표

커스텀 전략 빌더(Sprint 4.1)에서 로컬 zustand 스토어에만 저장되던 커스텀 전략을 DB에 영속 저장하고, DynamicStrategy 엔진을 통해 실제 매매 신호 평가에 활용할 수 있도록 백엔드-프론트엔드를 완전 연동한다.

---

## 배경 및 현황

### 현재 상태

- `strategies` 테이블에는 이미 `buy_conditions(JSONB)`, `sell_conditions(JSONB)`, `description(TEXT)` 컬럼이 ORM 모델(`backend/app/models/strategy.py`)에 정의되어 있음
- Alembic 마이그레이션(`f6a7b8c9d0e1`)도 이미 작성되어 있음 (미실행 상태)
- 프론트엔드 커스텀 전략 빌더는 로컬 zustand 스토어(`custom-strategy-store.ts`)에만 저장 중 (서버 동기화 없음)
- `use-strategy.ts`에 API 훅은 존재하나 커스텀 전략 생성/조건 업데이트 훅 없음
- `strategy_engine.py`에 `DynamicStrategy` 클래스 미구현 (프리셋 3종만 존재)

### 구현 목표

| 항목 | Before | After |
|------|--------|-------|
| 커스텀 전략 저장 위치 | localStorage (zustand persist) | PostgreSQL DB (JSONB) |
| 커스텀 전략 엔진 | 없음 (평가 불가) | DynamicStrategy (conditions 기반 신호 평가) |
| 커스텀 전략 생성 API | 없음 | POST /api/v1/strategies/custom |
| 조건 업데이트 API | 없음 | PUT /api/v1/strategies/{id}/conditions |
| 스키마 | buy_conditions 미노출 | StrategyResponse에 buy_conditions, sell_conditions, description 포함 |
| 프론트엔드 스토어 | 로컬 전용 | 서버 동기화 (optimistic update) |

---

## 구현 범위

### 포함 항목 (Must Have)

1. **Alembic 마이그레이션 실행**: `f6a7b8c9d0e1` (buy_conditions, sell_conditions, description 컬럼)
2. **DynamicStrategy 엔진 구현**: `strategy_engine.py`에 `DynamicStrategy` 클래스 추가
3. **커스텀 전략 생성 API**: `POST /api/v1/strategies/custom`
4. **조건 업데이트 API**: `PUT /api/v1/strategies/{id}/conditions`
5. **스키마 업데이트**: `StrategyResponse`에 `buy_conditions`, `sell_conditions`, `description` 필드 추가
6. **프론트엔드 훅 추가**: `use-strategy.ts`에 `useCreateCustomStrategy`, `useUpdateConditions` 추가
7. **커스텀 스토어 서버 동기화**: `custom-strategy-store.ts`를 서버 기반으로 전환

### 제외 항목 (Out of Scope)

- DynamicStrategy의 복잡한 지표 조합 검증 UI (빌더 UI는 Sprint 4.1에서 이미 구현됨)
- 커스텀 전략 백테스팅 연동 (별도 스프린트)
- 데모 모드 커스텀 전략 지원 (데모 모드는 서버 의존 없이 동작)

---

## Task 목록

### Task 0: 브랜치 확인 및 마이그레이션 파일 검증

**목적**: 작업 환경을 확인하고, 이미 작성된 마이그레이션 파일이 올바른지 검증한다.

**Files**:
- `backend/alembic/versions/f6a7b8c9d0e1_sprint23_커스텀전략_조건_컬럼_추가.py` (검증)

**검증**:
```bash
# 현재 브랜치 확인
git branch --show-current

# alembic 현재 버전 확인
docker compose exec backend alembic current

# 마이그레이션 파일 head 확인
docker compose exec backend alembic heads
```

**완료 기준**: 브랜치가 `sprint23`이고, 마이그레이션 파일이 `e5f6a7b8c9d0`을 부모로 가리킴을 확인

---

### Task 1: DynamicStrategy 엔진 구현

**목적**: `buy_conditions`/`sell_conditions` JSONB 데이터를 파싱하여 매매 신호를 평가하는 DynamicStrategy 클래스를 구현한다.

**Files**:
- `backend/app/services/strategy_engine.py` (수정)

**조건 구조 (JSONB 스키마)**:
```json
{
  "conditions": [
    {
      "id": "uuid",
      "leftOperand": { "type": "indicator", "indicator": "SMA", "params": { "period": 20 } },
      "operator": ">",
      "rightOperand": { "type": "indicator", "indicator": "SMA", "params": { "period": 60 } }
    }
  ],
  "logicOperators": ["AND"]
}
```

**지원 지표**: SMA, EMA, RSI, MACD, 볼린저밴드 상단/하단/중단, 거래량, 현재가

**지원 연산자**: `>`, `<`, `>=`, `<=`, `==`

**구현 내용**:
```python
class DynamicStrategy(BaseStrategy):
    """커스텀 조건 기반 동적 전략"""
    name = "Dynamic"
    description = "사용자 정의 조건 기반 커스텀 전략"

    def evaluate(self, df: pd.DataFrame, params: dict[str, Any]) -> Signal:
        # buy_conditions, sell_conditions는 params로 전달
        ...
```

**완료 기준**:
- `DynamicStrategy`가 `_STRATEGY_REGISTRY`에 등록됨
- 빈 조건 시 HOLD 신호 반환
- 유효한 조건 파싱 및 신호 평가 동작

---

### Task 2: 스키마 업데이트

**목적**: `StrategyResponse`에 `buy_conditions`, `sell_conditions`, `description` 필드를 추가하여 프론트엔드에서 조건 데이터를 수신할 수 있도록 한다.

**Files**:
- `backend/app/schemas/strategy.py` (수정)

**변경 내용**:
```python
from typing import Any, Dict, List, Optional
...

class StrategyResponse(BaseModel):
    id: int
    name: str
    strategy_type: str
    is_active: bool
    is_preset: bool
    user_id: int | None = None
    params: List[StrategyParamResponse] = []
    buy_conditions: Optional[Dict[str, Any]] = None   # 신규
    sell_conditions: Optional[Dict[str, Any]] = None  # 신규
    description: Optional[str] = None                  # 신규
    created_at: datetime

    model_config = {"from_attributes": True}


class CustomStrategyCreateRequest(BaseModel):
    """커스텀 전략 생성 요청 스키마"""
    name: str
    description: Optional[str] = None
    buy_conditions: Optional[Dict[str, Any]] = None
    sell_conditions: Optional[Dict[str, Any]] = None


class ConditionsUpdateRequest(BaseModel):
    """전략 조건 업데이트 요청 스키마"""
    buy_conditions: Optional[Dict[str, Any]] = None
    sell_conditions: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
```

**완료 기준**: 기존 `StrategyResponse` 직렬화에 신규 필드가 포함됨

---

### Task 3: 커스텀 전략 API 구현

**목적**: 커스텀 전략 생성 및 조건 업데이트 엔드포인트를 추가한다.

**Files**:
- `backend/app/api/v1/strategies.py` (수정)

**신규 엔드포인트**:

#### POST /api/v1/strategies/custom
```
- 요청: CustomStrategyCreateRequest
- 응답: StrategyResponse (201)
- 동작: 새 커스텀 전략 생성 (is_preset=False, strategy_type="custom", user_id=current_user.id)
- 데모 모드: 403 차단
```

#### PUT /api/v1/strategies/{id}/conditions
```
- 요청: ConditionsUpdateRequest
- 응답: StrategyResponse
- 동작: 본인 소유 커스텀 전략의 buy_conditions, sell_conditions, description 업데이트
- 권한: 본인 소유이며 is_preset=False인 전략만 허용
- 데모 모드: 403 차단
```

**라우터 등록 순서 주의**: `/custom` 경로가 `/{strategy_id}` 경로보다 먼저 등록되어야 함

**완료 기준**:
- `POST /api/v1/strategies/custom` → 201 응답, DB에 전략 저장됨
- `PUT /api/v1/strategies/{id}/conditions` → 200 응답, JSONB 데이터 업데이트됨
- 프리셋 전략 조건 변경 시도 시 404 반환

---

### Task 4: 백엔드 통합 테스트 추가

**목적**: 신규 엔드포인트에 대한 pytest 통합 테스트를 작성한다.

**Files**:
- `backend/tests/api/test_strategies.py` (수정 또는 신규)

**테스트 시나리오**:
```
TC-1: 커스텀 전략 생성 — POST /strategies/custom → 201, DB 저장 확인
TC-2: 커스텀 전략 조건 업데이트 — PUT /strategies/{id}/conditions → 200, JSONB 반환
TC-3: 프리셋 전략 조건 변경 차단 — 404 반환 확인
TC-4: 타인 소유 전략 조건 변경 차단 — 404 반환 확인
TC-5: StrategyResponse에 buy_conditions 필드 포함 확인
```

**완료 기준**: 신규 테스트 5개 포함, `pytest 56 passed` 이상 달성

---

### Task 5: 프론트엔드 훅 추가

**목적**: `use-strategy.ts`에 커스텀 전략 생성 및 조건 업데이트 훅을 추가한다.

**Files**:
- `frontend/src/hooks/use-strategy.ts` (수정)

**추가 타입 및 훅**:
```typescript
/** 커스텀 전략 생성 요청 타입 */
export interface CreateCustomStrategyRequest {
  name: string;
  description?: string;
  buy_conditions?: Record<string, unknown>;
  sell_conditions?: Record<string, unknown>;
}

/** 조건 업데이트 요청 타입 */
export interface UpdateConditionsRequest {
  buy_conditions?: Record<string, unknown>;
  sell_conditions?: Record<string, unknown>;
  description?: string;
}

// StrategyAPI 타입에 필드 추가
export interface StrategyAPI {
  // 기존 필드...
  buy_conditions: Record<string, unknown> | null;  // 신규
  sell_conditions: Record<string, unknown> | null; // 신규
  description: string | null;                      // 신규
}

/** 커스텀 전략 생성 훅 */
export function useCreateCustomStrategy() { ... }

/** 전략 조건 업데이트 훅 */
export function useUpdateConditions() { ... }
```

**완료 기준**: TypeScript 컴파일 오류 없음, 훅 export 확인

---

### Task 6: 커스텀 스토어 서버 동기화

**목적**: `custom-strategy-store.ts`가 서버(API)와 동기화되도록 전환한다. 로컬 persist 스토어는 draft(임시 작업) 상태 관리용으로 유지하고, save 시 서버에 동기화한다.

**Files**:
- `frontend/src/stores/custom-strategy-store.ts` (수정)

**설계 방향**:

| 항목 | 변경 전 | 변경 후 |
|------|---------|---------|
| 전략 ID 타입 | `string` (UUID, 로컬) | `number` (서버 DB ID) |
| 저장 트리거 | zustand set → localStorage 자동 저장 | save 액션 호출 시 API 뮤테이션 |
| 초기 데이터 | localStorage에서 복원 | 서버 API에서 fetch (`useStrategies()` 연동) |
| 신규 전략 생성 | 로컬 uuid로 즉시 생성 | `useCreateCustomStrategy()` API 호출 후 서버 ID로 저장 |
| 조건 변경 | 로컬 state만 수정 | 로컬 draft 수정 → `saveConditions()` 호출 시 API 동기화 |

**핵심 메서드 변경**:
- `addStrategy(name)` → API 호출 (`useCreateCustomStrategy`) 후 서버 ID로 전략 추가
- `saveConditions(strategyId)` → 현재 draft 상태를 `useUpdateConditions`로 서버에 저장
- `loadFromServer(strategies)` → 서버에서 받은 커스텀 전략 목록으로 스토어 초기화

**완료 기준**:
- 커스텀 전략 생성 시 DB에 저장됨 (새로고침 후에도 유지)
- 조건 수정 후 save 시 서버에 반영됨
- `useStrategies()` 쿼리 invalidation으로 목록 자동 갱신

---

### Task 7: 커스텀 전략 빌더 UI 서버 연동

**목적**: 커스텀 전략 빌더 페이지/컴포넌트에서 서버 동기화 훅을 연결한다.

**Files**:
- `frontend/src/app/strategy/page.tsx` (수정 — 커스텀 전략 탭 부분)
- `frontend/src/components/strategy/custom-strategy-builder.tsx` (수정 — 저장 버튼 연결)

**변경 내용**:
- 커스텀 전략 목록을 `useStrategies()` 결과에서 `strategy_type === "custom"` 필터로 표시
- "새 전략 만들기" 버튼 → `useCreateCustomStrategy()` 호출
- "저장" 버튼 → `useUpdateConditions()` 호출 + `toast.success`
- 저장 성공 시 `queryClient.invalidateQueries({ queryKey: ["strategy"] })`

**완료 기준**: 커스텀 전략 빌더에서 생성/저장/삭제가 서버와 동기화됨

---

## 실행 순서

```
Task 0 (환경 확인)
  ↓
Task 1 (DynamicStrategy 엔진)
  ↓
Task 2 (스키마 업데이트)
  ↓
Task 3 (커스텀 전략 API)
  ↓
Task 4 (백엔드 테스트) — Task 1~3 완료 후
  ↓
Task 5 (프론트엔드 훅) — Task 2~3 완료 후
  ↓
Task 6 (스토어 동기화) — Task 5 완료 후
  ↓
Task 7 (빌더 UI 연동) — Task 5~6 완료 후
```

---

## 핵심 파일 목록

| 파일 | 유형 | Task |
|------|------|------|
| `backend/alembic/versions/f6a7b8c9d0e1_sprint23_커스텀전략_조건_컬럼_추가.py` | 기존 (미실행) | Task 0 |
| `backend/app/services/strategy_engine.py` | 수정 | Task 1 |
| `backend/app/schemas/strategy.py` | 수정 | Task 2 |
| `backend/app/api/v1/strategies.py` | 수정 | Task 3 |
| `backend/tests/api/test_strategies.py` | 신규/수정 | Task 4 |
| `frontend/src/hooks/use-strategy.ts` | 수정 | Task 5 |
| `frontend/src/stores/custom-strategy-store.ts` | 수정 | Task 6 |
| `frontend/src/app/strategy/page.tsx` | 수정 | Task 7 |
| `frontend/src/components/strategy/custom-strategy-builder.tsx` | 수정 | Task 7 |

---

## 기술적 주의사항

### 백엔드

- **라우터 순서**: FastAPI는 경로를 등록 순서대로 매칭한다. `POST /strategies/custom`이 `POST /strategies/{id}`보다 먼저 등록되어야 `/custom`이 id로 해석되지 않는다.
- **JSONB None 처리**: `buy_conditions`가 None인 경우 DynamicStrategy 평가 시 빈 조건(HOLD)으로 처리해야 한다.
- **DynamicStrategy 등록**: `_STRATEGY_REGISTRY`와 `_NAME_TO_ENGINE` 양쪽 모두에 등록해야 한다.
- **데모 모드**: 커스텀 전략 생성/조건 업데이트는 데모 사용자에게 403을 반환한다.

### 프론트엔드

- **ID 타입 전환**: 기존 커스텀 스토어의 ID는 `string` (UUID), 서버 전환 후 ID는 `number` (DB PK). 전환 시 타입 불일치에 주의한다.
- **낙관적 업데이트**: 조건 수정은 로컬 draft로 즉시 반영하되, 서버 저장 실패 시 롤백 처리를 고려한다.
- **기존 로컬 데이터 마이그레이션**: localStorage에 기존 커스텀 전략이 있는 경우, 서버 전환 후 손실될 수 있음. 마이그레이션 안내 또는 자동 업로드 로직을 검토한다.
- **`strategy_type` 필터링**: 서버에서 받은 전략 목록 중 `strategy_type === "custom"`만 커스텀 빌더 탭에 표시한다.

---

## 완료 기준 (Definition of Done)

- ✅ Alembic 마이그레이션 파일 (`f6a7b8c9d0e1`) 검증 완료
- ⬜ `alembic upgrade head` 실행 후 `buy_conditions`, `sell_conditions`, `description` 컬럼 정상 생성 (수동)
- ⬜ `DynamicStrategy` 클래스 구현 및 `_STRATEGY_REGISTRY` 등록
- ⬜ `POST /api/v1/strategies/custom` → 201, 커스텀 전략 DB 저장
- ⬜ `PUT /api/v1/strategies/{id}/conditions` → 200, JSONB 업데이트
- ⬜ `StrategyResponse`에 `buy_conditions`, `sell_conditions`, `description` 포함
- ⬜ `pytest 56 passed` 이상 (기존 51 + 신규 5)
- ⬜ 프론트엔드 `useCreateCustomStrategy`, `useUpdateConditions` 훅 정상 동작
- ⬜ 커스텀 전략 빌더에서 생성 → 새로고침 후에도 서버에서 복원
- ⬜ TypeScript 빌드 오류 없음

---

## 검증 계획

### 자동 검증 (sprint-close 시점)

- `docker compose exec backend pytest -v` — 전체 테스트 통과 확인
- `curl -X POST .../api/v1/strategies/custom` — 커스텀 전략 생성 API 확인
- `curl -X PUT .../api/v1/strategies/{id}/conditions` — 조건 업데이트 API 확인
- Playwright: 커스텀 전략 빌더 페이지 렌더링 확인
- Playwright: 새 커스텀 전략 생성 후 목록에 표시 확인

### 수동 검증 필요 항목

- ⬜ Docker 재빌드: `docker compose up --build`
- ⬜ DB 마이그레이션: `docker compose exec backend alembic upgrade head` (buy_conditions 컬럼 추가)
- ⬜ 커스텀 전략 빌더에서 조건 설정 후 저장 → 새로고침 후 서버에서 복원 확인
- ⬜ DynamicStrategy 신호 평가 (`/evaluate/{symbol}`) 호출 결과 확인
- ⬜ 기존 로컬 커스텀 전략 데이터 마이그레이션 동작 확인
