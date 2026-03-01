# Sprint 6 완료 보고서

- **스프린트 번호:** Sprint 6
- **Phase:** Phase 3 - 백엔드 핵심 기능 개발
- **기간:** 2026-04-06 ~ 2026-04-11 (실제 완료: 2026-03-01)
- **브랜치:** sprint6
- **상태:** 완료

---

## 목표

전략 엔진과 자동매매 엔진을 구현한다.
pandas-ta 기반 기술적 지표 계산 서비스, 3종 프리셋 전략 엔진, KIS 주문 실행 서비스,
APScheduler 기반 장중 스케줄러를 구현하고 프론트엔드 hooks를 실제 API로 전환한다.

---

## 구현 내용

### 백엔드 신규 파일

#### 서비스 레이어
- `backend/app/services/indicators.py`: 기술적 지표 엔진
  - pandas-ta 기반 SMA(20/60), EMA(12/26), RSI(14), MACD, BB, ATR, 거래량비율 계산
  - Redis 5분 TTL 캐싱 (`indicators:{symbol}:{period}`)
  - `get_indicators(symbol)`: 비동기 API 연동 버전
  - `get_indicators_from_df(df)`: 백테스팅용 동기 버전

- `backend/app/services/strategy_engine.py`: 전략 엔진
  - `BaseStrategy`: 추상 기반 클래스 (`evaluate()`, `evaluate_from_ohlcv()`)
  - `Signal` 데이터클래스: signal_type, confidence, reason, target_price
  - `GoldenCrossRSIStrategy`: SMA(20)>SMA(60) AND RSI<40 AND 거래량>20일평균×1.5
  - `BollingerReversalStrategy`: 종가<BB하단 AND RSI<30
  - `ValueMomentumStrategy`: 20일 모멘텀>5% AND RSI<65
  - `STRATEGY_REGISTRY`: 전략 이름→인스턴스 딕셔너리

- `backend/app/services/order_executor.py`: 주문 실행 서비스
  - `execute_signal()`: Signal → KIS 주문 → DB 저장
  - 중복 주문 방지: 동일 종목+방향 미체결 주문 존재 시 스킵
  - KIS API 미설정 시 시뮬레이션 모드 (`status="simulated"`)
  - OrderLog에 판단 근거(reason, confidence) 저장

- `backend/app/services/scheduler.py`: APScheduler 스케줄러
  - `AsyncIOScheduler` 기반 싱글턴 스케줄러
  - 장중 매 5분(09:00~15:30, 월-금) 전략 평가 작업
  - 장중 매 1분 손절/익절 모니터링 (Sprint 7에서 구현 예정)
  - `start_scheduler()` / `stop_scheduler()` lifespan 훅 연결

#### Pydantic 스키마
- `backend/app/schemas/strategy.py`:
  - `StrategyParamResponse`, `StrategyParamUpdate`
  - `StrategyResponse`, `StrategyActivateRequest`
  - `StrategyParamBulkUpdate`, `StrategySignalResponse`

#### API 엔드포인트
- `backend/app/api/v1/strategies.py`:
  - `GET /api/v1/strategies`: 전략 목록 조회 (파라미터 포함)
  - `GET /api/v1/strategies/{id}`: 전략 상세 조회
  - `PUT /api/v1/strategies/{id}/activate`: 활성화/비활성화 토글
  - `PUT /api/v1/strategies/{id}/params`: 파라미터 일괄 업데이트
  - `POST /api/v1/strategies/{id}/evaluate/{symbol}`: 종목별 신호 평가

### 백엔드 수정 파일
- `backend/app/services/kis_client.py`:
  - `place_order()`: 매수/매도 주문 실행 (모의/실전 자동 선택)
  - `get_order_status()`: 주문 상태 조회
- `backend/app/main.py`: lifespan에 `start_scheduler()` / `stop_scheduler()` 추가
- `backend/app/api/v1/router.py`: `strategies` 라우터 등록
- `backend/requirements.txt`: `pandas>=2.0.0`, `pandas-ta>=0.3.14b`, `apscheduler>=3.10.0` 추가

### 프론트엔드
- `frontend/src/hooks/use-strategy.ts`: Mock 데이터 제거, 실제 API 전환
  - `useStrategies()`: `GET /api/v1/strategies` 조회
  - `useStrategy(id)`: `GET /api/v1/strategies/{id}` 조회
  - `useToggleStrategy()`: `PUT /api/v1/strategies/{id}/activate` mutation
  - `useUpdateStrategyParams()`: `PUT /api/v1/strategies/{id}/params` mutation
  - `useEvaluateSignal()`: `POST /api/v1/strategies/{id}/evaluate/{symbol}` mutation

---

## 주요 변경 파일 목록

| 파일 | 변경 유형 |
|------|-----------|
| `backend/app/services/indicators.py` | 신규 |
| `backend/app/services/strategy_engine.py` | 신규 |
| `backend/app/services/order_executor.py` | 신규 |
| `backend/app/services/scheduler.py` | 신규 |
| `backend/app/schemas/strategy.py` | 신규 |
| `backend/app/api/v1/strategies.py` | 신규 |
| `backend/app/services/kis_client.py` | 수정 |
| `backend/app/main.py` | 수정 |
| `backend/app/api/v1/router.py` | 수정 |
| `backend/requirements.txt` | 수정 |
| `frontend/src/hooks/use-strategy.ts` | 수정 |

---

## 검증 결과

- [코드 리뷰 보고서](sprint6/code-review.md)
- [Playwright 검증 보고서](sprint6/playwright-report.md)

---

## 사용자 직접 수행 필요 항목

Sprint 6 검증을 위해 아래 항목을 수행하세요. (`deploy.md` Section 11 참고)

1. Docker Compose 재빌드 (`pandas`, `pandas-ta`, `apscheduler` 신규 패키지 설치)
2. 백엔드 API 엔드포인트 동작 검증 (Swagger UI)
3. 전략 활성화 API 동작 확인
4. 프론트엔드 전략 화면 실제 API 연동 확인

---

## 다음 스프린트 (Sprint 7) 계획

- 손절/익절 자동 관리 (고정 비율, 트레일링 스톱, ATR 기반)
- 매매 안전장치 구현 (일일 손실 한도, 최대 주문 횟수, 종목별 최대 비중)
- 시스템 안전장치 (긴급 전체 매도 API, 중복 주문 Redis 락)
- 프론트엔드-백엔드 연동 (전략/주문 화면)
