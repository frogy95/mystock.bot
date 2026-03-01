# Sprint 3: 핵심 화면 UI 구현

**기간:** 2026-03-01
**브랜치:** `sprint3`
**Phase:** Phase 2 - 프론트엔드 UI 개발

---

## 목표

Mock 데이터 기반으로 대시보드, 관심종목, 포트폴리오 3개 핵심 화면 UI를 완성하여 Phase 2에 진입한다.

---

## 완료된 작업

### Task 0: 환경 준비
- `sprint3` 브랜치 생성
- `lightweight-charts@5.1.0`, `recharts` 설치
- shadcn/ui 추가 컴포넌트 15개 설치 (table, badge, tabs, dialog, select, dropdown-menu, popover, command, scroll-area, tooltip, skeleton, switch, slider, progress, avatar)
- `frontend/src/lib/mock/` 디렉토리 생성

### Task 1: Mock 데이터 정의
- `frontend/src/lib/mock/types.ts` - 공통 타입 (Stock, StockQuote, HoldingItem, PortfolioSummary, TradeSignal, OrderExecution, StrategyPerformance, MarketIndex, WatchlistGroup, WatchlistItem)
- `frontend/src/lib/mock/dashboard.ts` - 대시보드 Mock 데이터
- `frontend/src/lib/mock/watchlist.ts` - 관심종목 Mock 데이터 (3개 그룹, 12개 검색 가능 종목)
- `frontend/src/lib/mock/portfolio.ts` - 포트폴리오 파이차트 Mock 데이터
- `frontend/src/lib/mock/index.ts` - barrel export

### Task 2: 포맷 유틸리티 및 공통 컴포넌트
- `frontend/src/lib/format.ts` - formatKRW, formatKRWCompact, formatPercent, formatChange, formatVolume, formatDateTime, formatTime
- `frontend/src/components/common/price-change-badge.tsx` - 등락률 뱃지 (상승=빨강, 하락=파랑)
- `frontend/src/components/common/stat-card.tsx` - 통계 카드
- `frontend/src/components/common/loading-skeleton.tsx` - 로딩 스켈레톤

### Task 3~5: 대시보드 핵심 컴포넌트
- `frontend/src/hooks/use-dashboard.ts` - TanStack Query Mock queryFn 훅 6개
- `frontend/src/components/dashboard/portfolio-summary.tsx` - 총 평가금액/일일 손익/총 평가손익/예수금 4개 StatCard
- `frontend/src/components/dashboard/holdings-table.tsx` - 7열 보유종목 테이블
- `frontend/src/components/dashboard/trade-signals.tsx` - 매매 신호 카드 (매수=빨강/매도=파랑)
- `frontend/src/components/dashboard/order-timeline.tsx` - 주문 실행 타임라인 (체결/대기/취소)
- `frontend/src/components/dashboard/strategy-performance.tsx` - 전략별 성과 카드 (승률 Progress bar)

### Task 6: 지수 미니 차트
- `frontend/src/components/dashboard/market-index-chart.tsx` - Lightweight Charts v5 Area 미니 차트 (SSR 회피: `"use client"` + `useEffect` 내 초기화)
- **주의:** v5에서 `addAreaSeries()` → `addSeries(AreaSeries, options)` API 변경 대응

### Task 7: 관심종목 화면
- `frontend/src/stores/watchlist-store.ts` - zustand 스토어 (그룹/종목 CRUD)
- `frontend/src/hooks/use-watchlist.ts` - 종목 검색 훅
- `frontend/src/components/watchlist/stock-search.tsx` - 종목 검색 (Popover + 결과 드롭다운)
- `frontend/src/components/watchlist/watchlist-group-tabs.tsx` - 그룹 탭 + 종목 테이블 + 전략 할당
- `frontend/src/app/watchlist/page.tsx` - 관심종목 페이지

### Task 8: 포트폴리오 화면
- `frontend/src/hooks/use-portfolio.ts` - 포트폴리오 Mock 훅
- `frontend/src/components/portfolio/portfolio-holdings-table.tsx` - 10열 테이블 (인라인 손절/익절/전략 편집)
- `frontend/src/components/portfolio/portfolio-pie-chart.tsx` - Recharts 도넛 파이차트 + 범례

### Task 9: 반응형 레이아웃
- `frontend/src/stores/sidebar-store.ts` - 사이드바 상태 zustand 스토어
- `frontend/src/components/layout/app-sidebar.tsx` - 모바일: 오버레이 + 슬라이드인, 데스크톱: 항상 표시
- `frontend/src/components/layout/app-header.tsx` - 모바일 햄버거 버튼 (md:hidden)

---

## 기술적 결정 및 이슈

### Lightweight Charts v5 API 변경
- 계획 당시 v4 기준으로 `addAreaSeries()` 사용 예정
- 실제 설치 시 v5.1.0이 설치되어 `addAreaSeries()` deprecated → `addSeries(AreaSeries, options)` 방식으로 수정

### Mock-first 패턴
- TanStack Query의 `queryFn`을 Mock 함수로 구현 (300~700ms 지연 시뮬레이션)
- 추후 Phase 3에서 Mock 함수를 실제 API 클라이언트 호출로 교체

### 한국 주식 관례
- 상승=빨간색, 하락=파란색 (`PriceChangeBadge`, `TradeSignals` 등 전역 적용)

---

## 빌드 검증

```
✓ Compiled successfully in 1667.9ms
✓ TypeScript 타입 에러 없음
✓ 10개 라우트 정적 페이지 생성
```

---

## 파일 구조 (신규 생성)

```
frontend/src/
├── lib/
│   ├── mock/
│   │   ├── types.ts
│   │   ├── dashboard.ts
│   │   ├── watchlist.ts
│   │   ├── portfolio.ts
│   │   └── index.ts
│   └── format.ts
├── hooks/
│   ├── use-dashboard.ts
│   ├── use-watchlist.ts
│   └── use-portfolio.ts
├── stores/
│   ├── watchlist-store.ts
│   └── sidebar-store.ts
└── components/
    ├── common/
    │   ├── price-change-badge.tsx
    │   ├── stat-card.tsx
    │   └── loading-skeleton.tsx
    ├── dashboard/
    │   ├── portfolio-summary.tsx
    │   ├── holdings-table.tsx
    │   ├── trade-signals.tsx
    │   ├── order-timeline.tsx
    │   ├── strategy-performance.tsx
    │   └── market-index-chart.tsx
    ├── watchlist/
    │   ├── stock-search.tsx
    │   └── watchlist-group-tabs.tsx
    └── portfolio/
        ├── portfolio-holdings-table.tsx
        └── portfolio-pie-chart.tsx
```

---

## 검증 보고서

- [Sprint 3 Playwright MCP 테스트 보고서](sprint3/sprint3-test-report.md)

---

## 다음 Sprint (Sprint 4) 예정 작업

- 전략 설정 화면 UI (파라미터 슬라이더, 활성화 토글, 종목-전략 매핑)
- 백테스팅 화면 UI (기간 선택, 결과 차트, 거래 내역)
- 주문 내역 화면 UI (미체결/체결 탭, 필터)
- 설정 화면 UI (API 키, 자동매매 토글, 긴급 전체 매도)
