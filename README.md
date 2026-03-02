# AutoTrader KR (mystock.bot)

한국투자증권 Open API 기반 퀀트 자동매매 웹 애플리케이션

---

## 주요 기능

- **한국투자증권 API 연동** - 현재가, 일봉 데이터, 잔고 조회, 주문 실행
- **퀀트 전략 엔진** - 골든크로스+RSI, 볼린저밴드, 가치+모멘텀 복합 전략
- **자동매매 실행** - APScheduler 기반 장중 5분 간격 전략 평가 및 주문
- **손절/익절 관리** - 고정비율, 트레일링 스탑, ATR 기반 동적 손절
- **매매 안전장치** - 일일 최대손실 제한, 주문횟수 제한, 긴급 전체매도
- **백테스팅** - VectorBT 기반 CAGR/MDD/샤프비율 성과 분석
- **텔레그램 알림** - 체결, 손절/익절 트리거, 전략 신호, 일일 요약 알림
- **실시간 시세** - WebSocket 기반 실시간 주가 스트리밍
- **대시보드** - 포트폴리오 요약, 수익률 차트, 실시간 매매 신호 현황

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| **Backend** | FastAPI (Python 3.12), SQLAlchemy, Alembic, APScheduler |
| **퀀트 라이브러리** | pandas-ta, VectorBT, python-kis (PyKIS 2.x) |
| **Frontend** | Next.js 16 (App Router), TypeScript, TailwindCSS v4, shadcn/ui |
| **차트** | Lightweight Charts (TradingView), Recharts |
| **상태 관리** | TanStack Query, Zustand |
| **DB** | PostgreSQL 16 |
| **캐시/큐** | Redis 7 |
| **알림** | python-telegram-bot 22.x |
| **인프라** | Docker Compose |

---

## 아키텍처

```
┌─────────────────────────────────────────────────────┐
│                   Browser (3001)                     │
│              Next.js 16 (App Router)                 │
│        Dashboard / Strategy / Backtest / Orders      │
└──────────────────────┬──────────────────────────────┘
                       │ REST API / WebSocket
┌──────────────────────▼──────────────────────────────┐
│                 FastAPI (8000)                        │
│   API Router → Services → Scheduler → KIS Client    │
└───────┬──────────────┬──────────────┬───────────────┘
        │              │              │
┌───────▼──────┐ ┌─────▼──────┐ ┌────▼────────────────┐
│  PostgreSQL  │ │   Redis    │ │  한국투자증권 API     │
│  (거래내역)  │ │ (시세캐시) │ │  (REST + WebSocket)  │
└──────────────┘ └────────────┘ └─────────────────────┘
```

---

## 프로젝트 구조

```
mystock.bot/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API 라우터 (잔고, 주문, 전략, 백테스트 등)
│   │   ├── core/            # 설정, 의존성, 보안
│   │   ├── models/          # SQLAlchemy ORM 모델
│   │   ├── schemas/         # Pydantic 스키마
│   │   ├── services/        # 비즈니스 로직 (KIS, 전략, 스케줄러 등)
│   │   └── main.py          # FastAPI 앱 진입점
│   ├── alembic/             # DB 마이그레이션
│   ├── scripts/seed.py      # 시드 데이터
│   └── requirements.txt
├── frontend/
│   └── src/app/
│       ├── page.tsx         # 대시보드 (/)
│       ├── strategy/        # 전략 관리 (/strategy)
│       ├── watchlist/       # 관심종목 (/watchlist)
│       ├── orders/          # 주문 내역 (/orders)
│       ├── backtest/        # 백테스팅 (/backtest)
│       ├── dashboard/       # 상세 대시보드 (/dashboard)
│       └── settings/        # 설정 (/settings)
├── docker/                  # Dockerfile (backend, frontend)
├── docker-compose.yml
├── deploy.md                # 배포 가이드
└── ROADMAP.md               # 프로젝트 로드맵
```

---

## 시작하기

### 사전 요구사항

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Docker Compose](https://docs.docker.com/compose/) v2.x 이상
- 한국투자증권 개발자 계정 및 API 키 ([KIS Developers](https://apiportal.koreainvestment.com))
- 텔레그램 봇 토큰 (선택)

### 1. 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 파일에서 필수 값을 설정합니다:

```env
POSTGRES_PASSWORD=your_secure_password
KIS_APP_KEY=your_app_key
KIS_APP_SECRET=your_app_secret
KIS_ACCOUNT_NO=12345678-01
TELEGRAM_BOT_TOKEN=your_bot_token   # 선택
TELEGRAM_CHAT_ID=your_chat_id       # 선택
```

### 2. 서비스 실행

```bash
docker compose up --build
```

### 3. DB 초기화

```bash
# 마이그레이션 실행
docker compose exec backend alembic upgrade head

# 시드 데이터 삽입 (기본 전략, 설정 등)
docker compose exec backend python scripts/seed.py
```

### 4. 접속

| 서비스 | URL |
|--------|-----|
| 프론트엔드 | http://localhost:3001 |
| 백엔드 API | http://localhost:8000 |
| API 문서 (Swagger) | http://localhost:8000/docs |

> 상세 배포 및 운영 가이드는 [`deploy.md`](./deploy.md)를 참조하세요.

---

## 프론트엔드 페이지

| 경로 | 페이지 | 설명 |
|------|--------|------|
| `/` | 대시보드 | 포트폴리오 요약, 수익률 차트, 실시간 신호 |
| `/dashboard` | 상세 대시보드 | 종합 현황 및 분석 |
| `/strategy` | 전략 관리 | 전략 목록, 활성화/비활성화, 파라미터 설정 |
| `/watchlist` | 관심종목 | 종목 추가/삭제, 실시간 시세 |
| `/orders` | 주문 내역 | 체결 내역, 미체결 주문 조회 |
| `/backtest` | 백테스팅 | 전략 성과 분석 (CAGR, MDD, 샤프비율) |
| `/settings` | 설정 | API 키, 안전장치, 알림 설정 |

---

## 프로젝트 문서

- [`ROADMAP.md`](./ROADMAP.md) - 프로젝트 로드맵 및 스프린트 현황
- [`docs/prd.md`](./docs/prd.md) - 제품 요구사항 정의서
- [`deploy.md`](./deploy.md) - 배포 및 운영 가이드
- [`docs/sprint/`](./docs/sprint/) - 스프린트별 계획/완료 기록
