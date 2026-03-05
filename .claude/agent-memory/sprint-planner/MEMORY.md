# Sprint Planner 메모리

## 프로젝트 개요
- **프로젝트명:** AutoTrader KR (mystock.bot)
- **목표:** 한국투자증권 Open API 기반 KOSPI/KOSDAQ 퀀트 전략 자동매매 웹앱
- **전체 기간:** 2026-03-02 ~ 2026-05-10 (10주, 11 스프린트)
- **팀 규모:** 1-2인
- **원격 저장소:** https://github.com/frogy95/mystock.bot.git

## 기술 스택
- Frontend: Next.js 16+ (App Router) + TypeScript + TailwindCSS v4 + shadcn/ui
- Backend: FastAPI (Python)
- DB: PostgreSQL 16, Redis 7
- ORM: SQLAlchemy 2.x (asyncpg 드라이버)
- Migration: Alembic
- 증권 API: python-kis (PyKIS) 2.x
- 알림: python-telegram-bot 22.x
- 배포: Docker Compose

## 스프린트 현황
- **Sprint 0 (Phase 0):** 완료 (2026-02-28)
  - .gitignore, .env.example, 디렉토리 구조, deploy.md, sprint0.md
  - 수동: 한투 계정, 텔레그램 봇, 개발 도구, .env 18개 키
- **Sprint 1 (Phase 1):** 완료 (2026-03-01)
  - FastAPI 초기화, Next.js 초기화, Docker Compose 4서비스, DB 스키마 10테이블, Alembic, seed 3종 전략
  - 브랜치: sprint-1
- **Sprint 2 (Phase 1):** 완료 (2026-03-01)
  - KIS API 클라이언트, 단일 유저 인증, 프론트엔드 기본 레이아웃/라우팅
  - 인증: HMAC-SHA256 서명 토큰 (JWT 대신), 유효 24시간
  - 6개 API 엔드포인트 (health, login, quote, chart, balance, kis-status)
  - shadcn/ui 컴포넌트 5개 설치 (button, card, input, label, separator)
  - 브랜치: sprint2
- **Sprint 3 (Phase 2):** 완료 (2026-03-01, Playwright MCP 검증 완료)
  - 범위: 대시보드 UI, 관심종목 UI, 포트폴리오 UI (Mock 데이터 기반)
  - 브랜치: sprint3
  - shadcn/ui 컴포넌트 15개 추가 (총 20개)
  - Mock 데이터 패턴 확립: types.ts, dashboard.ts, watchlist.ts, portfolio.ts
  - 공통 컴포넌트: PriceChangeBadge, StatCard, LoadingSkeleton
  - 커스텀 훅 패턴: use-dashboard.ts, use-watchlist.ts, use-portfolio.ts
  - zustand 스토어: watchlist-store.ts, sidebar-store.ts
- **Sprint 4 (Phase 2):** 완료 (2026-03-01)
  - 범위: 전략 설정 UI, 백테스팅 UI, 주문 내역 UI, 설정 UI (Mock 데이터 기반)
  - 브랜치: sprint4
- **Sprint 4.1 (Phase 2):** 완료 (2026-03-01)
  - 커스텀 전략 빌더 UI (Could Have 항목)
- **Sprint 5 (Phase 3):** 완료 (2026-03-01)
  - 관심종목/보유종목 API 연동, Mock → 실제 API 교체
- **Sprint 6 (Phase 3):** 완료 (2026-03-01)
  - 전략 엔진 (indicators.py, strategy_engine.py), 자동 주문 실행 엔진
- **Sprint 7 (Phase 3):** 완료 (2026-03-01)
  - 손절/익절 자동 관리, 매매 안전장치, 시스템 안전장치
- **Sprint 8 (Phase 4):** 완료 (2026-03-01)
  - VectorBT 백테스팅 엔진, 결과 시각화 프론트엔드 연동
- **Sprint 9 (Phase 4):** 완료 (2026-03-02)
  - 텔레그램 알림 서비스 완성, 실시간 WebSocket 체결 알림 UI, 대시보드 Mock → 실제 API 교체
  - 브랜치: sprint9, PR: https://github.com/frogy95/mystock.bot/pull/14
- **Sprint 10 (Phase 5):** 완료 (2026-03-02)
  - 범위: 백엔드 에러 핸들링 강화, 구조화 로깅, 프론트엔드 에러 핸들링, Mock→API 전환, 통합 테스트
  - 브랜치: sprint10
- **Sprint 11 (Phase 5+):** 완료 (2026-03-02) — 로그인 페이지 + 데모 모드
- **Sprint 12 (Phase 5+):** 완료 (2026-03-03) — KIS API 듀얼 환경 분리
- **Sprint 13 (Phase 6):** 완료 (2026-03-03) — MVP 안정화 (긴급 버그 수정, 33개 테스트)
- **Sprint 14 (Phase 7):** 완료 (2026-03-03) — JWT 인증 + User 모델 확장, InvitationCode 모델
  - 관리자 API: GET/POST /admin/invitations, GET/PUT /admin/users (승인/비활성화)
  - 브랜치: sprint14, PR: #21, #22
- **Sprint 15 (Phase 7):** 완료 (2026-03-03) — 사용자별 전략/백테스트 데이터 격리
  - 전략 clone API, 프리셋 토글 차단 UI, 45개 테스트 통과
  - 브랜치: sprint-15
- **Sprint 16 (Phase 8):** 계획 수립 완료 (2026-03-03)
  - 범위: 관리자 대시보드 UI + 초대코드 회원가입 플로우 완성
  - 11개 Task (Task 0~11), 브랜치: sprint-16
  - 계획 파일: /docs/sprint/sprint16.md

## 핵심 파일 경로
- ROADMAP: /ROADMAP.md
- PRD: /docs/prd.md
- 스프린트 계획: /docs/sprint/sprint{N}.md
- plan 파일: /Users/choijiseon/.claude/plans/ 디렉토리

## DB 테이블 목록 (Sprint 1 설계)
users, watchlist_groups, watchlist_items, strategies, strategy_params, orders, order_logs, portfolio_snapshots, backtest_results, system_settings

## 개발 규칙
- karpathy-guidelines 준수 필수 (plan 모드에서)
- 스킬 위치: /Users/choijiseon/.claude/plugins/marketplaces/karpathy-skills/skills/karpathy-guidelines/SKILL.md
- writing-plans 스킬: /Users/choijiseon/.claude/plugins/cache/claude-plugins-official/superpowers/4.3.1/skills/writing-plans/SKILL.md
- 언어: 한국어 (코드 주석, 커밋, 문서), 변수명은 영어
- 사용자 수동 작업은 deploy.md에 정리
- 스프린트 시작 시 sprint{N} 브랜치 생성

## Plan 파일 형식 참고
- Sprint 0 plan: agile-squishing-breeze.md (간결, Task 단위, 검증 포함)
- Context -> Task 목록 -> 실행 순서 -> 제외 범위 -> 검증 계획 구조
- writing-plans 스킬: 각 Task에 Files, Step 단위, 검증 명령, 완료 기준, Commit 메시지 포함

## Sprint 1 설계 결정 사항 (Sprint 2에서 참고)
- CORS: allow_origins=["*"] + allow_credentials=False
- Docker 빌드 컨텍스트: 프로젝트 루트(.)
- Next.js hostname: -H 0.0.0.0
- Alembic: psycopg2 동기 드라이버 (마이그레이션 전용)
- Tailwind CSS v4: config 파일 불필요, PostCSS 플러그인 방식
- config.py: pydantic-settings, model_config extra="ignore"

## Sprint 2 설계 결정 사항 (Sprint 3에서 참고)
- 인증: HMAC-SHA256 서명 토큰, zustand persist로 localStorage에 저장
- API 클라이언트: fetch 기반, Bearer 토큰 자동 첨부 (`frontend/src/lib/api/client.ts`)
- TanStack Query: staleTime 1분 기본 설정
- 레이아웃: AppLayout(flex h-screen) -> AppSidebar(w-56) + AppHeader(h-14) + main
- shadcn/ui: Neutral 색상, oklch 색상 체계, dark 모드 변수 정의됨

## Sprint 3 핵심 주의사항
- Lightweight Charts: SSR 호환 안됨 -> "use client" + useEffect 내 초기화 필수
- Recharts: React 19 지원 확인됨
- Mock 데이터: /frontend/src/lib/mock/ 디렉토리에 분리, TanStack Query queryFn으로 감싸서 API 교체 용이
- 한국 주식 UI 관례: 상승=빨간색, 하락=파란색
- 사이드바 6개 메뉴 고정: dashboard, watchlist, strategy, backtest, orders, settings
- 포트폴리오 상세 화면은 대시보드 하단 섹션으로 통합 (별도 라우트 없음)

## Sprint 4 핵심 주의사항
- 기존 스캐폴딩 페이지 4개 (strategy, backtest, orders, settings) 교체 필요
- shadcn/ui 추가 설치 필요: alert-dialog, sonner, toggle, radio-group, textarea, accordion
- 전략 파라미터 UI: Slider + 숫자 Input + Select 3가지 타입 대응
- 백테스팅 수익 곡선: Recharts LineChart + 벤치마크 비교 Line
- 긴급 전체 매도: AlertDialog 확인 모달 필수 (UX 안전장치)
- 설정 화면: max-w-3xl 제한하여 과도한 폼 너비 방지
- 주문 내역: 상태별 Badge 색상 - FILLED(초록), PENDING(노랑), CANCELLED(회색)
- Mock delay: 300~700ms 범위 (Sprint 3 패턴 유지)

## Sprint 16 핵심 주의사항
- 관리자 백엔드 API(admin.py)는 이미 완성 — 프론트엔드 UI만 추가
- auth-store에 role 필드 없을 수 있음 → /auth/me 엔드포인트 추가 필요 여부 확인 필수
- useSearchParams()는 Next.js App Router에서 반드시 Suspense로 감싸야 함
- shadcn/ui table, select, badge 컴포넌트 설치 여부 사전 확인 필요
- 사이드바에 관리자 메뉴는 role === 'admin' 조건부로만 표시 (일반 유저 노출 금지)
- /register 는 middleware.ts publicPaths에 추가해야 함 (인증 없이 접근 가능해야 함)
- admin_user, client_with_admin 픽스처를 conftest.py에 추가해야 함

## Sprint 10 핵심 주의사항
- 표준 에러 응답 스키마: `{"error": {"code": "...", "message": "...", "detail": "..."}}` 형식
- 글로벌 예외 핸들러: AppError, IntegrityError, OperationalError, Exception 4가지 등록
- JSON 로깅: python-json-logger 2.0.7, pythonjsonlogger.JsonFormatter 사용
- Request ID 미들웨어: X-Request-ID 헤더, uuid4()[:8] 축약 형식
- pytest 테스트 DB: SQLite 인메모리(aiosqlite) 사용, PostgreSQL 의존성 제거
- Mock→API 전환 대상: orders/page.tsx, settings/page.tsx, backtest/page.tsx
- Next.js Error Boundary 3종: error.tsx(라우트), global-error.tsx(루트), not-found.tsx(404)
- TanStack Query mutationCache.onError: 개별 onError 없는 mutation에만 글로벌 toast.error 적용
- API 클라이언트 타임아웃: 30초(30_000ms), AbortController 기반
