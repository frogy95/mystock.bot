# Sprint 0 - Phase 0: 프로젝트 준비

**기간:** 2026-02-28
**완료일:** 2026-02-28
**상태:** ✅ 전체 완료 (자동화 + 수동 작업)
**커밋:** `cd3c6f3` → `origin/main` 푸시 완료
**목표:** Sprint 1 즉시 착수 가능한 프로젝트 뼈대 구성

---

## 완료된 작업

### 자동화 작업 (Claude 수행)

| # | 작업 | 파일/디렉토리 | 상태 |
|---|------|--------------|------|
| 1 | `.gitignore` 설정 | `.gitignore` | ✅ 완료 |
| 2 | `.env.example` 생성 | `.env.example` | ✅ 완료 |
| 3 | Monorepo 디렉토리 구조 생성 | `frontend/`, `backend/`, `docker/`, `docs/sprint/` | ✅ 완료 |
| 4 | 수동 작업 가이드 문서 생성 | `deploy.md` | ✅ 완료 |
| 5 | 스프린트 계획 문서 저장 | `docs/sprint/sprint0.md` | ✅ 완료 |

### 수동 작업 (사용자 수행 필요) — `deploy.md` 참조

- ✅ 한국투자증권 계좌 개설 및 KIS App Key 발급
- ✅ 텔레그램 봇 생성 및 토큰 발급
- ✅ 개발 도구 설치 확인 (Python 3.12.12, Node.js 25.6.0, Docker 29.2.1)
- ✅ `.env` 파일 생성 및 환경변수 입력 (전체 18개 키)

---

## 디렉토리 구조

```
mystock.bot/
├── .gitignore          # Git 추적 제외 패턴
├── .env.example        # 환경변수 예제
├── CLAUDE.md           # Claude Code 프로젝트 지침
├── ROADMAP.md          # 프로젝트 로드맵
├── deploy.md           # 수동 작업 가이드
├── frontend/           # Next.js 프론트엔드 (Sprint 1에서 초기화)
├── backend/            # FastAPI 백엔드 (Sprint 1에서 초기화)
├── docker/             # Docker 설정 (Sprint 1에서 구성)
└── docs/
    └── sprint/
        └── sprint0.md  # 이 파일
```

---

## Sprint 1 이관 항목

- Next.js 프론트엔드 초기화
- FastAPI 백엔드 초기화
- `docker-compose.yml` 작성
- 패키지 매니저 설정
- CI/CD 설정

---

## 검증 결과

1. ✅ `.env` 파일이 `git status`에 미표시 (gitignore 정상 동작)
2. ✅ 4개 디렉토리 (`frontend/`, `backend/`, `docker/`, `docs/sprint/`) 생성 확인
3. ✅ `.env.example` - KIS, 텔레그램, DB, Redis, 백엔드, 프론트엔드 키 포함
4. ✅ `deploy.md` - 모든 수동 작업 단계별 가이드 포함
5. ✅ `docs/sprint/sprint0.md` 파일 생성 완료
