# Sprint 19: 글로벌 종목 검색 구현

**Goal:** pykrx KRX API 403 에러로 동작하지 않던 종목 검색을 yfinance 기반으로 교체하고, 한국 종목 한국어 이름 매핑 및 한글 IME 입력 버그를 수정한다. 향후 글로벌 시장 확장을 위한 기반을 마련한다.

**Architecture:** yfinance Search API (전세계 종목 검색) + 정적 KRX JSON 파일 (한국어 이름 매핑) + Redis 캐시 (5분 TTL)

**Tech Stack:** `yfinance>=0.2.0` (pykrx 대체), `asyncio.to_thread` (블로킹 I/O 처리), React `useEffect` 디바운스

---

## 개요

- **스프린트 번호:** Sprint 19
- **브랜치:** develop
- **시작일:** 2026-03-06
- **완료일:** 2026-03-06
- **상태:** 완료 (Docker 재빌드 필요)
- **PR:** -

## 배경 및 문제

### 문제 1: 한글 IME 버그

Radix UI Popover가 열릴 때 포커스를 가져가면서 한글 조합 문자 입력이 중단되는 버그.
- **원인:** `PopoverContent`의 기본 `onOpenAutoFocus` 동작
- **해결:** `onOpenAutoFocus={(e) => e.preventDefault()}` 추가 + 300ms 디바운스 적용

### 문제 2: 검색 결과 없음

pykrx가 KRX 공식 API 호출 시 403 에러를 반환하여 Redis 캐시 구축 실패.
- **원인:** KRX API가 Docker 컨테이너 환경 및 일부 네트워크에서 403 반환 (알려진 이슈)
- **해결:** 런타임 pykrx 의존 제거 → yfinance Search API로 전환

### 사용자 요구사항 추가

> "앞으로 다른 나라의 시장 종목도 다룰 예정. 합리적이고 유지보수가 쉬운 방법을 찾아보렴."
> "한국 주식은 한국어로 저장/표기 되어야 해."

## 설계 결정

### 검색 엔진: yfinance

| 항목 | 내용 |
|------|------|
| 라이브러리 | `yfinance` (Yahoo Finance 래퍼) |
| 비용 | 무료, API 키 불필요 |
| 글로벌 | KRX, NYSE, NASDAQ, TSE 등 전세계 시장 |
| 검색 방식 | `yf.Search(query, max_results=N)` → 실시간 검색 |

### 한국어 종목명: 정적 KRX JSON 매핑

yfinance는 한국 종목을 영문명(`Samsung Electronics Co Ltd`)으로 반환하므로, 별도 한국어 이름 소스가 필요하다.

- `backend/data/krx_stocks.json` — 정적 파일, 앱 번들에 포함
- 앱 시작 시 메모리에 로드 → `get_korean_name(code)` / `get_market(code)` 조회
- KRX 심볼(`.KS`/`.KQ`) 감지 → 접미사 제거 → 한국어 이름 교체

**왜 Redis가 아닌 메모리인가:** 종목 이름 조회는 단순 dict 룩업으로 충분. Redis 의존 없이 프로세스 내에서 즉시 응답 가능. 검색 결과 자체는 Redis에 5분 캐시.

**갱신 주기:** 종목 목록은 자주 변하지 않으므로 월 1회 수동 갱신으로 충분.
`scripts/update_krx_stocks.py` (pykrx 사용, 로컬 실행)

## 구현 범위

### 신규 파일

| 파일 | 설명 |
|------|------|
| `backend/data/krx_stocks.json` | KRX 종목 정적 데이터 (KOSPI/KOSDAQ 주요 종목 ~180개 시드 포함) |
| `scripts/update_krx_stocks.py` | pykrx로 KRX 전 종목 갱신하는 유틸리티 스크립트 (로컬 전용) |
| `backend/app/services/krx_names.py` | JSON 로드 → 메모리 캐시 → `get_korean_name()` / `get_market()` |
| `backend/app/services/stock_search.py` | yfinance 검색 + KRX 한국어 매핑 + Redis 5분 캐시 |

### 수정 파일

| 파일 | 변경 내용 |
|------|-----------|
| `backend/app/services/stock_master.py` | pykrx 코드 제거, `stock_search`로 위임하는 래퍼만 유지 |
| `backend/app/api/v1/stocks.py` | import 경로 `stock_master` → `stock_search` |
| `backend/app/main.py` | lifespan: `load_stock_master()` → `load_krx_names()` |
| `backend/requirements.txt` | `pykrx>=1.0.0` 제거, `setuptools>=65.0.0` 제거, `yfinance>=0.2.0` 추가 |
| `frontend/src/lib/mock/types.ts` | `Stock.market`, `WatchlistItem.market`: `"KOSPI" \| "KOSDAQ"` → `string` |
| `frontend/src/components/watchlist/stock-search.tsx` | 300ms 디바운스 추가, `as "KOSPI" \| "KOSDAQ"` 타입 캐스팅 제거 |

## 검색 흐름

```
사용자 입력 (300ms 디바운스)
    ↓
GET /api/v1/stocks/search?q={query}
    ↓
Redis 캐시 확인 (stock_search:{query}, 5분 TTL)
    ↓ (캐시 미스)
asyncio.to_thread → yfinance.Search(query)
    ↓
심볼별 정규화:
  ├─ *.KS → 접미사 제거 → get_korean_name() → market=KOSPI
  ├─ *.KQ → 접미사 제거 → get_korean_name() → market=KOSDAQ
  └─ 그 외 → symbol 그대로, exchange를 market으로
    ↓
Redis 캐시 저장
    ↓
[{symbol, name, market}, ...]
```

## 완료 기준

- ✅ `backend/data/krx_stocks.json` 생성 (시드 데이터 포함)
- ✅ `scripts/update_krx_stocks.py` 작성
- ✅ `backend/app/services/krx_names.py` 구현
- ✅ `backend/app/services/stock_search.py` 구현 (yfinance + Redis 캐시)
- ✅ `backend/requirements.txt`: pykrx/setuptools 제거, yfinance 추가
- ✅ `backend/app/main.py`: lifespan 변경
- ✅ `frontend/src/lib/mock/types.ts`: market 타입 확장 (`string`)
- ✅ `frontend/src/components/watchlist/stock-search.tsx`: 디바운스 + IME 수정
- ✅ `pytest 51 passed` (기존 테스트 회귀 없음)
- ✅ KRX 한국어 이름 매핑 로드 정상 확인 (메모리 내)
- ⬜ yfinance 실제 검색 동작 확인 — **Docker 재빌드 후 검증 필요**

## 수동 검증 항목

Docker 재빌드 후 사용자가 직접 확인:

```bash
# 1. Docker 재빌드 (yfinance 설치 포함)
docker compose up --build

# 2. 한국 종목 검색 (한국어 이름 반환 확인)
curl "http://localhost:8000/api/v1/stocks/search?q=삼성" \
  -H "Authorization: Bearer <토큰>"
# 기대: [{"symbol": "005930", "name": "삼성전자", "market": "KOSPI"}, ...]

# 3. 글로벌 종목 검색
curl "http://localhost:8000/api/v1/stocks/search?q=AAPL" \
  -H "Authorization: Bearer <토큰>"
# 기대: [{"symbol": "AAPL", "name": "Apple Inc.", "market": "NMS"}, ...]

# 4. UI 검증: 관심종목 검색창에서 한글 입력 → 결과 표시 → 종목 추가
```

## KRX 데이터 갱신 방법

pykrx가 사용 가능한 환경(KRX API 접근 가능)에서 실행:

```bash
pip install pykrx
python scripts/update_krx_stocks.py
# → backend/data/krx_stocks.json 갱신 (KOSPI + KOSDAQ 전 종목, 약 2,500개)
```

현재 시드 데이터: KOSPI 주요 종목 ~130개 + KOSDAQ 주요 종목 ~50개 포함.
