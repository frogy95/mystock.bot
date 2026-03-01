# Sprint 6 Playwright 검증 보고서

- **검증 일시:** 2026-03-01
- **검증 대상:** Sprint 6 전략 엔진 및 자동매매 API 연동
- **검증 환경:** Docker Compose 환경 필요 (미실행 상태)

---

## 검증 상태 요약

| 항목 | 상태 | 비고 |
|------|------|------|
| 백엔드 API (Swagger) | 수동 검증 필요 | Docker 환경 필요 |
| 전략 목록 API | 수동 검증 필요 | Docker 환경 필요 |
| 전략 활성화 토글 | 수동 검증 필요 | Docker 환경 필요 |
| 파라미터 업데이트 | 수동 검증 필요 | Docker 환경 필요 |
| 프론트엔드 연동 | 수동 검증 필요 | Docker 환경 필요 |
| APScheduler 시작 | 수동 검증 필요 | 로그 확인 필요 |

---

## 자동 검증 불가 사유

Sprint 6 검증 항목은 FastAPI 백엔드 서버, PostgreSQL, Redis가 모두 실행 중인 Docker Compose 환경이 필요합니다. 현재 환경에서는 Docker 컨테이너가 실행되지 않아 Playwright MCP를 통한 자동 검증을 수행할 수 없습니다.

---

## 수동 검증 시나리오

`deploy.md` Section 11 참고하여 아래 순서로 검증하세요.

### 시나리오 1: 백엔드 API 기본 동작

```
1. docker compose up --build -d 실행
2. docker compose logs backend | grep "APScheduler 시작" 확인
3. http://localhost:8000/docs 접속
4. /api/v1/strategies 엔드포인트 5개 확인:
   - GET /api/v1/strategies
   - GET /api/v1/strategies/{id}
   - PUT /api/v1/strategies/{id}/activate
   - PUT /api/v1/strategies/{id}/params
   - POST /api/v1/strategies/{id}/evaluate/{symbol}
```

### 시나리오 2: 전략 목록 및 상세 조회

```
1. POST /api/v1/auth/login → Bearer 토큰 발급
2. GET /api/v1/strategies → 전략 3개 목록 반환 확인
   기대 응답:
   [
     {"id": 1, "name": "GoldenCrossRSI", "is_active": false, ...},
     {"id": 2, "name": "BollingerReversal", "is_active": false, ...},
     {"id": 3, "name": "ValueMomentum", "is_active": false, ...}
   ]
3. GET /api/v1/strategies/1 → 전략 상세 + 파라미터 확인
```

### 시나리오 3: 전략 활성화 API

```
1. PUT /api/v1/strategies/1/activate
   Body: {"is_active": true}
   기대 응답: {"id": 1, "is_active": true, ...}
2. GET /api/v1/strategies/1 → is_active=true 확인
```

### 시나리오 4: 전략 파라미터 업데이트

```
1. PUT /api/v1/strategies/1/params
   Body: {"params": [{"param_key": "rsi_threshold", "param_value": "35", "param_type": "float"}]}
   기대 응답: {"params": [{"param_key": "rsi_threshold", "param_value": "35", ...}], ...}
```

### 시나리오 5: 프론트엔드 전략 화면 연동

```
1. http://localhost:3001/strategy 접속
2. 전략 카드 3개 렌더링 확인 (실제 DB 데이터)
3. 전략 활성화 토글 클릭
4. 브라우저 개발자도구 Network 탭에서
   PUT /api/v1/strategies/{id}/activate 호출 200 응답 확인
5. 파라미터 수정 후 저장
6. PUT /api/v1/strategies/{id}/params 호출 200 응답 확인
7. 콘솔 에러 없음 확인
```

### 시나리오 6: 신호 평가 (KIS API 연동 시)

```
1. .env에 KIS API 키 설정
2. POST /api/v1/strategies/1/evaluate/005930
   기대 응답:
   {
     "symbol": "005930",
     "signal_type": "HOLD" | "BUY" | "SELL",
     "confidence": 0.0 ~ 1.0,
     "reason": "조건 미충족" 등,
     "target_price": null | 숫자
   }
```

---

## 검증 결과 기록란

검증 완료 후 아래 표를 업데이트하세요.

| 시나리오 | 결과 | 확인 일시 | 비고 |
|---------|------|-----------|------|
| 1. 백엔드 API 기본 동작 | | | |
| 2. 전략 목록 및 상세 조회 | | | |
| 3. 전략 활성화 API | | | |
| 4. 전략 파라미터 업데이트 | | | |
| 5. 프론트엔드 전략 화면 연동 | | | |
| 6. 신호 평가 (KIS 연동) | | | |
