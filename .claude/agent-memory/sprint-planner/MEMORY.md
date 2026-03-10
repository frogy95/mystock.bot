# Sprint Planner 메모리

## 프로젝트 개요
- **프로젝트명:** AutoTrader KR (mystock.bot)
- **목표:** 한국투자증권 Open API 기반 KOSPI/KOSDAQ 퀀트 전략 자동매매 웹앱
- **원격 저장소:** https://github.com/frogy95/mystock.bot.git
- **팀 규모:** 1-2인

## 기술 스택
- Frontend: Next.js 16+ (App Router) + TypeScript + TailwindCSS v4 + shadcn/ui + TanStack Query + zustand
- Backend: FastAPI (Python) + SQLAlchemy 2.x (asyncpg) + Alembic
- DB: PostgreSQL 16, Redis 7
- 증권 API: python-kis (PyKIS) 2.x
- 알림: python-telegram-bot 22.x
- 배포: Docker Compose + GitHub Actions → AWS Lightsail

## 스프린트 현황

**완료된 스프린트 (Sprint 0~27)**:
- Sprint 0~27 완료. 상세 내용은 `docs/sprint/sprint{N}.md` 및 `docs/deploy-history/` 참조.
- Sprint 26 (2026-03-09): 개발 프로세스 정책 재정비
- Sprint 27 (2026-03-09): 관심종목 시세 표시 + 백테스팅 UX 개선 (SSE 스트리밍, O(n) 최적화, 종목탭)

**현재 상태**:
- 다음 사용 가능한 스프린트 번호: **Sprint 29**
- 최신 pytest: 51 passed (Sprint 27~28 기준)
- 추가된 테이블: chart_data_cache (Sprint 22)
- Sprint 28 (2026-03-10): 전략 알고리즘 보강 — 기존 전략 3종 개선 + 신규 전략 3종 추가
  - 신규 지표: MOMENTUM_20/60, SMA60_SLOPE, calculate_beta(Vasicek w=0.5), get_market_returns
  - 신규 전략: MACDTrend(technical), LowBetaMomentum(quantitative), MomentumRiskSwitch(quantitative)
  - 전략 레지스트리: 3 → 6개 확장
  - 알고리즘 설계 문서: docs/algorithm.md (BAB, Dual Momentum 이론 → 구현)

## 핵심 파일 경로
- ROADMAP: `/ROADMAP.md`
- PRD: `/docs/prd.md`
- 스프린트 계획: `/docs/sprint/sprint{N}.md`
- 개발 프로세스 정책: `/docs/dev-process.md` (검증 원칙, 워크플로우, 문서 관리)
- plan 파일: `/Users/choijiseon/.claude/plans/`

## DB 테이블 목록
users, watchlist_groups, watchlist_items, strategies, strategy_params, orders, order_logs, portfolio_snapshots, backtest_results, system_settings, chart_data_cache

InvitationCode 모델 추가 (Sprint 14)

## 개발 규칙
- karpathy-guidelines 준수 필수 (plan 모드에서)
- 검증/프로세스 정책 → `/docs/dev-process.md` 참조 (Single Source of Truth)
- 언어: 한국어 (코드 주석, 커밋, 문서), 변수명은 영어
- 스프린트 시작 시 sprint{N} 브랜치 생성 (worktree 사용 금지)
- 사용자 수동 작업은 deploy.md에 정리 (완료 기록은 docs/deploy-history/ 아카이브)

## 핵심 설계 결정사항
- 인증: JWT(python-jose) + bcrypt 직접 사용 (Sprint 14)
- API 클라이언트: `frontend/src/lib/api/client.ts` (fetch 기반, Bearer 토큰 자동 첨부)
- Mock 데이터: `/frontend/src/lib/mock/` 디렉토리 분리
- KIS API 키: DB(`system_settings`)에서 관리 (Sprint 12 이후, `.env` 아님)
- 한국 주식 색상: 상승=빨간색, 하락=파란색
- Playwright: Chromium 사용 (Chrome 세션 충돌 방지)

## Plan 파일 형식 참고
- Context → Task 목록 → 실행 순서 → 제외 범위 → 검증 계획 구조
- writing-plans 스킬: 각 Task에 Files, Step 단위, 검증 명령, 완료 기준, Commit 메시지 포함
