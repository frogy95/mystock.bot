# Sprint 4 Playwright 검증 보고서

**검증 일시:** 2026-03-01
**검증 도구:** Playwright MCP
**검증 대상:** http://localhost:3001 (Next.js dev server)

---

## 검증 결과 요약

| 항목 | 결과 |
|------|------|
| 전략 설정 화면 렌더링 | 통과 |
| 전략 카드 클릭 후 상세 패널 표시 | 통과 |
| 백테스팅 설정 폼 렌더링 | 통과 |
| 백테스팅 실행 및 결과 표시 | 통과 |
| 주문 내역 화면 렌더링 | 통과 |
| 주문 상세 다이얼로그 | 통과 |
| 설정 화면 렌더링 | 통과 |
| 긴급 전체 매도 AlertDialog | 통과 |
| AlertDialog 취소 버튼 (닫힘) | 통과 |
| 모바일 375px 반응형 레이아웃 | 통과 |
| 콘솔 에러 | 0건 |

**전체 결과: 11/11 항목 통과**

---

## 시나리오별 상세 결과

### 1. 전략 설정 화면 (`/strategy`)

**결과: 통과**

- 프리셋 전략 3종 카드가 모두 렌더링됨
  - 골든크로스 + RSI (총 수익률 +8.50%, 승률 65.0%, 매매횟수 23회)
  - 볼린저 밴드 반전 (총 수익률 +12.10%, 승률 72.0%, 매매횟수 18회)
  - 가치 + 모멘텀 (총 수익률 +5.20%, 승률 58.0%, 매매횟수 12회)
- 전략 카드 클릭 시 상세 패널 정상 표시
  - 파라미터 슬라이더 (단기/장기 이동평균 기간, RSI 과매도 기준)
  - 숫자 입력 필드 (RSI 기간)
  - 종목 매핑 테이블 (005930, 000660, 051910)
- 활성화 토글 스위치 정상 동작

**스크린샷:**
- [전략 카드 목록](playwright-strategy-page.png)
- [전략 상세 패널](playwright-strategy-detail.png)

---

### 2. 백테스팅 화면 (`/backtest`)

**결과: 통과**

- 설정 폼 정상 렌더링 (전략 드롭다운, 종목코드 입력, 시작/종료일 날짜 입력)
- 전략 미선택 시 실행 버튼 비활성화 (disabled) 확인
- 전략 선택 후 종목/기간 입력 시 실행 버튼 활성화 확인
- 백테스팅 실행 (골든크로스+RSI, 005930, 2023-01-01 ~ 2025-12-31) 후 결과 표시
  - 총 수익률: 15.32%
  - 연환산 수익률: 22.48%
  - 최대 낙폭(MDD): -8.14%
  - 승률: 65.2%
  - 매매횟수: 23회
  - 샤프 지수: 1.42
  - 벤치마크(KOSPI) 대비: +7.47%
  - 수익 곡선 차트 (전략 수익 vs 벤치마크 비교 라인) 렌더링 확인

**스크린샷:**
- [백테스팅 설정 폼](playwright-backtest-form.png)
- [백테스팅 결과 대시보드](playwright-backtest-result.png)

---

### 3. 주문 내역 화면 (`/orders`)

**결과: 통과**

- 주문 목록 테이블 정상 렌더링 (10개 주문)
- 탭 표시 (전체 / 미체결 / 체결완료 / 취소)
- 필터 (매수/매도 드롭다운, 종목코드 검색)
- 미체결 주문에 취소 버튼 표시 확인 (카카오, 삼성SDI, LG전자)
- 주문 행 클릭 시 상세 다이얼로그 표시
  - 삼성전자 매수 체결완료 주문 클릭
  - 수량(100주), 가격(72,000원), 총액(7,200,000원) 표시
  - 전략명 (골든크로스 + RSI) 표시
  - 판단 근거: "SMA(20) > SMA(60) 골든크로스 발생, RSI(14) = 33.5 (과매도 회복 신호)"
  - 신뢰도 82% + Progress bar 표시

**스크린샷:**
- [주문 내역 테이블](playwright-orders-page.png)
- [주문 상세 다이얼로그](playwright-order-dialog.png)

---

### 4. 설정 화면 (`/settings`)

**결과: 통과**

- 자동매매 마스터 스위치 카드 표시 (현재: 중지됨)
- KIS API 설정 폼 렌더링 (App Key/Secret 마스킹, 투자 모드 라디오 버튼)
- 텔레그램 설정 폼 렌더링 (Bot Token, Chat ID, 알림 토글 3개)
- 매매 시간 설정 폼 렌더링 (시작/종료 시간, 마감 전 제외 슬라이더)
- 안전장치 설정 폼 렌더링 (손실 한도 3%, 최대 주문 10회, 종목 비중 20%, 손절률 5%)
- 긴급 전체 매도 버튼 클릭 시 AlertDialog 표시
  - 제목: "정말로 전체 매도하시겠습니까?"
  - 경고 문구: "모든 보유 종목을 현재가에 즉시 매도합니다. 이 작업은 되돌릴 수 없습니다."
  - 취소 / 전체 매도 실행 버튼
- 취소 클릭 시 다이얼로그 정상 닫힘

**스크린샷:**
- [설정 화면](playwright-settings-page.png)
- [긴급 매도 AlertDialog](playwright-emergency-sell-dialog.png)

---

### 5. 반응형 레이아웃 (375px 모바일)

**결과: 통과**

- 사이드바 숨김 처리 확인
- 헤더 좌측 햄버거 메뉴(≡) 버튼 표시 확인
- 전략 카드가 세로 스택 레이아웃으로 정상 렌더링

**스크린샷:**
- [모바일 375px 레이아웃](playwright-mobile-375px.png)

---

### 6. 콘솔 에러 검증

**결과: 통과 (에러 0건)**

- 검증된 페이지: /strategy, /backtest, /orders, /settings
- Error 레벨 메시지: 0건
- Warning 레벨 메시지: 2건 (shadcn/ui AlertDialog `aria-describedby` 접근성 힌트 — 기능에 영향 없음)
- VERBOSE 레벨: password field 접근성 힌트 2건 — App Key/Secret 필드 관련, 기능에 영향 없음

---

## 스크린샷 목록

| 파일명 | 설명 |
|--------|------|
| [playwright-strategy-page.png](playwright-strategy-page.png) | 전략 설정 화면 - 카드 3종 |
| [playwright-strategy-detail.png](playwright-strategy-detail.png) | 전략 상세 패널 - 파라미터/종목 매핑 |
| [playwright-backtest-form.png](playwright-backtest-form.png) | 백테스팅 설정 폼 |
| [playwright-backtest-result.png](playwright-backtest-result.png) | 백테스팅 결과 대시보드 + 차트 |
| [playwright-orders-page.png](playwright-orders-page.png) | 주문 내역 테이블 |
| [playwright-order-dialog.png](playwright-order-dialog.png) | 주문 상세 다이얼로그 |
| [playwright-settings-page.png](playwright-settings-page.png) | 설정 화면 전체 |
| [playwright-emergency-sell-dialog.png](playwright-emergency-sell-dialog.png) | 긴급 전체 매도 AlertDialog |
| [playwright-mobile-375px.png](playwright-mobile-375px.png) | 모바일 375px 반응형 레이아웃 |
