# Sprint 4.1 코드 리뷰 보고서

**리뷰 대상:** PR #8 - feat: Sprint 4.1 커스텀 전략 빌더 UI
**리뷰 일시:** 2026-03-01
**커밋:** `dcd401e`
**리뷰어:** sprint-close agent (자동 코드 리뷰)

---

## 리뷰 요약

| 항목 | 결과 |
|------|------|
| Critical 이슈 | 0건 |
| High 이슈 | 1건 |
| Medium 이슈 | 3건 |
| Low 이슈 | 4건 |
| 긍정적 사항 | 6건 |

---

## Critical 이슈 (없음)

Critical 수준의 이슈는 발견되지 않았습니다.

---

## High 이슈

### H-1. MACD 우변 온체인지 핸들러 미구현 (`condition-row-editor.tsx` 라인 224-225)

```tsx
// 현재 코드: onValueChange가 빈 함수
<Select
  value="0"
  onValueChange={() => {}}
>
```

**문제:** MACD 우변이 고정값 0 또는 시그널선으로 제한되는 것은 설계 의도이나, `onValueChange`에 빈 함수를 넣어 경고를 억제하는 방식은 Select 컴포넌트의 접근성(aria)과 UX 측면에서 혼란을 줄 수 있습니다. `disabled` 또는 read-only 처리가 더 명확합니다.

**권장 수정:** Select를 `disabled` 상태로 렌더링하거나, 단순 텍스트(Badge/Label)로 표시하는 것이 낫습니다.

**영향 범위:** Medium (기능 동작에는 문제 없음, UX 개선 필요)

---

## Medium 이슈

### M-1. 타입 단언(as) 사용 (`condition-row-editor.tsx` 라인 78)

```tsx
operator: op as ConditionRow["operator"],
```

**문제:** `handleOperatorChange` 함수에서 Select onValueChange의 `string` 타입을 `ConditionRow["operator"]`로 단언합니다. 잘못된 값이 들어올 경우 런타임 에러 없이 타입 불일치가 발생할 수 있습니다.

**권장 수정:** 지원하는 연산자 배열에서 값을 검증하는 가드 함수를 추가하거나, zod 스키마를 활용하세요.

```typescript
const VALID_OPERATORS: ComparisonOperator[] = [">", ">=", "<", "<=", "CROSS_ABOVE", "CROSS_BELOW"];
function isValidOperator(op: string): op is ComparisonOperator {
  return VALID_OPERATORS.includes(op as ComparisonOperator);
}
```

### M-2. `getIndicatorById` 예외 처리 범위 (`indicator-definitions.ts` 라인 191-194)

```typescript
export function getIndicatorById(id: IndicatorId): IndicatorDefinition {
  const def = INDICATOR_DEFINITIONS.find((d) => d.id === id);
  if (!def) throw new Error(`Unknown indicator: ${id}`);
  return def;
}
```

**문제:** `IndicatorId` 타입이 엄격하게 정의되어 있어 런타임에서 에러가 발생할 가능성은 낮으나, `localStorage`에서 역직렬화된 구버전 데이터가 존재할 경우 앱 전체가 크래시될 수 있습니다. persist 스토어에서 버전 마이그레이션을 고려해야 합니다.

**권장 수정:** Zustand persist의 `version`과 `migrate` 옵션을 활용하거나, `getIndicatorById` 호출 전 유효성 검사를 추가하세요.

### M-3. 조건 행의 input 요소가 shadcn/ui Input이 아닌 네이티브 input 혼용 (`custom-strategy-list.tsx` 라인 47-55)

```tsx
<input
  autoFocus
  type="text"
  value={newName}
  ...
  className="flex-1 h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
/>
```

**문제:** 프로젝트 전반적으로 shadcn/ui 컴포넌트를 사용하는데, 전략 이름 입력 부분에서만 네이티브 `<input>`을 사용하고 클래스명을 수동으로 입력합니다. 다크 모드 전환이나 테마 변경 시 불일치가 발생할 수 있습니다.

**권장 수정:** shadcn/ui의 `<Input>` 컴포넌트로 교체하세요.

---

## Low 이슈

### L-1. `strategy-preview.tsx`에서 이모지 사용

```tsx
<p className="text-xs font-semibold text-green-600 dark:text-green-400">
  📈 매수 조건
</p>
```

**문제:** 이모지는 스크린 리더에서 예상치 못한 방식으로 읽힐 수 있습니다. 프로젝트 코딩 스타일 가이드에서 이모지 사용이 명시적으로 금지되어 있지 않지만, 일관성을 위해 아이콘 컴포넌트(TrendingUp, TrendingDown 등)로 교체하는 것을 권장합니다.

### L-2. `condition-row-editor.tsx`의 불필요한 중복 타입 체크 (라인 293-297)

```tsx
{condition.rightOperand.type === "indicator" &&
  getIndicatorById(condition.rightOperand.indicator).params.map((paramDef) => {
    const val =
      condition.rightOperand.type === "indicator"  // 이미 위에서 체크됨
        ? (condition.rightOperand.params[paramDef.key] ?? paramDef.defaultValue)
        : paramDef.defaultValue;
```

**문제:** 외부 조건에서 이미 `condition.rightOperand.type === "indicator"`를 체크했음에도 내부에서 다시 동일한 체크를 합니다. TypeScript 타입 좁히기(narrowing)가 올바르게 작동한다면 내부 체크가 불필요합니다.

### L-3. `custom-strategy-store.ts`에서 `"use client"` 지시어 위치

**문제:** `"use client"` 지시어가 스토어 파일 최상단에 있습니다. Zustand 스토어는 일반적으로 클라이언트 컴포넌트에서만 임포트되지만, 스토어 파일 자체에 `"use client"`를 선언하는 것은 Next.js App Router에서 약간의 번들 사이즈 증가를 유발할 수 있습니다. 이 패턴은 프로젝트 전반적으로 일관되게 사용 중이므로 현재는 Low 우선순위입니다.

### L-4. `condition-section.tsx`에서 Badge 클릭 이벤트 접근성

```tsx
<Badge
  variant={...}
  className="cursor-pointer select-none hover:opacity-80 transition-opacity px-4"
  onClick={() => toggleLogicOperator(strategyId, section, i - 1)}
  title="클릭하여 AND/OR 전환"
>
```

**문제:** Badge는 버튼처럼 동작하나 시멘틱하게 버튼이 아닙니다. 키보드 접근성(Enter/Space 키 이벤트)과 `role="button"` 또는 `aria-pressed` 속성이 누락되어 있습니다.

---

## 긍정적 사항

1. **타입 안전성 우수:** `ConditionRow`, `Operand`, `ConditionGroup` 등 복잡한 유니온 타입을 명확하게 정의하여 컴파일 타임에 대부분의 오류를 잡을 수 있습니다.

2. **Zustand persist 구현 견고성:** `removeCondition` 에서 `logicOperators` 배열 인덱스 정합성을 꼼꼼하게 처리했습니다 (첫 번째 조건 삭제와 그 이외 삭제를 구분).

3. **지표 메타데이터 분리:** `indicator-definitions.ts`에 지표 메타데이터를 중앙집중식으로 관리하여 새 지표 추가 시 단일 파일만 수정하면 됩니다. 확장성이 좋습니다.

4. **사용자 경험:** 조건이 없는 경우 빈 상태(empty state) 안내 메시지, 전략 생성 시 자동 선택, Enter 키로 전략 추가, Escape 키로 취소 등 세밀한 UX 처리가 잘 되어 있습니다.

5. **전략 복제 시 딥 카피:** `duplicateStrategy`에서 조건 행 ID를 `crypto.randomUUID()`로 재생성하여 참조 공유 문제를 방지했습니다.

6. **전략 미리보기의 포매팅:** `formatConditionGroup`이 순수 함수로 구현되어 테스트 작성이 용이합니다.

---

## 결론 및 권장 사항

High 이슈 1건(MACD onValueChange 빈 함수)은 기능 동작에는 영향이 없으나 접근성 개선을 위해 추후 수정을 권장합니다.

Medium 이슈 중 M-2 (persist 스토어 버전 마이그레이션)는 향후 타입 확장 시 문제가 될 수 있으므로 Sprint 5에서 `migrate` 옵션 추가를 권장합니다.

나머지 이슈는 현 MVP 단계에서 허용 가능한 수준이며, Phase 3 이후 리팩토링 시 개선 참고 자료로 활용합니다.

**전반적으로 코드 품질은 양호하며 PR 머지를 진행해도 무방합니다.**
