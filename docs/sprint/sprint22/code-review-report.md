# Sprint 22 코드 리뷰 보고서

- **PR**: https://github.com/frogy95/mystock.bot/pull/45
- **브랜치**: sprint22 → develop
- **리뷰 일시**: 2026-03-08
- **대상 커밋**: a2711b2 (문서), 487b00c (구현)

## 리뷰 범위

| 파일 | 유형 |
|------|------|
| `backend/app/models/chart_cache.py` | 신규 |
| `backend/app/services/chart_data_service.py` | 신규 |
| `backend/app/services/backtest_engine.py` | 수정 |
| `backend/app/services/kis_client.py` | 수정 |

## Critical/High 이슈

없음.

## Medium 이슈

### M1: `_upsert_chart_data`에서 날짜 파싱 실패 시 경고 로그 없음
- **위치**: `chart_data_service.py` L160
- **내용**: `len(date_str) != 8`인 경우 `continue`로 건너뜨리나 경고 로그가 없음. 디버깅 시 파악 어려움.
- **권고**: 추후 개선 시 `logger.warning("날짜 형식 오류: %s", date_str)` 추가 고려.

### M2: `interval` 컬럼 없이 UniqueConstraint 구성
- **위치**: `chart_cache.py` L17-19
- **내용**: 현재 day 단위만 사용하므로 문제 없으나, 추후 week/month 데이터 추가 시 UniqueConstraint에 interval 컬럼 추가 필요.
- **권고**: 추후 다주기 데이터 지원 시 마이그레이션으로 처리.

### M3: `AsyncSessionLocal` 직접 생성 패턴
- **위치**: `chart_data_service.py` L34
- **내용**: `get_chart_data` 함수 내부에서 세션을 직접 생성. 테스트 격리가 어려울 수 있음.
- **권고**: 기존 프로젝트 패턴과 일관적이므로 현 단계에서 허용. 추후 DI 패턴 도입 시 개선.

## Low 이슈

없음.

## 긍정적 평가

- 3단계 폴백 전략(DB → KIS → yfinance)이 명확하게 구분됨
- 각 단계별 로그 메시지가 풍부하여 운영 시 추적 용이
- PostgreSQL UPSERT (`on_conflict_do_update`) 활용으로 중복 데이터 안전 처리
- `backtest_engine.py`에서 `chart_data_service` 호출부가 간결하고 명확함
- `kis_client.get_chart()` 예외 처리가 None 반환으로 통일되어 폴백 로직 단순화

## Playwright UI 검증 결과

| 시나리오 | 결과 |
|----------|------|
| 메인 페이지 렌더링 (`/`) | ✅ 통과 |
| 백테스트 페이지 렌더링 (`/backtest`) | ✅ 통과 |
| 전략 드롭다운 API 연동 (3개 전략 로드) | ✅ 통과 |

스크린샷:
- [backtest-page.png](backtest-page.png) — 백테스트 페이지 초기 상태
- [backtest-strategy-dropdown.png](backtest-strategy-dropdown.png) — 전략 드롭다운 (골든크로스+RSI, 가치+모멘텀, 볼린저밴드반전)

## 종합 판단

Critical/High 이슈 없음. 코드 품질 양호. Playwright UI 검증 3개 시나리오 모두 통과. Medium 이슈 3건은 즉각 수정 불필요하며 추후 개선 참고 자료로 기록.
