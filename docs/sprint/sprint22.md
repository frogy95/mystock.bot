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

### 자동 검증 (sprint-close 시점)
- ✅ `pytest -v` — 51개 테스트 모두 통과
- ✅ `chart_cache.py` 모델 임포트 성공
- ✅ `chart_data_service.py` 임포트 성공

### 수동 검증 필요 항목
- ⬜ Docker 재빌드: `docker compose up --build`
- ⬜ DB 마이그레이션: `docker compose exec backend alembic upgrade head` (chart_data_cache 테이블 생성)
- ⬜ 백테스트 실행 (첫 실행 — yfinance 또는 KIS 호출 후 DB 저장 확인)
  - 종목: 229200, 전략: 골든크로스+RSI, 기간: 2025.10 ~ 2026.03
- ⬜ 백테스트 재실행 — DB 캐시 히트 확인 (백엔드 로그에 "차트 캐시 히트" 출력 확인)
- ⬜ 평일 KIS API 정상 시 KIS 데이터 우선 사용 확인 (로그: "차트 조회 완료")
- ⬜ 주말/KIS 점검 시 yfinance 폴백 동작 확인 (로그: "yfinance 조회 완료")

## 완료 기준 (Definition of Done)

- ✅ ChartDataCache 모델 및 마이그레이션 파일 생성
- ✅ chart_data_service: DB 캐시 → KIS → yfinance 3단계 폴백 구현
- ✅ backtest_engine이 chart_data_service를 사용하도록 변경
- ✅ 기존 pytest 51개 회귀 없음
- ⬜ alembic upgrade head 후 chart_data_cache 테이블 정상 생성 확인 (수동)
- ⬜ 백테스트 캐시 히트/미스 동작 확인 (수동)
