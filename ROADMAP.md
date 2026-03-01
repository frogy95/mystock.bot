# 프로젝트 로드맵 - AutoTrader KR

## 개요
- **목표:** 한국투자증권 Open API를 활용한 KOSPI/KOSDAQ 퀀트 전략 기반 자동매매 웹 애플리케이션
- **전체 예상 기간:** 10주 (2026-03-02 ~ 2026-05-10)
- **현재 진행 단계:** Phase 3 진행 중 (Sprint 6 완료)
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
| 전체 진행률 | 72% (Sprint 0~6 완료) |
| 현재 Phase | Phase 3 진행 중 (Sprint 6 완료) |
| 완료된 스프린트 | Sprint 0 (2026-02-28), Sprint 1 (2026-03-01), Sprint 2 (2026-03-01), Sprint 3 (2026-03-01), Sprint 4 (2026-03-01), Sprint 4.1 (2026-03-01), Sprint 5 (2026-03-01), Sprint 6 (2026-03-01) |
| 다음 마일스톤 | Phase 3 Sprint 7 - 손절/익절 및 안전장치 |
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
| Backend | FastAPI (Python) | python-kis, TA-Lib, VectorBT 등 Python 퀀트 생태계 활용 |
| DB | PostgreSQL | ACID 트랜잭션, 거래 내역의 안정적 저장 |
| 캐시/큐 | Redis | 실시간 시세 버퍼, 작업 큐, 세션 관리 |
| 스케줄러 | APScheduler (MVP) -> Celery (확장) | MVP에서는 경량 스케줄러로 시작, 추후 Celery로 전환 |
| 증권 API | python-kis (PyKIS) 2.x | 커뮤니티 검증, WebSocket 자동 재연결, Thread-safe |
| 기술 분석 | pandas-ta (우선) / TA-Lib (고성능 필요 시) | pandas-ta는 순수 Python으로 설치 용이, TA-Lib은 C 의존성 |
| 백테스팅 | VectorBT 0.26.x | 벡터화 연산으로 고속 백테스팅, pandas 네이티브, Apache 2.0 |
| 알림 | python-telegram-bot 22.x | 텔레그램 Bot API, 실시간 알림 |
| 배포 | Docker Compose | 로컬 개발 및 단일 서버 배포, 향후 K8s 확장 가능 |

---

## 의존성 맵

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
- [x] **한국투자증권 계정 준비**
  - [x] 한국투자증권 계좌 개설 (비대면)
  - [x] HTS ID 등록
  - [x] KIS Developers 서비스 신청
  - [x] App Key / App Secret 발급 (실계좌 + 모의투자)
  - [x] 모의투자 계정 별도 신청
- [x] **텔레그램 봇 생성**
  - [x] BotFather로 봇 생성
  - [x] 봇 토큰 발급
  - [x] 테스트 채팅방 설정 및 Chat ID 확인
- [x] **개발 환경 설정**
  - [x] Python 3.12+ 설치 확인 — Python 3.12.12 (Homebrew)
  - [x] Node.js 22+ (LTS) 설치 확인 — Node.js 25.6.0 (Homebrew)
  - [x] Docker Desktop 설치 및 설정 — Docker 29.2.1 (Homebrew Cask)
  - [x] Git 레포지토리 초기화 (monorepo 구조) — `cd3c6f3` (2026-02-28)
  - [x] `.env.example` 파일 생성 (API 키 템플릿) — `cd3c6f3` (2026-02-28)
  - [x] `.gitignore` 설정 (API 키, 환경변수 파일 제외) — `cd3c6f3` (2026-02-28)
  - [x] `.env` 파일 생성 및 전체 환경변수 입력 완료 (2026-03-01)

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
- [x] **Monorepo 프로젝트 구조 생성** [Must Have] [복잡도: 낮음]
  - `/frontend` - Next.js 16 프로젝트 초기화 (App Router, TypeScript, Tailwind v4)
  - `/backend` - FastAPI 프로젝트 초기화 (pydantic-settings, SQLAlchemy 2.x)
  - `/docker` - Docker 관련 설정 파일 (backend/frontend Dockerfile)
  - `docker-compose.yml` 생성 (frontend, backend, postgres, redis)
- [x] **Docker Compose 환경 구성** [Must Have] [복잡도: 중간]
  - PostgreSQL 16 컨테이너 설정 (healthcheck 포함)
  - Redis 7 컨테이너 설정 (healthcheck 포함)
  - FastAPI 백엔드 컨테이너 (핫 리로드 지원)
  - Next.js 프론트엔드 컨테이너 (핫 리로드 지원)
  - 네트워크 및 볼륨 설정 (postgres_data 영구 볼륨)
  - 환경변수 파일 연동 (`.env`) + Docker 네트워크 호스트 오버라이드
- [x] **FastAPI 백엔드 기본 설정** [Must Have] [복잡도: 중간]
  - FastAPI 앱 초기화 (`app/main.py`)
  - CORS 미들웨어 설정
  - 환경변수 설정 모듈 (`app/core/config.py`)
  - 로깅 설정 (`app/core/logging.py`)
  - 헬스체크 엔드포인트 (`/api/v1/health`)
- [x] **DB 스키마 설계 및 마이그레이션 설정** [Must Have] [복잡도: 중간]
  - SQLAlchemy 2.x ORM 모델 정의 (10개 테이블)
    - `users`, `watchlist_groups`, `watchlist_items`
    - `strategies`, `strategy_params`
    - `orders`, `order_logs`
    - `portfolio_snapshots`, `backtest_results`, `system_settings`
  - Alembic 마이그레이션 초기화 및 env.py 설정
  - 초기 마이그레이션 스크립트 생성 (`alembic/versions/`)
  - seed 데이터 스크립트 (`scripts/seed.py`, 기본 전략 프리셋 3종)

#### Sprint 2 (Week 2): API 연동 기반
- [x] **한국투자증권 API 클라이언트 모듈** [Must Have] [복잡도: 높음]
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
- [x] **기본 인증 시스템 (단일 유저)** [Must Have] [복잡도: 낮음]
  - 환경변수 기반 단일 유저 인증
  - API 엔드포인트 보호 미들웨어
  - 설정 페이지용 API 키 등록/조회 엔드포인트
- [x] **Next.js 프론트엔드 기본 설정** [Must Have] [복잡도: 중간]
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
- [x] **대시보드 화면 UI** [Must Have] [복잡도: 높음]
  - 포트폴리오 총 평가금액 / 일일 손익 / 총 수익률 카드
  - 보유종목 리스트 테이블 (Mock 데이터)
  - 오늘의 매매 신호 요약 카드
  - 실행된 주문 요약 타임라인
  - 전략별 성과 요약 카드
  - KOSPI/KOSDAQ 지수 미니 차트 (Lightweight Charts v5)
- [x] **관심종목 관리 화면 UI** [Must Have] [복잡도: 중간]
  - 종목 검색 입력 (종목코드 또는 종목명)
  - 검색 결과 드롭다운 (Popover)
  - 그룹별 관심종목 목록 (Tabs)
  - 종목별 현재가, 등락률, 주요 지표 테이블
  - 종목 추가/삭제 기능
  - 종목별 전략 할당 드롭다운
- [x] **보유종목(포트폴리오) 화면 UI** [Must Have] [복잡도: 중간]
  - 보유종목 테이블 (종목명, 매입가, 수량, 현재가, 수익률, 평가금액)
  - 종목별 손절/익절 라인 설정 인라인 편집
  - 종목별 매도 전략 선택
  - 포트폴리오 파이 차트 (Recharts 도넛)

#### Sprint 4 (Week 4): 전략/백테스팅/설정 화면 UI ✅ 완료 (2026-03-01)
- [x] **전략 설정 화면 UI** [Must Have] [복잡도: 높음]
  - 프리셋 전략 3종 카드 형태 표시
    - 골든크로스 + RSI 복합
    - 가치 + 모멘텀 하이브리드
    - 볼린저 밴드 반전
  - 전략 상세 파라미터 조절 폼 (슬라이더, 숫자 입력 필드)
  - 전략 활성화/비활성화 토글
  - 종목-전략 매핑 테이블 (어떤 종목에 어떤 전략 적용 중인지)
- [x] **백테스팅 화면 UI** [Should Have] [복잡도: 중간]
  - 전략 선택 드롭다운
  - 종목 선택 (멀티 셀렉트)
  - 기간 선택 (데이트 레인지 피커, 3년~10년)
  - 실행 버튼 및 로딩 상태
  - 결과 대시보드 (Mock): 수익 곡선, MDD, 샤프비율 카드
  - 벤치마크(KOSPI) 대비 비교 차트
  - 거래 내역 테이블 (진입/청산 가격, 수익률)
- [x] **주문 내역 화면 UI** [Must Have] [복잡도: 중간]
  - 미체결 주문 목록 탭
  - 체결 완료 주문 히스토리 탭
  - 주문별 전략명, 판단 근거 표시
  - 수동 주문 취소 버튼
  - 필터 (날짜, 종목, 전략, 매수/매도)
- [x] **설정 화면 UI** [Must Have] [복잡도: 낮음]
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
- [x] **커스텀 전략 빌더 UI** [Could Have] [복잡도: 높음] ✅ 완료 (2026-03-01, Sprint 4.1)
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
- [x] **종목 검색 API** [Must Have] [복잡도: 중간]
  - pykrx 기반 종목 마스터 Redis 캐시 (TTL 24시간)
  - `GET /api/v1/stocks/search?q={query}` 엔드포인트
- [x] **관심종목 CRUD API** [Must Have] [복잡도: 중간]
  - 관심종목 그룹 생성/조회/수정/삭제
  - 관심종목 추가/삭제
  - 종목별 전략 할당
  - `POST/GET/PUT/DELETE /api/v1/watchlist/...` 엔드포인트
- [x] **보유종목 동기화 API** [Must Have] [복잡도: 중간]
  - 한국투자증권 잔고 조회 API 연동 (avg_price 포함)
  - 보유종목 데이터 DB upsert 동기화
  - 포트폴리오 요약 계산 (총평가/손익/예수금)
  - 종목별 손절/익절 라인 설정 API
  - `GET/POST /api/v1/holdings/...` 엔드포인트
- [x] **프론트엔드-백엔드 연동 (관심종목/보유종목)** [Must Have] [복잡도: 중간]
  - Mock 데이터를 실제 API 호출로 교체 (use-watchlist, use-portfolio, use-dashboard)
  - TanStack Query mutation hooks 신규 구현 (use-watchlist-mutations, use-holdings-mutations)
  - 에러 핸들링 및 로딩 상태 처리

#### Sprint 6 (Week 6): 전략 엔진 및 자동매매 - 완료 (2026-03-01)
- [x] **기술적 분석 지표 엔진** [Must Have] [복잡도: 높음]
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
- [x] **프리셋 전략 3종 구현** [Must Have] [복잡도: 높음]
  - 전략 엔진 코어 (`services/strategy_engine.py`) - BaseStrategy 추상 클래스
  - 전략 1: GoldenCrossRSIStrategy - SMA(20)>SMA(60) AND RSI<40 AND 거래량>20일평균×1.5
  - 전략 2: BollingerReversalStrategy - 종가<BB하단 AND RSI<30
  - 전략 3: ValueMomentumStrategy - 20일 모멘텀>5% AND RSI<65
  - 전략 파라미터 조정 API (`api/v1/strategies.py`)
  - 전략 실행 스케줄러 (`services/scheduler.py`, APScheduler, 장중 매 5분)
- [x] **자동 주문 실행 엔진** [Must Have] [복잡도: 높음]
  - 주문 실행 서비스 (`services/order_executor.py`)
  - 매수/매도 주문 실행 (KIS API: place_order)
  - 중복 주문 방지 (동일 종목+방향 미체결 주문 확인)
  - 주문 실행 로그 DB 저장 (판단 근거 포함)
  - KIS API 미설정 시 시뮬레이션 모드 지원

#### Sprint 7 (Week 7): 손절/익절 및 안전장치
- [ ] **손절/익절 자동 관리** [Must Have] [복잡도: 중간]
  - 고정 비율 손절 (-N%)
  - 트레일링 스톱 (고점 대비 -N%)
  - ATR 기반 손절 (ATR * N배)
  - 고정 비율 익절 (+N%)
  - 분할 익절 (50% 매도 후 나머지 트레일링)
  - 손절/익절 모니터링 스케줄러 (장중 1분 간격)
- [ ] **매매 안전장치 구현** [Must Have] [복잡도: 중간]
  - 일일 최대 손실 한도 체크 (초과 시 당일 매매 중단)
  - 일일 최대 주문 횟수 체크
  - 단일 종목 최대 투자 비중 체크 (포트폴리오의 N%)
  - 자동매매 마스터 ON/OFF 스위치 API
  - 긴급 전체 매도 API (시장가 일괄 매도)
  - 모든 안전장치 트리거 시 로그 기록 및 알림
- [ ] **시스템 안전장치 구현** [Must Have] [복잡도: 중간]
  - API 호출 실패 시 재시도 (3회, 지수 백오프)
  - WebSocket 연결 끊김 시 자동 재연결
  - 중복 주문 방지 (Redis 기반 락)
  - 모든 주문/판단 로그 영구 저장
  - 시스템 에러 발생 시 텔레그램 즉시 알림
- [ ] **프론트엔드-백엔드 연동 (전략/주문)** [Must Have] [복잡도: 중간]
  - 전략 설정 화면 API 연동
  - 주문 내역 화면 API 연동
  - 대시보드 실시간 데이터 연동
  - 설정 화면 API 연동 (API 키 등록, 안전장치 설정)

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

#### Sprint 8 (Week 8): 백테스팅 엔진
- [ ] **VectorBT 연동 및 백테스팅 엔진** [Should Have] [복잡도: 높음]
  - VectorBT 라이브러리 설치 및 초기화
  - 한국투자증권 일봉 데이터 -> VectorBT pandas Series 변환
  - 3종 프리셋 전략을 VectorBT 시그널 로직으로 포팅
  - 백테스팅 실행 서비스 (`services/backtest_engine.py`)
  - 백테스팅 결과 계산
    - 총 수익률, CAGR
    - MDD (Maximum Drawdown)
    - 샤프 비율 (Sharpe Ratio)
    - 승률 (Win Rate)
    - 손익비 (Profit Factor)
  - 벤치마크(KOSPI 지수) 대비 비교 데이터 생성
  - 백테스팅 결과 DB 저장
  - `POST /api/v1/backtest/run` 엔드포인트 (비동기 실행)
  - `GET /api/v1/backtest/{id}/result` 엔드포인트
- [ ] **백테스팅 결과 시각화 연동** [Should Have] [복잡도: 중간]
  - 수익 곡선 차트 (Recharts)
  - 드로우다운 차트
  - 벤치마크 비교 오버레이 차트
  - 거래 내역 테이블 (진입/청산 가격, 수익률)
  - 성과 지표 카드 (CAGR, MDD, 샤프비율 등)
  - 프론트엔드 Mock 데이터를 실제 API로 교체

#### Sprint 9 (Week 9): 알림 및 실시간 기능
- [ ] **텔레그램 알림 서비스** [Must Have] [복잡도: 중간]
  - python-telegram-bot 연동
  - 알림 서비스 (`services/alert_service.py`)
  - 알림 유형 구현
    - 매수/매도 주문 실행 알림
    - 주문 체결 확인 알림
    - 손절/익절 트리거 알림
    - 전략 신호 발생 알림 (사전 알림)
    - 일일 포트폴리오 요약 (장 마감 후 15:30~16:00)
    - 시스템 에러 알림
  - 알림 템플릿 (Markdown 포맷)
  - 알림 ON/OFF 개별 설정 API
- [ ] **실시간 WebSocket 연동** [Should Have] [복잡도: 높음]
  - 한국투자증권 WebSocket 실시간 체결 연동
  - 프론트엔드 WebSocket 클라이언트 구현
  - 보유종목 실시간 시세 업데이트
  - 실시간 체결 알림 UI (토스트/스낵바)
- [ ] **대시보드 실시간 데이터 완성** [Must Have] [복잡도: 중간]
  - 대시보드의 모든 데이터를 실시간 API 연동으로 교체
  - 전략별 성과 집계 API
  - 일일 매매 요약 API
  - 자동 새로고침 (TanStack Query refetchInterval)

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

### 작업 목록
- [ ] **통합 테스트 (모의투자)** [Must Have] [복잡도: 높음]
  - 전체 흐름 E2E 테스트
    - 관심종목 등록 -> 전략 할당 -> 매매 신호 생성 -> 자동 주문 -> 체결 -> 알림
  - 3종 전략별 모의투자 실행 (각 최소 2일)
  - 손절/익절 트리거 검증
  - 장중 연속 운영 안정성 테스트 (5일 연속 목표)
  - API Rate Limit 내 정상 동작 검증
- [ ] **에러 핸들링 강화** [Must Have] [복잡도: 중간]
  - 모든 API 엔드포인트 에러 응답 표준화 (에러 코드, 메시지)
  - 프론트엔드 글로벌 에러 핸들러 구현
  - API 호출 실패 시 사용자 친화적 에러 메시지 표시
  - 네트워크 오류 시 자동 재시도 (TanStack Query retry)
- [ ] **로깅 및 모니터링 강화** [Must Have] [복잡도: 중간]
  - 구조화된 로그 포맷 (JSON)
  - 로그 레벨 설정 (DEBUG/INFO/WARNING/ERROR)
  - 주문 실행 감사 로그 (audit log)
  - 시스템 상태 모니터링 대시보드 (간단한 헬스 페이지)
- [ ] **안전장치 최종 검증** [Must Have] [복잡도: 중간]
  - 일일 최대 손실 한도 도달 시 매매 자동 중단 검증
  - 일일 최대 주문 횟수 초과 방지 검증
  - 단일 종목 최대 비중 초과 방지 검증
  - 긴급 전체 매도 기능 검증
  - 중복 주문 방지 검증
  - WebSocket 재연결 검증
- [ ] **문서화** [Should Have] [복잡도: 낮음]
  - README.md 작성 (프로젝트 소개, 설치 가이드, 실행 방법)
  - 환경변수 설정 가이드 (`.env.example` 상세 주석)
  - API 문서 최종 검토 (FastAPI Swagger 자동 문서)
  - 면책 조항 작성 (자동매매 투자 조언 해당하지 않음)
- [ ] **실전 투자 전환 준비** [Must Have] [복잡도: 낮음]
  - 모의투자 -> 실전투자 환경변수 전환 가이드
  - 실전투자 전환 체크리스트 작성
  - API 도메인 전환 (`openapivts` -> `openapi`)
  - 실전 Rate Limit(초당 20건) 적용 확인

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
- [ ] 프론트엔드 Mock 데이터 하드코딩 (Phase 3에서 해소)
- [ ] 단일 유저 인증 시스템 (향후 JWT 기반 멀티유저로 전환 필요)
- [ ] APScheduler 단일 프로세스 스케줄러 (트래픽 증가 시 Celery로 전환)

### Phase 3-4 발생 예상 기술 부채
- [ ] 전략 로직과 주문 실행의 강결합 (이벤트 드리븐 아키텍처로 리팩토링 필요)
- [ ] 백테스팅 동기 실행 (대용량 데이터 시 비동기 태스크 큐 필요)
- [ ] 캐싱 전략 미세 조정 (TTL 최적화)

### 향후 리팩토링 계획
- Phase 5 이후: 이벤트 드리븐 아키텍처 도입 (전략 신호 -> 주문 실행 -> 알림 파이프라인)
- 멀티유저 확장 시: JWT 인증, 사용자별 격리, RBAC(역할 기반 접근 제어)
- 대규모 확장 시: Celery + Redis 작업 큐, Docker Swarm/K8s 배포

---

## 향후 계획 (Backlog) - MVP 이후

### 단기 (MVP 완료 후 1-2개월)
- [ ] 실전투자 환경 전환 및 소액 테스트 운영
- [ ] 커스텀 전략 빌더 고도화 (드래그 앤 드롭 UI)
- [ ] 전략별 상세 성과 분석 리포트
- [ ] 카카오톡 알림 연동 (나에게 보내기)
- [ ] 모바일 최적화 (PWA)

### 중기 (MVP 완료 후 3-6개월)
- [ ] 멀티유저 지원 (회원가입, 로그인, JWT 인증)
- [ ] 사용자별 전략/포트폴리오 격리
- [ ] Celery 기반 분산 작업 스케줄링
- [ ] 실시간 호가 모니터링 (WebSocket)
- [ ] 해외 주식 지원 (미국 주식)

### 장기 (6개월 이후)
- [ ] AWS/GCP 클라우드 배포 + Kubernetes
- [ ] AI/ML 기반 전략 추천
- [ ] 소셜 트레이딩 기능 (전략 공유/구독)
- [ ] 금융 규제 대응 (멀티유저 오픈 시)
- [ ] 모바일 네이티브 앱 (React Native)

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

> **참고:** 1-2인 소규모 팀 기준으로 각 스프린트는 5 영업일(월-금)로 설정. 주말 및 공휴일은 버퍼로 활용. 예상보다 빠르게 진행되면 Phase 간 간격을 줄이고, 지연 시 Could Have 항목을 다음 Phase로 이동.
