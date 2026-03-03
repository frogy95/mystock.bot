# Sprint 14: JWT 인증 + User 모델 확장

## 개요

멀티유저 MVP 1단계: HMAC-SHA256 커스텀 토큰을 JWT로 교체하고, User 모델을 확장하여 회원가입/로그인 기반을 마련한다.

## 완료 항목

- ✅ requirements.txt에 `python-jose[cryptography]`, `passlib[bcrypt]` 추가
- ✅ config.py에 JWT 설정 추가 (`JWT_SECRET`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`, `ADMIN_EMAIL`)
- ✅ User 모델 확장 (`email`, `password_hash`, `role`, `invited_by`, `is_approved`)
- ✅ InvitationCode 모델 신규 생성 (`code`, `created_by`, `used_by`, `expires_at`, `is_used`)
- ✅ `core/auth.py` JWT 기반으로 재작성 (`create_access_token`, `create_refresh_token`, `get_current_user` → User 객체 반환)
- ✅ `schemas/auth.py` 확장 (`RegisterRequest`, `RefreshRequest`, `TokenResponse.refresh_token` 추가)
- ✅ `api/v1/auth.py` 재작성 (`/register`, `/login`, `/refresh`, `/demo`)
- ✅ `api/v1/admin.py` 신규 (초대 코드 CRUD, 사용자 목록/승인/비활성화)
- ✅ `api/v1/router.py`에 admin 라우터 포함
- ✅ 전체 라우터 의존성 업데이트 (`current_user: str` → `current_user: User`, `get_user_id()` 제거)
- ✅ `core/deps.py` 정리 (`get_user_id` 함수 제거)
- ✅ Alembic 마이그레이션 생성 (`c3d4e5f6a7b8`)
- ✅ 프론트엔드 `auth-store.ts` 업데이트 (refreshToken 추가, setToken 메서드)
- ✅ 프론트엔드 `client.ts` 업데이트 (401 시 자동 토큰 갱신)
- ✅ 로그인 페이지 이메일 방식으로 변경
- ✅ `scripts/seed.py` 관리자 계정 생성 시 JWT 필드 포함

## 핵심 변경 사항

### 인증 방식 변경
- 기존: `username:expires_at:signature` HMAC 토큰
- 신규: JWT (HS256) - access token (1시간) + refresh token (30일)

### 회원가입 플로우
1. 관리자가 초대 코드 생성 (`POST /api/v1/admin/invitations`)
2. 사용자가 초대 코드로 회원가입 (`POST /api/v1/auth/register`)
3. 회원가입 후 `is_approved=false` 상태 (관리자 승인 대기)
4. 관리자 승인 후 로그인 가능 (`PUT /api/v1/admin/users/{id}/approve`)

### 데모 모드
- 기존 `POST /auth/demo` 엔드포인트 유지
- 데모 유저는 가상 User 객체 반환 (DB 비의존)

## 환경변수 추가 필요

```env
JWT_SECRET=<랜덤 시크릿 키>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30
ADMIN_EMAIL=admin@mystock.bot
```

## 배포 절차

1. 환경변수 추가 (`.env` 파일)
2. `pip install -r requirements.txt` (python-jose, passlib 설치)
3. `alembic upgrade head` (User 컬럼 추가, InvitationCode 테이블 생성)
4. `python scripts/seed.py` (기존 운영 중이면 스킵 - 마이그레이션에서 자동 처리)

## 검증 결과

- [Sprint 14 검증 보고서](sprint14/validation-report.md)

**자동 검증 결과:** 59/59 항목 통과 (100%)
- Python 파일 문법, JWT 설정, 인증/관리자 API 엔드포인트, User 모델 필드, 라우터 의존성, Alembic 마이그레이션, 프론트엔드 auth-store, client.ts 401 갱신 로직, JWT 보안 토큰 타입, 관리자 보안 로직 전부 통과

**수동 검증 필요:** Docker 환경에서 실제 로그인, 마이그레이션, 회원가입 플로우 확인 필요 (deploy.md 섹션 14 참고)

---

## 다음 스프린트 (Sprint 15)

- Strategy/BacktestResult 모델에 user_id FK 추가 (데이터 격리)
- KIS 설정 멀티유저화
- 스케줄러 멀티유저화
