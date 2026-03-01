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
