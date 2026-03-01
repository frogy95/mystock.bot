# Sprint 7 Playwright 자동 검증 보고서

- **검증 일자:** 2026-03-01
- **검증 환경:** localhost:3001 (Next.js 프론트엔드, Docker 없이 직접 실행)
- **백엔드:** 미실행 상태 (프론트엔드 단독 검증)

---

## 자동 검증 결과 요약

| 항목 | 결과 |
|------|------|
| 설정 화면 렌더링 | 통과 |
| 자동매매 상태 표시 (중지됨) | 통과 |
| KIS API 설정 폼 렌더링 | 통과 |
| 안전장치 설정 폼 렌더링 | 통과 |
| 긴급 전체 매도 AlertDialog 표시 | 통과 |
| AlertDialog 취소 버튼 동작 | 통과 |
| 주문내역 테이블 렌더링 | 통과 |
| 주문 탭 (전체/미체결/체결완료/취소) 렌더링 | 통과 |
| 미체결 주문 취소 버튼 표시 | 통과 |
| 모바일 375px 반응형 레이아웃 | 통과 |
| 콘솔 에러 (Error 레벨) | 0건 — 통과 |

**자동 검증 통과: 11/11**

---

## 검증 상세

### 1. 설정 화면 (`/settings`)

**결과:** 통과

확인 항목:
- 자동매매 섹션: "중지됨" 배지 + ON/OFF 스위치 표시
- KIS API 설정: App Key/Secret 마스킹 입력 + 모의투자/실전투자 라디오 버튼
- 텔레그램 알림 설정 폼
- 매매 시간 설정 (시작 09:30 / 종료 15:00)
- 안전장치: 일일 손실 한도(3%) / 최대 주문 횟수(10건) / 종목당 최대 비중(20%) / 기본 손절률(5%)
- 긴급 전체 매도 버튼 (위험 구역 섹션)

스크린샷: [screenshot-settings.png](screenshot-settings.png)

### 2. 긴급 전체 매도 AlertDialog

**결과:** 통과

- "긴급 전체 매도" 버튼 클릭 시 AlertDialog 표시: "정말로 전체 매도하시겠습니까?"
- 경고 문구: "모든 보유 종목을 현재가에 즉시 매도합니다. 이 작업은 되돌릴 수 없습니다."
- "취소" 버튼 클릭 시 모달 닫힘 확인

스크린샷: [screenshot-emergency-sell-dialog.png](screenshot-emergency-sell-dialog.png)

### 3. 주문내역 화면 (`/orders`)

**결과:** 통과

확인 항목:
- 전체/미체결/체결완료/취소 탭 렌더링
- 주문 테이블 컬럼: 종목 / 구분 / 상태 / 수량 / 가격 / 총액 / 전략 / 생성일 / 액션
- 미체결 주문(카카오 매도, 삼성SDI 매수, LG전자 매수)에 취소 버튼 표시
- 체결완료/취소 주문에는 액션 버튼 없음

스크린샷: [screenshot-orders.png](screenshot-orders.png)

### 4. 모바일 반응형 (375px)

**결과:** 통과

- 사이드바 숨김, 헤더에 햄버거 메뉴(≡) 표시
- 테이블 가로 스크롤 정상 동작
- 탭 및 필터 영역 정상 렌더링

스크린샷: [screenshot-mobile-375.png](screenshot-mobile-375.png)

### 5. 콘솔 에러

**결과:** 통과 (Error 0건)

---

## 수동 검증 필요 항목 (백엔드 실행 후)

백엔드(Docker Compose) 실행 후 아래 항목을 수동으로 검증하세요.

### API 엔드포인트 검증

```bash
# 1. 로그인
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "설정한_비밀번호"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 2. 안전장치 상태 조회
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/safety/status
# 기대: {"auto_trade_enabled": false, "daily_loss_check": {...}, "daily_order_check": {...}, "system": {...}}

# 3. 자동매매 활성화
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}' \
  http://localhost:8000/api/v1/safety/auto-trade
# 기대: {"auto_trade_enabled": true}

# 4. 시스템 설정 전체 조회
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/system-settings
# 기대: 설정 항목 배열

# 5. 주문 목록 조회
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/orders
# 기대: 주문 목록 배열 (최신순)

# 6. Swagger UI 신규 엔드포인트 확인
# http://localhost:8000/docs
# safety (3개), system-settings (3개), orders (1개) 엔드포인트 확인
```

### 스케줄러 로그 확인

```bash
# 손절/익절 모니터링 스케줄러 시작 로그 확인
docker compose logs backend | grep -E "(risk|손절|익절|안전장치|스케줄)"
# 기대: "APScheduler 시작 (손절/익절 모니터링: 장중 매 1분)"
```

### 프론트엔드-백엔드 연동 확인

```bash
# 브라우저 개발자도구 Network 탭에서 확인:
# GET /api/v1/safety/status -> 200
# GET /api/v1/system-settings -> 200
# GET /api/v1/orders -> 200
```

---

## 스크린샷 목록

| 파일명 | 설명 |
|--------|------|
| [screenshot-settings.png](screenshot-settings.png) | 설정 화면 전체 |
| [screenshot-emergency-sell-dialog.png](screenshot-emergency-sell-dialog.png) | 긴급 전체 매도 AlertDialog |
| [screenshot-orders.png](screenshot-orders.png) | 주문내역 화면 |
| [screenshot-mobile-375.png](screenshot-mobile-375.png) | 모바일 375px 반응형 |
