# Sprint 12: KIS API 듀얼 환경 설정

## 스프린트 개요

| 항목 | 내용 |
|------|------|
| 스프린트 번호 | Sprint 12 |
| Phase | Phase 5+ (기반 개선) |
| 기간 | 2026-03-03 ~ 2026-03-04 (1-2일) |
| 우선순위 | Must Have |
| 브랜치 | `sprint12` |

---

## 배경 및 문제 정의

### 현재 상태

KIS API는 두 종류의 서버를 운영한다.

| 서버 | 엔드포인트 | 제공 기능 |
|------|-----------|-----------|
| 실전 서버 | `openapi.koreainvestment.com:9443` | 시세 조회, 주문, 잔고 (모두 제공) |
| 모의투자 서버 | `openapivts.koreainvestment.com:29443` | 주문, 잔고만 제공 (시세 조회 불가) |

현재 `.env`에는 단일 `KIS_APP_KEY` / `KIS_APP_SECRET` / `KIS_ACCOUNT_NUMBER`만 존재한다. `KIS_ENVIRONMENT=vts`로 설정 시 모의투자 서버를 사용하는데, `kis_client.py`의 시세 API(`get_quote`, `get_chart`, `get_market_index`)는 이미 `_KIS_REAL_BASE`(실전 서버)를 직접 호출하고 있다. 그러나 헤더에 삽입되는 `appkey` / `appsecret`은 `settings.KIS_APP_KEY`(모의투자 키)를 그대로 사용하고 있어, **모의투자 키로 실전 서버의 시세 API를 호출**하는 구조적 불일치가 존재한다.

KIS 실전 서버의 시세 API는 실전 앱 키로만 유효한 토큰을 수락하므로, 이 불일치로 인해 모의투자 모드에서 시세 조회가 실패할 수 있다.

### 해결 방향

모의투자 전용 키와 실전 전용 키를 분리하여 각각 독립적으로 관리한다.

- **시세 API**: 항상 실전 키 + 실전 서버 사용 (`KIS_REAL_APP_KEY`)
- **주문/잔고 API**: `KIS_ENVIRONMENT` 값에 따라 모의 또는 실전 키 선택

---

## 스프린트 목표

모의투자 모드에서도 현재가, 차트, 시장지수 데이터가 정상 조회되도록 KIS API 듀얼 환경 설정을 구현한다.

**완료 기준:**
- 모의투자 모드(`KIS_ENVIRONMENT=vts`)에서도 현재가, 차트, 시장지수 데이터가 정상 조회됨
- 주문/잔고는 모의투자 서버에서, 시세는 실전 서버에서 각각 처리됨
- `.env.example`에 새 환경변수 구조가 명확히 문서화됨
- 설정 페이지에 모의투자/실전투자 키 분리 섹션이 표시됨

---

## 구현 범위

### 포함 (In Scope)

- `backend/app/core/config.py` — 환경변수 구조 변경
- `backend/app/services/kis_client.py` — 듀얼 키 지원 리팩토링
- `.env.example` — 새 환경변수 문서화
- `frontend/src/lib/mock/types.ts` — `KisApiConfig` 타입 확장
- `frontend/src/components/settings/kis-api-form.tsx` — 듀얼 키 입력 UI
- `frontend/src/app/settings/page.tsx` — 파싱/저장 로직 업데이트
- `deploy.md` — 마이그레이션 가이드 추가

### 제외 (Out of Scope)

- DB 스키마 변경 (키는 `system_settings` 테이블에 key-value로 저장 중)
- 백테스팅 엔진 변경
- WebSocket 연결 방식 변경
- `rate_limiter.py` 변경 (기존 모의/실전 Rate Limiter 그대로 활용)

---

## 환경변수 설계

### 변경 전

```
KIS_APP_KEY=...
KIS_APP_SECRET=...
KIS_ACCOUNT_NUMBER=...
KIS_HTS_ID=...
KIS_ENVIRONMENT=vts
```

### 변경 후

```
# 모의투자 전용 (주문/잔고에 사용)
KIS_VTS_APP_KEY=...
KIS_VTS_APP_SECRET=...
KIS_VTS_ACCOUNT_NUMBER=...

# 실전 전용 (시세 조회 항상 + KIS_ENVIRONMENT=real 시 주문/잔고에도 사용)
KIS_REAL_APP_KEY=...
KIS_REAL_APP_SECRET=...
KIS_REAL_ACCOUNT_NUMBER=...

KIS_HTS_ID=...
KIS_ENVIRONMENT=vts   # vts=모의투자 모드, real=실전투자 모드
```

### 하위 호환성 전략

`KIS_APP_KEY`가 설정되어 있고 `KIS_VTS_APP_KEY`가 비어 있는 경우, 기존 단일 키를 VTS 키 fallback으로 사용하는 옵션도 고려하였으나, 명확성을 위해 명시적 분리를 원칙으로 한다. 기존 `.env`를 사용하는 사용자는 `deploy.md`의 마이그레이션 가이드를 따라 키를 분리 설정해야 한다.

---

## 작업 분해 (Task Breakdown)

### Task 0: Sprint 브랜치 생성

**우선순위:** Must Have
**예상 소요:** 5분

**Steps:**
1. `main` 브랜치 기준으로 `sprint12` 브랜치 생성
2. 브랜치 전환 확인

**Files:**
- (Git 브랜치 작업)

**완료 기준:**
- `git branch --show-current` 출력이 `sprint12`임

**커밋:** 없음 (브랜치 생성만)

---

### Task 1: `config.py` 환경변수 구조 변경

**우선순위:** Must Have
**예상 소요:** 30분

**변경 내용:**

기존 단일 키 필드(`KIS_APP_KEY`, `KIS_APP_SECRET`, `KIS_ACCOUNT_NUMBER`)를 제거하고 듀얼 키 필드로 교체한다.

```python
# 변경 전
KIS_APP_KEY: str = ""
KIS_APP_SECRET: str = ""
KIS_ACCOUNT_NUMBER: str = ""
KIS_HTS_ID: str = ""
KIS_ENVIRONMENT: str = "vts"

# 변경 후
# 모의투자 전용 키 (주문/잔고에 사용)
KIS_VTS_APP_KEY: str = ""
KIS_VTS_APP_SECRET: str = ""
KIS_VTS_ACCOUNT_NUMBER: str = ""

# 실전 전용 키 (시세 항상 사용 + 실전 모드 주문/잔고)
KIS_REAL_APP_KEY: str = ""
KIS_REAL_APP_SECRET: str = ""
KIS_REAL_ACCOUNT_NUMBER: str = ""

KIS_HTS_ID: str = ""
KIS_ENVIRONMENT: str = "vts"  # vts: 모의투자, real: 실전
```

**Files:**
- `backend/app/core/config.py`

**완료 기준:**
- `settings.KIS_VTS_APP_KEY`, `settings.KIS_REAL_APP_KEY` 등 6개 신규 필드 접근 가능
- 기존 `KIS_APP_KEY` 필드 제거 확인

**커밋:** `feat: KIS API 듀얼 환경변수 구조로 변경 (config.py)`

---

### Task 2: `kis_client.py` 듀얼 키 지원 리팩토링

**우선순위:** Must Have
**예상 소요:** 90분

**핵심 설계:**

토큰 캐시를 앱 키별로 분리하여 모의투자 토큰과 실전 토큰을 별도로 관리한다.

```
_token_cache = {
    "<vts_app_key>": {"token": "...", "expires_at": ...},
    "<real_app_key>": {"token": "...", "expires_at": ...},
}
```

**메서드별 키 선택 규칙:**

| 메서드 | 서버 | 앱 키 |
|--------|------|-------|
| `get_quote` | 실전(`_KIS_REAL_BASE`) | `KIS_REAL_APP_KEY` |
| `get_chart` | 실전(`_KIS_REAL_BASE`) | `KIS_REAL_APP_KEY` |
| `get_market_index` | 실전(`_KIS_REAL_BASE`) | `KIS_REAL_APP_KEY` |
| `get_balance` | `KIS_ENVIRONMENT`에 따라 선택 | VTS→`KIS_VTS_APP_KEY`, real→`KIS_REAL_APP_KEY` |
| `place_order` | `KIS_ENVIRONMENT`에 따라 선택 | VTS→`KIS_VTS_APP_KEY`, real→`KIS_REAL_APP_KEY` |
| `get_order_status` | `KIS_ENVIRONMENT`에 따라 선택 | VTS→`KIS_VTS_APP_KEY`, real→`KIS_REAL_APP_KEY` |

**Rate Limiter 선택 규칙:**

- 시세 API: 항상 실전 Rate Limiter (`_prod_limiter`, 20건/초) 사용
- 주문/잔고 API: `KIS_ENVIRONMENT`에 따라 VTS(`_vts_limiter`, 5건/초) 또는 실전(`_prod_limiter`) 선택

**`is_available()` 변경:**

기존에는 4개 단일 필드를 검사했다. 변경 후에는 환경에 따라 필요한 키를 검사한다.

```python
def is_available(self) -> bool:
    """KIS API 클라이언트 사용 가능 여부를 반환한다."""
    from app.core.config import settings
    is_virtual = settings.KIS_ENVIRONMENT == "vts"

    # 시세 API용 실전 키는 항상 필요
    real_keys_ok = all([settings.KIS_REAL_APP_KEY, settings.KIS_REAL_APP_SECRET])

    # 주문/잔고용 키: 환경에 따라 확인
    if is_virtual:
        trade_keys_ok = all([settings.KIS_VTS_APP_KEY, settings.KIS_VTS_APP_SECRET, settings.KIS_VTS_ACCOUNT_NUMBER])
    else:
        trade_keys_ok = all([settings.KIS_REAL_APP_KEY, settings.KIS_REAL_APP_SECRET, settings.KIS_REAL_ACCOUNT_NUMBER])

    return real_keys_ok and trade_keys_ok
```

**`_get_access_token(env: str)` 시그니처 변경:**

`env` 인자로 `"vts"` 또는 `"real"`을 받아 해당 키로 토큰을 발급한다.

```python
async def _get_access_token(self, env: str = "real") -> str:
    """지정된 환경의 KIS OAuth 액세스 토큰을 발급/캐싱한다.
    env: "vts" - 모의투자 키 사용, "real" - 실전 키 사용
    """
    from app.core.config import settings

    if env == "vts":
        app_key = settings.KIS_VTS_APP_KEY
        app_secret = settings.KIS_VTS_APP_SECRET
        base_url = _KIS_VTS_BASE
    else:
        app_key = settings.KIS_REAL_APP_KEY
        app_secret = settings.KIS_REAL_APP_SECRET
        base_url = _KIS_REAL_BASE

    cache_key = app_key
    # ... 이하 동일
```

**Files:**
- `backend/app/services/kis_client.py`

**완료 기준:**
- `get_quote`, `get_chart`, `get_market_index`에서 `_get_access_token("real")` 호출
- `get_balance`, `place_order`, `get_order_status`에서 `KIS_ENVIRONMENT` 값에 따라 적절한 env 선택
- 토큰 캐시 키가 앱 키 문자열 기준으로 분리됨
- 기존 `settings.KIS_APP_KEY` 참조 코드 없음

**커밋:** `feat: KIS API 듀얼 키 지원 - 시세/주문 환경 분리 (kis_client.py)`

---

### Task 3: `.env.example` 업데이트

**우선순위:** Must Have
**예상 소요:** 20분

**변경 내용:**

기존 단일 KIS 키 섹션을 두 섹션(모의투자 / 실전)으로 분리하고, 각 섹션의 용도와 발급 방법을 상세히 안내한다.

**Files:**
- `.env.example`

**완료 기준:**
- `KIS_VTS_APP_KEY`, `KIS_VTS_APP_SECRET`, `KIS_VTS_ACCOUNT_NUMBER` 섹션 존재
- `KIS_REAL_APP_KEY`, `KIS_REAL_APP_SECRET`, `KIS_REAL_ACCOUNT_NUMBER` 섹션 존재
- 각 섹션에 발급 방법 및 용도 주석 포함
- 기존 `KIS_APP_KEY`, `KIS_APP_SECRET`, `KIS_ACCOUNT_NUMBER` 제거

**커밋:** `docs: .env.example KIS 듀얼 환경변수 구조로 업데이트`

---

### Task 4: 프론트엔드 타입 및 UI 업데이트

**우선순위:** Must Have
**예상 소요:** 60분

#### Task 4-1: `types.ts` — `KisApiConfig` 타입 확장

기존 단일 키 구조에서 모의투자/실전 두 섹션 구조로 변경한다.

```typescript
// 변경 전
export interface KisApiConfig {
  appKey: string;
  appSecret: string;
  mode: "paper" | "real";
}

// 변경 후
export interface KisVtsConfig {
  vtsAppKey: string;      // 모의투자 App Key
  vtsAppSecret: string;   // 모의투자 App Secret
  vtsAccountNumber: string; // 모의투자 계좌번호
}

export interface KisRealConfig {
  realAppKey: string;      // 실전 App Key
  realAppSecret: string;   // 실전 App Secret
  realAccountNumber: string; // 실전 계좌번호
}

export interface KisApiConfig extends KisVtsConfig, KisRealConfig {
  mode: "paper" | "real"; // 주문/잔고 환경 선택
}
```

#### Task 4-2: `kis-api-form.tsx` — 듀얼 키 입력 UI

단일 키 입력 폼을 두 섹션(모의투자/실전투자)으로 분리한다.

**UI 구조:**

```
[KIS API 설정 카드]
├── [투자 모드 선택] RadioGroup: 모의투자 / 실전투자
├── ─────────────────────────────────────
├── [모의투자 키 섹션] (뱃지: "주문/잔고에 사용")
│   ├── 모의투자 App Key  [입력란] [표시/숨기기]
│   ├── 모의투자 App Secret  [입력란] [표시/숨기기]
│   └── 모의투자 계좌번호  [입력란]
├── ─────────────────────────────────────
├── [실전투자 키 섹션] (뱃지: "시세 조회 항상 사용")
│   ├── 실전 App Key  [입력란] [표시/숨기기]
│   ├── 실전 App Secret  [입력란] [표시/숨기기]
│   └── 실전 계좌번호  [입력란]
└── [저장] 버튼
```

각 입력란에는 Show/Hide 토글 버튼을 유지한다.

#### Task 4-3: `settings/page.tsx` — 파싱/저장 로직 업데이트

`parseKisApiConfig()` 함수와 `buildItems()` 호출부를 새 키 구조에 맞게 수정한다.

**setting_key 매핑:**

| `KisApiConfig` 필드 | DB `setting_key` |
|---------------------|-----------------|
| `vtsAppKey` | `kis_vts_app_key` |
| `vtsAppSecret` | `kis_vts_app_secret` |
| `vtsAccountNumber` | `kis_vts_account_number` |
| `realAppKey` | `kis_real_app_key` |
| `realAppSecret` | `kis_real_app_secret` |
| `realAccountNumber` | `kis_real_account_number` |
| `mode` | `kis_mode` |

**Files:**
- `frontend/src/lib/mock/types.ts`
- `frontend/src/components/settings/kis-api-form.tsx`
- `frontend/src/app/settings/page.tsx`

**완료 기준:**
- 설정 페이지에서 모의투자/실전투자 키 입력란이 각각 표시됨
- 저장 시 6개 키 필드 + mode가 모두 API로 전달됨
- TypeScript 타입 에러 없음

**커밋:** `feat: KIS API 설정 UI 듀얼 키 입력 섹션으로 개편`

---

### Task 5: `deploy.md` 마이그레이션 가이드 추가

**우선순위:** Must Have
**예상 소요:** 20분

**내용:**

기존 단일 키 `.env` 설정을 듀얼 키 구조로 마이그레이션하는 단계별 가이드를 작성한다.

```markdown
## 섹션 15: Sprint 12 — KIS API 듀얼 환경 마이그레이션

### 배경
모의투자 모드에서도 실시간 시세를 받기 위해 KIS 키 구조가 변경되었습니다.

### 마이그레이션 절차

1. `.env` 파일을 열어 기존 단일 키 항목을 확인합니다.
2. 아래와 같이 새 변수를 추가합니다:
   - `KIS_VTS_APP_KEY` = 기존 `KIS_APP_KEY` 값 (모의투자 앱 키)
   - `KIS_VTS_APP_SECRET` = 기존 `KIS_APP_SECRET` 값
   - `KIS_VTS_ACCOUNT_NUMBER` = 기존 `KIS_ACCOUNT_NUMBER` 값
   - `KIS_REAL_APP_KEY` = KIS Developers에서 발급받은 실전 앱 키
   - `KIS_REAL_APP_SECRET` = 실전 앱 시크릿
   - `KIS_REAL_ACCOUNT_NUMBER` = 실전 계좌번호
3. 기존 `KIS_APP_KEY`, `KIS_APP_SECRET`, `KIS_ACCOUNT_NUMBER` 항목을 삭제합니다.
4. Docker Compose를 재시작합니다: `docker compose restart backend`
```

**Files:**
- `deploy.md`

**완료 기준:**
- 마이그레이션 절차가 단계별로 명확히 작성됨
- 실전 앱 키 발급 방법 링크 포함

**커밋:** `docs: Sprint 12 KIS 듀얼 키 마이그레이션 가이드 추가 (deploy.md)`

---

### Task 6: Playwright MCP 검증

**우선순위:** Must Have
**예상 소요:** 30분

설정 페이지에서 듀얼 키 UI가 정상 동작하는지 검증한다.

**검증 시나리오:**

```
1. browser_navigate -> http://localhost:3001/settings 접속
2. browser_snapshot -> KIS API 설정 카드에 두 섹션(모의투자/실전투자) 표시 확인
3. browser_click -> 모의투자 App Key 표시 버튼
4. browser_snapshot -> App Key 입력란이 text 타입으로 변경됨 확인
5. browser_type -> 모의투자 App Key 입력란에 "test_vts_key" 입력
6. browser_type -> 실전 App Key 입력란에 "test_real_key" 입력
7. browser_click -> 저장 버튼
8. browser_wait_for -> "저장되었습니다" 토스트 메시지 대기
9. browser_network_requests -> /api/v1/settings 호출 200 확인
10. browser_console_messages(level: "error") -> 에러 없음 확인
```

**완료 기준:**
- 설정 페이지 KIS 섹션에 6개 입력란 표시됨
- 저장 API 호출 성공 (200)
- 콘솔 에러 없음

---

## 기술적 고려사항

### 토큰 캐시 분리

`_token_cache` 딕셔너리의 키를 앱 키 문자열로 사용하므로, 모의투자 앱 키와 실전 앱 키가 다른 이상 자연스럽게 분리된다. 별도의 구조 변경 없이 기존 캐시 딕셔너리를 그대로 활용할 수 있다.

### Rate Limiter 선택

시세 API는 항상 실전 Rate Limiter(20건/초)를 사용하므로 `get_rate_limiter(is_virtual=False)`를 명시적으로 호출한다. 이는 모의투자 모드에서도 시세 API가 실전 서버를 호출하는 현실을 반영한다.

### 설정 화면 UX

실전 앱 키 섹션에는 "시세 조회에 항상 사용됩니다" 안내 텍스트와 함께 경고 뱃지를 표시하여, 사용자가 실전 키를 반드시 입력해야 한다는 사실을 명확히 한다.

### 기존 `system_settings` 테이블

DB의 `system_settings` 테이블은 key-value 구조이므로 스키마 변경 없이 새로운 `setting_key`를 그대로 삽입할 수 있다. 단, 기존에 저장된 `kis_app_key`, `kis_app_secret` 레코드는 더 이상 참조되지 않으므로 수동으로 삭제하거나 무시해도 무방하다.

---

## 의존성 및 리스크

| 리스크 | 영향도 | 완화 방안 |
|--------|--------|-----------|
| 실전 앱 키 미발급 상태에서 시세 조회 불가 | 중간 | `is_available()` 분리로 시세 전용 가용성 체크, 로그로 안내 |
| 기존 `.env` 마이그레이션 누락 | 중간 | `deploy.md`에 단계별 가이드 제공 |
| 모의투자 키로 실전 시세 API 호출 시도 | 높음 | `_get_access_token("real")`에서 실전 키 강제 사용으로 방지 |

---

## 완료 기준 (Definition of Done)

- ✅ `config.py`: `KIS_VTS_*`, `KIS_REAL_*` 6개 신규 필드 정의, 기존 `KIS_APP_KEY` 제거
- ✅ `kis_client.py`: 시세 API는 실전 키, 주문/잔고 API는 환경에 따른 키 선택
- ✅ `kis_client.py`: 토큰 캐시가 앱 키별로 분리됨
- ✅ `.env.example`: 듀얼 키 구조 문서화
- ✅ `KisApiConfig` 타입: 6개 키 필드 + `mode`로 확장
- ✅ 설정 페이지: 모의투자/실전투자 두 섹션으로 분리된 키 입력 UI
- ✅ Playwright 검증: 설정 페이지 저장 성공, 에러 없음
- ✅ `deploy.md`: 마이그레이션 가이드 추가

---

## 예상 산출물

1. `backend/app/core/config.py` — 듀얼 키 환경변수 설정
2. `backend/app/services/kis_client.py` — 듀얼 키 지원 클라이언트
3. `.env.example` — 신규 환경변수 문서
4. `frontend/src/lib/mock/types.ts` — 확장된 `KisApiConfig` 타입
5. `frontend/src/components/settings/kis-api-form.tsx` — 듀얼 키 입력 UI
6. `frontend/src/app/settings/page.tsx` — 업데이트된 파싱/저장 로직
7. `deploy.md` — 마이그레이션 섹션 추가

---

## 실행 순서

```
Task 0: 브랜치 생성 (sprint12)
  |
  v
Task 1: config.py 환경변수 변경
  |
  v
Task 2: kis_client.py 듀얼 키 리팩토링
  |
  v
Task 3: .env.example 업데이트  (Task 1과 병행 가능)
  |
  v
Task 4: 프론트엔드 타입 및 UI 업데이트
  ├── Task 4-1: types.ts
  ├── Task 4-2: kis-api-form.tsx
  └── Task 4-3: settings/page.tsx
  |
  v
Task 5: deploy.md 마이그레이션 가이드
  |
  v
Task 6: Playwright MCP 검증
```

Task 1과 Task 3은 독립적으로 병행 작업이 가능하다. Task 4는 Task 1 완료 후 진행한다.

---

## 검증 결과

- [Playwright 검증 보고서](sprint12/playwright-report.md)
- [스크린샷 모음](sprint12/)

### 자동 검증 완료 항목 (2026-03-03)

- ✅ 설정 페이지 KIS API 섹션 모의투자/실전투자 두 섹션 분리 확인
- ✅ 비밀값 표시/숨기기 토글 정상 동작
- ✅ 저장 API 호출 (`PUT /api/v1/system-settings`) 호출 확인
- ✅ 데모 모드 차단 토스트 알림 정상 표시
- ✅ 긴급 전체 매도 확인 모달 정상 표시 및 취소 동작

### 사용자 직접 수행 필요 항목

`deploy.md` 섹션 15 체크리스트를 참고하여 수행합니다.

- ⬜ `.env` 파일에서 `KIS_VTS_*` / `KIS_REAL_*` 듀얼 키 입력 완료
- ⬜ `docker compose up --build` 성공
- ⬜ `GET /api/v1/settings/kis-status` → `is_available: true` 확인
- ⬜ `GET /api/v1/stocks/005930/quote` → 실제 시세 데이터 반환 확인 (실전 키 필요)
- ⬜ `docker compose exec backend pytest -v` → 14개 PASSED 확인
