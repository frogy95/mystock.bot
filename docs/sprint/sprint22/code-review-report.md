# Sprint 22 코드 리뷰 보고서

- **PR**: https://github.com/frogy95/mystock.bot/pull/45
- **브랜치**: sprint22 → develop
- **리뷰 일시**: 2026-03-08
- **대상 커밋**: 487b00c ~ 33d727b (전체 9개 커밋)

## 리뷰 범위

| 파일 | 유형 |
|------|------|
| `backend/app/models/chart_cache.py` | 신규 |
| `backend/alembic/versions/e5f6a7b8c9d0_chart_data_cache_테이블_추가.py` | 신규 |
| `backend/app/services/chart_data_service.py` | 신규 |
| `backend/app/services/backtest_engine.py` | 수정 |
| `backend/app/services/backtest_metrics.py` | 수정 |
| `backend/app/services/kis_client.py` | 수정 |
| `backend/app/schemas/backtest.py` | 수정 |
| `backend/app/api/v1/backtest.py` | 수정 |
| `frontend/src/hooks/use-backtest.ts` | 수정 |
| `frontend/src/lib/mock/types.ts` | 수정 |
| `frontend/src/app/backtest/page.tsx` | 수정 |
| `frontend/src/components/backtest/backtest-equity-chart.tsx` | 수정 |
| `frontend/src/components/backtest/backtest-trades-table.tsx` | 신규 |

## Critical/High 이슈

없음.

## Medium 이슈

### M1: `_upsert_chart_data`에서 날짜 파싱 실패 시 경고 로그 없음
- **위치**: `chart_data_service.py` L169
- **내용**: `len(date_str) != 8`인 경우 `continue`로 건너뛰나 경고 로그가 없음. 디버깅 시 파악 어려움.
- **권고**: 추후 개선 시 `logger.warning("날짜 형식 오류: %s", date_str)` 추가 고려.

### M2: `interval` 컬럼 없이 UniqueConstraint 구성
- **위치**: `chart_cache.py` L17-19
- **내용**: 현재 day 단위만 사용하므로 문제 없으나, 추후 week/month 데이터 추가 시 UniqueConstraint에 interval 컬럼 추가 필요.
- **권고**: 추후 다주기 데이터 지원 시 마이그레이션으로 처리.

### M3: `AsyncSessionLocal` 직접 생성 패턴
- **위치**: `chart_data_service.py` L34
- **내용**: `get_chart_data` 함수 내부에서 세션을 직접 생성. 테스트 격리가 어려울 수 있음.
- **권고**: 기존 프로젝트 패턴과 일관적이므로 현 단계에서 허용. 추후 DI 패턴 도입 시 개선.

### M4: `_build_stock_buyhold_values` 엣지 케이스 — `bfill` 후에도 NaN 가능성
- **위치**: `backtest_metrics.py` L88
- **내용**: `reindex` + `ffill` + `bfill` 조합으로 대부분의 날짜 불일치를 처리하나, 조회 구간 전체가 장 휴일인 극단적 케이스에서 모든 값이 NaN일 수 있음. 이 경우 `ValueError`를 raise하여 fallback(`[initial_cash] * len(dates)`)으로 처리하므로 실용적으로 안전함.
- **권고**: 현재 구현으로 충분. 추후 단위 테스트 케이스 추가 고려.

### M5: `_extract_vbt_trades` f-string 로깅 패턴
- **위치**: `backtest_metrics.py` L77
- **내용**: `logger.warning(f"...")` 형태 사용. 프로젝트 전반이 f-string 로깅을 혼용하고 있어 일관성 이슈가 있음. 성능에는 영향 없음.
- **권고**: 추후 `%s` 형식 통일 시 일괄 수정.

### M6: `backtest-trades-table.tsx`에서 `trade.id`가 index 기반
- **위치**: `frontend/src/app/backtest/page.tsx` L37
- **내용**: `id: String(i)` 형태로 배열 인덱스를 key로 사용. 거래 내역이 동적으로 재정렬되지 않으므로 실용적 문제는 없으나 React key 안정성 관점에서 개선 가능.
- **권고**: 향후 거래 내역 정렬/필터 기능 추가 시 고유 ID 생성 로직 도입 고려.

## Low 이슈

없음.

## 긍정적 평가

- 3단계 폴백 전략(DB 캐시 → KIS API → yfinance)이 명확하게 구분되어 있고 각 단계별 로그 메시지가 풍부함
- PostgreSQL UPSERT (`on_conflict_do_update`) 활용으로 중복 데이터 안전 처리
- `_build_stock_buyhold_values`, `_build_benchmark_values` 모두 예외 발생 시 fallback 값 반환으로 안정성 확보
- `_to_response()` 함수에서 `stock_buyhold` 누락 버그를 `ep.get("stock_buyhold", 0.0)`로 방어적으로 처리
- 프론트엔드 타입 흐름(`BacktestResultAPI` → `BacktestResult` → 각 컴포넌트 props)이 명확하고 일관성 있음
- `backtest-equity-chart.tsx`의 만원 단위 변환 로직(`v / 10000`)이 Y축, 툴팁 모두 일관되게 적용됨
- `backtest-trades-table.tsx`의 overflow-x 처리로 모바일 호환성 고려

## Playwright UI 검증 결과

| 시나리오 | 결과 |
|----------|------|
| 로그인 페이지 렌더링 (`/login`) | ✅ 통과 |
| 로그인 후 대시보드 이동 | ✅ 통과 |
| 백테스트 페이지 렌더링 (`/backtest`) | ✅ 통과 |
| 전략 드롭다운 API 연동 (3개 전략 로드) | ✅ 통과 |

스크린샷:
- [playwright-login-page.png](playwright-login-page.png) — 로그인 페이지
- [playwright-backtest-page.png](playwright-backtest-page.png) — 백테스트 페이지 초기 상태
- [playwright-backtest-strategy-dropdown.png](playwright-backtest-strategy-dropdown.png) — 전략 드롭다운 (골든크로스+RSI, 가치+모멘텀, 볼린저밴드반전)

## 종합 판단

Critical/High 이슈 없음. 코드 품질 양호. Playwright UI 검증 4개 시나리오 모두 통과. Medium 이슈 6건은 즉각 수정 불필요하며 추후 개선 참고 자료로 기록.
