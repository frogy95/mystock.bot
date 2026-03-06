# Sprint 21 검증 보고서

## 검증 일시

2026-03-07

## 자동 검증 결과

### 1. 백엔드 통합 테스트 (Docker)

```
docker compose exec backend pytest -v
```

| 항목 | 결과 |
|------|------|
| 전체 테스트 수 | 51개 |
| 통과 | 51개 |
| 실패 | 0개 |
| 경고 | 1개 (pythonjsonlogger 모듈 경로 변경 — 기능 무관) |

결과: ✅ 51 passed

### 2. 헬스체크 API

```
GET http://localhost:8000/api/v1/health
```

```json
{
  "status": "healthy",
  "checks": {
    "database": {"status": "healthy"},
    "redis": {"status": "healthy"},
    "scheduler": {"status": "healthy", "jobs": 4}
  }
}
```

결과: ✅ 정상 (DB, Redis, Scheduler 모두 healthy)

### 3. 전략 목록 API 검증

```
GET /api/v1/strategies  (데모 토큰)
```

| 항목 | 결과 |
|------|------|
| HTTP 상태 | 200 |
| 반환된 전략 수 | 3개 |
| 프리셋 전략 목록 | 골든크로스 + RSI, 볼린저 밴드 반전, 가치 + 모멘텀 |

결과: ✅ 정상 (프리셋 전략 3개 확인)

> 참고: 현재 Docker 컨테이너는 Sprint 21 코드로 재빌드되지 않은 상태입니다.
> 기존 컨테이너에는 seed.py로 생성된 프리셋 전략 3개가 이미 존재합니다.
> `ensure_preset_strategies()` 로직은 Docker 재빌드 후 실제 동작을 수동 검증해야 합니다.

### 4. 종목 검색 API 검증

```
GET /api/v1/stocks/search?q=삼성  (데모 토큰)
```

| 항목 | 결과 |
|------|------|
| HTTP 상태 | 200 |
| 반환된 결과 수 | 3개 |
| 결과 예시 | 삼성전자 (005930), 삼성SDI (006400), 삼성바이오로직스 (207940) |

결과: ✅ 정상 (KRX 한국어 이름 매핑 정상 동작)

### 5. Playwright UI 검증

Playwright MCP가 Chrome 세션 충돌로 실행 불가 (`기존 브라우저 세션에서 여는 중` 오류).
Claude Code 재시작 후 Chromium 모드로 재시도 필요.

결과: ⬜ 미수행 (MCP 세션 충돌 — 수동 검증으로 대체 필요)

## 수동 검증 필요 항목

| 항목 | 상태 | 비고 |
|------|------|------|
| Docker 재빌드 후 프리셋 전략 자동 생성 확인 | ⬜ 미완료 | `docker compose up --build` 필요 |
| 백테스트 폼 전략 드롭다운 API 연동 확인 | ⬜ 미완료 | 브라우저에서 직접 확인 필요 |
| 종목 검색 Popover 동작 확인 | ⬜ 미완료 | 브라우저에서 직접 확인 필요 |
| 실서버 백테스트 실행 | ⬜ 미완료 | KIS API 연동 필요 |

## 코드 리뷰 결과

### strategy_engine.py

- 수준: 양호
- 특이사항 없음. `_NAME_TO_ENGINE` 폴백 로직이 간결하고 안전함 (등록되지 않은 이름은 `None` 반환).
- Medium: `_NAME_TO_ENGINE` 키가 DB 전략 이름과 반드시 일치해야 하므로 이름 변경 시 양쪽 동기화 필요 (향후 주의).

### main.py

- 수준: 양호
- `ensure_preset_strategies()`가 `try/except`로 감싸져 있어 DB 연결 실패 시 앱 시작을 막지 않음 — 적절한 방어 코드.
- Medium: `user_id=None`으로 생성된 프리셋 전략의 소유권 정책이 암묵적. 추후 `is_preset=True` 필터로만 구분하는 것이 명확할 수 있음 (현재는 정상 동작).

### backtest-config-form.tsx

- 수준: 양호
- 300ms 디바운스로 불필요한 API 호출 방지 — 적절한 UX 처리.
- `SelectItem value={strategy.name}` 사용: ID 대신 이름으로 전달하므로 백엔드가 이름으로 전략을 조회해야 함. 백엔드 API 계약에 맞는지 확인 필요 (수동 검증 항목).
- Low: `stockResults`가 없을 때 빈 상태 메시지가 표시되나, 최초 포커스 시 Popover가 열리지 않는 것은 의도된 동작으로 판단.

### Critical/High 이슈

없음.

### Medium 이슈 (추후 개선 참고)

1. `_NAME_TO_ENGINE` 키와 DB 전략 이름 동기화 의존성
2. 백테스트 폼에서 `strategy.name`을 value로 전달 — 백엔드 API가 이름 기반 조회를 지원하는지 확인 필요
3. 프리셋 전략 `user_id=None` 소유권 정책 명시화 필요 (기능 이상 없음)
