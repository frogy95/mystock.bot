# Sprint Planner 메모리

## 프로젝트 개요
- **프로젝트명:** AutoTrader KR (mystock.bot)
- **목표:** 한국투자증권 Open API 기반 KOSPI/KOSDAQ 퀀트 전략 자동매매 웹앱
- **전체 기간:** 2026-03-02 ~ 2026-05-10 (10주, 11 스프린트)
- **팀 규모:** 1-2인
- **원격 저장소:** https://github.com/frogy95/mystock.bot.git

## 기술 스택
- Frontend: Next.js 16+ (App Router) + TypeScript + TailwindCSS + shadcn/ui
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
- **Sprint 1 (Phase 1):** 계획 수립 완료 (2026-03-01)
  - 범위: FastAPI 초기화, Next.js 초기화, Docker Compose 4서비스, DB 스키마 10테이블, Alembic, seed 3종 전략
  - 기간: 2026-03-02 ~ 2026-03-07

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
- 언어: 한국어 (코드 주석, 커밋, 문서), 변수명은 영어
- 사용자 수동 작업은 deploy.md에 정리

## Plan 파일 형식 참고
- Sprint 0 plan: agile-squishing-breeze.md (간결, Task 단위, 검증 포함)
- Context -> Task 목록 -> 실행 순서 -> 제외 범위 -> 검증 계획 구조
