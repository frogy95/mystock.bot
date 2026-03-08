# Sprint 22: 백테스트 차트 데이터 DB 캐싱 + yfinance 폴백

## 개요

- **기간**: 2026-03-08
- **브랜치**: `sprint22`
- **PR**: develop 브랜치로 PR 생성
- **상태**: ✅ 완료

## 목표

백테스트 실행 시 차트 데이터를 DB에 캐싱하고, KIS API 실패 시 yfinance로 폴백하여 안정적인 데이터 조회를 보장한다.

## 구현 내용

### 1. ChartDataCache ORM 모델 (신규)
- `backend/app/models/chart_cache.py`: `chart_data_cache` 테이블 정의
- symbol, interval, trade_date 컬럼으로 복합 인덱스 구성
- OHLCV 데이터를 JSON 컬럼에 저장

### 2. Alembic 마이그레이션 (신규)
- `backend/alembic/versions/e5f6a7b8c9d0_chart_data_cache_테이블_추가.py`
- `chart_data_cache` 테이블 생성 마이그레이션

### 3. chart_data_service (신규)
- `backend/app/services/chart_data_service.py`: 3단계 데이터 조회 전략
  1. DB 캐시 우선 조회 (캐시 히트 시 즉시 반환, 로그: "차트 캐시 히트")
  2. KIS API 조회 (성공 시 DB에 저장 후 반환, 로그: "차트 조회 완료")
  3. yfinance 폴백 (KIS 실패 시, 로그: "yfinance 조회 완료")

### 4. backtest_engine 연동 (수정)
- `backend/app/services/backtest_engine.py`: 기존 kis_client 직접 호출 → chart_data_service 사용

### 5. kis_client 개선 (수정)
- `backend/app/services/kis_client.py`: `get_chart()` 예외 발생 시 None 반환으로 폴백 가능하도록 수정

## 변경 파일 목록

| 파일 | 유형 | 설명 |
|------|------|------|
| `backend/app/models/chart_cache.py` | 신규 | ChartDataCache ORM 모델 |
| `backend/app/models/__init__.py` | 수정 | chart_cache 임포트 추가 |
| `backend/alembic/env.py` | 수정 | chart_cache 임포트 추가 |
| `backend/alembic/versions/e5f6a7b8c9d0_chart_data_cache_테이블_추가.py` | 신규 | DB 마이그레이션 |
| `backend/app/services/chart_data_service.py` | 신규 | DB 캐시 + KIS + yfinance 폴백 서비스 |
| `backend/app/services/backtest_engine.py` | 수정 | chart_data_service 사용으로 변경 |
| `backend/app/services/kis_client.py` | 수정 | get_chart() 예외 시 None 반환 |
| `deploy.md` | 수정 | Sprint 22 수동 검증 항목 기록 |

## 검증 결과

### 보고서 및 첨부 파일
- [코드 리뷰 보고서](sprint22/code-review-report.md)
- [Playwright 검증 스크린샷](sprint22/)

### 자동 검증 (sprint-close 시점)
- ✅ `pytest -v` — 51개 테스트 모두 통과
- ✅ 헬스체크 (`/api/v1/health`) — DB/Redis/Scheduler 모두 healthy
- ✅ Playwright: 로그인 페이지 렌더링 정상
- ✅ Playwright: 로그인 후 대시보드 이동 정상
- ✅ Playwright: 백테스트 페이지 렌더링 정상
- ✅ Playwright: 전략 드롭다운 API 연동 — 3개 전략 정상 로드 (골든크로스+RSI, 가치+모멘텀, 볼린저밴드반전)
- ✅ 코드 리뷰: Critical/High 이슈 없음 ([보고서](sprint22/code-review-report.md))

### 수동 검증 필요 항목
- ⬜ Docker 재빌드: `docker compose up --build`
- ⬜ DB 마이그레이션: `docker compose exec backend alembic upgrade head` (chart_data_cache 테이블 생성)
- ⬜ 백테스트 실행 (첫 실행 — yfinance 또는 KIS 호출 후 DB 저장 확인)
  - 종목: 229200, 전략: 골든크로스+RSI, 기간: 2025.10 ~ 2026.03
- ⬜ 백테스트 재실행 — DB 캐시 히트 확인 (백엔드 로그에 "차트 캐시 히트" 출력 확인)
- ⬜ 평일 KIS API 정상 시 KIS 데이터 우선 사용 확인 (로그: "차트 조회 완료")
- ⬜ 주말/KIS 점검 시 yfinance 폴백 동작 확인 (로그: "yfinance 조회 완료")
- ⬜ 백테스트 결과 차트에서 3개 라인(전략 수익/KOSPI 벤치마크/종목 바이앤홀드) 및 만원 단위 표시 확인
- ⬜ 백테스트 결과 거래 내역 테이블 표시 확인

## 추가 UX 개선 (2026-03-08)

### 종목 바이앤홀드 비교 라인 추가
- 백엔드 `EquityPoint` 스키마에 `stock_buyhold` 필드 추가
- `backtest_metrics.py`에 `_build_stock_buyhold_values()` 헬퍼 추가 (초기자본 × 종가비율)
- VBT/기본 시뮬레이션 양쪽 모두 equity_curve에 `stock_buyhold` 포함
- 차트에 녹색(#22c55e) "종목 바이앤홀드" 3번째 라인 추가

### 만원 단위 표기
- Y축: `(v/10000).toLocaleString() + "만"` 형태로 변경, 레이블 "만원"
- Tooltip: `(value/10000).toFixed(1) + "만원"` 형태
- 거래 내역 금액/손익: `(amount/10000).toFixed(0) + "만원"` 형태

### 변경 파일
| 파일 | 변경 |
|------|------|
| `backend/app/schemas/backtest.py` | `EquityPoint`에 `stock_buyhold` 필드 추가 |
| `backend/app/services/backtest_metrics.py` | 바이앤홀드 시계열 헬퍼 + equity_curve 반영 |
| `frontend/src/hooks/use-backtest.ts` | `EquityPoint`에 `stock_buyhold` 추가 |
| `frontend/src/lib/mock/types.ts` | `equityCurve` 타입에 `stockBuyhold` 추가 |
| `frontend/src/app/backtest/page.tsx` | `stock_buyhold` → `stockBuyhold` 매핑 |
| `frontend/src/components/backtest/backtest-equity-chart.tsx` | 3번째 라인 + 만원 단위 |
| `frontend/src/components/backtest/backtest-trades-table.tsx` | 금액/손익 만원 단위 |

## 완료 기준 (Definition of Done)

- ✅ ChartDataCache 모델 및 마이그레이션 파일 생성
- ✅ chart_data_service: DB 캐시 → KIS → yfinance 3단계 폴백 구현
- ✅ backtest_engine이 chart_data_service를 사용하도록 변경
- ✅ 기존 pytest 51개 회귀 없음
- ⬜ alembic upgrade head 후 chart_data_cache 테이블 정상 생성 확인 (수동)
- ⬜ 백테스트 캐시 히트/미스 동작 확인 (수동)
