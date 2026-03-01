# Sprint 5 코드 리뷰 보고서

- **검토 일자:** 2026-03-01
- **검토 대상:** sprint5 브랜치 (22개 파일 변경, 1131 라인 추가)
- **검토 범위:** 백엔드 API/모델/서비스/스키마, 프론트엔드 hooks

---

## 전체 평가

Sprint 5 구현은 전반적으로 아키텍처 설계가 일관되고 코드 품질이 양호합니다.
비동기 처리, 의존성 주입, 타입 안전성이 잘 지켜지고 있습니다.

---

## Critical 이슈 (즉시 수정 필요)

없음.

---

## High 이슈 (중요 개선 사항)

### H1. stock_master.py: 전체 List 메모리 로드로 인한 대용량 검색 성능 저하

**파일:** `backend/app/services/stock_master.py` (88-93번 라인)

```python
# 현재 코드
raw_list = await redis.lrange(STOCK_MASTER_KEY, 0, -1)
for raw in raw_list:
    item = json.loads(raw)
    if q in item["symbol"].lower() or q in item["name"].lower():
```

**문제:** Redis List에서 전체 데이터를 파이썬 메모리로 로드 후 선형 탐색합니다.
KOSPI(2,700종목) + KOSDAQ(1,700종목) 약 4,400건이므로 현재 규모에서는 큰 문제가 없으나,
데이터 증가 시 성능 저하 가능성이 있습니다.

**개선 방안:** Sprint 6 이후 Redis Hash + 검색 인덱스(RedisSearch) 또는 정렬된 Set으로 전환을 검토할 것을 권장합니다. 현재 규모(4,400건)에서는 허용 범위입니다.

---

## Medium 이슈 (추후 개선 권장)

### M1. watchlist.py, holdings.py: _get_user_id 헬퍼 함수 중복

**파일:** `backend/app/api/v1/watchlist.py`, `backend/app/api/v1/holdings.py`

두 파일 모두 동일한 `_get_user_id` 헬퍼 함수를 각자 정의하고 있습니다.
공통 의존성 모듈(`app.core.dependencies`)로 추출하여 재사용하는 것을 권장합니다.

### M2. holding.py 모델: created_at 타임스탬프 컬럼 누락

**파일:** `backend/app/models/holding.py`

다른 테이블(WatchlistItem 등)과 달리 `created_at` 컬럼이 없습니다.
`Base` 클래스에 공통 타임스탬프 믹스인(created_at, updated_at)을 적용하는 것을 검토하세요.

### M3. use-portfolio.ts: HoldingAPI 타입 중복 export 위험

**파일:** `frontend/src/hooks/use-portfolio.ts`, `frontend/src/hooks/use-holdings-mutations.ts`

`use-holdings-mutations.ts`에서 `use-portfolio.ts`의 `HoldingAPI`를 import하고 있습니다.
이 패턴은 순환 의존성 위험은 없으나, 타입을 별도 `types/api.ts`로 분리하는 것을 Sprint 6에서 고려하세요.

### M4. WatchlistGroupResponse: items 지연 로드 전략 확인 필요

**파일:** `backend/app/models/watchlist.py` (30-35번 라인)

```python
items: Mapped[List[WatchlistItem]] = relationship(
    "WatchlistItem",
    lazy="selectin",
)
```

`lazy="selectin"` 은 그룹 조회 시 항상 items를 함께 로드합니다.
그룹이 많고 항목이 많은 경우 N+1 문제 없이 처리되지만, 대용량에서는 별도 쿼리로 분리를 검토하세요.

### M5. calculate_summary 함수: KIS API 호출이 동기 요약 계산에 포함

**파일:** `backend/app/services/holding_service.py` (108-115번 라인)

포트폴리오 요약 계산 중 예수금 조회를 위해 KIS API를 호출합니다.
KIS API 지연 시 요약 응답 전체가 느려질 수 있습니다.
예수금을 별도 캐시(Redis, TTL 1분)에 저장하는 방식을 Sprint 6 이후 도입하는 것을 권장합니다.

---

## Low 이슈 (코드 품질 개선)

### L1. search_stocks 함수: 빈 캐시 시 fallback 없음

**파일:** `backend/app/services/stock_master.py` (81-84번 라인)

Redis 캐시가 없을 때 빈 배열을 반환하며 로그만 남깁니다.
개발 환경에서 Redis가 연결되어 있지만 캐시가 만료된 경우, 자동 재로드를 트리거하는 로직 추가를 권장합니다.

### L2. 에러 메시지 일관성

Holdings API에서 에러 메시지가 한국어이나, 일부 서비스 레이어에서 영어 메시지가 혼용됩니다.
전체적으로 한국어로 통일하는 것을 권장합니다.

---

## 긍정적 평가

1. **비동기 처리 일관성:** 모든 DB 쿼리와 Redis 작업이 `async/await`로 올바르게 처리됩니다.
2. **소유권 검증:** 모든 CRUD 엔드포인트에서 `user_id` 기반 소유권 검증이 일관되게 구현됩니다.
3. **Cascade 삭제:** `WatchlistGroup` 삭제 시 `WatchlistItem`이 자동으로 삭제되도록 올바르게 설정되었습니다.
4. **computed_field 활용:** `HoldingResponse`에서 `profit_loss`, `profit_loss_rate`, `total_value`를 computed_field로 계산하여 DB 컬럼 없이 동적 반환합니다.
5. **KIS 데이터 보존:** `sync_with_kis` 함수에서 기존의 `stop_loss_rate`, `take_profit_rate`, `sell_strategy_id` 값을 KIS 동기화 시 보존합니다.
6. **Graceful Fallback:** `load_stock_master` 실패 시 서버 시작에 영향을 주지 않도록 try/except로 처리됩니다.
7. **TanStack Query 캐시 무효화:** mutation 성공 후 관련 쿼리 키를 올바르게 무효화합니다.
8. **TypeScript 타입 안전성:** 프론트엔드 hooks에서 백엔드 응답 스키마와 일치하는 TypeScript 인터페이스가 정의됩니다.

---

## 결론

Sprint 5 구현은 Critical/High 이슈 없이 배포 가능한 수준입니다.
Medium 이슈들은 Sprint 6 이후 기술 부채로 등록하여 개선할 것을 권장합니다.
특히 `_get_user_id` 헬퍼 중복(M1)과 `calculate_summary` KIS API 호출(M5)은
Sprint 6 리팩토링 시 우선 처리를 권장합니다.
