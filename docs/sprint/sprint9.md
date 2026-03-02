# Sprint 9 완료 문서

## 개요

- **스프린트:** Sprint 9 (Week 9)
- **Phase:** Phase 4 - 부가 기능 개발
- **목표:** 텔레그램 알림 시스템 완성, 실시간 WebSocket 체결 알림 UI, 대시보드 Mock → 실제 API 전환
- **완료일:** 2026-03-02
- **브랜치:** sprint9
- **PR:** https://github.com/frogy95/mystock.bot/pull/14

---

## 구현 내용 (7개 태스크)

### T1: 텔레그램 알림 ON/OFF 개별 설정

**파일:** `backend/app/services/telegram_notifier.py`

- `_is_notification_enabled(setting_key)` 비동기 함수 구현
- `system_settings` 테이블에서 알림 설정 키 조회 (DB 조회 실패 시 기본값 True 반환)
- 설정 키별 알림 활성 여부 확인 — "false", "0", "off" 값이면 비활성화
- 적용 알림 유형: `notify_order_executed`, `notify_risk_triggered`, `notify_system_error`, `notify_auto_trade_disabled`, `notify_strategy_signal`, `notify_daily_summary`

### T2: 전략 신호 발생 사전 알림

**파일:** `backend/app/services/telegram_notifier.py`, `backend/app/services/scheduler.py`

- `notify_strategy_signal()` 함수 구현
  - 매수(🟢)/매도(🔴) 신호, 종목코드, 전략명, 신뢰도, 근거, 목표가 Markdown 포맷 알림
- 스케줄러 전략 평가 로직(`_run_strategy_evaluation`)에서 신호 신뢰도 >= 0.5 시 `asyncio.create_task()`로 fire-and-forget 전송

### T3: 일일 매매 요약 API

**파일:** `backend/app/api/v1/orders.py`

- `GET /api/v1/orders/daily-summary` 엔드포인트 추가
- `DailySummaryResponse` Pydantic 스키마: date, total_buy_count, total_sell_count, total_buy_amount, total_sell_amount, orders
- date 파라미터 미입력 시 오늘 날짜 기준 집계

### T4: 전략별 성과 집계 API

**파일:** `backend/app/api/v1/strategies.py`

- `GET /api/v1/strategies/performance` 엔드포인트 추가
- `StrategyPerformanceResponse` Pydantic 스키마: id, name, trade_count, buy_count, sell_count, win_rate, active_stocks, is_active
- 각 전략별 주문 이력에서 매수/매도 건수, 승률 집계
- 관심종목(WatchlistItem)에서 전략 적용 종목 수 집계

### T5: 일일 포트폴리오 요약 알림 (크론 잡)

**파일:** `backend/app/services/scheduler.py`, `backend/app/services/telegram_notifier.py`

- `_run_daily_summary()` 비동기 함수 구현
  - `calculate_summary()`로 포트폴리오 평가금액, 손익, 손익률 조회
  - 오늘 매수/매도 주문 건수 집계 후 `notify_daily_portfolio_summary()` 호출
- APScheduler 크론 잡 등록: 평일(mon-fri) 16:00 KST (`Asia/Seoul` timezone)
- `notify_daily_portfolio_summary()` 함수: 📈/📉 이모지, 총 평가금액, 평가손익, 매수/매도 건수 Markdown 포맷

### T6: 대시보드 Mock → 실제 API 교체

**파일:** `frontend/src/hooks/use-dashboard.ts`, `backend/app/api/v1/stocks.py`

프론트엔드 훅 4개 교체:
- `useTradeSignals()`: Mock → `GET /api/v1/orders` (오늘 주문 필터링, refetchInterval 60초)
- `useOrderExecutions()`: Mock → `GET /api/v1/orders` (최근 10건, refetchInterval 60초)
- `useStrategyPerformances()`: Mock → `GET /api/v1/strategies/performance` (refetchInterval 120초)
- `useMarketIndices()`: Mock → `GET /api/v1/stocks/market-index` (refetchInterval 60초)

백엔드 신규 엔드포인트:
- `GET /api/v1/stocks/market-index`: KOSPI/KOSDAQ 지수 데이터 반환 (KIS API 또는 Mock 폴백)

### T7: 실시간 체결 알림 UI

**파일:** `frontend/src/hooks/use-realtime.ts`, `frontend/src/app/dashboard/page.tsx`, `frontend/src/app/layout.tsx`

- `useRealtimeNotification()` 훅: WebSocket(`/ws/realtime`) 연결, 체결 이벤트 수신
- sonner 토스트 라이브러리로 실시간 체결 알림 표시 (매수=초록, 매도=빨강)
- `layout.tsx`에 `<Toaster />` 컴포넌트 추가
- 대시보드 페이지에 `useRealtimeNotification()` 훅 연결

---

## 변경 파일 목록

| 파일 | 변경 유형 | 설명 |
|------|-----------|------|
| `backend/app/services/telegram_notifier.py` | 수정 | 알림 ON/OFF 설정, notify_strategy_signal, notify_daily_portfolio_summary 추가 |
| `backend/app/services/scheduler.py` | 수정 | 전략 신호 사전 알림, _run_daily_summary, 16:00 KST 크론 잡 추가 |
| `backend/app/api/v1/orders.py` | 수정 | GET /orders/daily-summary 엔드포인트 추가 |
| `backend/app/api/v1/strategies.py` | 수정 | GET /strategies/performance 엔드포인트 추가 |
| `backend/app/api/v1/stocks.py` | 수정 | GET /stocks/market-index 엔드포인트 추가 |
| `backend/app/services/kis_client.py` | 수정 | 시장 지수 조회 메서드 추가 |
| `backend/app/services/order_executor.py` | 수정 | 체결 시 WebSocket 브로드캐스트 연동 |
| `frontend/src/hooks/use-dashboard.ts` | 수정 | 4개 훅 Mock → 실제 API 교체 |
| `frontend/src/hooks/use-realtime.ts` | 신규 | WebSocket 실시간 체결 알림 훅 |
| `frontend/src/app/dashboard/page.tsx` | 수정 | useRealtimeNotification 훅 연결 |
| `frontend/src/app/layout.tsx` | 수정 | sonner Toaster 컴포넌트 추가 |

변경 통계: 11 files changed, 474 insertions(+), 22 deletions(-)

---

## 커밋 내역

| 커밋 해시 | 메시지 |
|-----------|--------|
| `d8db0b9` | feat: Sprint 9 - VectorBT 백테스팅 엔진 개선 및 텔레그램 알림 통합 |
| `288524b` | feat: Sprint 9 나머지 구현 - 알림 설정, 전략 신호, 대시보드 API 연동, 토스트 알림 |

---

## 주요 기술 결정

| 항목 | 결정 사항 | 이유 |
|------|-----------|------|
| 알림 ON/OFF 저장 위치 | system_settings 테이블 | 기존 설정 인프라 재활용, 별도 테이블 불필요 |
| 전략 신호 알림 방식 | asyncio.create_task() (fire-and-forget) | 알림 실패가 주문 실행을 블로킹하지 않도록 |
| 일일 요약 전송 시각 | 평일 16:00 KST | 장 마감(15:30) 후 30분 여유 두어 주문 정산 완료 후 전송 |
| 대시보드 API 교체 전략 | useTradeSignals, useOrderExecutions는 /orders 공유 | 신규 엔드포인트 최소화, 기존 API 재활용 |
| WebSocket 토스트 라이브러리 | sonner | shadcn/ui 공식 권장, 간결한 API |
| market-index 폴백 | KIS API 실패 시 Mock 데이터 반환 | 개발/모의 환경에서도 대시보드 정상 렌더링 보장 |

---

## API 명세 (신규)

### GET /api/v1/orders/daily-summary

쿼리 파라미터: `date` (YYYY-MM-DD, 선택, 기본값: 오늘)

응답:
```json
{
  "date": "2026-03-02",
  "total_buy_count": 3,
  "total_sell_count": 1,
  "total_buy_amount": 15000000.0,
  "total_sell_amount": 5200000.0,
  "orders": [...]
}
```

### GET /api/v1/strategies/performance

응답:
```json
[
  {
    "id": 1,
    "name": "GoldenCrossRSI",
    "trade_count": 12,
    "buy_count": 6,
    "sell_count": 6,
    "win_rate": 50.0,
    "active_stocks": 3,
    "is_active": true
  }
]
```

### GET /api/v1/stocks/market-index

응답:
```json
[
  {
    "index_code": "0001",
    "name": "KOSPI",
    "current_value": 2650.5,
    "change_value": 12.3,
    "change_rate": 0.47
  },
  {
    "index_code": "1001",
    "name": "KOSDAQ",
    "current_value": 870.2,
    "change_value": -3.1,
    "change_rate": -0.35
  }
]
```

---

## 검증 결과

- [Playwright 테스트 보고서](sprint9/playwright-report.md)
- [스크린샷 모음](sprint9/)

---

## 남은 기술 부채

- 시장 지수 데이터는 KIS API가 설정되어야 실제 값 반환 (미설정 시 Mock 데이터 폴백)
- WebSocket 재연결 로직 — use-realtime.ts에서 기본 retry 3회 구현, 지수 백오프 미적용
- 전략 성과의 `totalReturn`은 백테스팅 결과 연동 시 실제 값으로 교체 필요 (현재 0 반환)
- Sprint 10 (Phase 5): 통합 테스트, 안정화, MVP 출시 준비
