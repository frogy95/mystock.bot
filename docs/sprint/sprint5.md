# Sprint 5 완료 보고서

- **스프린트 번호:** Sprint 5
- **Phase:** Phase 3 - 백엔드 핵심 기능 개발
- **기간:** 2026-03-30 ~ 2026-04-04 (실제 완료: 2026-03-01)
- **브랜치:** sprint5
- **상태:** 완료

---

## 목표

프론트엔드 Mock UI와 실제 백엔드 API를 연결한다.
관심종목/보유종목 관리에 필요한 모든 백엔드 서비스와 API 엔드포인트를 구현하고,
프론트엔드 hooks를 실제 API 호출로 교체한다.

---

## 구현 내용

### 백엔드

#### DB 스키마 및 마이그레이션
- `backend/app/models/holding.py`: holdings 테이블 ORM 모델 추가
  - 보유종목 정보 (종목코드, 종목명, 수량, 평균매수가, 현재가)
  - 손절/익절 비율 설정 컬럼
  - 매도 전략 외래 키
  - KIS 동기화 시각
- `backend/alembic/versions/a1b2c3d4e5f6_holdings_테이블_추가.py`: Alembic 마이그레이션
- `backend/app/models/watchlist.py`: WatchlistGroup/WatchlistItem relationship 추가
- `backend/app/models/__init__.py`: Holding 모델 임포트 추가

#### 서비스 레이어
- `backend/app/services/redis_client.py`: Redis 싱글턴 클라이언트
  - 비동기 redis.asyncio 기반
  - 앱 종료 시 연결 정리 (close_redis)
- `backend/app/services/stock_master.py`: pykrx 기반 종목 마스터 서비스
  - KOSPI/KOSDAQ 전종목 데이터 Redis 캐시 (TTL 24시간)
  - 종목코드/종목명 검색 기능
  - 초기 로드 실패 시 서버 시작에 영향 없음 (graceful fallback)
- `backend/app/services/holding_service.py`: 보유종목 서비스
  - KIS 잔고 API 연동 및 DB upsert 동기화
  - 기존 손절/익절/전략 설정 보존
  - 포트폴리오 요약 계산 (총평가금액, 총손익, 예수금)

#### Pydantic 스키마
- `backend/app/schemas/watchlist.py`: WatchlistGroup/Item 요청/응답 스키마
- `backend/app/schemas/holding.py`: Holding/Portfolio 요청/응답 스키마
- `backend/app/schemas/search.py`: 종목 검색 응답 스키마

#### API 엔드포인트
- `backend/app/api/v1/watchlist.py`: 관심종목 CRUD API
  - `GET /api/v1/watchlist/groups`: 그룹 전체 조회
  - `POST /api/v1/watchlist/groups`: 그룹 생성
  - `PUT /api/v1/watchlist/groups/{id}`: 그룹명 수정
  - `DELETE /api/v1/watchlist/groups/{id}`: 그룹 삭제 (cascade)
  - `POST /api/v1/watchlist/groups/{id}/items`: 종목 추가
  - `DELETE /api/v1/watchlist/groups/{id}/items/{item_id}`: 종목 제거
  - `PUT /api/v1/watchlist/items/{id}/strategy`: 전략 할당/해제
- `backend/app/api/v1/holdings.py`: 보유종목 API
  - `GET /api/v1/holdings`: 보유종목 목록 조회
  - `POST /api/v1/holdings/sync`: KIS 잔고 동기화
  - `PUT /api/v1/holdings/{id}/stop-loss`: 손절/익절 설정
  - `PUT /api/v1/holdings/{id}/sell-strategy`: 매도 전략 설정
  - `GET /api/v1/holdings/summary`: 포트폴리오 요약
- `backend/app/api/v1/stocks.py`: 종목 검색 엔드포인트 추가
  - `GET /api/v1/stocks/search?q={query}`: Redis 캐시 기반 종목 검색
- `backend/app/api/v1/router.py`: watchlist/holdings 라우터 등록
- `backend/app/main.py`: lifespan에 종목 마스터 초기 로드 추가
- `backend/app/services/kis_client.py`: `get_balance()` avg_price 필드 추가
- `backend/requirements.txt`: redis[hiredis]>=5.0.0, pykrx>=1.0.0 추가

### 프론트엔드

- `frontend/src/hooks/use-watchlist.ts`: Mock → 실제 API 전환
  - 종목 검색: `/api/v1/stocks/search`
  - 그룹 조회: `/api/v1/watchlist/groups`
- `frontend/src/hooks/use-watchlist-mutations.ts`: 신규 생성
  - 그룹 CRUD mutation
  - 종목 추가/제거 mutation
  - 전략 할당 mutation
- `frontend/src/hooks/use-portfolio.ts`: Mock → 실제 API 전환
  - 보유종목 조회: `/api/v1/holdings`
- `frontend/src/hooks/use-holdings-mutations.ts`: 신규 생성
  - KIS 동기화 mutation
  - 손절/익절 설정 mutation
  - 매도 전략 설정 mutation
- `frontend/src/hooks/use-dashboard.ts`: Mock → 실제 API 전환
  - 포트폴리오 요약: `/api/v1/holdings/summary`
  - 보유종목: `/api/v1/holdings`

---

## 주요 변경 파일 목록

| 파일 | 변경 유형 |
|------|-----------|
| `backend/alembic/versions/a1b2c3d4e5f6_holdings_테이블_추가.py` | 신규 |
| `backend/app/models/holding.py` | 신규 |
| `backend/app/models/watchlist.py` | 수정 |
| `backend/app/models/__init__.py` | 수정 |
| `backend/app/schemas/watchlist.py` | 신규 |
| `backend/app/schemas/holding.py` | 신규 |
| `backend/app/schemas/search.py` | 신규 |
| `backend/app/services/redis_client.py` | 신규 |
| `backend/app/services/stock_master.py` | 신규 |
| `backend/app/services/holding_service.py` | 신규 |
| `backend/app/api/v1/watchlist.py` | 신규 |
| `backend/app/api/v1/holdings.py` | 신규 |
| `backend/app/api/v1/stocks.py` | 수정 |
| `backend/app/api/v1/router.py` | 수정 |
| `backend/app/main.py` | 수정 |
| `backend/app/services/kis_client.py` | 수정 |
| `backend/requirements.txt` | 수정 |
| `frontend/src/hooks/use-watchlist.ts` | 수정 |
| `frontend/src/hooks/use-watchlist-mutations.ts` | 신규 |
| `frontend/src/hooks/use-portfolio.ts` | 수정 |
| `frontend/src/hooks/use-holdings-mutations.ts` | 신규 |
| `frontend/src/hooks/use-dashboard.ts` | 수정 |

---

## 검증 결과

- [코드 리뷰 보고서](sprint5/code-review.md)
- [Playwright 검증 보고서](sprint5/playwright-report.md)

---

## 사용자 직접 수행 필요 항목

Sprint 5 검증을 위해 아래 항목을 수행하세요. (`deploy.md` Section 10 참고)

1. Docker Compose 재빌드 (`redis[hiredis]`, `pykrx` 신규 패키지 설치)
2. Alembic 마이그레이션 실행 (`holdings` 테이블 생성)
3. 백엔드 API 엔드포인트 동작 검증 (Swagger UI)
4. 프론트엔드 watchlist/portfolio 화면 실제 API 연동 확인

---

## 다음 스프린트 (Sprint 6) 계획

- 기술적 분석 지표 엔진 (pandas-ta)
- 프리셋 전략 3종 구현 (골든크로스+RSI, 가치+모멘텀, 볼린저 밴드 반전)
- 자동 주문 실행 엔진
- APScheduler 기반 전략 실행 스케줄러
