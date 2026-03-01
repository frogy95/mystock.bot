# Sprint 6 코드 리뷰 보고서

- **리뷰 대상 브랜치:** sprint6
- **리뷰 일시:** 2026-03-01
- **리뷰 범위:** Sprint 6 신규/수정 파일 11개

---

## 전체 평가

전반적으로 구조가 명확하고 책임이 잘 분리되어 있습니다. 추상 클래스를 활용한 전략 엔진 설계, Redis 캐싱 적용, 중복 주문 방지 등 핵심 패턴이 잘 구현되었습니다. 아래에 발견된 이슈를 심각도별로 정리합니다.

---

## Critical 이슈 (즉시 수정 필요)

없음.

---

## High 이슈 (조속한 수정 권장)

### H1. `order_executor.py`: flush 후 rollback 미처리

**파일:** `backend/app/services/order_executor.py`

`db.flush()`로 Order id를 생성한 뒤 KIS 호출 중 예외 발생 시 `await db.commit()`이 실행되어 `status="failed"` 주문이 DB에 저장됩니다. 이 자체는 의도된 동작이나, `db.flush()` 이후 `commit()` 직전에 앱이 강제 종료되면 트랜잭션이 자동 롤백되어 Order 레코드가 사라질 수 있습니다. 현재 MVP 범위에서는 허용 가능하나, 운영 전 `idempotency_key`(예: KIS 주문번호 기반) 도입을 권장합니다.

**권장 대응:** Sprint 7 안전장치 구현 시 멱등성 키 도입 계획에 포함.

### H2. `strategy_engine.py`: `evaluate_from_ohlcv`의 지표 계산 중복

**파일:** `backend/app/services/strategy_engine.py` (43~53행)

`evaluate_from_ohlcv()`가 `_calculate_indicators(df)`를 호출하여 전체 지표를 계산한 뒤, 각 전략의 `evaluate()` 내부에서도 `df_copy.ta.sma()` 등을 **다시** 계산합니다. 이로 인해 동일 지표가 두 번 계산되는 불필요한 연산이 발생합니다.

**권장 대응:** `evaluate_from_ohlcv()`에서 반환된 지표 DataFrame을 전략의 `evaluate()`에 그대로 전달하거나, `indicators.py`의 `_calculate_indicators` 결과를 재활용하도록 리팩토링.

---

## Medium 이슈 (다음 스프린트에서 개선 권장)

### M1. `scheduler.py`: 손절/익절 모니터링 스텁

`_run_risk_monitoring()`이 로그만 출력하고 실제 동작이 없습니다. Sprint 7에서 반드시 구현이 필요한 항목입니다.

### M2. `scheduler.py`: 주문 수량 하드코딩

`quantity=1`로 고정되어 있어 실제 투자금액 및 포트폴리오 비중을 반영하지 못합니다. Sprint 7 안전장치 구현 시 수량 계산 로직 추가 필요.

### M3. `indicators.py`: `vol_ratio_20` 컬럼 이름 방식

`df["VOL_RATIO_20"]`을 직접 할당하는 방식은 pandas-ta의 `append=True` 패턴과 혼용됩니다. 일관성을 위해 pandas-ta 커스텀 지표로 등록하거나, 별도 후처리 단계로 분리하는 것을 권장합니다.

### M4. `strategies.py`: N+1 쿼리 패턴

`list_strategies()`에서 전략마다 `StrategyParam`을 별도 쿼리로 조회합니다. 전략 수가 늘어나면 N+1 쿼리 문제가 발생할 수 있습니다. `selectinload` 또는 `joinedload`를 사용하여 한 번에 로드하도록 개선을 권장합니다.

### M5. `strategy_engine.py`: `params` dict 타입 강제 없음

전략 파라미터를 `float(params.get("rsi_threshold", 40))`으로 변환하고 있으나, `param_value`가 문자열로 들어올 경우 자동 변환됩니다. `StrategyParam.param_type` 필드를 활용하여 명시적 타입 변환을 권장합니다.

---

## Low 이슈 (선택적 개선)

### L1. `kis_client.py`: `acnt_prdt_cd` 분리 로직 반복

계좌번호에서 `cano`와 `acnt_prdt_cd`를 분리하는 코드가 `get_balance()`와 `place_order()`에 중복됩니다. 공통 메서드로 추출하면 코드 품질이 향상됩니다.

### L2. `use-strategy.ts`: 에러 핸들링 미구현

각 mutation의 `onError` 핸들러가 없어 API 오류 발생 시 사용자에게 피드백이 없습니다. Toast 알림 연동을 권장합니다.

### L3. `indicators.py`: pandas-ta ImportError 처리

`ImportError` 발생 시 빈 dict를 반환하는데, 호출 측에서 빈 dict를 처리하지 않으면 `KeyError`가 발생할 수 있습니다. 반환 타입에 `Optional`을 명시하거나 예외를 상위로 전파하는 것을 고려하세요.

---

## 긍정적 측면

- **추상 클래스 설계:** `BaseStrategy` + `evaluate()`/`evaluate_from_ohlcv()` 분리로 전략 확장이 용이합니다.
- **시뮬레이션 모드:** KIS API 미설정 시 `status="simulated"`로 처리하여 개발 환경에서도 동작합니다.
- **Redis 캐싱:** 5분 TTL로 불필요한 KIS API 호출을 최소화합니다.
- **STRATEGY_REGISTRY:** 전략 이름→인스턴스 딕셔너리로 동적 전략 선택이 깔끔합니다.
- **APScheduler lifespan 통합:** `start_scheduler()`/`stop_scheduler()`를 FastAPI lifespan에 연결하여 정상 종료가 보장됩니다.
- **중복 주문 방지:** 동일 종목+방향 미체결 주문 확인으로 중복 주문 위험을 줄입니다.

---

## 총평

Critical 이슈 없음. High 이슈 2건은 운영 전 해소가 권장되나 MVP 범위에서는 허용 가능합니다. Sprint 7에서 안전장치 구현 시 H1(멱등성 키), H2(지표 중복 계산), M2(수량 계산)를 함께 해소하면 좋습니다.
