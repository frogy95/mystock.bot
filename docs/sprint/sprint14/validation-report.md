# Sprint 14 검증 보고서

**검증 일시:** 2026-03-03
**검증 방법:** 정적 코드 분석 (자동)
**PR:** https://github.com/frogy95/mystock.bot/pull/21

---

## 1. 코드 리뷰 결과

### Critical/High 이슈: 없음

### Medium 이슈 (추후 개선 권장)

| # | 파일 | 내용 | 우선순위 |
|---|------|------|----------|
| 1 | `backend/app/api/v1/auth.py` L84-88 | `register` 엔드포인트가 회원가입 성공 후 빈 access_token("")을 반환합니다. 회원가입 후 즉시 로그인이 안 되는 구조(관리자 승인 대기)이므로 의도적인 설계이지만, API 응답에 빈 토큰 대신 `202 Accepted`나 별도 응답 스키마를 사용하면 더 명확합니다. | Medium |
| 2 | `backend/app/core/deps.py` | 파일 내용이 완전히 비어 있습니다. 향후 공통 의존성이 추가될 때 파일이 존재하므로 괜찮으나, 파일 레벨 주석만 있고 실제 코드가 없어 혼란을 줄 수 있습니다. | Low |
| 3 | `frontend/src/lib/api/client.ts` L74-80 | 토큰 갱신 후 재요청(retryResponse)이 실패하는 경우(`!retryResponse.ok`)의 에러 처리가 없습니다. 현재 코드는 갱신 실패(`newToken === null`) 경우만 로그아웃을 처리하고, 재요청 실패는 별도 처리 없이 아래 logout 로직으로 흐릅니다. | Medium |
| 4 | `backend/app/models/user.py` L27 | `email` 필드가 `nullable=True`로 설정되어 있어, 기존 사용자(단일 유저 방식)와의 하위 호환을 위해서입니다. 신규 사용자 등록 API에서는 이메일을 필수로 받으므로 데이터 정합성은 유지됩니다. 추후 완전 전환 후에는 `nullable=False`로 변경을 권장합니다. | Low |

### 긍정적 평가

- JWT 토큰에 `type` 필드(`access`/`refresh`)가 포함되어 토큰 타입 혼용 공격을 방지합니다.
- `secrets.token_urlsafe(16)`으로 초대 코드를 생성하여 추측 불가능한 코드를 보장합니다.
- 관리자가 자기 자신을 비활성화하지 못하도록 보호 로직이 구현되어 있습니다.
- 전체 9개 라우터에서 `current_user: str` 의존성이 `current_user: User` 객체로 일관되게 교체되었습니다.
- bcrypt 해싱과 `passlib.context.CryptContext`를 사용하여 안전한 비밀번호 저장을 구현했습니다.
- refresh token 엔드포인트에서 `type != "refresh"` 검증으로 토큰 타입 혼용을 방지합니다.
- 데모 유저 처리를 가상 User 객체로 일관되게 구현하여 DB 의존 없이 동작합니다.
- 프론트엔드에서 로그인 페이지(`/login`)에서의 401 처리를 분리하여 무한 갱신 루프를 방지합니다.

---

## 2. 자동 검증 결과 (정적 분석)

### 2-1. Python 파일 문법 검증

| 파일 | 결과 |
|------|------|
| `backend/app/core/auth.py` | ✅ |
| `backend/app/api/v1/auth.py` | ✅ |
| `backend/app/api/v1/admin.py` | ✅ |
| `backend/app/models/user.py` | ✅ |
| `backend/app/models/invitation.py` | ✅ |
| `backend/app/schemas/auth.py` | ✅ |

### 2-2. JWT 설정 구조 검증

| 항목 | 결과 |
|------|------|
| JWT_SECRET 기본값 change-me 형태 | ✅ |
| JWT_ALGORITHM 기본값 HS256 | ✅ |
| ACCESS_TOKEN_EXPIRE_MINUTES 설정 | ✅ |
| REFRESH_TOKEN_EXPIRE_DAYS 설정 | ✅ |
| ADMIN_EMAIL 설정 | ✅ |

### 2-3. 인증 API 엔드포인트 존재 확인

| 엔드포인트 | 결과 |
|-----------|------|
| POST /auth/register | ✅ |
| POST /auth/login | ✅ |
| POST /auth/refresh | ✅ |
| POST /auth/demo | ✅ |

### 2-4. 관리자 API 엔드포인트 존재 확인

| 엔드포인트 | 결과 |
|-----------|------|
| GET /admin/invitations | ✅ |
| POST /admin/invitations | ✅ |
| GET /admin/users | ✅ |
| PUT /admin/users/{id}/approve | ✅ |
| PUT /admin/users/{id}/deactivate | ✅ |

### 2-5. User 모델 필드 검증

| 필드 | 결과 |
|------|------|
| email | ✅ |
| password_hash | ✅ |
| role | ✅ |
| invited_by | ✅ |
| is_approved | ✅ |
| is_active | ✅ |

### 2-6. 전체 라우터 의존성 업데이트 확인

| 파일 | 결과 |
|------|------|
| backtest.py (3개 의존성) | ✅ |
| holdings.py (5개 의존성) | ✅ |
| orders.py (3개 의존성) | ✅ |
| safety.py (3개 의존성) | ✅ |
| settings.py (1개 의존성) | ✅ |
| stocks.py (5개 의존성) | ✅ |
| strategies.py (6개 의존성) | ✅ |
| system_settings.py (3개 의존성) | ✅ |
| watchlist.py (7개 의존성) | ✅ |

### 2-7. Alembic 마이그레이션 검증

| 항목 | 결과 |
|------|------|
| Sprint 14 마이그레이션 파일 존재 (`c3d4e5f6a7b8`) | ✅ |
| User 테이블 수정 포함 | ✅ |
| invitation_codes 테이블 생성 포함 | ✅ |

### 2-8. 프론트엔드 auth-store 검증

| 항목 | 결과 |
|------|------|
| refreshToken 필드 존재 | ✅ |
| setToken 메서드 존재 | ✅ |
| login 시 refreshToken 저장 | ✅ |
| logout 시 refreshToken 초기화 | ✅ |
| persist 미들웨어 사용 | ✅ |
| refreshToken partialize 포함 | ✅ |

### 2-9. client.ts 401 자동 갱신 로직 검증

| 항목 | 결과 |
|------|------|
| tryRefreshToken 함수 존재 | ✅ |
| 401 상태 체크 | ✅ |
| /auth/refresh 엔드포인트 호출 | ✅ |
| 갱신 성공 후 재요청 | ✅ |
| 갱신 실패 시 logout + 리다이렉트 | ✅ |
| 로그인 페이지 예외 처리 | ✅ |

### 2-10. JWT 보안 토큰 타입 검증

| 항목 | 결과 |
|------|------|
| access token에 type=access 포함 | ✅ |
| refresh token에 type=refresh 포함 | ✅ |
| refresh 엔드포인트에서 type=refresh 검증 | ✅ |

### 2-11. requirements.txt JWT 패키지 확인

| 패키지 | 결과 |
|--------|------|
| python-jose[cryptography]>=3.3.0 | ✅ |
| passlib[bcrypt]>=1.7.4 | ✅ |

### 2-12. 관리자 API 보안 로직 검증

| 항목 | 결과 |
|------|------|
| require_admin 의존성 함수 존재 | ✅ |
| 자기 자신 비활성화 방지 로직 | ✅ |
| secrets.token_urlsafe로 초대 코드 생성 | ✅ |
| 초대 코드 만료 시간 처리 | ✅ |

---

## 3. 종합 결과

| 분류 | 항목 수 | 통과 | 실패 |
|------|---------|------|------|
| Python 문법 검증 | 6 | 6 | 0 |
| JWT 설정 | 5 | 5 | 0 |
| 인증 API 엔드포인트 | 4 | 4 | 0 |
| 관리자 API 엔드포인트 | 5 | 5 | 0 |
| User 모델 필드 | 6 | 6 | 0 |
| 라우터 의존성 업데이트 | 9 | 9 | 0 |
| Alembic 마이그레이션 | 3 | 3 | 0 |
| 프론트엔드 auth-store | 6 | 6 | 0 |
| client.ts 갱신 로직 | 6 | 6 | 0 |
| JWT 보안 | 3 | 3 | 0 |
| requirements.txt | 2 | 2 | 0 |
| 관리자 보안 | 4 | 4 | 0 |
| **합계** | **59** | **59** | **0** |

**자동 검증 결과: 59/59 항목 통과 (100%)**

---

## 4. 수동 검증 필요 항목

Docker 환경 실행 후 직접 확인이 필요한 항목입니다.

- ⬜ `alembic upgrade head` 실행 후 DB 스키마 확인
- ⬜ 관리자 이메일(`admin@mystock.bot`)로 로그인 및 JWT 토큰 수신 확인
- ⬜ 초대 코드 생성 (`POST /api/v1/admin/invitations`)
- ⬜ 새 사용자 초대 코드로 회원가입 (`POST /api/v1/auth/register`)
- ⬜ 관리자 승인 후 신규 사용자 로그인 확인
- ⬜ refresh token으로 access token 갱신 확인
- ⬜ 데모 모드 여전히 정상 동작 확인 (`POST /api/v1/auth/demo`)
- ⬜ 프론트엔드 로그인 페이지에서 이메일 로그인 동작 확인
- ⬜ 401 발생 시 자동 토큰 갱신 동작 확인
