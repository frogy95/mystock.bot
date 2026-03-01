# Sprint 4 코드 리뷰 보고서

**리뷰 대상:** PR #7 - feat: Sprint 4 완료 - 전략/백테스팅/주문/설정 화면 UI 구현
**리뷰 일시:** 2026-03-01
**리뷰어:** Claude Code (sprint-close agent)

---

## 요약

Sprint 4에서 추가된 25개 신규 파일을 전반적으로 검토한 결과, **Critical/High 이슈 없음**. Mock 데이터 기반 UI 구현으로서 코드 구조, 타입 안전성, 컴포넌트 설계 모두 양호하다.

---

## Critical 이슈 (0건)

없음.

---

## High 이슈 (0건)

없음.

---

## Medium 이슈 (3건)

### M-1. `use-strategy.ts` - TanStack Query와 Zustand 스토어 이중 관리

**파일:** `frontend/src/hooks/use-strategy.ts`, `frontend/src/stores/strategy-store.ts`

**현상:** 전략 데이터를 TanStack Query (`useStrategies`)와 Zustand 스토어 (`useStrategyStore.strategies`) 두 곳에서 각각 관리한다. TanStack Query는 서버 상태(데이터 페칭)를, Zustand는 클라이언트 상태(파라미터 편집, 토글 등 UI 인터랙션)를 담당하는 설계 의도는 이해되나, 현재 Mock 환경에서는 두 소스 간 동기화가 이루어지지 않는다.

**영향:** Mock 단계에서는 문제없으나, 백엔드 API 연동 시 TanStack Query 응답이 Zustand 스토어와 어긋날 수 있다.

**권고:** Sprint 5 API 연동 시 `useQuery`의 `onSuccess` 또는 `select`를 활용하여 서버 응답을 Zustand에 동기화하는 패턴을 도입하거나, Zustand를 클라이언트 전용 편집 상태로만 한정하고 서버 상태는 TanStack Query만 사용하도록 역할을 명확히 분리할 것을 권고.

---

### M-2. `settings/page.tsx` - 긴급 매도 핸들러 `console.log` 미완성

**파일:** `frontend/src/app/settings/page.tsx` (라인 14-17)

**현상:**
```typescript
const handleEmergencySell = () => {
  console.log("긴급 전체 매도 실행");
  // 실제 구현 시: 백엔드 API 호출
};
```

**영향:** 개발 환경에서는 문제없으나, 추후 실제 API 연동 시 누락될 위험이 있다. 또한 프로덕션 빌드에서 불필요한 `console.log`가 남을 수 있다.

**권고:** TODO 주석(`// TODO: Sprint 7 - 백엔드 긴급 매도 API 연동`)으로 변경하고, 프로덕션 빌드 시 `console.log`를 자동 제거하도록 `next.config` 설정 추가 검토.

---

### M-3. `backtest-equity-chart.tsx` - 범례 표시 방식 개선 여지

**파일:** `frontend/src/components/backtest/backtest-equity-chart.tsx`

**현상:** `Legend`와 `Tooltip` 모두 `value === "value"` 조건으로 문자열을 비교하여 한글 레이블을 표시한다. `dataKey`가 "value"라는 이름이 의미적으로 불명확하며, 추후 데이터 키 변경 시 하드코딩된 문자열도 함께 변경해야 한다.

**권고:** `dataKey`를 `"strategyReturn"` 또는 `"portfolioValue"` 등 의미 있는 이름으로 변경하고, 범례/툴팁 포맷터를 별도 상수(`CHART_LABELS`)로 분리하여 유지보수성 향상.

---

## Low 이슈 (2건)

### L-1. `format.ts` - `formatVolume`과 `formatKRWCompact` 유사 로직 중복

두 함수 모두 `>= 100_000_000`, `>= 10_000` 분기로 동일한 패턴을 사용한다. 공통 포맷 헬퍼로 추출하면 DRY 원칙을 더 잘 준수할 수 있다.

### L-2. 각 훅 파일에 `delay` 함수 중복 정의

`use-strategy.ts`, `use-backtest.ts`, `use-orders.ts`, `use-settings.ts` 네 파일 모두에 동일한 `delay` 함수가 각각 정의되어 있다. `lib/utils.ts` 또는 `lib/mock/index.ts`로 추출하면 중복을 제거할 수 있다.

---

## 긍정적 사항

1. **타입 안전성 우수:** `lib/mock/types.ts`에 10개 인터페이스가 명확하게 정의되어 있으며, 모든 컴포넌트와 훅에서 일관되게 사용됨.

2. **관심사 분리 명확:** Mock 데이터(`lib/mock/`), TanStack Query 훅(`hooks/`), Zustand 스토어(`stores/`), UI 컴포넌트(`components/`) 계층 구조가 체계적으로 분리됨.

3. **백엔드 연동 준비성:** `queryFn`을 Mock 함수로 구현하여 추후 실제 API 교체가 `queryFn` 내부 한 곳만 변경하면 되도록 설계됨.

4. **EmergencySellButton 안전 설계:** AlertDialog를 활용한 이중 확인 구조가 적절하게 구현됨. 취소/실행 버튼 색상 구분도 UX 관점에서 올바름.

5. **반응형 레이아웃:** `overflow-x-auto`, `sm/md/lg breakpoints` 활용으로 모바일/데스크톱 대응이 적절하게 구현됨.

---

## 결론

Sprint 4 코드는 Mock UI 구현 단계에서 **합격 수준**이다. Critical/High 이슈가 없으므로 PR 머지에 문제 없으며, Medium 이슈 3건은 Sprint 5 API 연동 시점에 함께 개선하는 것을 권고한다.
