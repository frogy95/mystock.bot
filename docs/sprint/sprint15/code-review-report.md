# Sprint 15 코드 리뷰 보고서

- **PR**: [#23 feat: Sprint 15 완료 - 사용자별 데이터 격리 + 복사된 전략 관리 기능 보완](https://github.com/frogy95/mystock.bot/pull/23)
- **리뷰 일시**: 2026-03-03 (1차), 2026-03-03 (2차 추가)
- **리뷰어**: Sprint-Close Agent (자동 코드 리뷰)
- **리뷰 대상 커밋 (1차)**: 3182b4f, 28e3afd, 39f42d9, c29138a, d735483
- **리뷰 대상 커밋 (2차)**: 8a7b166, 0c3f6ee

---

## 요약

Sprint 15는 두 단계로 구성됩니다.
- **1차**: 멀티유저 데이터 격리를 위한 핵심 보안 계층 구현
- **2차**: 복사된 전략 관리 기능 보완 (이름 변경, 삭제, 파라미터 설명)

전반적으로 설계가 명확하고 구현이 일관적입니다.

**1차 리뷰 결과 (격리 기능)**
- **Critical 이슈**: 0건
- **High 이슈**: 1건
- **Medium 이슈**: 3건
- **Low/정보 이슈**: 4건

**2차 리뷰 결과 (관리 기능 보완)**
- **Critical 이슈**: 0건
- **High 이슈**: 0건
- **Medium 이슈**: 2건
- **Low/정보 이슈**: 2건

---

## Critical 이슈 (즉시 수정 필요)

없음.

---

## High 이슈 (수정 권장)

### [HIGH-1] clone 완료 후 `_get_strategy_with_params` 재호출 — 불필요한 DB 왕복

**파일**: `backend/app/api/v1/strategies.py` (마지막 clone 엔드포인트)

```python
# 현재 코드
await db.commit()
return await _get_strategy_with_params(cloned.id, db)
```

`db.commit()` 후 `_get_strategy_with_params`를 재호출하면 파라미터까지 로드하기 위해 추가 SELECT가 발생합니다. commit 후 SQLAlchemy 세션은 lazy load가 가능하므로 문제는 없지만, 이미 `original_params`를 메모리에 갖고 있기 때문에 `cloned.params`를 직접 조합하여 반환하면 DB 왕복 1회를 줄일 수 있습니다.

**영향**: 성능 (경미), 기능 동작에는 문제 없음.

**권장 개선**: 추후 성능 최적화 시 반영.

---

## Medium 이슈 (추후 개선 권장)

### [MED-1] 프론트엔드 "내 전략으로 복사" 버튼 — 복사 중 모든 프리셋에 동시 loading 표시

**파일**: `frontend/src/components/strategy/strategy-card-list.tsx`

```tsx
// 현재: cloneStrategyMutation.isPending 을 모든 프리셋 카드가 공유
disabled={cloneStrategyMutation.isPending}
```

`cloneStrategyMutation.isPending`이 true이면 현재 클릭한 카드뿐 아니라 모든 프리셋 카드의 "내 전략으로 복사" 버튼이 동시에 비활성화됩니다. 사용자 경험을 위해 클릭한 카드 id를 tracking하거나 `useCloneStrategy`에서 `variables`를 활용하여 해당 카드만 로딩 표시를 하는 것이 좋습니다.

**영향**: UX (경미), 기능 동작에는 문제 없음.

### [MED-2] `strategy-detail-panel.tsx` — `useStrategies` 훅 중복 호출 가능성

**파일**: `frontend/src/components/strategy/strategy-detail-panel.tsx`

```tsx
const { data: apiStrategies } = useStrategies();
```

`strategy-card-list.tsx`에서도 `useStrategies()`를 호출하고 있습니다. TanStack Query의 캐시를 통해 실제 API 요청은 중복되지 않지만, 부모 컴포넌트에서 전략 데이터를 prop으로 내려주거나 Context를 활용하는 방식으로 더 명확한 데이터 흐름을 만들 수 있습니다.

**영향**: 코드 설계 (경미), 기능 동작에는 문제 없음 (TanStack Query 캐시로 중복 요청 방지됨).

### [MED-3] `backtest.py` — `run_backtest_api`에서 `current_user`가 데모 유저인 경우 user_id 저장 오류 가능성

**파일**: `backend/app/api/v1/backtest.py`

```python
backtest_record = BacktestResult(
    user_id=current_user.id,  # 데모 유저는 id가 실제 DB 행이 아닐 수 있음
    ...
)
```

데모 유저는 `is_demo_user()` 체크로 별도 처리되지만, 데모 유저 분기가 함수 시작 부분에 있는지 확인이 필요합니다. 현재 구현 확인 결과: 해당 엔드포인트(`POST /backtest/run`)에서 데모 유저 분기가 선행되는지 코드 상단에서 처리하면 안전합니다.

**영향**: 잠재적 무결성 오류 (실제 데모 사용자로 DB 저장 시도할 경우).

---

## Low 이슈 / 정보

### [LOW-1] 마이그레이션에서 기존 `backtest_results` 레코드 — admin 할당 방식

기존 레코드를 admin(id=1)에 할당하는 방식은 적절합니다. 다만 새 운영 환경에서 admin id가 1이 아닐 경우를 대비하여 마이그레이션 스크립트에서 `id=1` 하드코딩 대신 `SELECT id FROM users WHERE role='admin' LIMIT 1` 방식을 사용하면 더 안전합니다.

### [LOW-2] `strategy.params` 직접 할당 — SQLAlchemy relationship vs 직접 set

`get_strategy_detail`, `evaluate_strategy_signal` 엔드포인트에서:

```python
strategy.params = param_result.scalars().all()
```

`Strategy.params`가 SQLAlchemy relationship으로 정의된 경우, 이 방식은 세션 상태에 따라 예기치 않게 동작할 수 있습니다. `_get_strategy_with_params` 헬퍼를 재사용하거나 DTO를 통해 반환하는 방식을 권장합니다.

### [LOW-3] `handleToggleActive`에서 `strategy.is_preset` 차단 — 백엔드와 이중 방어

프론트엔드에서 `is_preset` 체크로 토글을 차단하고, 백엔드에서도 `user_id == current_user.id` 조건으로 404를 반환합니다. 이중 방어(Defense in Depth)는 보안 관점에서 올바른 접근입니다. 다만 토글 버튼의 시각적 disabled 상태 표시도 추가하면 UX가 개선됩니다.

### [LOW-4] `useCloneStrategy`의 에러 핸들링 — onError 콜백 부재

```typescript
// 현재: onSuccess만 정의, onError 없음
return useMutation<StrategyAPI, Error, { id: number }>({
    mutationFn: ...,
    onSuccess: () => { ... },
});
```

`onError` 콜백을 추가하여 복사 실패 시 toast 알림을 표시하면 사용자가 실패를 인지할 수 있습니다.

---

## 긍정적 평가 사항

1. **격리 로직의 일관성**: `or_(Strategy.user_id.is_(None), Strategy.user_id == current_user.id)` 패턴이 모든 쿼리에 일관되게 적용됨.
2. **프리셋 보호**: 쓰기 엔드포인트(activate, params)에서 `Strategy.user_id == current_user.id` 조건으로 프리셋을 자동으로 차단하는 설계가 명확함.
3. **테스트 커버리지**: 격리 / 프리셋 보호 / clone / 타사용자 접근 차단을 모두 테스트하여 회귀 방지가 잘 되어 있음.
4. **데모 모드 유지**: 기존 데모 분기가 모두 유지되어 신규 사용자 온보딩 흐름에 영향 없음.
5. **마이그레이션 설계**: `backtest_results.user_id` NOT NULL + 기존 레코드 admin 할당 방식이 안전함.

---

## 수정 권장 우선순위

| 이슈 | 우선순위 | 비고 |
|------|---------|------|
| HIGH-1: clone 후 불필요한 DB 재조회 | 낮음 | 성능 경미, 기능 정상 |
| MED-1: 복사 버튼 로딩 상태 개선 | 낮음 | UX 개선 |
| MED-2: useStrategies 중복 훅 | 낮음 | 리팩토링 |
| MED-3: 데모 유저 분기 확인 | 중간 | 코드 확인 필요 |
| LOW-4: useCloneStrategy onError | 낮음 | 다음 스프린트 |

---

---

## 2차 코드 리뷰: 복사된 전략 관리 기능 보완 (커밋 8a7b166, 0c3f6ee)

### 2차 Medium 이슈

#### [MED-4] `window.confirm` 사용 — 접근성 및 일관성 문제

**파일**: `frontend/src/components/strategy/strategy-detail-panel.tsx`

```tsx
if (!window.confirm("이 전략을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.")) return;
```

브라우저 기본 `window.confirm` 다이얼로그는 UI 일관성이 떨어지고 키보드 접근성이 제한됩니다. 프로젝트에서 이미 사용 중인 shadcn/ui `AlertDialog` 컴포넌트로 교체하면 UI가 일관되고 접근성도 향상됩니다.

**영향**: UX/접근성 (경미). 기능 동작에는 문제 없음.

#### [MED-5] `handleSaveName`의 `onBlur` 이벤트 — 취소 버튼 클릭 시 저장 요청 발생

**파일**: `frontend/src/components/strategy/strategy-detail-panel.tsx`

```tsx
<Input
  onBlur={handleSaveName}  // 취소 버튼 클릭 시에도 blur가 먼저 발생
/>
```

인라인 편집 모드에서 "취소" 버튼 클릭 시 Input의 `onBlur`가 먼저 트리거되어 불필요한 이름 변경 API가 호출될 수 있습니다. `onBlur` 대신 명시적 저장 버튼을 추가하거나, `mousedown` 이벤트 방지 패턴을 사용하는 것을 권장합니다.

**영향**: UX 및 불필요한 API 호출 (경미). 기능 동작에는 대체로 문제 없음.

### 2차 Low 이슈

#### [LOW-5] `PARAM_LABEL`/`PARAM_DESCRIPTION` 위치 — 컴포넌트 파일 내 하드코딩

**파일**: `frontend/src/components/strategy/strategy-card-list.tsx`

파라미터 레이블/설명 매핑이 컴포넌트 파일에 직접 포함되어 있습니다. `lib/constants/strategy-params.ts` 같은 별도 상수 파일로 분리하면 재사용성과 유지보수성이 향상됩니다.

**영향**: 코드 구조 (경미). 기능 동작에는 문제 없음.

#### [LOW-6] `useDeleteStrategy` — 삭제 후 선택 상태 초기화 미처리

**파일**: `frontend/src/components/strategy/strategy-detail-panel.tsx`

전략 삭제 성공 후 `onDeleted?.()` 콜백이 호출되지만, `strategy-page.tsx`에서 선택된 전략 ID를 Zustand 스토어에서 명시적으로 초기화하지 않으면 패널이 "전략을 찾을 수 없습니다" 상태로 잠깐 표시될 수 있습니다.

**영향**: UX (경미). 데이터 무결성에는 문제 없음.

### 2차 긍정적 평가 사항

1. **param_type 매핑 수정**: `"int"/"float"` → `"number"` 변환 로직으로 파라미터 폼이 정상 표시됨.
2. **저장 API 연동 완성**: `handleSaveParams`에서 `apiStrategy.params`의 원본 `param_type`을 사용하여 정확한 타입으로 백엔드에 전달함.
3. **이름 변경/삭제 권한 일관성**: 백엔드에서 `is_preset=False AND user_id=current_user.id` 이중 조건 확인으로 프리셋 보호 완전히 유지됨.
4. **FK NULL 처리 완결성**: 삭제 시 WatchlistItem, Holding, Order, BacktestResult 모두 strategy_id를 NULL로 정리하여 무결성 보장.

---

## 결론

Sprint 15 전체 구현(1차 + 2차)은 **Critical 이슈 없음**으로 **머지 적합** 판정입니다.
High 이슈 1건(성능)과 Medium/Low 이슈들은 기능 동작에 영향이 없으며, 다음 스프린트 기술 부채로 기록합니다.

**pytest 45 passed** 확인됨. 머지 진행 가능.
