# Sprint 21: 전략/백테스트 버그 수정

## 기본 정보

| 항목 | 내용 |
|------|------|
| 스프린트 번호 | Sprint 21 |
| 완료일 | 2026-03-07 |
| 브랜치 | `sprint-21` |
| PR | develop 브랜치로 PR 생성 |
| Phase | Phase 13 |

## 스프린트 목표

전략 엔진의 한글 전략명 매핑 오류를 수정하고, 앱 시작 시 프리셋 전략을 자동 생성하며, 백테스트 폼에서 API 기반 전략 목록 및 종목 검색 Popover를 연동한다.

## 구현 내용

### 1. 전략 이름 매핑 수정 (`backend/app/services/strategy_engine.py`)

- `_NAME_TO_ENGINE` 딕셔너리 추가: DB 한글 전략명 → 레지스트리 영문 키 매핑
  - 예: `"이동평균 교차 전략"` → `"moving_average_crossover"`
- `get_strategy()` 함수 수정: 영문 키 직접 조회 실패 시 `_NAME_TO_ENGINE`을 통해 한글 이름으로 폴백 조회
- 기존 `scheduler.py`, `strategies.py`의 `get_strategy(strategy.name)` 호출이 자동으로 수정됨 (코드 변경 불필요)

### 2. 앱 시작 시 프리셋 전략 자동 생성 (`backend/app/main.py`)

- `_PRESET_STRATEGIES` 상수: 3개 프리셋 전략 정의
  - 이동평균 교차 전략 / RSI 전략 / MACD 전략
- `ensure_preset_strategies()` 함수: DB에 동일 이름 전략이 없으면 자동 생성 (admin 사용자 소유)
- lifespan에서 호출 추가: 앱 시작 시 자동 실행

### 3. 백테스트 폼 개선 (`frontend/src/components/backtest/backtest-config-form.tsx`)

- `mockStrategies` 하드코딩 제거 → `useStrategies()` 훅으로 API에서 전략 목록 가져오기
- 종목코드 직접 입력 → `useStockSearch()` 훅을 활용한 Popover 기반 종목 검색 UI
  - Command 컴포넌트로 실시간 검색
  - 선택 시 종목명 + 코드 표시

## 변경 파일

| 파일 | 유형 | 설명 |
|------|------|------|
| `backend/app/services/strategy_engine.py` | 수정 | `_NAME_TO_ENGINE` 매핑, `get_strategy()` 한글 이름 지원 |
| `backend/app/main.py` | 수정 | `ensure_preset_strategies()` 추가, lifespan 연동 |
| `frontend/src/components/backtest/backtest-config-form.tsx` | 수정 | API 전략 목록, 종목 검색 Popover 연동 |

## 자동 검증 결과

| 항목 | 결과 | 비고 |
|------|------|------|
| `pytest -v` | ✅ 51 passed | 기존 테스트 회귀 없음 |
| TypeScript 타입 검사 | ✅ 오류 없음 | `tsc --noEmit` |

## 수동 검증 항목 (사용자 직접 수행)

- ⬜ Docker 재빌드 후 앱 시작 시 프리셋 전략 3개 자동 생성 확인
  - `docker compose up --build` 후 백엔드 로그에서 `ensure_preset_strategies` 실행 확인
  - 전략 페이지에서 이동평균/RSI/MACD 전략 3개 표시 확인
- ⬜ 백테스트 페이지에서 API 전략 목록 표시 확인
  - 폼의 전략 선택 드롭다운에 DB 전략 목록이 나타나는지 확인
- ⬜ 종목 검색 Popover 동작 확인
  - 종목 검색 입력 시 Popover 열림 및 결과 목록 표시 확인
  - 종목 선택 후 폼에 반영 확인
- ⬜ 실서버에서 백테스트 실행 확인 (KIS API 필요)
  - 전략 선택 + 종목 선택 + 기간 입력 후 백테스트 실행 버튼 동작 확인

## 검증 결과

- [검증 보고서](sprint21/)
