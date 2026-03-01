# Sprint 1 - Phase 1: 프로젝트 구조 및 인프라

**기간:** 2026-03-02 ~ 2026-03-07
**완료일:** 2026-03-01 (조기 완료)
**상태:** ✅ 구현 완료 (통합 검증은 사용자 수행 필요)
**브랜치:** `sprint-1`
**목표:** 실제 개발 가능한 인프라 구축 (Next.js + FastAPI + Docker + DB 스키마)

---

## 완료된 작업

### Task 1: FastAPI 백엔드 프로젝트 초기화

| 파일 | 내용 | 커밋 |
|------|------|------|
| `backend/app/main.py` | FastAPI 앱, CORS, lifespan | `64461b1` |
| `backend/app/core/config.py` | pydantic-settings 기반 환경변수 | `64461b1` |
| `backend/app/core/database.py` | SQLAlchemy 2.x 비동기 엔진/세션 | `64461b1` |
| `backend/app/core/logging.py` | DEBUG 분기 로깅 설정 | `64461b1` |
| `backend/app/api/v1/health.py` | `GET /api/v1/health` 엔드포인트 | `64461b1` |
| `backend/app/models/base.py` | DeclarativeBase + created_at/updated_at | `64461b1` |
| `backend/requirements.txt` | fastapi, uvicorn, sqlalchemy, alembic 등 | `64461b1` |

**수정 커밋:** `31f6394` - CORS credentials 버그 수정, 로깅 초기화 수정

### Task 2: Next.js 프론트엔드 프로젝트 초기화

| 파일 | 내용 | 커밋 |
|------|------|------|
| `frontend/package.json` | Next.js 16, TypeScript, Tailwind 의존성 | `3775da9` |
| `frontend/src/app/page.tsx` | "AutoTrader KR" 최소 홈 화면 | `3775da9` |
| `frontend/src/app/layout.tsx` | RootLayout, 메타데이터, lang="ko" | `d95d4b8` |

### Task 3: Docker Compose 환경 구성

| 파일 | 내용 | 커밋 |
|------|------|------|
| `docker-compose.yml` | 4개 서비스 (postgres, redis, backend, frontend) | `892212c` |
| `docker/backend/Dockerfile` | python:3.12-slim, uvicorn --reload | `892212c` |
| `docker/frontend/Dockerfile` | node:22-alpine, next dev -H 0.0.0.0 | `892212c` |

**수정 커밋:**
- `8c1933b` - Docker 빌드 컨텍스트를 프로젝트 루트로 수정
- `5112a79` - Next.js hostname 플래그 수정 (`--hostname` → `-H`)

### Task 4: DB 스키마 및 Alembic 마이그레이션

| 파일 | 테이블 | 커밋 |
|------|--------|------|
| `backend/app/models/user.py` | `users` | `28a8eca` |
| `backend/app/models/strategy.py` | `strategies`, `strategy_params` | `28a8eca` |
| `backend/app/models/watchlist.py` | `watchlist_groups`, `watchlist_items` | `28a8eca` |
| `backend/app/models/order.py` | `orders`, `order_logs` | `28a8eca` |
| `backend/app/models/portfolio.py` | `portfolio_snapshots` | `28a8eca` |
| `backend/app/models/backtest.py` | `backtest_results` | `28a8eca` |
| `backend/app/models/settings.py` | `system_settings` | `28a8eca` |
| `backend/alembic/versions/*.py` | 10개 테이블 upgrade/downgrade | `28a8eca` |
| `backend/scripts/seed.py` | admin 유저, 전략 3개, 시스템 설정 | `28a8eca` |

---

## 사용자 수행 필요 작업 (deploy.md 참조)

Sprint 1 코드 구현은 완료됐으나, 다음 검증 작업은 사용자가 직접 수행해야 합니다:

```bash
# 1. .env의 POSTGRES_PASSWORD 설정 (현재 placeholder)
# POSTGRES_PASSWORD=your_db_password_here → 실제 비밀번호로 변경

# 2. Docker 빌드 및 서비스 기동
docker compose up --build -d

# 3. 서비스 상태 확인
docker compose ps
# 모든 서비스 Up 상태여야 함

# 4. 헬스체크
curl http://localhost:8000/api/v1/health  # 200 OK 확인
curl http://localhost:3001                # Next.js 렌더링 확인

# 5. DB 마이그레이션 실행
docker compose exec backend alembic upgrade head

# 6. 테이블 확인 (10개)
docker compose exec postgres psql -U mystock_user -d mystock -c "\dt"

# 7. 시드 데이터 삽입
docker compose exec backend python scripts/seed.py

# 8. 로그 확인
docker compose logs --tail=20 backend
docker compose logs --tail=20 frontend
```

---

## 완료 기준 (Definition of Done)

- [x] `docker compose up`으로 4개 서비스 기동 가능한 코드 완성
- [x] `/api/v1/health` 200 OK 응답 구현
- [x] Swagger UI (`/docs`) 렌더링 가능
- [x] Next.js `localhost:3001` 렌더링 코드 완성
- [x] DB 10개 테이블 ORM 모델 및 마이그레이션 파일 작성
- [x] seed.py 스크립트 작성
- [ ] `docker compose up` 실제 검증 (사용자 수행 필요)
- [ ] `alembic upgrade head` 실행 (사용자 수행 필요)

---

## 주요 설계 결정

1. **CORS 설정**: `allow_origins=["*"]` + `allow_credentials=False` (개발 환경, wildcard 호환)
2. **Docker 빌드 컨텍스트**: 프로젝트 루트(`.`)를 컨텍스트로 사용하여 `docker/` Dockerfile에서 `backend/`, `frontend/` 접근
3. **Next.js hostname**: `-H 0.0.0.0` 플래그로 컨테이너 외부 접근 보장
4. **Alembic 드라이버**: `+asyncpg` 제거 → psycopg2 동기 드라이버 사용 (마이그레이션 전용)
5. **Tailwind CSS**: v4 (config 파일 불필요, PostCSS 플러그인 방식)

---

## 커밋 목록

| 커밋 | 내용 |
|------|------|
| `64461b1` | feat: FastAPI 백엔드 프로젝트 초기화 |
| `31f6394` | fix: CORS credentials 설정 및 로깅 초기화 수정 |
| `3775da9` | feat: Next.js 프론트엔드 프로젝트 초기화 |
| `d95d4b8` | fix: layout.tsx 메타데이터 및 언어 설정 수정 |
| `892212c` | feat: Docker Compose 환경 구성 |
| `8c1933b` | fix: Docker 빌드 컨텍스트 경로 수정 |
| `5112a79` | fix: Next.js 개발 서버 hostname 플래그 수정 |
| `28a8eca` | feat: DB 스키마 ORM 모델 및 Alembic 마이그레이션 추가 |
