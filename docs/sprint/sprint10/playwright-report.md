# Sprint 10 Playwright 자동 검증 보고서

**검증 일시:** 2026-03-02
**검증 환경:** localhost:3001 (Docker Compose), localhost:8000 (FastAPI)
**브라우저:** Playwright MCP (Chromium)

---

## 검증 결과 요약

| 항목 | 결과 | 비고 |
|------|------|------|
| 대시보드 렌더링 | ✅ 통과 | 스켈레톤 로딩 상태 정상 표시 (인증 미로그인) |
| 백테스팅 페이지 렌더링 | ✅ 통과 | 실행 폼 정상 렌더링 |
| 404 커스텀 페이지 | ✅ 통과 | not-found.tsx 렌더링 확인 |
| 주문 내역 실제 API 호출 | ✅ 통과 | /api/v1/orders 호출 확인 (401 = 미인증 정상) |
| 설정 페이지 실제 API 호출 | ✅ 통과 | /api/v1/system-settings, /api/v1/safety/status 호출 확인 |
| 모바일 375px 반응형 | ✅ 통과 | 사이드바 숨김, 햄버거 메뉴(≡) 표시 |
| Health Check API | ✅ 통과 | database/redis/scheduler 상태 포함 응답 |
| X-Request-ID 헤더 | ✅ 통과 | 모든 응답에 헤더 포함 확인 |
| 잘못된 날짜 → 400 에러 | ✅ 통과 | HTTPException(400) 정상 응답 |
| 인증 없이 접근 → 401 | ✅ 통과 | 보호 엔드포인트 401 차단 확인 |

**종합 결과: 10/10 항목 통과**

---

## 상세 검증 내용

### 1. 백엔드 API 검증

#### 1-1. Health Check
```json
{
  "status": "healthy",
  "timestamp": "2026-03-02T03:00:37.197613+00:00",
  "version": "0.1.0",
  "checks": {
    "database": { "status": "healthy" },
    "redis": { "status": "healthy" },
    "scheduler": { "status": "healthy", "jobs": 3 }
  }
}
```
- DB, Redis, 스케줄러 모두 healthy 상태
- 3개 APScheduler 잡 실행 중

#### 1-2. X-Request-ID 헤더
```
x-request-id: 8b030164-f16c-4b36-a90d-57264a167b43
```
- RequestIdMiddleware 정상 동작 확인

#### 1-3. 에러 핸들링
- 잘못된 날짜 형식(`date=not-a-date`): HTTP 400 반환 확인
- 인증 없이 보호 엔드포인트 접근: HTTP 401 반환 확인
- 표준 에러 응답 형식: `{"detail": "..."}` 또는 `{"code": "VALIDATION_ERROR", ...}`

### 2. 프론트엔드 검증

#### 2-1. 대시보드 (http://localhost:3001/dashboard)
- 사이드바 6개 메뉴 정상 렌더링
- API 미인증 상태에서 스켈레톤 로딩 카드 표시 (정상 동작)
- 실제 API 호출: `/api/v1/holdings`, `/api/v1/stocks/market-index`, `/api/v1/orders`, `/api/v1/strategies/performance`
- 스크린샷: [dashboard-page.png](dashboard-page.png)

#### 2-2. 백테스팅 (http://localhost:3001/backtest)
- 백테스팅 설정 폼 정상 렌더링 (전략 선택, 종목코드, 시작/종료일)
- 전략 미선택 시 실행 버튼 비활성화(disabled) 확인
- 스크린샷: [backtest-page.png](backtest-page.png)

#### 2-3. 주문 내역 (http://localhost:3001/orders)
- 실제 API `/api/v1/orders` 호출 확인 (Mock 데이터 제거 확인)
- 인증 없이 로딩 중 상태 표시

#### 2-4. 설정 (http://localhost:3001/settings)
- 실제 API `/api/v1/system-settings`, `/api/v1/safety/status` 호출 확인 (Mock 데이터 제거 확인)

#### 2-5. 404 커스텀 페이지 (http://localhost:3001/nonexistent-page)
- not-found.tsx 정상 렌더링: "404 - 페이지를 찾을 수 없습니다"
- "홈으로 돌아가기" 링크 → /dashboard 확인
- 스크린샷: [not-found-page.png](not-found-page.png)

#### 2-6. 모바일 375px 반응형
- 사이드바 숨김 확인
- 햄버거 메뉴 버튼(≡, "메뉴 열기") 표시 확인
- 스크린샷: [mobile-375px.png](mobile-375px.png)

---

## 콘솔 에러 분석

대시보드 등에서 발생하는 `Failed to load resource: 401 (Unauthorized)` 에러는 브라우저 세션에 인증 토큰이 없어서 발생하는 **예상된 정상 동작**입니다. 실제 사용자가 로그인한 상태에서는 발생하지 않습니다.

---

## 수동 검증 필요 항목

다음 항목은 Docker 환경에서 직접 수행이 필요합니다:

- ⬜ `docker compose exec backend pytest -v` → 14개 테스트 PASSED 확인
- ⬜ 백엔드 로그 JSON 포맷 확인 (`docker compose up --build` 후 재확인 필요)
- ⬜ `/orders`, `/settings` 페이지 → 로그인 후 실제 API 데이터 렌더링 확인
- ⬜ `/backtest` → 로그인 후 실제 백테스팅 API 호출 확인
- ⬜ API 오류 시 toast 알림 표시 확인

---

## 스크린샷 목록

| 파일명 | 설명 |
|--------|------|
| [dashboard-page.png](dashboard-page.png) | 대시보드 페이지 (스켈레톤 로딩) |
| [backtest-page.png](backtest-page.png) | 백테스팅 설정 폼 |
| [not-found-page.png](not-found-page.png) | 커스텀 404 페이지 |
| [mobile-375px.png](mobile-375px.png) | 모바일 375px 반응형 레이아웃 |
