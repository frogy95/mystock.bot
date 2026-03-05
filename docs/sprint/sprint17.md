# Sprint 17: MVP 프로덕션 배포 준비

**Goal:** Docker 프로덕션 환경을 구성하고 EC2 배포를 위한 인프라를 준비한다.

**Architecture:** 개발용 `docker-compose.yml`과 분리된 `docker-compose.prod.yml`을 작성하고, 멀티스테이지 Dockerfile로 이미지를 경량화한다. Nginx를 리버스 프록시로 추가하여 80 포트 단일 진입점을 구성한다.

**Tech Stack:** Docker (멀티스테이지 빌드), Docker Compose v2, Nginx, Gunicorn, Next.js standalone output

---

## 개요

- **스프린트 번호:** Sprint 17
- **브랜치:** sprint-17
- **시작일:** 2026-03-04
- **완료일:** 2026-03-05
- **상태:** 완료
- **PR:** #26

## 목표

개발 환경에서 검증된 애플리케이션을 프로덕션 EC2 인스턴스에 배포할 수 있도록 Docker 프로덕션 설정 일체를 구성한다.

### 핵심 목표
1. 프로덕션 Dockerfile 작성 (backend/frontend 멀티스테이지, 비-root 실행)
2. `docker-compose.prod.yml` 작성 (외부 포트 최소화, restart 정책, 로그 rotation)
3. Nginx 리버스 프록시 구성 (80 포트, /api/* → backend, / → frontend)
4. 보안 설정 강화 (DEBUG=False 경고, CORS 환경변수화, 헬스체크 503)
5. EC2 배포 절차 문서화 (`deploy.md`)

## 구현 범위

### 포함 항목 (Must Have)
- `.dockerignore` — 빌드 컨텍스트 최적화 (node_modules, __pycache__, .env 제외)
- `frontend/next.config.ts` — `output: 'standalone'`, `poweredByHeader: false`
- `backend/Dockerfile.prod` — 멀티스테이지 빌드, `appuser` 비-root 실행
- `frontend/Dockerfile.prod` — 멀티스테이지 빌드, standalone 출력 복사
- `docker-compose.prod.yml` — postgres/redis 외부 포트 미노출, `restart: unless-stopped`, 로그 rotation
- `docker/nginx/nginx.conf` — 리버스 프록시 설정
- `deploy.md` — EC2 배포 절차, 체크리스트, 5일 안정 운영 가이드

### 제외 항목 (Out of Scope)
- HTTPS/TLS 인증서 설정 (별도 스프린트 또는 수동 적용)
- GitHub Actions CI/CD 자동 배포 (향후 Phase)
- 모니터링/알림 연동 (Prometheus, Grafana 등)

## 기술적 접근 방법

### 멀티스테이지 빌드 전략

```
backend/Dockerfile.prod
  Stage 1 (builder): Python 의존성 설치 (requirements.txt)
  Stage 2 (runtime): slim 이미지 + 의존성 복사 + appuser 실행
  실행: gunicorn -k uvicorn.workers.UvicornWorker

frontend/Dockerfile.prod
  Stage 1 (deps): node_modules 설치
  Stage 2 (builder): next build (standalone 출력)
  Stage 3 (runner): standalone 복사 + nextjs 비-root 실행
```

### Nginx 라우팅
```
/ (80 포트)
  /api/*     → http://backend:8000
  /          → http://frontend:3000
```

### 보안 설정
- `CORS_ORIGINS` 환경변수로 허용 오리진 관리
- `DEBUG=False` 상태에서 기본 SECRET_KEY 사용 시 경고 로그
- 헬스체크 엔드포인트: 503 반환 (unhealthy 감지)
- postgres/redis: 내부 네트워크만 노출 (외부 포트 바인딩 제거)

## 완료 기준 (Definition of Done)

- ✅ `.dockerignore` 추가 (빌드 컨텍스트 최적화)
- ✅ `frontend/next.config.ts`: output='standalone', poweredByHeader=false 설정
- ✅ 프로덕션 Dockerfile 작성 (backend/frontend 멀티스테이지 빌드, 비-root 실행)
- ✅ `docker-compose.prod.yml` 작성 (postgres/redis 외부 포트 미노출, restart 정책, 로그 rotation)
- ✅ Nginx 리버스 프록시 추가 (80 포트, /api/* → backend, / → frontend)
- ✅ CORS_ORIGINS 환경변수화, DEBUG=False 시 시크릿 키 경고, 헬스체크 503 반환
- ✅ `gunicorn>=22.0.0` 의존성 추가
- ✅ deploy.md: EC2 프로덕션 배포 절차, 체크리스트, 5일 안정 운영 가이드 추가
- ✅ 빌드/테스트 버그 3건 수정 (.dockerignore tests 제외, Dockerfile.prod npm ci, test 패치)
- ✅ pytest 통과 (기존 테스트 회귀 없음)

## 산출물

| 파일 | 유형 | 설명 |
|------|------|------|
| `.dockerignore` | 신규 | 빌드 컨텍스트 최적화 |
| `backend/Dockerfile.prod` | 신규 | 백엔드 프로덕션 멀티스테이지 빌드 |
| `frontend/Dockerfile.prod` | 신규 | 프론트엔드 프로덕션 멀티스테이지 빌드 |
| `docker-compose.prod.yml` | 신규 | 프로덕션 Docker Compose 설정 |
| `docker/nginx/nginx.conf` | 신규 | Nginx 리버스 프록시 설정 |
| `frontend/next.config.ts` | 수정 | standalone output, poweredByHeader=false |
| `backend/requirements.txt` | 수정 | gunicorn>=22.0.0 추가 |
| `backend/app/core/config.py` | 수정 | CORS_ORIGINS 환경변수화, SECRET_KEY 경고 |
| `backend/app/api/v1/health.py` | 수정 | unhealthy 시 503 반환 |
| `deploy.md` | 수정 | EC2 배포 절차, 체크리스트 추가 |

## 버그 수정 내역 (Sprint 17 후속)

빌드/테스트 과정에서 발견된 버그 3건을 수정하여 커밋 `cd5a83f`에 반영:

1. **`.dockerignore` tests 제외 오류** — 테스트 파일이 프로덕션 이미지에 포함되는 문제 수정
2. **`frontend/Dockerfile.prod` npm ci 오류** — 의존성 설치 명령 수정
3. **테스트 패치 오류** — pytest 실행 시 발생하는 패치 관련 오류 수정

## 수동 검증 항목

배포 후 사용자가 직접 확인해야 하는 항목 (deploy.md 참조):

- ⬜ `docker compose -f docker-compose.prod.yml up --build -d` 실행
- ⬜ `http://<EC2-IP>` 접속하여 프론트엔드 로딩 확인
- ⬜ `http://<EC2-IP>/api/v1/health` 200 응답 확인
- ⬜ 관리자 로그인 및 기능 동작 확인
- ⬜ 5일 안정 운영 모니터링 (CPU, 메모리, 디스크)
