# Sprint 7 완료 문서

## 개요

- **스프린트:** Sprint 7 (Week 7)
- **Phase:** Phase 3 - 백엔드 핵심 기능 개발
- **목표:** 손절/익절 자동 관리, 매매 안전장치, 시스템 안전장치 구현 및 프론트엔드 연동
- **완료일:** 2026-03-01
- **브랜치:** sprint7
- **PR:** sprint7 → main

---

## 구현 내용

### 백엔드 신규 파일 (6개)

#### 1. `backend/app/services/risk_manager.py` - 손절/익절 엔진
- **고정비율 손절 (stop_loss_rate):** 매입가 대비 -N% 이하 시 매도 신호 생성
- **분할 익절:** take_profit_rate의 50% 도달 시 반량 매도, 100% 도달 시 전량 매도
- **트레일링 스탑:** Redis에 최고가 기록, 최고가 대비 -N% 하락 시 매도
- **ATR 기반 동적 손절:** ATR * N배를 손절 폭으로 사용
- `RiskSignal` 데이터클래스 및 `to_signal()` 변환 함수 제공

#### 2. `backend/app/services/safety_guard.py` - 매매 안전장치
- `is_auto_trade_enabled()` / `set_auto_trade()`: Redis+DB 연동 자동매매 ON/OFF
- `check_daily_loss_limit()`: DB 보유종목 기반 일일 손실 한도 체크
- `check_max_daily_orders()`: 오늘 주문 수 DB 조회 후 최대 횟수 비교
- `check_position_ratio()`: 단일 종목 포트폴리오 비중 체크
- `run_all_checks()`: 모든 안전장치 통합 실행
- `emergency_sell_all()`: 긴급 전체 시장가 매도 + 자동매매 비활성화

#### 3. `backend/app/services/system_monitor.py` - 시스템 안전장치
- `acquire_order_lock()`: Redis SET NX EX 패턴 분산 락 (중복 주문 방지)
- `record_error()` / `clear_errors()`: 에러 카운터 (Redis 기반)
- `check_error_threshold()`: 임계값 초과 시 자동매매 자동 중단
- `get_system_status()`: 시스템 상태 전체 조회

#### 4. `backend/app/api/v1/safety.py` - 안전장치 API
- `GET /api/v1/safety/status`: 자동매매 ON/OFF, 일일 손실, 주문 횟수, 시스템 에러 통합 상태
- `POST /api/v1/safety/auto-trade`: 자동매매 활성화/비활성화
- `POST /api/v1/safety/emergency-sell`: 긴급 전체 매도

#### 5. `backend/app/api/v1/system_settings.py` - 시스템 설정 CRUD API
- `GET /api/v1/system-settings`: 전체 설정 조회
- `PUT /api/v1/system-settings`: 일괄 업데이트
- `GET /api/v1/system-settings/{key}`: 단일 설정 조회

#### 6. `backend/app/api/v1/orders.py` - 주문 목록 API
- `GET /api/v1/orders`: 주문 목록 최신순 조회 (limit/offset 페이지네이션)

### 백엔드 수정 파일 (3개)

#### 7. `backend/app/services/order_executor.py` - 주문 실행 안전장치 통합
- 매수 주문 전 `safety_guard.run_all_checks()` 실행
- `system_monitor.acquire_order_lock()` 분산 락 적용 (중복 주문 방지)
- 안전장치 또는 락 획득 실패 시 주문 취소

#### 8. `backend/app/services/scheduler.py` - 손절/익절 스케줄 완성
- `risk_manager.check_all_positions()` 장중 1분 간격 실행
- 기존 전략 평가 (5분) + 손절/익절 모니터링 (1분) 이중 스케줄 구성

#### 9. `backend/app/api/v1/router.py` - 라우터 등록
- `safety`, `system_settings`, `orders` 라우터 추가 등록

### 프론트엔드 수정 파일 (2개)

#### 10. `frontend/src/hooks/use-settings.ts` - Mock → 실제 API 연동
- `useSystemSettings`: 시스템 설정 조회
- `useSafetyStatus`: 안전장치 상태 조회
- `useUpdateSettings`: 설정 일괄 업데이트 mutation
- `useToggleAutoTrade`: 자동매매 ON/OFF mutation
- `useEmergencySell`: 긴급 전체 매도 mutation

#### 11. `frontend/src/hooks/use-orders.ts` - Mock → 실제 API 연동
- `useOrders`: 실제 `/api/v1/orders` 엔드포인트 연동

---

## 검증 결과

- [Playwright 자동 검증 보고서](sprint7/playwright-report.md) — 11/11 통과
- [코드 리뷰 보고서](sprint7/code-review.md) — Critical/High 이슈 없음, Medium 4건
- [스크린샷 모음](sprint7/)

---

## 주요 기술 결정

| 항목 | 결정 사항 | 이유 |
|------|-----------|------|
| 트레일링 스탑 최고가 저장 | Redis (TTL 1일) | 빠른 읽기/쓰기, 장 마감 후 자동 초기화 |
| 분산 락 구현 | Redis SET NX EX | 단순하고 검증된 패턴, 타임아웃 자동 해제 |
| 안전장치 트리거 기준 | DB 조회 기반 | 정확성 우선 (Redis 캐시는 보조) |
| 매수 전용 안전장치 | 매수만 적용 | 매도(손절/익절)는 안전장치 없이 즉시 실행 필요 |

---

## 남은 기술 부채

- WebSocket 연결 끊김 시 자동 재연결 (Phase 4에서 처리)
- 텔레그램 알림 연동 미완료 (Sprint 9에서 처리)
- 대시보드 실시간 데이터 연동 미완료 (Sprint 9에서 처리)
