# Sprint 20: GHCR 이미지 기반 CI/CD 전환

**Goal:** `docker-compose.prod.yml`의 `build:` 방식을 제거하고 GHCR 이미지 기반으로 전환하여, CD 워크플로우가 `docker compose pull && up -d`만으로 30초 내 자동 배포되도록 개선한다.

**Architecture:** GHCR(GitHub Container Registry) 3개 이미지 (backend / frontend / nginx) + SCP compose 파일 자동 전송

---

## 개요

- **스프린트 번호:** Sprint 20
- **브랜치:** sprint20
- **시작일:** 2026-03-06
- **완료일:** 2026-03-06
- **상태:** 완료
- **PR:** https://github.com/frogy95/mystock.bot/pull/34 (sprint20 → develop, CI 통과)

## 배경 및 문제

Sprint 19 완료 후 실서버 검증 과정에서 다음 문제가 발견됐습니다:

- `docker-compose.prod.yml`이 `build:` 방식이라 CD의 `docker compose pull`이 실제로 이미지를 갱신하지 못함
- nginx가 GHCR에 push되지 않아 pull 불가
- CD 워크플로우가 compose 파일을 서버에 전달하지 않아 `git pull` 없이는 반영 불가

## 구현 내용

### 변경 파일

| 파일 | 유형 | 설명 |
|------|------|------|
| `docker-compose.prod.yml` | 수정 | `build:` 3개 제거, nginx `image: ghcr.io/frogy95/mystock-bot-nginx:latest` 추가 |
| `.github/workflows/deploy.yml` | 수정 | `NGINX_IMAGE` env 추가, nginx 빌드+push 스텝, SCP compose 파일 전송 스텝 추가 |
| `.github/workflows/ci.yml` | 수정 | nginx 이미지 빌드 검증 스텝 추가 |
| `docs/ci-policy.md` | 수정 | nginx 이미지 테이블, SCP 방식 CD 설명, 롤백 절차 업데이트 |

### 핵심 변경사항

1. **docker-compose.prod.yml**: `build:` 블록 완전 제거 → 서버가 `docker compose pull`로 최신 이미지를 받을 수 있게 됨
2. **nginx GHCR 이미지**: CI에서 nginx 빌드 검증, CD에서 nginx 이미지 빌드+push 추가
3. **SCP 파일 전송**: `appleboy/scp-action`으로 compose 파일을 서버에 자동 전송 — `git pull` 의존성 제거
4. **30초 배포**: `docker compose pull && up -d`만으로 프로덕션 배포 완료

## 해결된 문제

- Sprint 19 실서버 배포 실패 원인(`build:` 방식) 구조적 해결
- nginx가 GHCR에 push 안 되던 문제 해결
- compose 파일 미갱신 문제 → SCP로 해결

## 검증 결과

### 자동 검증 완료 (CI)
- ✅ pytest 통과 (PR #34 CI 체크)
- ✅ Docker 빌드 3종 통과 (backend / frontend / nginx)
- ✅ `docker-compose.prod.yml` 구문 정상 — 모든 서비스 `image:` 기반

### 수동 검증 필요
- ⬜ develop merge 후 로컬 Docker 검증 (`docker compose up --build`)
- ⬜ main merge 후 GHCR 3종 이미지 push 확인
- ⬜ 실서버 헬스체크 및 컨테이너 상태 확인

## 코드 리뷰 요약

- Critical/High 이슈: 없음
- Medium: `appleboy/scp-action@v0.1.7` SHA 고정 미적용 (공급망 보안 — MVP 수준 허용)
- Low: CD에 `--remove-orphans` 미사용 / 배포 후 헬스체크 단계 부재

## 검증 결과

- [검증 보고서](sprint20/)
