# Sprint 11: 로그인 페이지 + 데모 모드

## 개요

| 항목 | 내용 |
|------|------|
| **스프린트** | Sprint 11 |
| **기간** | 2026-03-02 |
| **브랜치** | sprint-11 |
| **목표** | 로그인 페이지 구현 및 데모 모드 지원으로 서비스 진입점 완성 |

## 배경

기존에 백엔드 로그인 API(`POST /api/v1/auth/login`)는 존재했지만 프론트엔드에 로그인 페이지가 없어 토큰을 얻을 방법이 없었습니다. 모든 API가 `401 Unauthorized`로 실패하고 대시보드가 스켈레톤 로딩 상태에서 영원히 멈추는 문제를 해결합니다.

추가로 데모 보기 기능을 통해 비회원도 더미 데이터로 서비스를 체험할 수 있게 합니다.

## 구현 내용

### 백엔드

#### 1. 데모 인증 인프라
- `backend/app/core/auth.py` — `DEMO_USERNAME = "__demo__"`, `is_demo_user()` 헬퍼 추가
- `backend/app/api/v1/auth.py` — `POST /api/v1/auth/demo` 엔드포인트 추가 (비밀번호 없이 즉시 토큰 발급)

#### 2. 데모 더미 데이터 모듈
- `backend/app/services/demo_data.py` (신규) — 13개 더미 데이터 함수
  - 보유종목: 삼성전자, SK하이닉스, 카카오, LG화학, 삼성SDI
  - 전략: 골든크로스+RSI, 볼린저밴드반전, 가치+모멘텀
  - 관심종목: 반도체, 2차전지, 바이오 그룹
  - 주문내역, 포트폴리오 요약, 시스템설정, 안전장치, 백테스팅 등
  - 날짜는 오늘 기준 상대적으로 계산

#### 3. 라우터 데모 분기 (9개 파일)
- GET 요청: 데모 유저 감지 시 더미 데이터 반환
- POST/PUT/DELETE 요청: `403 "데모 모드에서는 사용할 수 없습니다."` 반환
- 수정 파일: `holdings.py`, `orders.py`, `strategies.py`, `watchlist.py`, `system_settings.py`, `safety.py`, `stocks.py`, `backtest.py`, `settings.py`

### 프론트엔드

#### 4. 로그인 페이지
- `frontend/src/app/login/page.tsx` (신규) — 좌우 분할 레이아웃
  - 왼쪽 패널 (데스크톱): mystock.bot 로고 + 기능 하이라이트 4개 (실시간시세, AI전략, 자동매매, 안전장치)
  - 오른쪽 패널: 아이디/비밀번호 폼 + "데모 보기" 버튼
  - 로그인: `POST /api/v1/auth/login` → 대시보드 이동
  - 데모: `POST /api/v1/auth/demo` → 대시보드 이동

#### 5. 조건부 레이아웃 + 인증 가드
- `frontend/src/components/layout/conditional-layout.tsx` (신규) — `/login`은 사이드바/헤더 없이 렌더링
- `frontend/src/components/layout/auth-guard.tsx` (신규) — Zustand hydration 완료 후 토큰 확인, 없으면 `/login` 리다이렉트
- `frontend/src/app/layout.tsx` — `AppLayout` → `ConditionalLayout` 교체

#### 6. Next.js 미들웨어 인증 가드
- `frontend/src/middleware.ts` (신규) — `auth-token` 쿠키 없으면 서버사이드에서 `/login` 리다이렉트

#### 7. 인증 스토어 보강
- `frontend/src/stores/auth-store.ts` — `isDemo()` 헬퍼 추가, `login()`/`logout()` 시 쿠키 동기화

#### 8. API 클라이언트 401 처리
- `frontend/src/lib/api/client.ts` — 401 응답 시 자동 로그아웃 + `/login` 리다이렉트 (로그인 페이지 자신은 제외)

#### 9. 헤더 업데이트
- `frontend/src/components/layout/app-header.tsx` — 사용자명 + 로그아웃 버튼 + 데모 모드 뱃지

## 검증 결과

### Playwright E2E 테스트 (TC-1 ~ TC-7 전부 통과)

| 시나리오 | 결과 | 설명 |
|----------|------|------|
| TC-1: 미인증 접근 차단 | ✅ | `/dashboard` 접근 시 `/login`으로 리다이렉트 |
| TC-2: 로그인 페이지 레이아웃 | ✅ | 데스크톱 좌우 분할 + 모바일 단일 폼 |
| TC-3: 로그인 실패 | ✅ | 오류 메시지 "유저명 또는 비밀번호가 올바르지 않습니다." 표시 |
| TC-4: 로그인 성공 | ✅ | 대시보드 이동, 헤더에 사용자명 + 로그아웃 버튼 |
| TC-5: 데모 보기 | ✅ | "데모 모드" 뱃지 + "데모 사용자" + 더미 데이터 표시 |
| TC-6: 데모 쓰기 차단 | ✅ | 전략 토글 시 "데모 모드에서는 사용할 수 없습니다." toast |
| TC-7: 로그아웃 | ✅ | `/login` 리다이렉트 + 재접근 시 다시 차단 |

## 버그 수정

- **TC-3 401 무한 리다이렉트**: 로그인 페이지에서 잘못된 비밀번호 입력 시 API가 401을 반환하고, 클라이언트 401 핸들러가 다시 `/login`으로 리다이렉트하여 에러 메시지가 표시되지 않던 문제. `/login` 경로에서는 401 리다이렉트를 건너뛰도록 수정.

## 커밋 내역

| 커밋 | 내용 |
|------|------|
| `8b935f4` | chore: .worktrees/ gitignore에 추가 |
| `c6f5262` | feat: 데모 인증 인프라 추가 (DEMO_USERNAME, /auth/demo, demo_data.py) |
| `51f591c` | feat: 백엔드 라우터 데모 분기 추가 (9개 파일) |
| `d258f60` | feat: 로그인 페이지, 인증 가드, 미들웨어, 헤더 업데이트 |
| `3442743` | fix: 로그인 페이지에서 401 응답 시 무한 리다이렉트 방지 |

## 알려진 제한사항

- 전략 카드 총 수익률/승률이 0으로 표시되는 문제: `StrategyPerformanceResponse` 스키마에 `total_return` 필드 미포함. Sprint 4.1부터 존재하던 기존 버그.
- 대시보드 toFixed 에러: 포트폴리오 요약 일부 값이 undefined인 경우. 기존 버그.
