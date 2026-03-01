# Sprint 4 완료 보고서

**기간:** 2026-03-23 ~ 2026-03-28 (계획) / 실제 완료: 2026-03-01
**Phase:** Phase 2 - 프론트엔드 UI 개발
**브랜치:** `sprint4` → `main`
**상태:** 완료

---

## 스프린트 개요

Sprint 4는 Phase 2의 두 번째 스프린트로, Sprint 3에서 구현한 대시보드/관심종목/포트폴리오 화면에 이어 전략 설정, 백테스팅, 주문 내역, 시스템 설정 화면을 Mock 데이터 기반으로 구현했다. 이로써 프론트엔드 6개 전체 화면의 UI 구현이 완료되었으며, Phase 2 목표를 달성했다.

### 핵심 목표

- 전략 설정 화면 UI (프리셋 3종, 파라미터 편집, 종목-전략 매핑)
- 백테스팅 화면 UI (설정 폼, 수익 곡선 차트, 성과 지표 카드, 거래 내역)
- 주문 내역 화면 UI (미체결/체결 탭, 필터, 주문 상세 다이얼로그)
- 설정 화면 UI (KIS API, 텔레그램, 매매 시간, 안전장치, 긴급 매도)

---

## 구현된 기능 목록

### 전략 설정 화면 (`/strategy`)

- 프리셋 전략 3종 카드 표시
  - 골든크로스 + RSI 복합 전략
  - 가치 + 모멘텀 하이브리드 전략
  - 볼린저 밴드 반전 전략
- 전략 활성화/비활성화 Toggle 스위치
- 전략 상세 파라미터 조절 폼 (슬라이더, 숫자 입력)
- 종목-전략 매핑 테이블 (어떤 종목에 어떤 전략 적용 중인지)
- 전략 카드 클릭 시 상세 패널 사이드 표시

### 백테스팅 화면 (`/backtest`)

- 전략 선택 드롭다운
- 종목 선택 (멀티 셀렉트, 최대 5개)
- 기간 설정 (시작일/종료일 날짜 입력)
- 백테스팅 실행 버튼 및 로딩 상태 시뮬레이션 (2초)
- 결과 대시보드 (Mock 데이터)
  - 총 수익률, CAGR, MDD, 샤프비율, 승률 지표 카드
  - 수익 곡선 차트 (Recharts AreaChart, 벤치마크 비교 오버레이)
  - 거래 내역 테이블 (진입/청산 가격, 수익률, 전략명)

### 주문 내역 화면 (`/orders`)

- 미체결 / 체결 완료 탭 전환
- 날짜, 종목, 매수/매도 필터
- 주문 테이블 (전략명, 판단 근거 포함)
- 주문 상세 다이얼로그 (클릭 시 팝업)
- 수동 주문 취소 버튼 (미체결 탭)

### 설정 화면 (`/settings`)

- 한국투자증권 API 키 등록 폼 (appkey, appsecret, 계좌번호)
- 모의투자/실전투자 환경 전환 라디오 버튼
- 텔레그램 봇 토큰 및 Chat ID 설정 폼
- 매매 시간 설정 (시작/종료 시각)
- 안전장치 설정
  - 일일 최대 손실 한도 (금액)
  - 일일 최대 주문 횟수
  - 단일 종목 최대 투자 비중 (%)
- 자동매매 마스터 ON/OFF 스위치
- 긴급 전체 매도 버튼 (AlertDialog 확인 모달 포함)

---

## 파일 구조

```
frontend/
├── lib/
│   ├── mock/
│   │   ├── strategy.ts          # 전략 Mock 데이터
│   │   ├── backtest.ts          # 백테스팅 Mock 데이터
│   │   ├── orders.ts            # 주문 내역 Mock 데이터
│   │   └── settings.ts          # 설정 Mock 데이터
│   ├── types.ts                 # 10개 타입 추가
│   │   # StrategyParam, StrategyDetail, BacktestResult
│   │   # BacktestTrade, OrderDetail, KisApiConfig
│   │   # TelegramConfig, TradingTimeConfig, SafetyConfig, SystemSettings
│   └── format.ts                # 유틸리티 함수 (포맷 헬퍼)
├── hooks/
│   ├── use-strategy.ts          # 전략 TanStack Query 훅
│   ├── use-backtest.ts          # 백테스팅 TanStack Query 훅
│   ├── use-orders.ts            # 주문 TanStack Query 훅
│   └── use-settings.ts          # 설정 TanStack Query 훅
├── stores/
│   ├── strategy-store.ts        # 전략 Zustand 스토어
│   ├── backtest-store.ts        # 백테스팅 Zustand 스토어
│   ├── orders-store.ts          # 주문 Zustand 스토어
│   └── settings-store.ts        # 설정 Zustand 스토어
├── components/
│   ├── strategy/
│   │   ├── strategy-card.tsx            # 전략 카드 단일 컴포넌트
│   │   ├── strategy-card-list.tsx       # 전략 카드 목록
│   │   ├── strategy-param-form.tsx      # 파라미터 편집 폼
│   │   ├── strategy-stock-mapping.tsx   # 종목-전략 매핑 테이블
│   │   └── strategy-detail-panel.tsx    # 전략 상세 패널
│   ├── backtest/
│   │   ├── backtest-config-form.tsx     # 백테스팅 설정 폼
│   │   ├── backtest-result-cards.tsx    # 성과 지표 카드
│   │   ├── backtest-equity-chart.tsx    # 수익 곡선 차트
│   │   └── backtest-trades-table.tsx    # 거래 내역 테이블
│   ├── orders/
│   │   ├── orders-filter.tsx            # 주문 필터 컴포넌트
│   │   ├── orders-table.tsx             # 주문 테이블
│   │   └── order-detail-dialog.tsx      # 주문 상세 다이얼로그
│   └── settings/
│       ├── kis-api-form.tsx             # KIS API 설정 폼
│       ├── telegram-form.tsx            # 텔레그램 설정 폼
│       ├── trading-time-form.tsx        # 매매 시간 설정 폼
│       ├── safety-settings-form.tsx     # 안전장치 설정 폼
│       ├── auto-trade-control.tsx       # 자동매매 ON/OFF 스위치
│       └── emergency-sell-button.tsx    # 긴급 전체 매도 버튼
├── app/
│   ├── strategy/page.tsx        # 전략 설정 페이지
│   ├── backtest/page.tsx        # 백테스팅 페이지
│   ├── orders/page.tsx          # 주문 내역 페이지
│   └── settings/page.tsx        # 설정 페이지
```

### 추가된 shadcn/ui 컴포넌트

- `alert-dialog` - 긴급 매도 확인 모달
- `sonner` - Toast 알림
- `toggle` - 활성화 토글
- `radio-group` - 환경 전환 라디오
- `textarea` - 텍스트 입력
- `accordion` - 설정 섹션 아코디언

---

## 완료 기준 달성 여부

| 완료 기준 | 달성 여부 |
|-----------|-----------|
| 모든 화면이 Mock 데이터로 정상 렌더링됨 | 완료 |
| 사이드바 네비게이션으로 모든 페이지 이동 가능 | 완료 |
| 반응형 레이아웃 모바일(375px) 정상 동작 | 완료 |
| 반응형 레이아웃 데스크톱(1920px) 정상 동작 | 완료 |
| 폼 입력/버튼 클릭 UI 피드백 구현 | 완료 |
| 차트 컴포넌트 Mock 데이터 렌더링 | 완료 |
| TypeScript 빌드 에러 0개 | 완료 |
| 콘솔 에러 없음 | 완료 (VERBOSE 접근성 힌트만 존재) |
| AlertDialog (긴급 매도 모달) 동작 | 완료 |

---

## 커밋 이력

| 커밋 해시 | 내용 |
|-----------|------|
| `a7a894b` | chore: sprint4 브랜치 생성 및 shadcn/ui 컴포넌트 추가 |
| `cc4f64c` | feat: Sprint 4 Task 1 - Mock 데이터 및 타입 정의 추가 |
| `422dc96` | feat: 전략 zustand 스토어 및 TanStack Query 훅 구현 |
| `763f2a0` | feat: 전략 카드 목록 컴포넌트 구현 (Task 3) |
| `e7c95f2` | feat: 전략 파라미터 편집 및 종목-전략 매핑 컴포넌트 추가 |
| `d594d57` | feat: Task 5 - 전략 페이지 조립 |
| `85142fd` | feat: Task 6 백테스팅 컴포넌트 구현 |
| `4b00416` | feat: 백테스팅 페이지 조립 (Task 7) |
| `fab08ac` | feat: Task 8 - 주문 내역 화면 구현 |
| `248faf3` | feat: Task 9 설정 화면 구현 |
| `91446e3` | feat: 반응형 레이아웃 보강 및 format.ts 유틸리티 함수 추가 |

---

## 검증 결과

> Playwright MCP 자동 검증 완료 (2026-03-01) — 11/11 항목 통과, 콘솔 에러 0건

- [Playwright 검증 보고서](sprint4/playwright-report.md)
- [코드 리뷰 보고서](sprint4/code-review-report.md)
- [스크린샷 모음](sprint4/)

| 검증 항목 | 결과 |
|-----------|------|
| 전략 설정 화면 렌더링 | 통과 |
| 전략 카드 클릭 → 상세 패널 | 통과 |
| 백테스팅 실행 및 결과 차트 | 통과 |
| 주문 내역 테이블 + 상세 다이얼로그 | 통과 |
| 설정 화면 + 긴급 매도 AlertDialog | 통과 |
| 모바일 375px 반응형 레이아웃 | 통과 |
| 콘솔 에러 | 0건 |

---

---

# Sprint 4.1 완료 보고서

**기간:** 2026-03-01 (Sprint 4 완료 후 즉시 진행)
**Phase:** Phase 2 - 프론트엔드 UI 개발 (마무리)
**브랜치:** `sprint4` (Sprint 4와 동일 브랜치)
**PR:** https://github.com/frogy95/mystock.bot/pull/8
**상태:** 완료 (2026-03-01)

---

## 스프린트 개요

Sprint 4.1은 Sprint 4에서 Could Have로 분류되어 미완성이었던 커스텀 전략 빌더 UI를 구현했다. 이로써 Phase 2 프론트엔드 UI 개발이 완전히 완료되었다.

### 핵심 목표

- 커스텀 전략 타입 시스템 설계
- 지표 메타데이터 정의 (8종 지표)
- Zustand persist 스토어 구현
- AND/OR 조건 조합 빌더 UI
- 지표별 동적 파라미터 렌더링
- 전략 미리보기 텍스트 자동 변환

---

## 구현된 기능 목록

### 타입 정의 (`/frontend/src/lib/mock/custom-strategy-types.ts`)

- `IndicatorId`: SMA / EMA / RSI / MACD / BB / ATR / VOLUME_RATIO / PRICE 8종
- `ComparisonOperator`: `>` / `>=` / `<` / `<=` / CROSS_ABOVE / CROSS_BELOW
- `LogicOperator`: AND / OR
- `Operand`: 지표 피연산자 또는 고정값 피연산자 유니온 타입
- `ConditionRow`: 조건 행 (좌측 피연산자, 비교 연산자, 우측 피연산자)
- `ConditionGroup`: 조건 그룹 (조건 행 목록 + 논리 연산자 목록)
- `CustomStrategy`: 커스텀 전략 전체 구조

### 지표 메타데이터 (`/frontend/src/lib/mock/indicator-definitions.ts`)

- 8종 지표별 레이블, 파라미터 스키마, 미리보기 텍스트 생성 함수
- 지표별 파라미터: SMA/EMA(period), RSI(period), MACD(fast/slow/signal), BB(period/stdDev), ATR(period), VOLUME_RATIO(period), PRICE(고정)

### Zustand persist 스토어 (`/frontend/src/stores/custom-strategy-store.ts`)

- `strategies`: 커스텀 전략 목록
- `selectedStrategyId`: 선택된 전략 ID
- `addStrategy(name)`: 새 전략 생성 및 자동 선택
- `removeStrategy(id)`: 전략 삭제
- `duplicateStrategy(id)`: 전략 복제 (딥 카피, 조건 ID 재생성)
- `toggleActive(id)`: 활성화 토글
- `addCondition(strategyId, section)`: 매수/매도 조건 행 추가
- `removeCondition(strategyId, section, conditionId)`: 조건 행 삭제 (logicOperators 인덱스 정합성 유지)
- `updateCondition(...)`: 조건 행 수정
- `toggleLogicOperator(strategyId, section, index)`: AND ↔ OR 토글
- localStorage persist (키: `custom-strategies`)

### 조건 행 편집기 (`/frontend/src/components/strategy/condition-row-editor.tsx`)

- 좌측 피연산자 지표 선택 드롭다운 (8종)
- 지표 선택 시 파라미터 입력 필드 동적 렌더링
- 비교 연산자 선택 드롭다운 (6종)
- 우측 피연산자 (지표 또는 고정값 전환 가능)
- 조건 행 삭제 버튼

### 조건 섹션 (`/frontend/src/components/strategy/condition-section.tsx`)

- 매수/매도 섹션 분리 표시
- 조건 행 사이 AND/OR 토글 버튼
- 조건 추가 버튼

### 전략 편집기 (`/frontend/src/components/strategy/custom-strategy-editor.tsx`)

- 전략 이름/설명 인라인 편집
- 매수 조건 섹션 + 매도 조건 섹션

### 전략 미리보기 (`/frontend/src/components/strategy/strategy-preview.tsx`)

- 조건 구조를 자연어 텍스트로 자동 변환
- 매수/매도 조건 섹션 분리 표시
- 조건이 없는 경우 안내 메시지 표시

### 전략 목록 (`/frontend/src/components/strategy/custom-strategy-list.tsx`)

- 커스텀 전략 카드 목록
- 생성/삭제/복제/활성화 토글 기능
- 빈 상태(empty state) 안내 표시

### 커스텀 전략 빌더 진입점

- `custom-strategy-builder.tsx`: 전략 목록 + 편집기 레이아웃 통합
- `strategy/page.tsx`: 프리셋 탭 / 커스텀 탭 전환 구조 추가

---

## 파일 구조 (신규 추가)

```
frontend/src/
├── lib/mock/
│   ├── custom-strategy-types.ts    # 커스텀 전략 타입 정의
│   ├── indicator-definitions.ts    # 지표 메타데이터 (8종)
│   └── index.ts                    # 타입 재내보내기 추가
├── stores/
│   └── custom-strategy-store.ts    # Zustand persist 스토어
└── components/strategy/
    ├── condition-row-editor.tsx     # 조건 행 편집기
    ├── condition-section.tsx        # 조건 섹션 (AND/OR 토글)
    ├── custom-strategy-builder.tsx  # 빌더 레이아웃 통합
    ├── custom-strategy-editor.tsx   # 전략 편집기
    ├── custom-strategy-list.tsx     # 전략 목록
    └── strategy-preview.tsx         # 전략 미리보기
```

**수정된 파일:**
- `frontend/src/app/strategy/page.tsx` - 프리셋/커스텀 탭 구조 추가
- `frontend/src/lib/mock/index.ts` - 신규 타입 재내보내기

---

## 완료 기준 달성 여부

| 완료 기준 | 달성 여부 |
|-----------|-----------|
| 지표 선택 드롭다운 (8종 지표) | 완료 |
| AND/OR 조건 조합 빌더 | 완료 |
| 파라미터 입력 필드 (동적 렌더링) | 완료 |
| 전략 미리보기 (텍스트 요약) | 완료 |
| 전략 저장/불러오기 (localStorage persist) | 완료 |
| TypeScript 빌드 에러 0개 (`tsc --noEmit`) | 완료 |
| 빌드 성공 (`npm run build`) | 완료 |
| Playwright UI 검증 | 완료 |

---

## 커밋 이력

| 커밋 해시 | 내용 |
|-----------|------|
| `dcd401e` | feat: Sprint 4.1 커스텀 전략 빌더 UI 구현 |

---

## 검증 결과

- [Sprint 4.1 Playwright 검증 보고서](sprint4.1/playwright-report.md)
- [Sprint 4.1 코드 리뷰 보고서](sprint4.1/code-review-report.md)

| 검증 항목 | 결과 |
|-----------|------|
| 커스텀 전략 탭 전환 | 통과 |
| 전략 생성 및 편집기 표시 | 통과 |
| 조건 행 추가/삭제 | 통과 |
| AND/OR 토글 동작 | 통과 |
| 전략 미리보기 업데이트 | 통과 |
| TypeScript 컴파일 에러 | 0건 |
| 빌드 성공 | 통과 |

---

## 다음 단계 (Sprint 5)

**Phase 3: 백엔드 핵심 기능 개발 - 관심종목/보유종목 API 연동**

Sprint 5에서는 Mock 데이터를 실제 백엔드 API와 연동한다.

### 주요 작업 목록

1. **종목 검색 API** - `GET /api/v1/stocks/search?q={query}`
   - 한국투자증권 API를 통한 종목 검색
   - Redis 캐싱 (TTL 1일)
2. **관심종목 CRUD API** - `/api/v1/watchlist/...`
   - 관심종목 그룹 생성/조회/수정/삭제
   - 종목별 전략 할당
3. **보유종목 동기화 API** - `/api/v1/portfolio/...`
   - 한국투자증권 잔고 조회 연동
   - 실시간 수익률 계산
4. **프론트엔드-백엔드 연동**
   - Mock 데이터를 실제 API 호출로 교체
   - TanStack Query queryFn 업데이트
   - 에러 핸들링 UI (토스트 알림)
   - 로딩 스켈레톤 UI

### 기술적 고려사항

- TanStack Query의 `queryFn`을 Mock 함수에서 실제 API 클라이언트로 교체하는 방식으로 연동
- API Rate Limit (모의투자: 초당 5건) 준수를 위한 Redis 캐싱 전략 수립
- Docker Compose 환경에서 프론트엔드 → 백엔드 API 호출 경로 확인
