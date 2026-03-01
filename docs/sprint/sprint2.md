# Sprint 2: API 연동 기반 구축

**기간:** 2026-03-01
**브랜치:** `sprint2` (main에서 분기)
**상태:** 완료

---

## 목표

Sprint 0~1에서 완성된 프로젝트 뼈대(FastAPI + Next.js 16 + PostgreSQL + Redis + Docker Compose) 위에
**KIS API 클라이언트 연동**, **단일 유저 인증**, **프론트엔드 기본 레이아웃/라우팅**을 구현하여 Phase 1을 완료한다.

---

## 완료된 태스크 (10개)

### 백엔드

| Task | 파일 | 내용 |
|------|------|------|
| Task 1 | `backend/app/core/config.py`, `.env.example` | KIS API 4개 + 인증 2개 + 텔레그램 2개 환경변수 추가 |
| Task 2 | `backend/app/services/kis_client.py` | python-kis 래핑 싱글턴 클래스, lazy 초기화 |
| Task 3 | `backend/app/services/rate_limiter.py` | 슬라이딩 윈도우 RateLimiter, 지수 백오프 retry |
| Task 4 | `backend/app/api/v1/stocks.py`, `backend/app/schemas/stock.py` | 현재가/차트/잔고 엔드포인트 |
| Task 5 | `backend/app/core/auth.py`, `backend/app/api/v1/auth.py`, `backend/app/api/v1/settings.py` | HMAC-SHA256 토큰 인증, 로그인/KIS상태 엔드포인트 |

### 프론트엔드

| Task | 파일 | 내용 |
|------|------|------|
| Task 6 | `frontend/src/lib/query-provider.tsx` | shadcn/ui + TanStack Query + zustand 설치 및 설정 |
| Task 7 | `frontend/src/components/layout/` | 사이드바(6개 메뉴), 헤더, 통합 레이아웃 |
| Task 8 | `frontend/src/lib/api/client.ts`, `frontend/src/app/*/page.tsx` | fetch 기반 API 클라이언트, 6개 페이지 스캐폴딩 |
| Task 9 | `frontend/src/stores/auth-store.ts` | persist 미들웨어 zustand auth 스토어 |

### 통합

| Task | 내용 |
|------|------|
| Task 10 | 통합 검증, deploy.md 업데이트, ROADMAP.md 완료 표시 |

---

## API 엔드포인트 목록 (v1)

| 메서드 | 경로 | 인증 | 설명 |
|--------|------|------|------|
| GET | `/api/v1/health` | 불필요 | 헬스체크 |
| POST | `/api/v1/auth/login` | 불필요 | 로그인 → Bearer 토큰 발급 |
| GET | `/api/v1/stocks/{symbol}/quote` | 필요 | 현재가 조회 |
| GET | `/api/v1/stocks/{symbol}/chart` | 필요 | OHLCV 차트 조회 |
| GET | `/api/v1/stocks/balance` | 필요 | 계좌 잔고 조회 |
| GET | `/api/v1/settings/kis-status` | 필요 | KIS API 연결 상태 |

---

## 주요 설계 결정

### 인증 방식
- JWT 대신 HMAC-SHA256 서명 토큰 사용 → 의존성 최소화
- 토큰 형식: `username:expires_at:hmac_signature`
- 유효 기간: 24시간

### KIS API 클라이언트
- Lazy 초기화: 키 미설정 시 경고 출력 후 정상 기동
- Rate Limit: 모의투자 5건/초, 실전 20건/초 (슬라이딩 윈도우)
- Retry: 지수 백오프 최대 3회

### shadcn/ui + Tailwind v4
- `npx shadcn@latest init` → Tailwind v4 자동 감지 성공
- Neutral 색상 기반 컴포넌트 (button, card, input, label, separator)

---

## 신규 파일 목록

**백엔드 (9개):**
- `backend/app/services/__init__.py`
- `backend/app/services/kis_client.py`
- `backend/app/services/rate_limiter.py`
- `backend/app/core/auth.py`
- `backend/app/schemas/stock.py`
- `backend/app/schemas/auth.py`
- `backend/app/api/v1/stocks.py`
- `backend/app/api/v1/auth.py`
- `backend/app/api/v1/settings.py`

**프론트엔드 (12개):**
- `frontend/src/lib/query-provider.tsx`
- `frontend/src/lib/api/client.ts`
- `frontend/src/components/layout/app-sidebar.tsx`
- `frontend/src/components/layout/app-header.tsx`
- `frontend/src/components/layout/app-layout.tsx`
- `frontend/src/stores/auth-store.ts`
- `frontend/src/stores/index.ts`
- `frontend/src/app/dashboard/page.tsx`
- `frontend/src/app/watchlist/page.tsx`
- `frontend/src/app/strategy/page.tsx`
- `frontend/src/app/backtest/page.tsx`
- `frontend/src/app/orders/page.tsx`
- `frontend/src/app/settings/page.tsx`
- `frontend/src/components/ui/` (shadcn/ui 컴포넌트 5개)

---

## 커밋 로그

1. `feat: config.py에 KIS API 및 인증 환경변수 추가`
2. `feat: python-kis 기반 KIS API 클라이언트 서비스 구현`
3. `feat: KIS API Rate Limit 유틸리티 및 재시도 로직 구현`
4. `feat: KIS API 현재가/차트/잔고 조회 엔드포인트 추가`
5. `feat: 환경변수 기반 단일 유저 인증 시스템 구현`
6. `feat: shadcn/ui, TanStack Query, zustand 프론트엔드 설정`
7. `feat: 사이드바/헤더 공통 레이아웃 컴포넌트 구현`
8. `feat: 6개 페이지 라우팅 구조 및 API 클라이언트 구현`
9. `feat: zustand auth 스토어 초기 구조 구현`
10. `feat: Sprint 2 통합 검증 및 문서 업데이트`

---

## 다음 단계 (Sprint 3)

- 대시보드 UI: 실시간 현재가 카드, OHLCV 차트 컴포넌트
- 관심종목 CRUD: 추가/삭제/정렬
- 로그인 페이지 및 인증 흐름 UI
