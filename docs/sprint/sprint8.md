# Sprint 8 완료 문서

## 개요

- **스프린트:** Sprint 8 (Week 8)
- **Phase:** Phase 4 - 부가 기능 개발
- **목표:** VectorBT 백테스팅 엔진 구현, 백테스팅 결과 API 제공, 프론트엔드 실제 API 연동
- **완료일:** 2026-03-01
- **브랜치:** sprint8
- **PR:** sprint8 → main

---

## 구현 내용

### 백엔드 신규 파일 (4개)

#### 1. `backend/app/services/backtest_engine.py` - 백테스팅 엔진

- `BacktestConfig` 데이터클래스: 백테스팅 설정 (symbol, strategy_name, params, start_date, end_date, initial_cash, commission)
- `run_backtest()` 비동기 함수: KIS API 일봉 데이터 조회 → DataFrame 변환 → 기술 지표 계산 → 전략 신호 생성 → 포트폴리오 시뮬레이션
- VectorBT `Portfolio.from_signals()` 활용 (설치 시), 미설치 시 `_simulate_portfolio_basic()` 폴백 지원
- KIS API 날짜 형식(`YYYYMMDD`) 파싱 처리
- `_VBT_AVAILABLE` 플래그로 선택적 VectorBT 사용

#### 2. `backend/app/services/backtest_metrics.py` - 성과 지표 계산

- `calculate_metrics()`: VectorBT 또는 기본 시뮬레이션 결과에서 성과 지표 계산
- 계산 지표:
  - 총 수익률 (total_return)
  - 연간 복리 수익률 CAGR
  - 최대 낙폭 MDD (Maximum Drawdown)
  - 샤프 비율 (Sharpe Ratio) - 일간 수익률 기반 커스텀 계산
  - 총 거래 횟수, 승률 (Win Rate)
  - 벤치마크 대비 수익률 (benchmark_return)
  - 자산 곡선 데이터 (equity_curve, 날짜별 포트폴리오 가치)

#### 3. `backend/app/schemas/backtest.py` - Pydantic 스키마

- `BacktestRunRequest`: 백테스팅 실행 요청 스키마 (symbol, strategy_name, params, start_date, end_date, initial_cash)
- `EquityPoint`: 자산 곡선 데이터 포인트 (date, value)
- `BacktestResultResponse`: 결과 응답 스키마 (성과 지표 전체 + equity_curve + created_at)
- `BacktestResultListResponse`: 목록 조회용 요약 스키마

#### 4. `backend/app/api/v1/backtest.py` - 백테스팅 REST API

- `POST /api/v1/backtest/run`: 백테스팅 실행 및 결과 DB 저장
- `GET /api/v1/backtest/results`: 백테스팅 결과 목록 조회 (최신순, limit/offset)
- `GET /api/v1/backtest/results/{result_id}`: 특정 백테스팅 결과 상세 조회
- `_to_response()` 헬퍼 함수로 ORM 레코드 → 응답 스키마 변환

### 백엔드 수정 파일 (3개)

#### 5. `backend/app/models/backtest.py` - ORM 모델 스키마 확장

- `strategy_id`: NOT NULL → nullable (Optional[int])로 변경 (FK 관계 유지)
- `symbol` (String(20)): 대상 종목 코드 컬럼 추가
- `start_date` (Date): 백테스팅 시작일 컬럼 추가
- `end_date` (Date): 백테스팅 종료일 컬럼 추가

#### 6. `backend/alembic/versions/b2c3d4e5f6a7_backtest_results_sprint8_컬럼_추가.py` - 마이그레이션

- revision: `b2c3d4e5f6a7`, down_revision: `a1b2c3d4e5f6`
- `strategy_id` FK 제약 삭제 → nullable 변경 → FK 재생성
- `symbol`, `start_date`, `end_date` 컬럼 추가

#### 7. `backend/app/api/v1/router.py` - 라우터 등록

- `backtest` 라우터 추가 (`/backtest` prefix)

#### 8. `backend/requirements.txt` - 의존성 추가

- `numpy>=1.24.0` 추가
- `vectorbt>=0.26.0` 추가

### 프론트엔드 수정 파일 (1개)

#### 9. `frontend/src/hooks/use-backtest.ts` - Mock → 실제 API 연동

- 기존 `useBacktestResult()` (Mock 기반 단일 훅) 제거
- `useBacktestRun()`: `POST /api/v1/backtest/run` mutation 훅 (useMutation)
- `useBacktestResults()`: `GET /api/v1/backtest/results` 조회 훅 (useQuery)
- `useBacktestResult(id)`: `GET /api/v1/backtest/results/{id}` 상세 조회 훅 (useQuery)
- `BacktestRunParams`, `BacktestResultAPI`, `EquityPoint` TypeScript 인터페이스 정의

---

## 커밋 내역

| 커밋 해시 | 메시지 |
|-----------|--------|
| `9029503` | feat: Sprint 8 - VectorBT 백테스팅 엔진 구현 |

변경 통계: 9 files changed, 818 insertions(+), 19 deletions(-)

---

## 주요 기술 결정

| 항목 | 결정 사항 | 이유 |
|------|-----------|------|
| VectorBT 선택 | Apache 2.0 라이선스, 벡터화 연산 | 빠른 백테스팅 속도, 상용 배포 라이선스 문제 없음 |
| VectorBT 폴백 지원 | 미설치 시 기본 시뮬레이션 사용 | Docker 이미지 빌드 실패 방지, 의존성 유연화 |
| strategy_id nullable | 단일 유저 시스템 특성 | 백테스팅은 DB 전략 레코드 없이도 실행 가능하도록 |
| 샤프비율 직접 계산 | 연간화 계수 252일 적용 | VectorBT 미설치 환경에서도 동일한 지표 제공 |
| KIS 날짜 형식 처리 | `pd.to_datetime(format="%Y%m%d")` | KIS API가 `YYYYMMDD` 문자열로 날짜 반환 |
| equity_curve JSONB 저장 | `result_data` 필드 내 저장 | 별도 테이블 없이 유연하게 시계열 데이터 저장 |

---

## API 명세

### POST /api/v1/backtest/run

요청:
```json
{
  "symbol": "005930",
  "strategy_name": "golden_cross_rsi",
  "params": {"short_window": 20, "long_window": 60},
  "start_date": "2021-01-01",
  "end_date": "2024-01-01",
  "initial_cash": 10000000
}
```

응답:
```json
{
  "id": 1,
  "symbol": "005930",
  "strategy_name": "golden_cross_rsi",
  "start_date": "2021-01-01",
  "end_date": "2024-01-01",
  "total_return": 0.2345,
  "cagr": 0.0845,
  "mdd": -0.1523,
  "sharpe_ratio": 1.23,
  "total_trades": 18,
  "win_rate": 0.6111,
  "benchmark_return": 0.1234,
  "equity_curve": [
    {"date": "2021-01-04", "value": 10000000},
    {"date": "2021-01-05", "value": 10050000}
  ],
  "created_at": "2026-03-01T12:00:00"
}
```

### GET /api/v1/backtest/results

응답: BacktestResultListResponse 목록 (symbol, strategy_name, total_return, sharpe_ratio, created_at)

### GET /api/v1/backtest/results/{id}

응답: BacktestResultResponse (전체 상세 포함)

---

## 남은 기술 부채

- 백테스팅 결과 시각화 차트 컴포넌트 (수익 곡선, 드로우다운 차트) 미구현 → 프론트엔드 backtest 페이지에서 추가 작업 필요
- VectorBT 설치 및 Docker 이미지 빌드 검증 미완료 (실제 Docker 환경에서 의존성 확인 필요)
- 텔레그램 알림 연동 미완료 (Sprint 9에서 처리)
- 실시간 WebSocket 데이터 연동 미완료 (Sprint 9에서 처리)
