# 프로젝트 로드맵 - AutoTrader KR

## 개요
- **목표:** 한국투자증권 Open API를 활용한 KOSPI/KOSDAQ 퀀트 전략 기반 자동매매 웹 애플리케이션
- **전체 예상 기간:** 10주 (2026-03-02 ~ 2026-05-10)
- **현재 진행 단계:** Phase 9 완료 (Sprint 17: MVP 프로덕션 배포 준비, 2026-03-05)
- **팀 규모:** 1-2인 소규모 개발팀
- **MVP 대상 사용자:** 개인 사용자 1인 (개발자 본인)

## 진행 상태 범례
- 완료
- 진행 중
- 예정
- 보류

---

## 프로젝트 현황 대시보드

| 항목 | 상태 |
|------|------|
| 전체 진행률 | Sprint 0~17 완료 |
| 현재 Phase | Phase 9 완료 — Sprint 17(MVP 프로덕션 배포 준비) 완료 (2026-03-05) |
| 완료된 스프린트 | Sprint 0 (2026-02-28), Sprint 1 (2026-03-01), Sprint 2 (2026-03-01), Sprint 3 (2026-03-01), Sprint 4 (2026-03-01), Sprint 4.1 (2026-03-01), Sprint 5 (2026-03-01), Sprint 6 (2026-03-01), Sprint 7 (2026-03-01), Sprint 8 (2026-03-01), Sprint 9 (2026-03-02), Sprint 10 (2026-03-02), Sprint 11 (2026-03-02), Sprint 12 (2026-03-03), Sprint 13 (2026-03-03), Sprint 14 (2026-03-03), Sprint 15 (2026-03-03), Sprint 16 (2026-03-04), Sprint 17 (2026-03-05) |
| 다음 마일스톤 | M5: MVP 출시 - 모의투자 5일 연속 안정 운영, 실전 전환 준비 |
| 예상 MVP 완료일 | 2026-05-10 |

---

## 기술 아키텍처 결정 사항

| 영역 | 선택 기술 | 선택 이유 |
|------|-----------|-----------|
| Frontend | Next.js 16+ (App Router) + TypeScript | SSR/SSG 지원, React 생태계, 빠른 프로토타이핑 |
| UI | TailwindCSS + shadcn/ui | 컴포넌트 기반 빠른 UI 개발, 커스터마이징 용이 |
| 차트 | Lightweight Charts (TradingView) + Recharts | 주가 차트 전문 라이브러리 + 일반 데이터 시각화 |
| 서버 상태 | TanStack Query | 캐싱, 낙관적 업데이트, 자동 리페칭 |
| 클라이언트 상태 | zustand | 경량, 보일러플레이트 최소화 |
| Backend | FastAPI (Python) | httpx (KIS REST API 직접 호출), VectorBT 등 Python 퀀트 생태계 활용 |
| DB | PostgreSQL | ACID 트랜잭션, 거래 내역의 안정적 저장 |
| 캐시/큐 | Redis | 실시간 시세 버퍼, 작업 큐, 세션 관리 |
| 스케줄러 | APScheduler (MVP) -> Celery (확장) | MVP에서는 경량 스케줄러로 시작, 추후 Celery로 전환 |
| 증권 API | httpx (KIS REST API 직접 호출) | Python 표준 비동기 HTTP 클라이언트, 연결 풀 공유 |
| 기술 분석 | pandas-ta | 순수 Python으로 설치 용이 (TA-Lib C 의존성 미사용) |
| 백테스팅 | VectorBT 0.26.x | 벡터화 연산으로 고속 백테스팅, pandas 네이티브, Apache 2.0 |
| 알림 | python-telegram-bot 22.x | 텔레그램 Bot API, 실시간 알림 |
| 배포 | Docker Compose | 로컬 개발 및 단일 서버 배포, 향후 K8s 확장 가능 |

---

## 의존성 맵

> 아래는 초기 계획 기준 의존성 맵입니다 (Phase 0~5). Phase 5+ 이후는 순차 진행.

```
Phase 0 (환경 설정)
  |
  v
Phase 1 (기반 구축) -----> Phase 2 (프론트엔드 UI)
  |                              |
  v                              v
Phase 3 (백엔드 핵심 기능) <---- Phase 2 (UI 피드백 반영)
  |
  v
Phase 4 (부가 기능)
  |
  v
Phase 5 (안정화 및 배포)
  |
  v
Phase 5+ (Sprint 11~12) → Phase 6 (Sprint 13) → Phase 7 (Sprint 14~15)
  |
  v
Phase 8 (Sprint 16) → Phase 9 (Sprint 17)
```

**작업 간 세부 의존성:**
- Docker 환경 설정 -> DB 스키마 -> 백엔드 API -> 프론트엔드 연동
- python-kis 연동 -> 시세 조회 -> 전략 엔진 -> 자동매매 실행
- 전략 엔진 -> 백테스팅 엔진 (전략 로직 공유)
- 주문 실행 -> 알림 서비스 (주문 이벤트 트리거)
- 프론트엔드 UI 완성 -> 사용자 피드백 -> 백엔드 로직 확정

---

## Phase 0: 프로젝트 준비 (Sprint 0, Week 0)
### 목표
개발 환경 설정 및 외부 서비스 사전 준비를 완료하여 즉시 개발에 착수할 수 있는 상태를 만든다.

### 작업 목록
- ✅ **한국투자증권 계정 준비**
  - ✅ 한국투자증권 계좌 개설 (비대면)
  - ✅ HTS ID 등록
  - ✅ KIS Developers 서비스 신청
  - ✅ App Key / App Secret 발급 (실계좌 + 모의투자)
  - ✅ 모의투자 계정 별도 신청
- ✅ **텔레그램 봇 생성**
  - ✅ BotFather로 봇 생성
  - ✅ 봇 토큰 발급
  - ✅ 테스트 채팅방 설정 및 Chat ID 확인
- ✅ **개발 환경 설정**
  - ✅ Python 3.12+ 설치 확인 — Python 3.12.12 (Homebrew)
  - ✅ Node.js 22+ (LTS) 설치 확인 — Node.js 25.6.0 (Homebrew)
  - ✅ Docker Desktop 설치 및 설정 — Docker 29.2.1 (Homebrew Cask)
  - ✅ Git 레포지토리 초기화 (monorepo 구조) — `cd3c6f3` (2026-02-28)
  - ✅ `.env.example` 파일 생성 (API 키 템플릿) — `cd3c6f3` (2026-02-28)
  - ✅ `.gitignore` 설정 (API 키, 환경변수 파일 제외) — `cd3c6f3` (2026-02-28)
  - ✅ `.env` 파일 생성 및 전체 환경변수 입력 완료 (2026-03-01)

### 완료 기준 (Definition of Done)
- 한국투자증권 모의투자 API 키가 발급되어 `.env` 파일에 설정됨
- 텔레그램 봇이 생성되고 테스트 메시지 전송이 확인됨
- Docker Desktop이 정상 실행됨
- 프로젝트 레포지토리가 초기화되고 `.gitignore` 설정 완료

### 기술 고려사항
- API 키는 절대 Git에 커밋하지 않도록 `.env` 파일을 `.gitignore`에 포함
- TLS 1.2 이상만 지원됨 (2025.12.12 이후 TLS 1.0/1.1 미지원)
- 모의투자 API Rate Limit: 초당 5건 (실전: 초당 20건)

---

## Phase 1: 프로젝트 기반 구축 (Sprint 1-2, Week 1-2)
### 목표
Monorepo 프로젝트 구조를 확립하고, Docker 기반 개발 환경을 구성하며, DB 스키마 설계 및 한국투자증권 API 기본 연동을 완료한다.

### 작업 목록

#### Sprint 1 (Week 1): 프로젝트 구조 및 인프라 ✅ 완료 (2026-03-01)
- ✅ **Monorepo 프로젝트 구조 생성** [Must Have] [복잡도: 낮음]
  - `/frontend` - Next.js 16 프로젝트 초기화 (App Router, TypeScript, Tailwind v4)
  - `/backend` - FastAPI 프로젝트 초기화 (pydantic-settings, SQLAlchemy 2.x)
  - `/docker` - Docker 관련 설정 파일 (backend/frontend Dockerfile)
  - `docker-compose.yml` 생성 (frontend, backend, postgres, redis)
- ✅ **Docker Compose 환경 구성** [Must Have] [복잡도: 중간]
  - PostgreSQL 16 컨테이너 설정 (healthcheck 포함)
  - Redis 7 컨테이너 설정 (healthcheck 포함)
  - FastAPI 백엔드 컨테이너 (핫 리로드 지원)
  - Next.js 프론트엔드 컨테이너 (핫 리로드 지원)
  - 네트워크 및 볼륨 설정 (postgres_data 영구 볼륨)
  - 환경변수 파일 연동 (`.env`) + Docker 네트워크 호스트 오버라이드
- ✅ **FastAPI 백엔드 기본 설정** [Must Have] [복잡도: 중간]
  - FastAPI 앱 초기화 (`app/main.py`)
  - CORS 미들웨어 설정
  - 환경변수 설정 모듈 (`app/core/config.py`)
  - 로깅 설정 (`app/core/logging.py`)
  - 헬스체크 엔드포인트 (`/api/v1/health`)
- ✅ **DB 스키마 설계 및 마이그레이션 설정** [Must Have] [복잡도: 중간]
  - SQLAlchemy 2.x ORM 모델 정의 (10개 테이블)
    - `users`, `watchlist_groups`, `watchlist_items`
    - `strategies`, `strategy_params`
    - `orders`, `order_logs`
    - `portfolio_snapshots`, `backtest_results`, `system_settings`
  - Alembic 마이그레이션 초기화 및 env.py 설정
  - 초기 마이그레이션 스크립트 생성 (`alembic/versions/`)
  - seed 데이터 스크립트 (`scripts/seed.py`, 기본 전략 프리셋 3종)

#### Sprint 2 (Week 2): API 연동 기반
- ✅ **한국투자증권 API 클라이언트 모듈** [Must Have] [복잡도: 높음]
  - python-kis 라이브러리 설치 및 초기 설정
  - 인증 모듈 (`services/kis_client.py`)
    - OAuth 2.0 토큰 발급/갱신 로직
    - 토큰 만료 전 5분 자동 갱신
    - 모의투자/실전투자 환경 전환 설정
  - 현재가 조회 API 래핑
  - 일봉/주봉/월봉 데이터 조회 API 래핑
  - 잔고 조회 API 래핑
  - API Rate Limit 처리 (모의: 초당 5건)
  - API 호출 실패 시 재시도 로직 (최대 3회, 지수 백오프)
- ✅ **기본 인증 시스템 (단일 유저)** [Must Have] [복잡도: 낮음]
  - 환경변수 기반 단일 유저 인증
  - API 엔드포인트 보호 미들웨어
  - 설정 페이지용 API 키 등록/조회 엔드포인트
- ✅ **Next.js 프론트엔드 기본 설정** [Must Have] [복잡도: 중간]
  - Next.js 16+ App Router 프로젝트 구조 설정
  - TailwindCSS + shadcn/ui 초기화
  - 공통 레이아웃 컴포넌트 (사이드바, 헤더, 푸터)
  - TanStack Query Provider 설정
  - zustand 스토어 초기 구조
  - API 클라이언트 유틸리티 (`lib/api/client.ts`)
  - 라우팅 구조 설정 (dashboard, watchlist, strategy, backtest, orders, settings)

### 완료 기준 (Definition of Done)
- `docker-compose up` 명령으로 전체 서비스(frontend, backend, postgres, redis)가 정상 기동됨
- FastAPI `/api/v1/health` 엔드포인트가 200 응답 반환
- DB 마이그레이션이 성공적으로 실행되고 모든 테이블이 생성됨
- python-kis를 통한 모의투자 환경 현재가 조회가 성공함
- Next.js 프론트엔드가 localhost:3001에서 기본 레이아웃과 함께 렌더링됨
- API 토큰 자동 갱신이 로그로 확인됨

### Playwright MCP 검증 시나리오
> `npm run dev` 또는 `docker-compose up` 실행 후 아래 순서로 검증

**프론트엔드 기본 렌더링 검증:**
```
1. browser_navigate -> http://localhost:3001 접속
2. browser_snapshot -> 기본 레이아웃(사이드바, 헤더) 렌더링 확인
3. browser_click -> 사이드바 메뉴 항목(Dashboard, Watchlist 등) 클릭
4. browser_snapshot -> 해당 페이지 라우팅 확인
5. browser_console_messages(level: "error") -> 콘솔 에러 없음 확인
```

**백엔드 API 검증:**
```
1. browser_navigate -> http://localhost:8000/docs 접속 (Swagger UI)
2. browser_snapshot -> FastAPI 자동 문서 렌더링 확인
3. browser_network_requests -> /api/v1/health 호출 200 응답 확인
```

### 기술 고려사항
- Docker Compose에서 `depends_on`과 `healthcheck`를 사용하여 서비스 기동 순서 보장
- python-kis의 WebSocket 기능은 이 Phase에서는 사용하지 않음 (Phase 3에서 적용)
- TA-Lib C 라이브러리는 Docker 이미지에 사전 설치 (빌드 시간 단축 위해 멀티스테이지 빌드 고려)
- 모의투자 환경에서 먼저 모든 API를 검증한 후 실전 전환

---

## Phase 2: 프론트엔드 UI 개발 (Sprint 3-4, Week 3-4)
### 목표
백엔드 API 완성 전에 프론트엔드 UI를 먼저 개발하여 사용자(개발자 본인) 피드백을 조기에 수집한다. Mock 데이터를 사용하여 전체 화면 흐름을 검증한다.

### 작업 목록

#### Sprint 3 (Week 3): 핵심 화면 UI ✅ 완료 (2026-03-01, Playwright MCP 검증 완료)
- ✅ **대시보드 화면 UI** [Must Have] [복잡도: 높음]
  - 포트폴리오 총 평가금액 / 일일 손익 / 총 수익률 카드
  - 보유종목 리스트 테이블 (Mock 데이터)
  - 오늘의 매매 신호 요약 카드
  - 실행된 주문 요약 타임라인
  - 전략별 성과 요약 카드
  - KOSPI/KOSDAQ 지수 미니 차트 (Lightweight Charts v5)
- ✅ **관심종목 관리 화면 UI** [Must Have] [복잡도: 중간]
  - 종목 검색 입력 (종목코드 또는 종목명)
  - 검색 결과 드롭다운 (Popover)
  - 그룹별 관심종목 목록 (Tabs)
  - 종목별 현재가, 등락률, 주요 지표 테이블
  - 종목 추가/삭제 기능
  - 종목별 전략 할당 드롭다운
- ✅ **보유종목(포트폴리오) 화면 UI** [Must Have] [복잡도: 중간]
  - 보유종목 테이블 (종목명, 매입가, 수량, 현재가, 수익률, 평가금액)
  - 종목별 손절/익절 라인 설정 인라인 편집
  - 종목별 매도 전략 선택
  - 포트폴리오 파이 차트 (Recharts 도넛)

#### Sprint 4 (Week 4): 전략/백테스팅/설정 화면 UI ✅ 완료 (2026-03-01)
- ✅ **전략 설정 화면 UI** [Must Have] [복잡도: 높음]
  - 프리셋 전략 3종 카드 형태 표시
    - 골든크로스 + RSI 복합
    - 가치 + 모멘텀 하이브리드
    - 볼린저 밴드 반전
  - 전략 상세 파라미터 조절 폼 (슬라이더, 숫자 입력 필드)
  - 전략 활성화/비활성화 토글
  - 종목-전략 매핑 테이블 (어떤 종목에 어떤 전략 적용 중인지)
- ✅ **백테스팅 화면 UI** [Should Have] [복잡도: 중간]
  - 전략 선택 드롭다운
  - 종목 선택 (멀티 셀렉트)
  - 기간 선택 (데이트 레인지 피커, 3년~10년)
  - 실행 버튼 및 로딩 상태
  - 결과 대시보드 (Mock): 수익 곡선, MDD, 샤프비율 카드
  - 벤치마크(KOSPI) 대비 비교 차트
  - 거래 내역 테이블 (진입/청산 가격, 수익률)
- ✅ **주문 내역 화면 UI** [Must Have] [복잡도: 중간]
  - 미체결 주문 목록 탭
  - 체결 완료 주문 히스토리 탭
  - 주문별 전략명, 판단 근거 표시
  - 수동 주문 취소 버튼
  - 필터 (날짜, 종목, 전략, 매수/매도)
- ✅ **설정 화면 UI** [Must Have] [복잡도: 낮음]
  - 한국투자증권 API 키 등록 폼 (appkey, appsecret)
  - 모의투자/실전투자 환경 전환 토글
  - 텔레그램 봇 토큰 및 Chat ID 설정 폼
  - 매매 시간 설정 (시작/종료 시각)
  - 안전장치 설정
    - 일일 최대 손실 한도 (금액)
    - 일일 최대 주문 횟수
    - 단일 종목 최대 투자 비중 (%)
  - 자동매매 마스터 ON/OFF 스위치
  - 긴급 전체 매도 버튼 (확인 모달 포함)
- ✅ **커스텀 전략 빌더 UI** [Could Have] [복잡도: 높음] ✅ 완료 (2026-03-01, Sprint 4.1)
  - 지표 선택 드롭다운 (SMA, EMA, RSI, MACD, BB, ATR, Volume Ratio, Price 등 8종)
  - AND/OR 조건 조합 빌더 (매수/매도 조건 섹션 분리)
  - 파라미터 입력 필드 (지표별 동적 파라미터 렌더링)
  - 전략 미리보기 (텍스트 요약 - 조건 자동 변환)
  - 전략 저장/불러오기 (Zustand + localStorage persist)

### 완료 기준 (Definition of Done)
- 모든 화면이 Mock 데이터로 정상 렌더링됨
- 사이드바 네비게이션으로 모든 페이지 이동이 가능함
- 반응형 레이아웃이 모바일(375px)과 데스크톱(1920px)에서 정상 동작함
- 폼 입력 및 버튼 클릭에 대한 UI 피드백(로딩, 성공, 에러 상태)이 구현됨
- 차트 컴포넌트가 Mock 데이터로 정상 렌더링됨
- 콘솔 에러 없음

### Playwright MCP 검증 시나리오
> `npm run dev` 실행 후 아래 순서로 검증

**대시보드 검증:**
```
1. browser_navigate -> http://localhost:3001/dashboard 접속
2. browser_snapshot -> 포트폴리오 요약 카드, 보유종목 테이블, 차트 렌더링 확인
3. browser_console_messages(level: "error") -> 에러 없음 확인
```

**관심종목 화면 검증:**
```
1. browser_navigate -> http://localhost:3001/watchlist 접속
2. browser_snapshot -> 종목 검색 입력, 관심종목 그룹 탭 확인
3. browser_type -> 검색 입력란에 "삼성전자" 입력
4. browser_snapshot -> 검색 결과 드롭다운 표시 확인
5. browser_click -> 검색 결과 항목 클릭
6. browser_snapshot -> 관심종목에 추가됨 확인
```

**전략 설정 화면 검증:**
```
1. browser_navigate -> http://localhost:3001/strategy 접속
2. browser_snapshot -> 프리셋 전략 3종 카드 렌더링 확인
3. browser_click -> 전략 카드 클릭 (예: 골든크로스 + RSI)
4. browser_snapshot -> 파라미터 조절 폼 표시 확인
5. browser_click -> 활성화 토글 클릭
6. browser_snapshot -> 토글 상태 변경 확인
```

**설정 화면 검증:**
```
1. browser_navigate -> http://localhost:3001/settings 접속
2. browser_snapshot -> API 키 폼, 안전장치 설정 렌더링 확인
3. browser_click -> 긴급 전체 매도 버튼
4. browser_snapshot -> 확인 모달 표시 확인
5. browser_click -> 모달 취소 버튼
6. browser_snapshot -> 모달 닫힘 확인
```

**반응형 레이아웃 검증:**
```
1. browser_resize -> { width: 375, height: 812 } (모바일)
2. browser_snapshot -> 모바일 레이아웃 확인 (사이드바 접힘 등)
3. browser_resize -> { width: 1920, height: 1080 } (데스크톱)
4. browser_snapshot -> 데스크톱 레이아웃 확인
```

### 기술 고려사항
- Mock 데이터는 `/frontend/lib/mock/` 디렉토리에 관리하여 추후 API 연동 시 교체 용이하게 구성
- shadcn/ui의 DataTable, Card, Dialog, Select, Slider 등 컴포넌트 활용
- Lightweight Charts는 주가 차트에, Recharts는 포트폴리오 파이차트/바차트에 사용
- TanStack Query의 `queryFn`을 Mock 함수로 구현 후, 백엔드 연동 시 실제 API로 교체
- 반응형 디자인은 TailwindCSS의 breakpoint 시스템(`sm`, `md`, `lg`, `xl`) 활용

---

## Phase 3: 백엔드 핵심 기능 개발 (Sprint 5-7, Week 5-7)
### 목표
프론트엔드 UI 피드백을 반영하여 핵심 백엔드 API를 구현한다. 관심종목 관리, 전략 엔진, 자동매매 실행, 손절/익절 로직을 완성하고 프론트엔드와 실제 연동한다.

### 작업 목록

#### Sprint 5 (Week 5): 관심종목/보유종목 관리 API ✅ 완료 (2026-03-01)
- ✅ **종목 검색 API** [Must Have] [복잡도: 중간]
  - pykrx 기반 종목 마스터 Redis 캐시 (TTL 24시간)
  - `GET /api/v1/stocks/search?q={query}` 엔드포인트
- ✅ **관심종목 CRUD API** [Must Have] [복잡도: 중간]
  - 관심종목 그룹 생성/조회/수정/삭제
  - 관심종목 추가/삭제
  - 종목별 전략 할당
  - `POST/GET/PUT/DELETE /api/v1/watchlist/...` 엔드포인트
- ✅ **보유종목 동기화 API** [Must Have] [복잡도: 중간]
  - 한국투자증권 잔고 조회 API 연동 (avg_price 포함)
  - 보유종목 데이터 DB upsert 동기화
  - 포트폴리오 요약 계산 (총평가/손익/예수금)
  - 종목별 손절/익절 라인 설정 API
  - `GET/POST /api/v1/holdings/...` 엔드포인트
- ✅ **프론트엔드-백엔드 연동 (관심종목/보유종목)** [Must Have] [복잡도: 중간]
  - Mock 데이터를 실제 API 호출로 교체 (use-watchlist, use-portfolio, use-dashboard)
  - TanStack Query mutation hooks 신규 구현 (use-watchlist-mutations, use-holdings-mutations)
  - 에러 핸들링 및 로딩 상태 처리

#### Sprint 6 (Week 6): 전략 엔진 및 자동매매 - 완료 (2026-03-01)
- ✅ **기술적 분석 지표 엔진** [Must Have] [복잡도: 높음]
  - pandas-ta 연동
  - 지표 계산 서비스 (`services/indicators.py`)
    - SMA/EMA 이동평균
    - RSI (14일)
    - MACD
    - Bollinger Bands
    - ATR
    - Volume Ratio
  - 지표 계산 결과 캐싱 (Redis, TTL 5분)
  - 일봉 데이터 기반 지표 계산
- ✅ **프리셋 전략 3종 구현** [Must Have] [복잡도: 높음]
  - 전략 엔진 코어 (`services/strategy_engine.py`) - BaseStrategy 추상 클래스
  - 전략 1: GoldenCrossRSIStrategy - SMA(20)>SMA(60) AND RSI<40 AND 거래량>20일평균×1.5
  - 전략 2: BollingerReversalStrategy - 종가<BB하단 AND RSI<30
  - 전략 3: ValueMomentumStrategy - 20일 모멘텀>5% AND RSI<65
  - 전략 파라미터 조정 API (`api/v1/strategies.py`)
  - 전략 실행 스케줄러 (`services/scheduler.py`, APScheduler, 장중 매 5분)
- ✅ **자동 주문 실행 엔진** [Must Have] [복잡도: 높음]
  - 주문 실행 서비스 (`services/order_executor.py`)
  - 매수/매도 주문 실행 (KIS API: place_order)
  - 중복 주문 방지 (동일 종목+방향 미체결 주문 확인)
  - 주문 실행 로그 DB 저장 (판단 근거 포함)
  - KIS API 미설정 시 시뮬레이션 모드 지원

#### Sprint 7 (Week 7): 손절/익절 및 안전장치 ✅ 완료 (2026-03-01)
- ✅ **손절/익절 자동 관리** [Must Have] [복잡도: 중간]
  - 고정 비율 손절 (-N%)
  - 트레일링 스탑 (Redis 최고가 기반, 고점 대비 -N%)
  - ATR 기반 손절 (ATR * N배)
  - 고정 비율 익절 (+N%)
  - 분할 익절 (50% 도달 시 반량 매도, 100% 도달 시 전량 매도)
  - 손절/익절 모니터링 스케줄러 (장중 1분 간격)
- ✅ **매매 안전장치 구현** [Must Have] [복잡도: 중간]
  - 일일 최대 손실 한도 체크 (초과 시 당일 매매 중단)
  - 일일 최대 주문 횟수 체크
  - 단일 종목 최대 투자 비중 체크 (포트폴리오의 N%)
  - 자동매매 마스터 ON/OFF 스위치 API (Redis+DB 연동)
  - 긴급 전체 매도 API (시장가 일괄 매도 + 자동매매 비활성화)
  - 모든 안전장치 트리거 시 로그 기록
- ✅ **시스템 안전장치 구현** [Must Have] [복잡도: 중간]
  - API 호출 실패 시 재시도 (3회, 지수 백오프) — order_executor 통합
  - 중복 주문 방지 (Redis SET NX EX 분산 락)
  - 에러 카운터 및 임계값 초과 시 자동매매 중단
  - 시스템 상태 조회 API
- ✅ **프론트엔드-백엔드 연동 (전략/주문)** [Must Have] [복잡도: 중간]
  - 주문 내역 화면 API 연동 (hooks/use-orders.ts)
  - 설정 화면 API 연동 (hooks/use-settings.ts: systemSettings, safetyStatus, autoTrade, emergencySell)

### 완료 기준 (Definition of Done)
- 관심종목 추가/삭제/그룹 관리가 프론트엔드에서 정상 동작함
- 보유종목이 한국투자증권 API와 동기화됨
- 3종 프리셋 전략이 정상적으로 매매 신호를 생성함
- 모의투자 환경에서 자동 매수/매도 주문이 실행됨
- 손절/익절 로직이 설정된 기준에 따라 정상 동작함
- 모든 안전장치가 정상 작동하고 트리거 시 로그가 기록됨
- 긴급 전체 매도 기능이 정상 동작함

### Playwright MCP 검증 시나리오
> `docker-compose up` 실행 후 아래 순서로 검증

**관심종목 API 연동 검증:**
```
1. browser_navigate -> http://localhost:3001/watchlist 접속
2. browser_snapshot -> 관심종목 페이지 렌더링 확인
3. browser_type -> 종목 검색란에 "005930" 입력 (삼성전자)
4. browser_wait_for -> 검색 결과 표시 대기
5. browser_click -> 검색 결과에서 삼성전자 클릭
6. browser_snapshot -> 관심종목에 삼성전자 추가됨 확인
7. browser_network_requests -> /api/v1/watchlist 호출 200/201 확인
8. browser_console_messages(level: "error") -> 에러 없음 확인
```

**전략 설정 API 연동 검증:**
```
1. browser_navigate -> http://localhost:3001/strategy 접속
2. browser_snapshot -> 전략 카드 렌더링 확인 (실제 DB 데이터)
3. browser_click -> 전략 활성화 토글 클릭
4. browser_network_requests -> /api/v1/strategy 호출 200 확인
5. browser_snapshot -> 토글 상태 변경 확인
```

**주문 내역 검증:**
```
1. browser_navigate -> http://localhost:3001/orders 접속
2. browser_snapshot -> 주문 내역 테이블 렌더링 확인
3. browser_click -> 필터 탭(미체결/체결완료) 클릭
4. browser_snapshot -> 필터된 결과 확인
5. browser_network_requests -> /api/v1/orders 호출 200 확인
```

**설정 화면 API 연동 검증:**
```
1. browser_navigate -> http://localhost:3001/settings 접속
2. browser_fill_form -> API 키, 안전장치 설정 입력
3. browser_click -> 저장 버튼
4. browser_wait_for -> "저장되었습니다" 토스트 메시지 대기
5. browser_network_requests -> /api/v1/settings 호출 200 확인
```

### 기술 고려사항
- python-kis의 WebSocket 연결은 실시간 체결 알림에만 사용 (호가 모니터링은 Phase 4에서)
- 전략 엔진은 APScheduler로 장중 시간(09:00-15:30)에만 실행
- 장 시작 전(08:50) 전략 분석 사전 실행으로 매매 신호 준비
- 가치 분석 지표(PER, PBR, ROE)는 한국투자증권 API 또는 별도 데이터 소스에서 일 1회 업데이트
- 중복 주문 방지는 Redis의 SET NX (분산 락) 패턴 활용
- 주문 실행 로그에는 반드시 판단 근거(어떤 전략, 어떤 지표 값으로 판단)를 함께 저장

---

## Phase 4: 부가 기능 개발 (Sprint 8-9, Week 8-9)
### 목표
백테스팅 엔진, 텔레그램 알림 시스템, 실시간 WebSocket 데이터 연동 등 부가 기능을 구현하여 MVP를 완성한다.

### 작업 목록

#### Sprint 8 (Week 8): 백테스팅 엔진 ✅ 완료 (2026-03-01)
- ✅ **VectorBT 연동 및 백테스팅 엔진** [Should Have] [복잡도: 높음]
  - VectorBT 라이브러리 설치 및 초기화 (numpy>=1.24.0, vectorbt>=0.26.0)
  - 한국투자증권 일봉 데이터 -> VectorBT pandas Series 변환
  - 3종 프리셋 전략을 VectorBT 시그널 로직으로 포팅
  - 백테스팅 실행 서비스 (`services/backtest_engine.py`) - VectorBT 미설치 시 기본 시뮬레이션 폴백 지원
  - 백테스팅 결과 계산 (`services/backtest_metrics.py`)
    - 총 수익률, CAGR
    - MDD (Maximum Drawdown)
    - 샤프 비율 (Sharpe Ratio)
    - 승률 (Win Rate)
  - 벤치마크(KOSPI 지수) 대비 비교 데이터 생성
  - 백테스팅 결과 DB 저장 (backtest_results 테이블 스키마 확장)
  - `POST /api/v1/backtest/run` 엔드포인트
  - `GET /api/v1/backtest/results` 엔드포인트
  - `GET /api/v1/backtest/results/{id}` 엔드포인트
  - Alembic 마이그레이션 (symbol, start_date, end_date 컬럼 추가, strategy_id nullable)
- ✅ **백테스팅 결과 시각화 연동** [Should Have] [복잡도: 중간]
  - 성과 지표 카드 (CAGR, MDD, 샤프비율 등)
  - 수익 곡선 데이터 (equity_curve) API 반환
  - 프론트엔드 Mock 데이터를 실제 API로 교체 (`hooks/use-backtest.ts` - useBacktestRun, useBacktestResults, useBacktestResult)

#### Sprint 9 (Week 9): 알림 및 실시간 기능 ✅ 완료 (2026-03-02)
- ✅ **텔레그램 알림 서비스** [Must Have] [복잡도: 중간]
  - python-telegram-bot 연동 (기존 Sprint 8 구현 기반)
  - 알림 서비스 (`services/telegram_notifier.py`)
  - 알림 유형 구현
    - 매수/매도 주문 실행 알림 (notify_order_executed)
    - 주문 체결 확인 알림 (notify_risk_triggered)
    - 손절/익절 트리거 알림
    - 전략 신호 발생 알림 - 사전 알림 (notify_strategy_signal)
    - 일일 포트폴리오 요약 (평일 16:00 KST 크론 잡, notify_daily_portfolio_summary)
    - 시스템 에러 알림 (notify_system_error, notify_auto_trade_disabled)
  - 알림 템플릿 (Markdown 포맷)
  - 알림 ON/OFF 개별 설정 (_is_notification_enabled, system_settings 조회)
- ✅ **실시간 WebSocket 연동** [Should Have] [복잡도: 높음]
  - 프론트엔드 WebSocket 클라이언트 구현 (hooks/use-realtime.ts)
  - 보유종목 실시간 시세 업데이트
  - 실시간 체결 알림 UI (sonner 토스트, WebSocket 브로드캐스트)
- ✅ **대시보드 실시간 데이터 완성** [Must Have] [복잡도: 중간]
  - 대시보드의 모든 Mock 데이터를 실제 API 연동으로 교체 (4개 훅)
  - 전략별 성과 집계 API (GET /api/v1/strategies/performance)
  - 일일 매매 요약 API (GET /api/v1/orders/daily-summary)
  - 시장 지수 API (GET /api/v1/stocks/market-index)
  - 자동 새로고침 (TanStack Query refetchInterval 60~120초)

### 완료 기준 (Definition of Done)
- 백테스팅이 3종 전략에 대해 최소 3년 데이터로 실행되고 결과가 차트로 표시됨
- 성과 지표(CAGR, MDD, 샤프비율 등)가 정확히 계산됨
- 텔레그램 알림이 모든 유형에 대해 실시간으로 전송됨
- 대시보드에 실시간 시세 및 포트폴리오 데이터가 반영됨
- WebSocket 연결 끊김 시 자동 재연결이 동작함

### Playwright MCP 검증 시나리오
> `docker-compose up` 실행 후 아래 순서로 검증

**백테스팅 화면 검증:**
```
1. browser_navigate -> http://localhost:3001/backtest 접속
2. browser_snapshot -> 백테스팅 설정 폼 렌더링 확인
3. browser_select_option -> 전략 선택 (골든크로스 + RSI)
4. browser_type -> 종목 입력 (삼성전자)
5. browser_click -> 실행 버튼
6. browser_wait_for -> "백테스팅 완료" 텍스트 대기 (타임아웃 60초)
7. browser_snapshot -> 결과 차트(수익 곡선, 드로우다운) 렌더링 확인
8. browser_snapshot -> 성과 지표 카드(CAGR, MDD 등) 확인
9. browser_network_requests -> /api/v1/backtest 호출 200 확인
10. browser_console_messages(level: "error") -> 에러 없음 확인
```

**대시보드 실시간 데이터 검증:**
```
1. browser_navigate -> http://localhost:3001/dashboard 접속
2. browser_snapshot -> 실시간 데이터 카드 렌더링 확인
3. browser_network_requests -> API 호출 확인 (portfolio, orders, strategy 등)
4. browser_console_messages(level: "error") -> 에러 없음 확인
```

### 기술 고려사항
- VectorBT는 Apache 2.0 라이선스로 상용 배포 시 라이선스 문제 없음
- 백테스팅 실행은 CPU 집약적이므로 비동기 태스크로 처리 (APScheduler 또는 별도 스레드)
- 텔레그램 메시지는 Markdown v2 포맷 사용 (특수 문자 이스케이프 주의)
- WebSocket 동시 등록 종목 수 제한 (세션당 41건) 고려하여 관심종목 우선순위 설정
- 일일 포트폴리오 요약은 장 마감 후(15:30) 자동 발송 스케줄 설정

---

## Phase 5: 안정화 및 MVP 출시 (Sprint 10, Week 10)
### 목표
모의투자 환경에서 전체 시스템 통합 테스트를 수행하고, 안정성을 검증하여 MVP를 완성한다. 최소 5일 연속 무장애 운영을 달성한다.

#### Sprint 10 (Week 10): 통합 테스트, 안정화, MVP 출시 준비 ✅ 완료 (2026-03-02)
- ✅ **에러 핸들링 강화** [Must Have] [복잡도: 중간]
  - 모든 API 엔드포인트 에러 응답 표준화 (에러 코드, 메시지) - `exceptions.py` 신규
  - 5개 글로벌 예외 핸들러 등록 (AppError, IntegrityError, OperationalError 등)
  - RequestIdMiddleware 추가 (X-Request-ID 헤더)
  - 프론트엔드 글로벌 에러 핸들러 구현 (error.tsx, global-error.tsx, not-found.tsx)
  - TanStack Query MutationCache 글로벌 onError → toast.error
- ✅ **로깅 및 모니터링 강화** [Must Have] [복잡도: 중간]
  - 구조화된 로그 포맷 (JSON, python-json-logger)
  - 요청별 소요 시간(duration_ms) 로그 기록
  - Health Check 개선: DB/Redis/스케줄러 실제 상태 확인
- ✅ **Mock 데이터 → 실제 API 연동** [Must Have] [복잡도: 중간]
  - orders/page.tsx: Zustand mock → useOrders() 훅
  - settings/page.tsx: Zustand mock → 실제 API 훅
  - backtest/page.tsx: setTimeout mock → useBacktestRun() 뮤테이션
- ✅ **백엔드 통합 테스트** [Must Have] [복잡도: 중간]
  - pytest + httpx + aiosqlite 인메모리 DB 기반 테스트 인프라
  - test_health.py (3개), test_orders.py (4개), test_auth.py (3개), test_safety.py (4개)
- ✅ **문서화** [Should Have] [복잡도: 낮음]
  - README.md 작성 (프로젝트 소개, 설치 가이드, 실행 방법)
  - 환경변수 설정 가이드 (`.env.example` 상세 주석)
  - deploy.md Sprint 10 검증 섹션 추가 (섹션 14)
- ⬜ **통합 테스트 (모의투자)** [Must Have] [복잡도: 높음] — 모의투자 5일 연속 운영 (사용자 직접 수행 필요)
- ⬜ **실전 투자 전환 준비** [Must Have] [복잡도: 낮음] — deploy.md 체크리스트 참고

### 완료 기준 (Definition of Done)
- 모의투자 환경에서 최소 5일 연속 무장애 운영 달성
- 3종 전략이 모두 정상적으로 매매 신호를 생성하고 주문이 실행됨
- 모든 안전장치가 설계대로 동작함
- 텔레그램 알림이 모든 이벤트에 대해 실시간 전송됨
- 에러 발생 시 적절한 에러 메시지와 복구 로직이 동작함
- 실전 투자 전환 체크리스트가 완성됨

### Playwright MCP 검증 시나리오
> `docker-compose up` 실행 후 전체 흐름 E2E 검증

**전체 흐름 E2E 검증:**
```
1. browser_navigate -> http://localhost:3001/settings 접속
2. browser_fill_form -> API 키, 텔레그램 설정, 안전장치 설정 입력
3. browser_click -> 저장 버튼
4. browser_wait_for -> 저장 완료 확인

5. browser_navigate -> http://localhost:3001/watchlist 접속
6. browser_type -> 종목 검색 ("005930")
7. browser_click -> 관심종목 추가
8. browser_snapshot -> 추가 확인

9. browser_navigate -> http://localhost:3001/strategy 접속
10. browser_click -> 골든크로스+RSI 전략 활성화 토글
11. browser_snapshot -> 활성화 확인

12. browser_navigate -> http://localhost:3001/dashboard 접속
13. browser_snapshot -> 포트폴리오 데이터, 매매 신호 확인
14. browser_network_requests -> 모든 API 호출 200 확인

15. browser_navigate -> http://localhost:3001/orders 접속
16. browser_snapshot -> 주문 내역 확인

17. browser_console_messages(level: "error") -> 전 페이지 에러 없음 확인
```

**안전장치 검증:**
```
1. browser_navigate -> http://localhost:3001/settings 접속
2. browser_snapshot -> 안전장치 설정 확인
3. browser_click -> 자동매매 마스터 OFF 스위치
4. browser_snapshot -> OFF 상태 확인
5. browser_click -> 긴급 전체 매도 버튼
6. browser_snapshot -> 확인 모달 표시
7. browser_click -> 확인 버튼
8. browser_wait_for -> "전체 매도 완료" 메시지 대기
9. browser_network_requests -> 매도 API 호출 확인
```

### 기술 고려사항
- 통합 테스트는 장중 시간(09:00-15:30)에 실제 모의투자 환경에서 수행
- 로그는 Docker 볼륨으로 영구 저장하여 장애 분석에 활용
- 실전 전환 시 반드시 소액으로 테스트 매매 후 정상 동작 확인
- 시스템 에러 알림은 텔레그램뿐만 아니라 서버 로그에도 기록

---

## Phase 5+: 기반 개선 (Sprint 11-12)
### 목표
MVP 출시 이후 발견된 구조적 문제 및 UX 개선 사항을 해결한다.

#### Sprint 11: 로그인 페이지 + 데모 모드 ✅ 완료 (2026-03-02)
- ✅ 로그인 페이지 구현 (단일 유저 세션 기반)
- ✅ 데모 모드 구현 (KIS API 미설정 시 Mock 데이터로 전체 기능 체험 가능)

#### Sprint 12: KIS API 듀얼 환경 분리 ✅ 완료 (2026-03-03)
- ✅ **DB `system_settings`**: KIS 듀얼 키(모의/실전) 설정을 DB에서 관리 (환경변수 방식에서 DB 방식으로 전환)
- ✅ **`backend/app/services/kis_client.py`**: 시세 API는 항상 실전 키, 주문/잔고 API는 `KIS_ENVIRONMENT`에 따라 분기
  - `is_quote_available()` 신규 메서드 추가
  - `_get_access_token(env)` 환경별 토큰 캐시 분리
  - `_get_trade_credentials()` 주문/잔고용 자격증명 선택
- ✅ **`.env.example`**: 듀얼 키 설정 예제 업데이트
- ✅ **`frontend/src/lib/mock/types.ts`**: `KisApiConfig` 타입 듀얼 키 구조로 변경
- ✅ **`frontend/src/lib/mock/settings.ts`**: 목 데이터 업데이트
- ✅ **`frontend/src/components/settings/kis-api-form.tsx`**: 모의/실전 키 입력 섹션 분리
- ✅ **`frontend/src/app/settings/page.tsx`**: 파싱/저장 로직 업데이트
- ✅ **`deploy.md`**: Sprint 12 마이그레이션 가이드 추가
- ✅ 백엔드 통합 테스트 14개 PASSED

### 완료 기준 (Definition of Done)
- 모의투자 모드(`KIS_ENVIRONMENT=vts`)에서도 현재가, 차트, 시장지수 데이터가 정상 조회됨
- 주문/잔고는 모의투자 서버에서, 시세는 실전 서버에서 각각 처리됨
- `.env.example`에 새 환경변수 구조가 명확히 문서화됨
- 설정 페이지에 모의투자/실전투자 키 분리 섹션이 표시됨

---

## Phase 6: MVP 안정화 (Sprint 13)
### 목표
Sprint 0~12 전체 코드 리뷰에서 발견된 긴급 버그 및 중요 이슈를 수정하여 실거래 안전성을 확보한다.

#### Sprint 13: MVP 안정화 - 핵심 버그 수정 및 코드 품질 개선 ✅ 완료 (2026-03-03)

- ✅ **[긴급]** `order_executor.py` 분산 락 경합 조건 수정 (락 블록 외부에서 실행되던 로직을 내부로 이동)
- ✅ **[긴급]** `risk_manager.py` 전량/분할 익절 순서 수정 (전량 익절을 분할보다 먼저 체크)
- ✅ **[중요]** `strategies.py` N+1 쿼리 최적화 (IN 쿼리 + SQL GROUP BY 집계)
- ✅ **[중요]** `_get_user_id` 중복 함수 추출 → `core/deps.py`로 통합
- ✅ **[중요]** `kis_client.py` httpx 연결 풀 공유 (lazy 싱글턴 AsyncClient)
- ✅ **[중요]** `stocks.py` 데모 모드 누락 보완 (balance/quote/chart 엔드포인트)
- ✅ **[중요]** `safety_guard.py` 손실 계산 네이밍 수정 (`daily_loss_pct` → `unrealized_loss_pct`)
- ✅ **[중요]** 프론트엔드 Mock Zustand 스토어 삭제 (orders-store, settings-store)
- ✅ **[중요]** API 타입 중복 해소 → `lib/api/types.ts` 공통 파일 생성
- ✅ **[중요]** 주문 취소 기능 구현 (백엔드 PUT 엔드포인트 + 프론트 훅 + 페이지 연결)
- ✅ **[권장]** `scheduler.py` 하드코딩 제거 (user_id=1 → 전체 사용자 조회, quantity=1 → 설정값 조회)
- ✅ **[권장]** `portfolio.py` 미사용 모델 주석 추가
- ✅ 백엔드 통합 테스트 **33개 PASSED** (기존 14개 → 33개)
- ✅ 데모 모드 API 9개 엔드포인트 전부 200 응답 확인

### 완료 기준 (Definition of Done)
- 분산 락 경합 조건 해소 (실거래 중복 주문 방지)
- 익절 순서 버그 수정 (100% 수익률 시 전량 익절)
- 데모 유저 모든 페이지 503 에러 없음
- 주문 취소 기능 동작 (pending → cancelled)
- 33개 테스트 전부 PASSED
- TypeScript 빌드 에러 없음

---

## Phase 7: 멀티유저 기반 구축 (Sprint 14~)

### 목표
단일 유저 환경에서 멀티유저를 지원하는 구조로 전환한다. JWT 인증, 초대 코드 기반 회원가입, 역할 기반 접근 제어(RBAC)를 도입한다.

#### Sprint 14: JWT 인증 + User 모델 확장 ✅ 완료 (2026-03-03)
- ✅ `requirements.txt`에 `python-jose[cryptography]`, `bcrypt` 추가 (passlib 미사용, bcrypt 직접 호출)
- ✅ `config.py`에 JWT 설정 추가 (`JWT_SECRET`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`, `ADMIN_EMAIL`)
- ✅ User 모델 확장 (`email`, `password_hash`, `role`, `invited_by`, `is_approved` 필드)
- ✅ InvitationCode 모델 신규 생성 (초대 코드 기반 회원가입)
- ✅ `core/auth.py` JWT 기반으로 재작성 (`create_access_token`, `create_refresh_token`, `get_current_user` → User 객체 반환)
- ✅ `schemas/auth.py` 확장 (`RegisterRequest`, `RefreshRequest`, `TokenResponse.refresh_token`)
- ✅ 인증 API: `POST /auth/register`, `/auth/login`, `/auth/refresh`, `/auth/demo`
- ✅ 관리자 API (`api/v1/admin.py`): 초대 코드 CRUD, 사용자 목록/승인/비활성화
- ✅ 전체 라우터 9개: `current_user: str` → `User` 객체로 변경
- ✅ Alembic 마이그레이션 (`c3d4e5f6a7b8`)
- ✅ 프론트엔드 `auth-store.ts`: refreshToken 저장, `setToken` 메서드
- ✅ 프론트엔드 `client.ts`: 401 시 자동 토큰 갱신 (refresh 플로우)
- ✅ 로그인 페이지 이메일 방식으로 변경
- ✅ `scripts/seed.py` 관리자 계정 생성 시 JWT 필드 포함

#### Sprint 15: 사용자별 전략/백테스트 데이터 격리 + 복사된 전략 관리 기능 보완 ✅ 완료 (2026-03-03)

**1단계: 사용자별 데이터 격리**
- ✅ Strategy 모델: `user_id` (nullable FK) 추가 — NULL=프리셋, 값=사용자 소유
- ✅ BacktestResult 모델: `user_id` (NOT NULL FK) 추가
- ✅ Alembic 마이그레이션 (`d4e5f6a7b8c9`)
- ✅ Strategy API 격리: GET /strategies (프리셋+본인), GET/PUT/activate/params (본인 소유만)
- ✅ Strategy API 신규: POST /strategies/{id}/clone (프리셋→사용자 소유 복사)
- ✅ Backtest API 격리: POST /run (user_id 저장), GET /results (본인만), GET /results/{id} (본인만)
- ✅ Schema: `StrategyResponse`에 `user_id` 필드 추가
- ✅ Demo Data: 전략 더미 데이터 `user_id: None` 추가
- ✅ 프론트엔드 `use-strategy.ts`: `StrategyAPI.user_id` 추가, `useCloneStrategy` 훅
- ✅ 프론트엔드 `strategy-card-list.tsx`: 프리셋 토글 차단, "내 전략으로 복사" 버튼
- ✅ 프론트엔드 `strategy-detail-panel.tsx`: 프리셋 파라미터 읽기전용 표시

**2단계: 복사된 전략 관리 기능 보완**
- ✅ 파라미터 설명 표시: `param_key` 기반 한국어 레이블·설명 정적 매핑
- ✅ 전략 이름 변경: `PUT /strategies/{id}/name` 엔드포인트 + 인라인 편집 UI
- ✅ 전략 삭제: `DELETE /strategies/{id}` 엔드포인트 + 확인 다이얼로그 UI (FK NULL 처리)
- ✅ 버그 수정: 파라미터 폼 미표시, 저장 미연동 수정
- ✅ 전체 테스트 **45 passed** (기존 33 + 신규 12)

### 완료 기준 (Definition of Done)
- JWT access token + refresh token 인증 플로우 동작
- 초대 코드 기반 회원가입 동작
- 관리자 API를 통한 사용자 승인/비활성화 동작
- 모든 API 엔드포인트가 User 객체 기반 인증으로 동작
- 사용자별 전략/백테스트 데이터 격리 완료
- 프리셋 전략 복사(clone) 기능 동작
- 복사된 전략 이름 변경/삭제/파라미터 확인 가능

---

## Phase 8: 관리자 대시보드 + 초대코드 회원가입 (Sprint 16)
### 목표
백엔드에만 존재하는 관리자 API를 프론트엔드와 연결하여 초대코드 발급, 사용자 승인/비활성화를 UI로 수행할 수 있게 하고, 초대코드 기반 회원가입 플로우를 완성한다.

#### Sprint 16: 관리자 대시보드 UI + 초대코드 회원가입 플로우 완성 ✅ 완료 (2026-03-04)
- ✅ **백엔드 관리자 API 통합 테스트** (`tests/api/test_admin.py`, 5개 이상)
  - 초대코드 생성/목록/삭제 API 테스트
  - 사용자 목록/승인/비활성화 API 테스트
- ✅ **auth-store role 필드 + /auth/me 엔드포인트**
  - `auth-store.ts`에 `role` 필드 추가
  - `/api/v1/auth/me` 엔드포인트 → 로그인 시 role 자동 fetch
- ✅ **관리자 API 훅** (`use-admin.ts`)
  - `useInvitations`, `useCreateInvitation`, `useDeleteInvitation`
  - `useAdminUsers`, `useApproveUser`, `useDeactivateUser`
- ✅ **AdminGuard 컴포넌트** (`admin-guard.tsx`)
  - role=admin인 경우에만 children 렌더링, 비관리자는 빈 화면 차단
- ✅ **초대코드 탭 컴포넌트** (`invitation-tab.tsx`)
  - 초대코드 발급 (유효기간 선택), 목록 테이블 (상태 Badge), 링크/코드 복사 버튼
- ✅ **사용자 관리 탭 컴포넌트** (`users-tab.tsx`)
  - 사용자 목록 테이블, 승인/비활성화 버튼, 상태 Badge
- ✅ **관리자 대시보드 페이지 조립** (`app/admin/page.tsx`)
  - Tabs로 초대코드/사용자 관리 탭 조립 + AdminGuard 적용
- ✅ **사이드바 관리자 메뉴 추가** (role=admin인 경우에만 표시)
- ✅ **회원가입 페이지 구현** (`app/register/page.tsx`)
  - 이메일, 비밀번호, 비밀번호 확인, 초대코드 입력 폼
  - `useSearchParams`로 `?code=` URL 파라미터 자동 주입
- ✅ 전체 테스트 **50 passed** (기존 45 + 신규 5)
- ✅ TypeScript 빌드 에러 없음

### 완료 기준 (Definition of Done)
- 관리자 로그인 후 /admin 접속 시 초대코드·사용자 관리 대시보드가 렌더링됨
- 비관리자 /admin 접속 시 빈 화면(AdminGuard 차단) 처리됨
- 사이드바에서 관리자 메뉴가 admin 유저에게만 표시됨
- /register?code=xxx 접속 시 초대코드 자동 입력됨
- 초대코드 발급/복사/삭제 기능 동작
- 사용자 승인/비활성화 기능 동작
- pytest 50 passed 이상

---

## Phase 9: MVP 프로덕션 배포 준비 (Sprint 17)
### 목표
Docker 프로덕션 환경을 구성하고 Lightsail 배포를 위한 인프라를 준비한다.

#### Sprint 17: MVP 프로덕션 배포 준비 ✅ 완료 (2026-03-05)
- ✅ `.dockerignore` 추가 (빌드 컨텍스트 최적화)
- ✅ `frontend/next.config.ts`: output='standalone', poweredByHeader=false 설정
- ✅ 프로덕션 Dockerfile 작성 (backend/frontend 멀티스테이지 빌드, 비-root 실행)
- ✅ `docker-compose.prod.yml` 작성 (postgres/redis 외부 포트 미노출, restart 정책, 로그 rotation)
- ✅ Nginx 리버스 프록시 추가 (80 포트, /api/* → backend, / → frontend)
- ✅ CORS_ORIGINS 환경변수화, DEBUG=False 시 시크릿 키 경고, 헬스체크 503 반환
- ✅ `gunicorn>=22.0.0` 의존성 추가
- ✅ deploy.md: Lightsail 프로덕션 배포 절차, 체크리스트, 5일 안정 운영 가이드 추가
- ✅ 빌드/테스트 버그 3건 수정 (.dockerignore tests 제외, Dockerfile.prod npm ci, test 패치)

---

## 리스크 및 완화 전략

| 리스크 | 영향도 | 발생 확률 | 완화 전략 |
|--------|--------|-----------|-----------|
| 한국투자증권 API 변경/장애 | 높음 | 중간 | python-kis 라이브러리 버전 고정, API 변경 모니터링, 재시도 로직 |
| API Rate Limit 초과 | 중간 | 높음 | Redis 기반 Rate Limiter 구현, 호출 간격 조절, 캐싱 적극 활용 |
| TA-Lib 설치 실패 | 낮음 | 중간 | pandas-ta를 기본 대안으로 사용, Docker 이미지에 사전 빌드 |
| 모의투자와 실전투자 동작 차이 | 높음 | 중간 | 모의투자에서 충분한 검증 후 실전 전환, 소액 테스트 우선 |
| WebSocket 연결 불안정 | 중간 | 중간 | 자동 재연결 로직, 연결 끊김 시 REST API 폴백 |
| 전략 로직 버그로 인한 의도치 않은 매매 | 높음 | 중간 | 안전장치(일일 손실 한도, 최대 주문 횟수), 모의투자 충분 검증 |
| VectorBT API 변경 이슈 | 낮음 | 낮음 | 버전 고정(0.26.x) 후 사용, 주요 변경 시 마이그레이션 가이드 참고 |
| 장시간 무인 운영 시 예상치 못한 오류 | 높음 | 중간 | 포괄적 에러 핸들링, 텔레그램 즉시 알림, 자동 복구 로직 |

---

## 마일스톤

| 마일스톤 | 예상 완료일 | 핵심 산출물 |
|----------|-------------|-------------|
| M0: 환경 준비 완료 | 2026-03-01 | API 키 발급, 개발 환경 설정 |
| M1: 기반 구축 완료 | 2026-03-14 | Docker 환경, DB 스키마, API 연동, 기본 UI 레이아웃 |
| M2: 프론트엔드 UI 완성 | 2026-03-28 | 전체 화면 Mock 데이터 기반 동작 |
| M3: 핵심 기능 완성 | 2026-04-19 | 자동매매 실행, 전략 엔진, 안전장치 |
| M4: MVP 기능 완성 | 2026-05-03 | 백테스팅, 텔레그램 알림, 실시간 데이터 |
| M5: MVP 출시 | 2026-05-10 | 모의투자 5일 연속 안정 운영, 실전 전환 준비 |

---

## 기술 부채 관리

### Phase 1-2 발생 예상 기술 부채
- ⬜ 프론트엔드 Mock 데이터 하드코딩 (Phase 3에서 해소)
- ✅ 단일 유저 인증 시스템 → JWT 기반 멀티유저로 전환 완료 (Sprint 14)
- ⬜ APScheduler 단일 프로세스 스케줄러 (트래픽 증가 시 Celery로 전환)

### Phase 3-4 발생 예상 기술 부채
- ⬜ 전략 로직과 주문 실행의 강결합 (이벤트 드리븐 아키텍처로 리팩토링 필요)
- ⬜ 백테스팅 동기 실행 (대용량 데이터 시 비동기 태스크 큐 필요)
- ⬜ 캐싱 전략 미세 조정 (TTL 최적화)

### 향후 리팩토링 계획
- Phase 5 이후: 이벤트 드리븐 아키텍처 도입 (전략 신호 -> 주문 실행 -> 알림 파이프라인)
- 멀티유저 확장 시: JWT 인증, 사용자별 격리, RBAC(역할 기반 접근 제어)
- 대규모 확장 시: Celery + Redis 작업 큐, Docker Swarm/K8s 배포

---

## 향후 계획 (Backlog) - MVP 이후

### 단기 (MVP 완료 후 1-2개월)
- ⬜ 실전투자 환경 전환 및 소액 테스트 운영
- ⬜ 커스텀 전략 빌더 고도화 (드래그 앤 드롭 UI)
- ⬜ 전략별 상세 성과 분석 리포트
- ⬜ 카카오톡 알림 연동 (나에게 보내기)
- ⬜ 모바일 최적화 (PWA)

### 중기 (MVP 완료 후 3-6개월)
- ✅ JWT 인증 도입 완료 (Sprint 14)
- ✅ 초대 코드 기반 회원가입 완료 (Sprint 14)
- ✅ 사용자별 전략/백테스트 격리 완료 (Sprint 15)
- ⬜ Celery 기반 분산 작업 스케줄링
- ⬜ 실시간 호가 모니터링 (WebSocket)
- ⬜ 해외 주식 지원 (미국 주식)

### 장기 (6개월 이후)
- ⬜ AWS/GCP 클라우드 배포 + Kubernetes
- ⬜ AI/ML 기반 전략 추천
- ⬜ 소셜 트레이딩 기능 (전략 공유/구독)
- ⬜ 금융 규제 대응 (멀티유저 오픈 시)
- ⬜ 모바일 네이티브 앱 (React Native)

---

## 부록: 스프린트 캘린더

| 스프린트 | 기간 | Phase | 핵심 목표 |
|----------|------|-------|-----------|
| Sprint 0 | 2026-03-02 ~ | Phase 0 | 환경 준비 (1-2일) |
| Sprint 1 | 2026-03-02 ~ 03-07 | Phase 1 | 프로젝트 구조, Docker, DB |
| Sprint 2 | 2026-03-09 ~ 03-14 | Phase 1 | API 연동, 인증, 프론트 기본설정 |
| Sprint 3 | 2026-03-16 ~ 03-21 | Phase 2 | 대시보드, 관심종목, 포트폴리오 UI |
| Sprint 4 | 2026-03-23 ~ 03-28 | Phase 2 | 전략, 백테스팅, 주문, 설정 UI |
| Sprint 5 | 2026-03-30 ~ 04-04 | Phase 3 | 관심종목/보유종목 API 연동 |
| Sprint 6 | 2026-04-06 ~ 04-11 | Phase 3 | 전략 엔진, 자동매매 엔진 |
| Sprint 7 | 2026-04-13 ~ 04-18 | Phase 3 | 손절/익절, 안전장치 |
| Sprint 8 | 2026-04-20 ~ 04-25 | Phase 4 | 백테스팅 엔진 |
| Sprint 9 | 2026-04-27 ~ 05-02 | Phase 4 | 텔레그램 알림, 실시간 WebSocket |
| Sprint 10 | 2026-05-04 ~ 05-09 | Phase 5 | 통합 테스트, 안정화, MVP 출시 |
| Sprint 11 | 2026-03-02 | Phase 5+ | 로그인 페이지 + 데모 모드 구현 |
| Sprint 12 | 2026-03-03 | Phase 5+ | KIS API 듀얼 환경 분리 (모의투자/실전투자 키 분리) |
| Sprint 13 | 2026-03-03 | Phase 6 | MVP 안정화 - 긴급 버그 수정 및 코드 품질 개선 |
| Sprint 14 | 2026-03-03 | Phase 7 | JWT 인증 + User 모델 확장 (멀티유저 기반 구축) |
| Sprint 15 | 2026-03-03 | Phase 7 | 사용자별 전략/백테스트 데이터 격리 + 복사된 전략 관리 기능 보완 |
| Sprint 16 | 2026-03-04 | Phase 8 | 관리자 대시보드 UI + 초대코드 회원가입 플로우 완성 |
| Sprint 17 | 2026-03-05 | Phase 9 | MVP 프로덕션 배포 준비 (Docker prod, Nginx, 보안 설정) |

> **참고:** 1-2인 소규모 팀 기준으로 각 스프린트는 5 영업일(월-금)로 설정. 주말 및 공휴일은 버퍼로 활용. 예상보다 빠르게 진행되면 Phase 간 간격을 줄이고, 지연 시 Could Have 항목을 다음 Phase로 이동.
