# AutoTrader KR - PRD to Roadmap 메모리

## 프로젝트 개요
- **프로젝트명:** AutoTrader KR (주식 자동매매 웹앱)
- **PRD 위치:** `/docs/prd.md` (v1.0 MVP, 2026-02-28)
- **ROADMAP 위치:** `/ROADMAP.md`
- **팀 규모:** 1-2인 소규모 개발팀
- **MVP 대상:** 개인 사용자 1인 (개발자 본인)

## 기술 스택 결정사항
- Frontend: Next.js 16+ (App Router), TailwindCSS v4, shadcn/ui, TanStack Query, zustand
- Backend: FastAPI (Python), SQLAlchemy 2.x, Alembic
- DB: PostgreSQL 16, Redis 7
- 증권 API: python-kis (PyKIS) 2.x
- 기술 분석: pandas-ta, vectorbt (백테스팅)
- 인프라: Docker Compose + GitHub Actions → AWS Lightsail
- 알림: python-telegram-bot 22.x
- 인증: JWT (python-jose) + bcrypt

## 로드맵 구조 (진행 현황)
- Phase 0: 환경 준비 — ✅ 완료 (Sprint 0)
- Phase 1: 기반 구축 — ✅ 완료 (Sprint 1~2)
- Phase 2: 프론트엔드 UI — ✅ 완료 (Sprint 3~4)
- Phase 3: 백엔드 핵심 — ✅ 완료 (Sprint 5~7)
- Phase 4: 부가 기능 — ✅ 완료 (Sprint 8~9)
- Phase 5: 안정화/데모 모드 — ✅ 완료 (Sprint 10~11)
- Phase 6: KIS 듀얼환경/MVP 안정화 — ✅ 완료 (Sprint 12~13)
- Phase 7: JWT 인증/사용자 격리 — ✅ 완료 (Sprint 14~15)
- Phase 8: 관리자 대시보드 — ✅ 완료 (Sprint 16)
- Phase 9: 프로덕션 배포 준비 — ✅ 완료 (Sprint 17)
- Phase 10: 설정 UX 개선 — ✅ 완료 (Sprint 18)
- Phase 11: 글로벌 종목 검색 — ✅ 완료 (Sprint 19)
- Phase 12: CI/CD 전환 — ✅ 완료 (Sprint 20)
- Phase 13: 버그 수정/안정화 — ✅ 완료 (Sprint 21)
- Phase 14: 백테스트 DB 캐싱 — ✅ 완료 (Sprint 22)
- Phase 15: 전략 테스팅 업그레이드 — ✅ 완료 (Sprint 23~25)
- Phase 16 이후: ROADMAP.md 참조

## 주요 설계 원칙
- 프론트엔드 먼저 개발 → 피드백 수집 → 백엔드 구현 순서
- 안전장치 필수: 일일 손실 한도, 주문 횟수, 단일 종목 비중 제한
- 모의투자 환경에서 충분한 검증 후 실전 전환

## 주요 리스크
- 한국투자증권 API Rate Limit (모의: 초당 5건)
- WebSocket 동시 등록 41건 제한
