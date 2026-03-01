# AutoTrader KR - PRD to Roadmap 메모리

## 프로젝트 개요
- **프로젝트명:** AutoTrader KR (주식 자동매매 웹앱)
- **PRD 위치:** `/docs/prd.md` (v1.0 MVP, 2026-02-28)
- **ROADMAP 위치:** `/ROADMAP.md`
- **팀 규모:** 1-2인 소규모 개발팀
- **MVP 대상:** 개인 사용자 1인 (개발자 본인)

## 기술 스택 결정사항
- Frontend: Next.js 16+ (App Router), TailwindCSS, shadcn/ui, TanStack Query, zustand
- Backend: FastAPI (Python), SQLAlchemy 2.x, Alembic
- DB: PostgreSQL 16, Redis 7
- 증권 API: python-kis (PyKIS) 2.x
- 기술 분석: pandas-ta (우선, TA-Lib 대안), Backtrader (백테스팅)
- 인프라: Docker Compose
- 알림: python-telegram-bot 22.x

## 로드맵 구조 (10주, 5 Phase)
- Phase 0: 환경 준비 (1-2일)
- Phase 1: 기반 구축 (Week 1-2) - Docker, DB, API 연동
- Phase 2: 프론트엔드 UI (Week 3-4) - Mock 데이터 기반 전체 화면
- Phase 3: 백엔드 핵심 (Week 5-7) - 전략, 자동매매, 안전장치
- Phase 4: 부가 기능 (Week 8-9) - 백테스팅, 텔레그램, WebSocket
- Phase 5: 안정화 (Week 10) - 통합 테스트, MVP 출시

## 주요 설계 원칙
- 프론트엔드 먼저 개발 -> 피드백 수집 -> 백엔드 구현 순서
- APScheduler(MVP) -> Celery(확장) 점진적 전환
- 모의투자 환경에서 충분한 검증 후 실전 전환
- 안전장치 필수: 일일 손실 한도, 주문 횟수, 단일 종목 비중 제한

## 주요 리스크
- 한국투자증권 API Rate Limit (모의: 초당 5건)
- WebSocket 동시 등록 41건 제한
- Backtrader GPL v3.0 라이선스 (멀티유저 오픈 시 검토 필요)
- TA-Lib C 라이브러리 설치 이슈 -> pandas-ta로 대체 가능
