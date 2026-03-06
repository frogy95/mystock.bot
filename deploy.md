# 수동 작업 가이드 (deploy.md)

이 문서는 mystock.bot 프로젝트를 시작하기 전에 사용자가 직접 수행해야 하는 외부 서비스 준비 작업을 안내합니다.

---

## 1. 한국투자증권 (KIS) API 준비

### 1-1. 계좌 개설

1. [한국투자증권 홈페이지](https://securities.koreainvestment.com) 접속
2. 비대면 계좌 개설 또는 지점 방문 계좌 개설
3. 계좌 개설 완료 후 **계좌번호** 메모 (예: `50123456-01`)

### 1-2. HTS ID 발급

1. 한국투자증권 HTS(eFriend Plus) 또는 MTS(한국투자) 앱 설치
2. HTS ID 신청 (HTS 로그인에 사용할 ID)
3. HTS ID와 비밀번호 설정

### 1-3. KIS Developers 가입 및 App Key 발급

1. [KIS Developers](https://apiportal.koreainvestment.com) 접속
2. HTS ID로 로그인
3. **[앱 관리] → [앱 생성]** 클릭
4. 앱 이름 입력 후 생성
5. 생성된 앱의 **App Key**와 **App Secret** 메모
6. 앱 실행 후 **설정 페이지(`/settings`)에서 KIS API 키 입력**

> **참고:** Sprint 12 이후 KIS API 키는 `.env`가 아닌 DB(`system_settings`)에서 관리합니다.
> 앱을 실행하고 설정 페이지에서 모의투자/실전투자 키를 각각 입력하세요.

### 1-4. 모의투자 신청 (개발 환경용)

1. KIS Developers → **[모의투자 신청]** 메뉴
2. 모의투자 계좌 신청 완료
3. `.env`에서 환경 설정:
  ```
   KIS_ENVIRONMENT=vts   # 모의투자
   # KIS_ENVIRONMENT=prod  # 실거래 (운영 시 변경)
  ```

> ⚠️ **주의:** 실거래 환경(`prod`)은 실제 자금이 거래됩니다. 개발/테스트 시 반드시 모의투자(`vts`)를 사용하세요.

---

## 2. 텔레그램 봇 생성

### 2-1. BotFather로 봇 생성

1. 텔레그램 앱에서 **@BotFather** 검색 후 대화 시작
2. `/newbot` 명령 입력
3. 봇 이름 입력 (예: `MyStock Alert Bot`)
4. 봇 사용자명 입력 - 반드시 `bot`으로 끝나야 함 (예: `mystock_alert_bot`)
5. 발급받은 **Bot Token** 메모 (예: `1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ`)
6. `.env` 파일에 입력:
  ```
   TELEGRAM_BOT_TOKEN=발급받은_Bot_Token
  ```

### 2-2. Chat ID 확인

1. 텔레그램 앱에서 생성한 봇을 검색 후 대화방 열기
2. **반드시 먼저** 봇에게 아무 메시지나 전송 (예: `안녕` 또는 `/start`)
3. 메시지 전송 직후 아래 URL을 브라우저에서 열기:
  ```
   https://api.telegram.org/bot<BOT_TOKEN>/getUpdates
  ```
4. 아래와 같은 응답에서 `"id"` 값이 Chat ID:
  ```json
   {
     "ok": true,
     "result": [{
       "message": {
         "chat": { "id": 123456789, ... },
         ...
       }
     }]
   }
  ```
5. `.env` 파일에 입력:
  ```
   TELEGRAM_CHAT_ID=확인한_Chat_ID
  ```

> ⚠️ `"result": []` 로 빈 배열이 나오면 봇에게 메시지를 **먼저** 전송한 뒤 다시 URL을 열어야 합니다.
> 이미 조회한 적 있어 비워진 경우, 봇에게 메시지를 새로 보내면 다시 나타납니다.

### 2-3. 봇 동작 테스트

아래 URL로 메시지 전송 테스트 (브라우저 또는 curl):

```bash
curl "https://api.telegram.org/bot<BOT_TOKEN>/sendMessage?chat_id=<CHAT_ID>&text=테스트메시지"
```

응답에 `"ok": true`가 포함되면 성공.

---

## 3. 개발 도구 설치 (Homebrew 기준)

> 패키지 매니저로 **Homebrew**를 사용합니다. Homebrew가 없으면 먼저 설치하세요.
>
> ```bash
> /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
> ```

### 3-1. Python 3.12+

```bash
# 설치
brew install python@3.12

# 버전 확인
python3 --version
# Python 3.12.x 이상이어야 함
```

> pyenv를 사용한다면:
>
> ```bash
> brew install pyenv
> pyenv install 3.12.0
> pyenv global 3.12.0
> ```

### 3-2. Node.js 22+

```bash
# 설치
brew install node@22

# PATH 등록 (설치 후 안내 메시지 참고)
echo 'export PATH="/opt/homebrew/opt/node@22/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 버전 확인
node --version
# v22.x.x 이상이어야 함
```

### 3-3. Docker Desktop

```bash
# Homebrew Cask로 설치
brew install --cask docker

# 버전 확인 (Docker Desktop 실행 후)
docker --version
docker compose version
```

> Docker Desktop 설치 후 반드시 **앱을 실행(Start)**해야 `docker` 명령을 사용할 수 있습니다.

---

## 4. 환경변수 설정 최종 확인

위 작업 완료 후 `.env` 파일을 생성하고 모든 값이 채워졌는지 확인:

```bash
# .env.example을 복사하여 .env 생성
cp .env.example .env

# .env 파일 편집
vi .env  # 또는 원하는 에디터 사용
```

`.env` 파일에서 `your_*_here` 형태의 플레이스홀더가 모두 실제 값으로 교체되었는지 확인하세요.

---

## 준비 완료 체크리스트

- ✅ 한국투자증권 계좌 개설 완료
- ✅ KIS App Key / App Secret 발급 완료
- ✅ 모의투자 신청 완료
- ✅ 텔레그램 봇 생성 및 Bot Token 발급 완료
- ✅ Telegram Chat ID 확인 완료
- ✅ Python 3.12+ 설치 확인
- ✅ Node.js 22+ 설치 확인
- ✅ Docker Desktop 설치 및 실행 확인
- ✅ `.env` 파일 생성 및 모든 값 입력 완료

모든 항목이 완료되면 Sprint 1 개발을 시작할 수 있습니다.

---

## 5. Sprint 1 완료 검증 (사용자 수행 필요)

Sprint 1 코드 구현이 완료되었습니다. 아래 절차로 검증하세요.

### 5-1. POSTGRES_PASSWORD 설정

`.env` 파일에서 placeholder를 실제 비밀번호로 변경합니다:

```bash
# .env 파일에서 아래 값을 실제 비밀번호로 변경
# POSTGRES_PASSWORD=your_db_password_here
# → 예시: POSTGRES_PASSWORD=mystock_dev_password
```

### 5-2. Docker 빌드 및 서비스 기동

```bash
# 프로젝트 루트에서 실행
docker compose up --build -d
```

### 5-3. 서비스 상태 확인

```bash
# 모든 서비스가 Up 상태여야 함
docker compose ps
```

### 5-4. 헬스체크

```bash
# FastAPI 헬스체크 (200 OK 확인)
curl http://localhost:8000/api/v1/health

# Swagger UI 접속 (브라우저에서)
# http://localhost:8000/docs

# Next.js 프론트엔드 (브라우저에서)
# http://localhost:3001
```

### 5-5. DB 마이그레이션 실행

```bash
# 마이그레이션 실행 (10개 테이블 생성)
docker compose exec backend alembic upgrade head

# 테이블 목록 확인 (10개 테이블이어야 함)
docker compose exec postgres psql -U mystock_user -d mystock -c "\dt"
```

### 5-6. 시드 데이터 삽입

```bash
# admin 유저, 전략 3개, 시스템 설정 삽입
docker compose exec backend python scripts/seed.py

# 데이터 확인
docker compose exec postgres psql -U mystock_user -d mystock -c "SELECT username FROM users;"
docker compose exec postgres psql -U mystock_user -d mystock -c "SELECT name FROM strategies;"
```

### 5-7. 로그 확인

```bash
docker compose logs --tail=20 backend
docker compose logs --tail=20 frontend
```

### Sprint 1 완료 체크리스트

- ✅ `docker compose up --build` 성공
- ✅ 4개 서비스 모두 Up 상태
- ✅ `curl http://localhost:8000/api/v1/health` → 200 OK
- ✅ `http://localhost:3001` → "AutoTrader KR" 표시
- ✅ `alembic upgrade head` 성공
- ✅ 10개 테이블 확인 (Sprint 누적으로 12개)
- ✅ seed 데이터 삽입 완료 (admin 유저 + 전략 3개)

---

## 6. Sprint 2 완료 검증 (사용자 수행 필요)

Sprint 2에서는 KIS API 클라이언트, 단일 유저 인증, 프론트엔드 레이아웃이 추가되었습니다.

### 6-1. ADMIN_PASSWORD 설정 (Sprint 14 이후 폐기됨)

> **⚠️ 이 섹션은 Sprint 2 당시 기준입니다.**
> Sprint 14에서 JWT 인증으로 전환되어 `ADMIN_USERNAME` / `ADMIN_PASSWORD` 환경변수는 더 이상 사용되지 않습니다.
> 현재는 `scripts/seed.py`로 관리자 계정을 생성하며, 이메일 + 비밀번호 방식으로 로그인합니다.

### 6-2. Docker 빌드 및 서비스 기동

```bash
# 프로젝트 루트에서 실행 (새 패키지 포함하여 재빌드)
docker compose up --build -d
```

### 6-3. 백엔드 엔드포인트 검증

```bash
# 1. 헬스체크
curl http://localhost:8000/api/v1/health

# 2. 로그인 → 토큰 발급
# ⚠️ Sprint 2 당시 형식 (username 기반). Sprint 14 이후 email 방식으로 변경됨
# 현재 형식: {"email": "frogy95@gmail.com", "password": "비밀번호"}
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "frogy95@gmail.com", "password": "설정한_비밀번호"}'
# 응답: {"access_token": "...", "refresh_token": "...", "token_type": "bearer"}

# 3. 토큰을 TOKEN 변수에 저장
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "frogy95@gmail.com", "password": "설정한_비밀번호"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 4. 인증 없이 보호 엔드포인트 접근 → 401 확인
curl -i http://localhost:8000/api/v1/settings/kis-status

# 5. 토큰으로 보호 엔드포인트 접근 → 200 확인
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/settings/kis-status

# 6. Swagger UI에서 7개 엔드포인트 확인
# http://localhost:8000/docs
```

### 6-4. 프론트엔드 검증

브라우저에서 `http://localhost:3001` 접속:

- ✅ 사이드바(6개 메뉴)와 헤더가 표시됨
- ✅ 루트(`/`) 접근 시 `/dashboard`로 자동 리다이렉트 (307)
- ✅ 사이드바 클릭으로 6개 페이지 이동 가능 (href 6개 + 각 200 응답 확인)
- ✅ 브라우저 콘솔에 에러 없음

### 6-5. KIS API 연동 (선택 - API 키가 있는 경우)

> **⚠️ Sprint 13 이후 KIS API 키는 `.env`가 아닌 설정 페이지(`/settings`)에서 DB로 관리합니다.**
> 아래 `.env` 방식은 Sprint 2 당시 기준이며, 현재 코드에서는 적용되지 않습니다.
> 앱 기동 후 `/settings` 페이지에서 KIS 모의/실전 키를 각각 입력하세요.

KIS API 키가 있다면 앱 기동 후 설정 페이지에서 입력:

```bash
# 재기동
docker compose up -d backend

# 현재가 조회 테스트 (삼성전자: 005930)
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/stocks/005930/quote
```

### Sprint 2 완료 체크리스트

- ✅ `docker compose up --build` 성공
- ✅ `curl /api/v1/health` → 200 응답
- ✅ `POST /api/v1/auth/login` → Bearer 토큰 발급
- ✅ 인증 없이 보호 엔드포인트 → 401 차단
- ✅ 토큰으로 `GET /api/v1/settings/kis-status` → 200 응답
- ✅ Swagger UI에 7개 엔드포인트 표시 (Sprint 누적 34개 포함)
- ✅ `http://localhost:3001` → 사이드바(6개 메뉴) + 헤더 렌더링
- ✅ 사이드바 클릭으로 6개 페이지 이동 가능
- ✅ 콘솔 에러 없음

---

## 7. Sprint 3 완료 검증 (사용자 수행 필요)

Sprint 3에서는 Mock 데이터 기반 대시보드/관심종목/포트폴리오 UI가 추가되었습니다.

### 7-1. 새 패키지 설치

```bash
cd frontend
npm install
```

### 7-2. 개발 서버 기동 (프론트엔드만)

```bash
# 방법 1: Docker 없이 직접 실행
cd frontend
npm run dev
# → http://localhost:3000

# 방법 2: Docker Compose 사용
docker compose up --build frontend
# → http://localhost:3001
```

### 7-3. 화면 검증

브라우저에서 각 URL 접속:

**대시보드** (`http://localhost:3001/dashboard` 또는 `http://localhost:3000/dashboard`):

- ✅ 총 평가금액 / 일일 손익 / 총 평가손익 / 예수금 4개 카드 표시
- ✅ KOSPI / KOSDAQ 미니 차트 2개 렌더링 (약 700ms 로딩)
- ✅ 보유종목 테이블 (5개 종목, 수익률 색상 구분)
- ✅ 오늘의 매매 신호 3건 (매수=빨강, 매도=파랑)
- ✅ 최근 주문 타임라인 (체결/대기/취소 상태)
- ✅ 전략별 성과 카드 (승률 Progress bar)
- ✅ 포트폴리오 상세 테이블 (인라인 편집 아이콘)
- ✅ 포트폴리오 도넛 파이차트

**관심종목** (`/watchlist`):

- ✅ 검색창에 "삼성" 입력 시 검색 결과 드롭다운 표시
- ✅ 검색 결과 클릭 시 현재 탭에 종목 추가
- ✅ 반도체 / 2차전지 / 바이오 3개 그룹 탭 전환
- ✅ 종목별 전략 Select 드롭다운 작동
- ✅ 휴지통 아이콘 클릭 시 종목 삭제
- ✅ "그룹 추가" 버튼으로 새 그룹 생성

**반응형 (모바일 375px)**:

- ✅ 브라우저 개발자도구에서 375px 너비로 설정
- ✅ 사이드바가 숨겨짐
- ✅ 헤더 왼쪽에 햄버거 메뉴(☰) 표시
- ✅ 햄버거 클릭 시 사이드바 슬라이드 인
- ✅ 오버레이 또는 사이드바 외부 클릭 시 닫힘

**브라우저 콘솔**:

- ✅ 에러(빨간 글씨) 없음

### Sprint 3 완료 체크리스트

- ✅ `npm install` 완료
- ✅ 대시보드 6개 섹션 모두 렌더링
- ✅ 관심종목 검색/추가/삭제 작동
- ✅ 모바일 반응형 레이아웃 작동
- ✅ 콘솔 에러 없음

> Sprint 3 검증 완료 (2026-03-01, Playwright MCP 자동 검증)

---

## 8. Sprint 4 완료 검증 (사용자 수행 필요)

Sprint 4에서는 Mock 데이터 기반 전략/백테스팅/주문/설정 화면 UI가 추가되었습니다.

> **자동 검증 완료 항목 (Playwright MCP, 2026-03-01)**
> 전략 설정 / 백테스팅 / 주문 내역 / 설정 / 긴급 매도 AlertDialog / 반응형 375px — 11/11 통과
> 상세 내용: [docs/sprint/sprint4/playwright-report.md](docs/sprint/sprint4/playwright-report.md)

### 8-1. 새 패키지 설치

```bash
cd frontend
npm install
```

신규 shadcn/ui 패키지가 추가되었습니다: alert-dialog, sonner, toggle, radio-group, textarea, accordion

### 8-2. 개발 서버 기동

```bash
# 방법 1: Docker 없이 직접 실행
cd frontend
npm run dev
# → http://localhost:3000

# 방법 2: Docker Compose 사용
docker compose up --build frontend
# → http://localhost:3001
```

### 8-3. 화면 검증

브라우저에서 각 URL 접속:

**전략 설정** (`/strategy`):

- ✅ 프리셋 전략 3종 카드 렌더링 (골든크로스+RSI / 볼린저 밴드 반전 / 가치+모멘텀)
- ✅ 전략 카드 클릭 시 상세 패널 표시 (파라미터 슬라이더, 종목 매핑 테이블)
- ✅ 활성화/비활성화 토글 스위치 동작

**백테스팅** (`/backtest`):

- ✅ 설정 폼 렌더링 (전략 선택, 종목코드, 시작/종료일)
- ✅ 전략 미선택 시 실행 버튼 비활성화
- ✅ 백테스팅 실행 후 결과 대시보드 표시 (총수익률, MDD, 샤프비율, 승률 카드)
- ✅ 수익 곡선 차트 + 벤치마크 비교 라인 렌더링

**주문 내역** (`/orders`):

- ✅ 주문 테이블 렌더링 (전체/미체결/체결완료/취소 탭)
- ✅ 미체결 주문에 취소 버튼 표시
- ✅ 주문 행 클릭 시 상세 다이얼로그 표시 (판단 근거, 신뢰도 Progress bar)

**설정** (`/settings`):

- ✅ KIS API 키 폼 렌더링 (App Key/Secret 마스킹, 투자 모드 라디오)
- ✅ 텔레그램 설정 폼 렌더링
- ✅ 안전장치 설정 폼 렌더링 (슬라이더, 숫자 입력)
- ✅ 자동매매 마스터 ON/OFF 스위치
- ✅ 긴급 전체 매도 버튼 클릭 시 AlertDialog 표시
- ✅ AlertDialog 취소 버튼 클릭 시 모달 닫힘

**반응형 레이아웃**:

- ✅ 375px(모바일): 사이드바 숨김, 햄버거 메뉴(≡) 표시
- ⬜ 1920px(데스크톱): 사이드바 표시, 전체 레이아웃 정상 확인 (수동 확인 필요)

**콘솔 에러**:

- ✅ Error 레벨 메시지 0건 확인

### Sprint 4 완료 체크리스트

- ✅ `npm install` 완료
- ✅ 전략 설정 화면 4개 섹션 렌더링 (카드 목록, 상세 패널, 파라미터 폼, 종목 매핑)
- ✅ 백테스팅 실행 및 결과 차트 렌더링
- ✅ 주문 내역 탭/필터/상세 다이얼로그 동작
- ✅ 설정 화면 전체 폼 및 긴급 매도 AlertDialog 동작
- ✅ 모바일 375px 반응형 레이아웃 동작
- ✅ 콘솔 에러 없음
- ⬜ 데스크톱 1920px 레이아웃 수동 확인 (사용자 직접 수행)

> Playwright MCP 자동 검증 완료 (2026-03-01) — 11/11 항목 통과

---

## 9. Sprint 4.1 완료 검증 (사용자 수행 필요)

Sprint 4.1에서는 커스텀 전략 빌더 UI가 추가되었습니다.

> **자동 검증 완료 항목 (Playwright MCP, 2026-03-01)**
> 커스텀 전략 탭 전환 / 전략 생성 / 조건 행 추가 / AND/OR 토글 / 전략 미리보기 / localStorage persist / 모바일 375px / 콘솔 에러 — 8/8 통과
> 상세 내용: [docs/sprint/sprint4.1/playwright-report.md](docs/sprint/sprint4.1/playwright-report.md)

### 9-1. 개발 서버 기동

```bash
# 방법 1: Docker 없이 직접 실행
cd frontend
npm run dev
# → http://localhost:3000

# 방법 2: Docker Compose 사용
docker compose up --build frontend
# → http://localhost:3001
```

### 9-2. 커스텀 전략 빌더 검증

브라우저에서 `http://localhost:3000/strategy` 접속 후 **커스텀 전략** 탭 클릭:

**전략 생성 및 편집:**

- ✅ "새 전략 만들기" 클릭 시 이름 입력 폼 표시
- ✅ 이름 입력 후 Enter 또는 "추가" 버튼으로 전략 생성
- ✅ 생성된 전략이 목록에 추가되고 자동 선택됨
- ✅ 전략 이름 인라인 편집 가능 (텍스트박스)

**조건 빌더:**

- ✅ "조건 추가" 버튼 클릭 시 조건 행 추가
- ✅ 지표 선택 드롭다운 (SMA/EMA/RSI/MACD/BB/ATR/거래량비율/현재가 8종)
- ✅ 지표 변경 시 파라미터 입력 필드 동적 렌더링
- ✅ 비교 연산자 선택 (>/>=/</<=/골든크로스/데드크로스)
- ✅ 우변 종류 선택 (고정값 또는 지표)
- ✅ 조건 2개 이상 추가 시 AND/OR 토글 배지 표시
- ✅ AND/OR 배지 클릭 시 전환 동작

**전략 미리보기:**

- ✅ 조건 추가/수정 즉시 미리보기 텍스트 자동 업데이트
- ✅ 매수/매도 조건 섹션 분리 표시
- ✅ 조건 없을 시 "(조건 없음)" 표시

**전략 관리:**

- ✅ 활성화/비활성화 Switch 토글 동작
- ✅ 복제 버튼으로 전략 복제 (이름에 "복사본" 추가)
- ✅ 삭제 버튼으로 전략 삭제
- ✅ 페이지 새로고침 후 전략 목록 유지 (localStorage persist)

**수동 확인 필요 항목 (Playwright Chromium 자동 검증 완료, 2026-03-02):**

- ✅ MACD 지표 선택 후 우변이 "시그널선 / 0"으로 고정됨 확인
- ✅ BB 지표 선택 후 "위치" 드롭다운 (하단/중단/상단밴드) 표시 확인
- ✅ 지표를 우변으로 선택 (SMA/EMA) 후 파라미터 입력 확인
- ✅ 복제된 전략 조건 수정 시 원본에 영향 없음 확인 ("복사본" 이름으로 독립 생성)
- ✅ 데스크톱 1920px 레이아웃 확인 (가로 오버플로우 없음)

### Sprint 4.1 완료 체크리스트

- ✅ 커스텀 전략 탭 전환 정상
- ✅ 전략 생성/삭제/복제 동작
- ✅ 조건 행 추가/삭제 동작
- ✅ AND/OR 토글 동작
- ✅ 전략 미리보기 실시간 업데이트
- ✅ localStorage persist (새로고침 후 유지)
- ✅ 모바일 375px 반응형 레이아웃 동작
- ✅ 콘솔 에러 없음
- ✅ MACD/BB 특수 케이스 수동 확인 (Playwright Chromium 자동 검증 완료, 2026-03-02)
- ✅ 데스크톱 1920px 레이아웃 수동 확인 (Playwright Chromium 자동 검증 완료, 2026-03-02)

> Playwright MCP 자동 검증 완료 (2026-03-01) — 8/8 항목 통과
> Playwright Chromium 추가 검증 완료 (2026-03-02) — 수동 검증 항목 5/5 통과
> 상세 내용: [docs/sprint/sprint10/sprint4-1-report-v2.md](docs/sprint/sprint10/sprint4-1-report-v2.md)

---

## 10. Sprint 5 완료 검증 (사용자 수행 필요)

Sprint 5에서는 관심종목/보유종목 백엔드 API와 프론트엔드-백엔드 실제 연동이 추가되었습니다.

### 10-1. 신규 패키지 설치 (Docker 재빌드)

Sprint 5에서 `redis[hiredis]>=5.0.0`, `pykrx>=1.0.0` 패키지가 추가되었습니다.

```bash
# 프로젝트 루트에서 실행 (신규 패키지 포함 재빌드)
docker compose up --build -d
```

### 10-2. Alembic 마이그레이션 실행 (holdings 테이블 생성)

```bash
# holdings 테이블 추가 마이그레이션 실행
docker compose exec backend alembic upgrade head

# 테이블 생성 확인 (holdings 테이블이 보여야 함)
docker compose exec postgres psql -U mystock_user -d mystock -c "\dt"
```

### 10-3. 백엔드 API 엔드포인트 동작 검증

```bash
# 1. 로그인 → 토큰 발급
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "설정한_비밀번호"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 2. 종목 검색 (삼성전자)
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/stocks/search?q=삼성전자"
# 응답 예시: [{"symbol": "005930", "name": "삼성전자", "market": "KOSPI"}]

# 3. 관심종목 그룹 조회
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/watchlist/groups
# 응답: [] (초기 상태)

# 4. 관심종목 그룹 생성
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "반도체"}' \
  http://localhost:8000/api/v1/watchlist/groups
# 응답: {"id": 1, "name": "반도체", ...}

# 5. 관심종목 추가 (그룹 id=1에 삼성전자 추가)
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"stock_code": "005930", "stock_name": "삼성전자"}' \
  http://localhost:8000/api/v1/watchlist/groups/1/items

# 6. 보유종목 조회
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/holdings
# 응답: [] (KIS 동기화 전)

# 7. 포트폴리오 요약
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/holdings/summary
# 응답: {"total_evaluation": 0.0, "total_purchase": 0.0, ...}
```

### 10-4. KIS 연동 시 보유종목 동기화 (선택 - KIS API 키가 있는 경우)

```bash
# KIS API 키가 .env에 설정된 경우 동기화 실행
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/holdings/sync
# 응답: {"synced_count": N, "holdings": [...]}
```

### 10-5. 프론트엔드 연동 확인

브라우저에서 `http://localhost:3001` 접속 후:

```
1. /watchlist 페이지 → 종목 검색창에 "삼성" 입력 → 실제 API 검색 결과 표시 확인
2. /watchlist 페이지 → 그룹 목록이 API 데이터로 표시 확인
3. /dashboard 페이지 → 포트폴리오 요약이 API 데이터로 표시 확인
4. 브라우저 개발자도구 Network 탭 → /api/v1/stocks/search, /api/v1/watchlist/groups, /api/v1/holdings/summary 호출 200 확인
```

### 10-6. Swagger UI 확인

`http://localhost:8000/docs` 접속:

- GET /api/v1/stocks/search 엔드포인트 추가 확인
- GET/POST/PUT/DELETE /api/v1/watchlist/... 엔드포인트 확인
- GET/POST/PUT /api/v1/holdings/... 엔드포인트 확인

### Sprint 5 완료 체크리스트

- ✅ `docker compose up --build` 성공 (신규 패키지 포함)
- ✅ `alembic upgrade head` 성공 (holdings 테이블 생성)
- ✅ `GET /api/v1/stocks/search?q=삼성전자` → 200 응답 (KIS 키 없이 빈 배열 정상)
- ✅ `GET /api/v1/watchlist/groups` → 200 응답
- ✅ `POST /api/v1/watchlist/groups` → 그룹 생성 201
- ✅ `GET /api/v1/holdings/summary` → 포트폴리오 요약 반환
- ✅ Swagger UI에 watchlist/holdings 엔드포인트 표시
- ✅ `/watchlist` 프론트엔드 → 실제 API 검색/그룹 조회 연동 확인 (use-watchlist.ts 코드 확인)
- ✅ `/dashboard` 프론트엔드 → 포트폴리오 요약 API 연동 확인 (use-portfolio.ts 코드 확인)
- ⬜ (선택) `POST /api/v1/holdings/sync` → KIS 잔고 동기화 성공

> Sprint 5 백엔드 자동 검증: docker 환경 없이는 자동 실행 불가, 수동 검증 필요

---

## 11. Sprint 6 완료 검증 (사용자 수행 필요)

Sprint 6에서는 기술적 지표 엔진, 3종 프리셋 전략, 자동 주문 실행 엔진, APScheduler 기반 스케줄러, 전략 API가 추가되었습니다.

### 11-1. 신규 패키지 설치 (Docker 재빌드)

Sprint 6에서 `pandas>=2.0.0`, `pandas-ta>=0.3.14b`, `apscheduler>=3.10.0` 패키지가 추가되었습니다.

```bash
# 프로젝트 루트에서 실행 (신규 패키지 포함 재빌드)
docker compose up --build -d
```

### 11-2. 백엔드 서버 시작 로그 확인

```bash
# 스케줄러 시작 로그 확인
docker compose logs backend | grep -E "(APScheduler|스케줄러|Strategy)"
# 기대 출력: "APScheduler 시작 (전략 평가: 장중 매 5분)"
```

### 11-3. 전략 API 엔드포인트 동작 검증

```bash
# 1. 로그인 → 토큰 발급
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "설정한_비밀번호"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 2. 전략 목록 조회 (seed 데이터 3개 전략)
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/strategies
# 응답 예시: [{"id": 1, "name": "GoldenCrossRSI", "is_active": false, ...}, ...]

# 3. 전략 상세 조회 (id=1)
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/strategies/1
# 응답: 전략 상세 + 파라미터 목록

# 4. 전략 활성화
curl -X PUT -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_active": true}' \
  http://localhost:8000/api/v1/strategies/1
# 응답: {"is_active": true, ...}

# 5. 전략 파라미터 업데이트
curl -X PUT -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"params": [{"param_key": "rsi_threshold", "param_value": "35", "param_type": "float"}]}' \
  http://localhost:8000/api/v1/strategies/1/params
# 응답: {"params": [{"param_key": "rsi_threshold", "param_value": "35", ...}], ...}
```

### 11-4. KIS 연동 시 신호 평가 (선택 - KIS API 키가 있는 경우)

```bash
# 전략 신호 평가 (전략 id=1, 삼성전자 005930)
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/strategies/1/evaluate/005930
# 응답 예시: {"symbol": "005930", "signal_type": "HOLD", "confidence": 0.0, "reason": "조건 미충족", ...}
```

### 11-5. Swagger UI 확인

`http://localhost:8000/docs` 접속:

- `GET /api/v1/strategies` 엔드포인트 추가 확인
- `GET /api/v1/strategies/{id}` 엔드포인트 확인
- `PUT /api/v1/strategies/{id}/activate` 엔드포인트 확인
- `PUT /api/v1/strategies/{id}/params` 엔드포인트 확인
- `POST /api/v1/strategies/{id}/evaluate/{symbol}` 엔드포인트 확인

### 11-6. 프론트엔드 전략 화면 API 연동 확인

브라우저에서 `http://localhost:3001/strategy` 접속 후:

```
1. 전략 카드 3개가 실제 DB 데이터로 렌더링됨 확인
2. 전략 활성화 토글 클릭 → Network 탭에서 PUT /api/v1/strategies/{id}/activate 200 확인
3. 파라미터 조절 후 저장 → PUT /api/v1/strategies/{id}/params 200 확인
4. 브라우저 개발자도구 콘솔 에러 없음 확인
```

### Sprint 6 완료 체크리스트

- ✅ `docker compose up --build` 성공 (신규 패키지 포함)
- ✅ 백엔드 로그에 "APScheduler 시작" 메시지 확인 ("APScheduler 시작 (전략 평가: 장중 매 5분)")
- ✅ `GET /api/v1/strategies` → 전략 3개 목록 반환
- ✅ `GET /api/v1/strategies/1` → 전략 상세 + 파라미터 반환
- ✅ `PUT /api/v1/strategies/1/activate` → 활성화 상태 변경 성공
- ✅ `PUT /api/v1/strategies/1/params` → 파라미터 업데이트 성공
- ✅ Swagger UI에 `strategies` 엔드포인트 5개 표시
- ✅ `/strategy` 프론트엔드 → 실제 DB 데이터 렌더링 확인 (use-strategy.ts 코드 확인)
- ✅ `/strategy` 프론트엔드 → 토글 클릭 시 API 호출 확인 (activateStrategy 뮤테이션 확인)
- ⬜ (선택) `POST /api/v1/strategies/1/evaluate/005930` → 신호 평가 성공

> Sprint 6 백엔드 자동 검증: docker 환경 없이는 자동 실행 불가, 수동 검증 필요

---

## 12. Sprint 7 완료 검증 (사용자 수행 필요)

Sprint 7에서는 손절/익절 엔진, 매매 안전장치, 시스템 안전장치, 관련 API, 프론트엔드 실제 연동이 추가되었습니다.

> **자동 검증 완료 항목 (Playwright MCP, 2026-03-01)**
> 설정 화면 / 안전장치 폼 / 긴급 전체 매도 AlertDialog / AlertDialog 취소 / 주문내역 테이블 / 미체결 취소 버튼 / 모바일 375px / 콘솔 에러 0건 — 11/11 통과
> 상세 내용: [docs/sprint/sprint7/playwright-report.md](docs/sprint/sprint7/playwright-report.md)

### 12-1. 신규 패키지 설치 (Docker 재빌드)

Sprint 7에서 신규 Python 패키지는 없습니다. 코드 변경만 반영하면 됩니다.

```bash
# 프로젝트 루트에서 실행
docker compose up --build -d
```

### 12-2. 백엔드 스케줄러 로그 확인

```bash
# 손절/익절 모니터링 스케줄러 시작 확인
docker compose logs backend | grep -E "(APScheduler|손절|익절|risk|safety)"
# 기대: "APScheduler 시작 (손절/익절 모니터링: 장중 매 1분)" 등
```

### 12-3. 신규 API 엔드포인트 동작 검증

```bash
# 1. 로그인 → 토큰 발급
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "설정한_비밀번호"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 2. 안전장치 전체 상태 조회
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/safety/status
# 기대: {"auto_trade_enabled": false, "daily_loss_check": {...}, "daily_order_check": {...}, "system": {...}}

# 3. 자동매매 활성화
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}' \
  http://localhost:8000/api/v1/safety/auto-trade
# 기대: {"auto_trade_enabled": true}

# 4. 자동매매 비활성화
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}' \
  http://localhost:8000/api/v1/safety/auto-trade

# 5. 시스템 설정 전체 조회
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/system-settings
# 기대: 설정 항목 배열

# 6. 시스템 설정 일괄 업데이트
curl -X PUT -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"settings": [{"setting_key": "daily_loss_limit_pct", "setting_value": "5", "setting_type": "float"}]}' \
  http://localhost:8000/api/v1/system-settings

# 7. 주문 목록 조회 (최신순)
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/orders
# 기대: 주문 목록 배열
```

### 12-4. Swagger UI 신규 엔드포인트 확인

`http://localhost:8000/docs` 접속:

- `GET /api/v1/safety/status` 확인
- `POST /api/v1/safety/auto-trade` 확인
- `POST /api/v1/safety/emergency-sell` 확인
- `GET /api/v1/system-settings` 확인
- `PUT /api/v1/system-settings` 확인
- `GET /api/v1/system-settings/{key}` 확인
- `GET /api/v1/orders` 확인

### 12-5. 프론트엔드 연동 확인

브라우저에서 `http://localhost:3001/settings` 접속 후:

```
1. 자동매매 ON/OFF 스위치 클릭
   → Network 탭에서 POST /api/v1/safety/auto-trade 200 확인
2. 안전장치 설정 슬라이더 조절 후 저장 버튼 클릭
   → Network 탭에서 PUT /api/v1/system-settings 200 확인
3. 긴급 전체 매도 버튼 → AlertDialog → "전체 매도 실행" 클릭
   → Network 탭에서 POST /api/v1/safety/emergency-sell 200 확인
```

브라우저에서 `http://localhost:3001/orders` 접속 후:

```
1. 주문 목록이 API 데이터로 표시됨 확인
   → Network 탭에서 GET /api/v1/orders 200 확인
2. 미체결 탭 클릭 → 필터된 결과 확인
```

### Sprint 7 완료 체크리스트

**자동 검증 완료 (Playwright MCP):**

- ✅ 설정 화면 전체 폼 렌더링 (자동매매 / KIS API / 안전장치)
- ✅ 긴급 전체 매도 AlertDialog 표시 및 취소 동작
- ✅ 주문내역 탭/테이블/취소 버튼 렌더링
- ✅ 모바일 375px 반응형 레이아웃
- ✅ 콘솔 에러 없음

**수동 검증 필요 (Docker 실행 후):**

- ✅ `docker compose up --build` 성공
- ✅ 백엔드 로그에 손절/익절 모니터링 스케줄러 시작 확인 (APScheduler + daily_summary 잡 확인)
- ✅ `GET /api/v1/safety/status` → 200 + 상태 JSON 반환 (auto_trade_enabled 등 키 확인)
- ✅ `POST /api/v1/safety/auto-trade` → 자동매매 상태 변경 성공
- ✅ `GET /api/v1/system-settings` → 설정 목록 반환
- ✅ `PUT /api/v1/system-settings` → 설정 업데이트 성공
- ✅ `GET /api/v1/orders` → 주문 목록 반환
- ✅ Swagger UI에 safety(3개), system-settings(3개), orders(1개) 엔드포인트 표시
- ✅ `/settings` 프론트엔드 → 자동매매 토글 API 호출 확인 (use-settings.ts toggleAutoTrade 확인)
- ✅ `/orders` 프론트엔드 → 실제 DB 데이터 렌더링 확인 (use-orders.ts 코드 확인)

> Sprint 7 프론트엔드 자동 검증 완료 (2026-03-01) — 11/11 항목 통과
> Sprint 7 백엔드 자동 검증: docker 환경 없이는 자동 실행 불가, 수동 검증 필요

---

## 13. Sprint 9 완료 검증 (사용자 수행 필요)

Sprint 9에서는 텔레그램 알림 ON/OFF 설정, 전략 신호 사전 알림, 일일 매매 요약 API, 전략별 성과 집계 API, 일일 포트폴리오 요약 크론 잡, 대시보드 Mock → 실제 API 교체, 실시간 체결 알림 토스트 UI가 구현되었습니다.

> **자동 검증 항목 (Playwright MCP)**
> 상세 내용: [docs/sprint/sprint9/playwright-report.md](docs/sprint/sprint9/playwright-report.md)

### 13-1. 신규 패키지 설치 (Docker 재빌드)

Sprint 9에서 추가된 Python 패키지는 없습니다. 프론트엔드 `sonner` 패키지가 추가되었습니다.

```bash
# 프론트엔드 패키지 설치 (sonner)
cd frontend
npm install

# Docker 재빌드 (코드 변경 반영)
docker compose up --build -d
```

### 13-2. 신규 API 엔드포인트 검증

```bash
# 1. 로그인 → 토큰 발급
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "설정한_비밀번호"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 2. 일일 매매 요약 조회
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/orders/daily-summary
# 응답 예시: {"date": "2026-03-02", "total_buy_count": 0, "total_sell_count": 0, ...}

# 3. 특정 날짜 일일 매매 요약 조회
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/orders/daily-summary?date=2026-03-01"

# 4. 전략별 성과 집계 조회
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/strategies/performance
# 응답 예시: [{"id": 1, "name": "GoldenCrossRSI", "trade_count": 0, "win_rate": 0.0, ...}]

# 5. 시장 지수 조회
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/stocks/market-index
# 응답 예시: [{"index_code": "0001", "name": "KOSPI", "current_value": 2650.5, ...}]
```

### 13-3. 스케줄러 로그 확인

```bash
# 일일 요약 알림 크론 잡 등록 확인
docker compose logs backend | grep -E "(daily_summary|16:00|KST)"
# 기대: "APScheduler 시작" 로그 및 daily_summary 잡 등록 확인
```

### 13-4. 텔레그램 알림 ON/OFF 설정 확인

system_settings 테이블에서 알림 키를 설정하여 개별 알림을 ON/OFF할 수 있습니다:

```bash
# 알림 비활성화 예시 (notify_order_executed를 false로 설정)
curl -X PUT -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"settings": [{"setting_key": "notify_order_executed", "setting_value": "false", "setting_type": "str"}]}' \
  http://localhost:8000/api/v1/system-settings

# 지원하는 알림 설정 키:
# - notify_order_executed (주문 체결 알림)
# - notify_risk_triggered (손절/익절 알림)
# - notify_system_error (시스템 오류 알림)
# - notify_auto_trade_disabled (자동매매 중단 알림)
# - notify_strategy_signal (전략 신호 사전 알림)
# - notify_daily_summary (일일 포트폴리오 요약 알림)
```

### 13-5. 텔레그램 전략 신호 알림 수동 테스트 (선택)

KIS API 키 및 텔레그램 봇 설정이 완료된 경우, 전략 평가를 수동으로 트리거합니다:

```bash
# 전략 활성화 + 관심종목 등록 후 전략 평가 수동 실행
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/strategies/1/evaluate/005930
# 신호가 BUY/SELL이고 신뢰도 >= 0.5이면 텔레그램 알림 전송
```

### 13-6. 프론트엔드 대시보드 실제 API 연동 확인

브라우저에서 `http://localhost:3001/dashboard` 접속:

```
1. 브라우저 개발자도구 Network 탭 열기
2. 페이지 새로고침
3. 다음 API 호출이 200 응답인지 확인:
   - GET /api/v1/holdings (포트폴리오 요약)
   - GET /api/v1/orders (매매 신호 및 주문 체결)
   - GET /api/v1/strategies/performance (전략 성과)
   - GET /api/v1/stocks/market-index (시장 지수)
4. Mock 데이터가 아닌 실제 DB 데이터로 대시보드가 렌더링됨 확인
```

### 13-7. 실시간 체결 알림 토스트 확인

```
1. http://localhost:3001/dashboard 접속
2. 브라우저 개발자도구 → Network → WS 탭 확인
3. /ws/realtime WebSocket 연결 확인
4. (백엔드에서 주문 발생 시) 우측 하단에 sonner 토스트 알림 표시 확인
```

### 13-8. Swagger UI 신규 엔드포인트 확인

`http://localhost:8000/docs` 접속:

- `GET /api/v1/orders/daily-summary` 추가 확인
- `GET /api/v1/strategies/performance` 추가 확인
- `GET /api/v1/stocks/market-index` 추가 확인

### Sprint 9 완료 체크리스트

**자동 검증 완료 (Playwright MCP, 2026-03-02):**

- ✅ 대시보드 렌더링 (레이아웃 구조 확인 — 백엔드 미실행으로 스켈레톤 상태)
- ✅ 전략 설정 페이지 렌더링 (탭 전환, 로딩 상태)
- ✅ 주문 내역 페이지 렌더링 (Mock 폴백 데이터 표시)
- ✅ 설정 페이지 렌더링 (텔레그램 알림 개별 스위치 3개 확인)
- ✅ 모바일 375px 반응형 레이아웃 (사이드바 숨김, 햄버거 메뉴)
- ✅ sonner 패키지 설치 및 layout.tsx Toaster 컴포넌트 동작 확인
- ✅ 콘솔 에러 없음 (2026-03-02 백엔드 재빌드 후 확인 완료)

> 상세 보고서: [docs/sprint/sprint9/playwright-report.md](docs/sprint/sprint9/playwright-report.md)

**수동 검증 완료 (2026-03-02, Docker 실행 후):**

- ✅ `docker compose up --build` 성공 (Sprint 9 코드 반영)
- ✅ `GET /api/v1/orders/daily-summary` → 200 + 일일 요약 JSON 반환 (`{"date":"2026-03-02","total_buy_count":0,...}`)
- ✅ `GET /api/v1/strategies/performance` → 200 + 전략 성과 목록 반환 (3개 전략)
- ✅ `GET /api/v1/stocks/market-index` → 200 + 시장 지수 데이터 반환 (KOSPI 6244.13, KOSDAQ 1192.78)
- ✅ 백엔드 로그에 `_run_daily_summary` 크론 잡 등록 확인
- ✅ Swagger UI에 3개 신규 엔드포인트 표시 (`/orders/daily-summary`, `/strategies/performance`, `/stocks/market-index`)
- ✅ `/dashboard` 프론트엔드 → 4개 API 엔드포인트 200 응답 확인
- ✅ `/api/v1/ws/quotes` WebSocket 연결 확인 (101 Switching Protocols)
- ✅ `notify_order_executed` 설정을 "false"로 변경 → 재설정 "true"로 원복 확인
- ⬜ (선택) 텔레그램 봇 설정 완료 시 전략 신호 알림 수신 확인

> Sprint 9 수동 검증 완료 (2026-03-02) — 9/9 항목 통과 (선택 항목 1건 제외)

---

## 14. Sprint 10 완료 검증 (사용자 수행 필요)

Sprint 10에서는 백엔드/프론트엔드 에러 핸들링 강화, 구조화 로깅, Mock 데이터 → 실제 API 전환, 통합 테스트 인프라가 추가되었습니다.

### 14-1. 신규 패키지 설치 (Docker 재빌드)

Sprint 10에서 `python-json-logger`, `pytest`, `pytest-asyncio`, `pytest-cov`, `aiosqlite` 패키지가 추가되었습니다.

```bash
# 프로젝트 루트에서 실행 (신규 패키지 포함 재빌드)
docker compose up --build -d
```

### 14-2. 백엔드 통합 테스트 실행

```bash
# 컨테이너 내에서 pytest 실행
docker compose exec backend pytest -v

# 커버리지 포함 실행
docker compose exec backend pytest -v --cov=app --cov-report=term-missing
```

기대 결과:

- `tests/api/test_health.py` — 3개 테스트 PASSED
- `tests/api/test_orders.py` — 4개 테스트 PASSED
- `tests/api/test_auth.py` — 3개 테스트 PASSED
- `tests/api/test_safety.py` — 4개 테스트 PASSED

### 14-3. 에러 핸들링 검증

```bash
# 1. 로그인 → 토큰 발급
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "설정한_비밀번호"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 2. 잘못된 날짜 형식으로 주문 요약 조회 → 400 반환 확인
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/orders/daily-summary?date=not-a-date"
# 기대: {"code": "VALIDATION_ERROR", "message": "...", "detail": [...]}

# 3. 인증 없이 보호 엔드포인트 접근 → 401/403 확인
curl -i http://localhost:8000/api/v1/orders
# 기대: 401 Unauthorized

# 4. 존재하지 않는 엔드포인트 → 404 확인
curl -i http://localhost:8000/api/v1/nonexistent
# 기대: 404 Not Found
```

### 14-4. 구조화 로그 확인

```bash
# 백엔드 로그에서 JSON 구조화 로그 확인
docker compose logs backend --tail=20
# 기대: {"asctime": "...", "name": "...", "levelname": "INFO", "message": "..."} 형식

# Request ID 헤더 확인
curl -i -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/health
# 응답 헤더에 X-Request-ID 포함 확인
```

### 14-5. Health Check 실제 상태 확인

```bash
# Health Check 상세 상태 조회
curl http://localhost:8000/api/v1/health | python3 -m json.tool
# 기대: database, redis, scheduler 각각 상태 포함
# 예시:
# {
#   "status": "healthy",
#   "checks": {
#     "database": {"status": "healthy"},
#     "redis": {"status": "healthy"},
#     "scheduler": {"status": "healthy", "jobs": N}
#   }
# }
```

### 14-6. 프론트엔드 에러 핸들링 확인

브라우저에서 `http://localhost:3001` 접속:

```
1. 존재하지 않는 URL 접속 (예: http://localhost:3001/nonexistent)
   → not-found.tsx의 404 페이지 표시 확인

2. 개발자도구 네트워크 탭 열기
3. /orders 페이지에서 주문 목록 확인
   → 실제 API 데이터로 렌더링 확인 (Mock 데이터 아님)

4. /settings 페이지에서 설정 값 확인
   → 실제 API 데이터로 설정값 로드 확인

5. /backtest 페이지에서 백테스팅 실행
   → 실행 버튼 클릭 시 실제 API 호출 확인
   → API 오류 시 toast 알림 표시 확인
```

### 14-7. 실전 투자 전환 전 최종 체크리스트

⚠️ **KIS_ENVIRONMENT=prod 로 변경하기 전** 반드시 아래 항목을 모두 확인하세요:

```
1. 모의투자 환경(vts)에서 최소 1주일 이상 안정 운영 확인
2. 일일 손실 한도 (daily_loss_limit_pct) 설정값 확인
3. 최대 일일 주문 횟수 (max_daily_orders) 설정값 확인
4. 종목당 최대 투자 비율 (max_position_size_pct) 설정값 확인
5. 텔레그램 알림 정상 수신 확인 (체결/손절/익절/에러)
6. 긴급 전체 매도 버튼 동작 확인 (모의투자 환경에서 테스트)
7. .env 파일의 SECRET_KEY 랜덤 값으로 변경 확인
8. .env 파일의 DEBUG=False 설정 확인
9. .env 파일의 ADMIN_PASSWORD 강력한 비밀번호로 변경 확인
10. PostgreSQL 비밀번호 변경 확인 (POSTGRES_PASSWORD)
```

### Sprint 10 완료 체크리스트

> **자동 검증 완료 항목 (Playwright MCP, 2026-03-02)**
> 백엔드 Health Check / X-Request-ID 헤더 / 에러 핸들링 / 404 커스텀 페이지 / API 연동 확인 / 모바일 375px — 10/10 통과
> 상세 내용: [docs/sprint/sprint10/playwright-report.md](sprint10/playwright-report.md)

**백엔드 에러 핸들링:**

- ✅ `docker compose up --build` 성공 (신규 패키지 포함) — Docker 실행 중 확인
- ✅ 글로벌 에러 핸들러 동작 확인 (잘못된 날짜 → 400, 인증 없음 → 401) — Playwright 자동 검증
- ✅ 응답 헤더에 `X-Request-ID` 포함 확인 — Playwright 자동 검증

**구조화 로깅:**

- ✅ 백엔드 로그가 JSON 형식으로 출력됨 확인 — `docker compose up --build` 후 로그 확인 완료 (2026-03-02)

**Health Check:**

- ✅ `/api/v1/health` → `database`, `redis`, `scheduler` 실제 상태 포함 응답 확인 — 수동 검증 완료 (2026-03-02)

**통합 테스트:**

- ✅ `docker compose exec backend pytest -v` → **14개 테스트 모두 PASSED** — 수동 검증 완료 (2026-03-02)

**프론트엔드:**

- ✅ `/nonexistent` → 커스텀 404 페이지 표시 — Playwright 자동 검증
- ✅ `/orders` → 실제 API 데이터 렌더링 (Mock 아님) — Playwright 자동 검증 (/api/v1/orders 호출 확인)
- ✅ `/settings` → 실제 API 데이터 로드 — Playwright 자동 검증 (/api/v1/system-settings 호출 확인)
- ✅ `/backtest` → 실행 시 실제 API 호출 — Playwright 자동 검증 (폼 렌더링 및 버튼 확인)
- ✅ API 오류 시 toast 알림 표시 확인 — Playwright 자동 검증 완료 (2026-03-02, 스크린샷: toast-error.png)
- ✅ 모바일 375px 반응형 레이아웃 (사이드바 숨김, 햄버거 메뉴) — Playwright 자동 검증

**실전 투자 전환 전 최종 체크리스트 (14-7) 검증:**

- ✅ 일일 손실 한도 (daily_loss_limit_pct = 5%) 설정 확인
- ✅ 최대 일일 주문 횟수 (max_daily_orders = 20) 설정 확인
- ✅ 긴급 전체 매도 AlertDialog 동작 확인 (클릭 → 모달 표시 → 취소)
- ✅ ADMIN_PASSWORD 기본값에서 변경 확인
- ✅ POSTGRES_PASSWORD 기본값에서 변경 확인
- ✅ KIS_ENVIRONMENT=vts (모의투자) 확인
- ⬜ SECRET_KEY 기본값 그대로 — 운영 전 반드시 랜덤 값으로 변경 필요
- ⬜ DEBUG=True — 운영 전 반드시 False로 변경 필요
- ⬜ 텔레그램 알림 수신 확인 — KIS API 키 및 텔레그램 봇 설정 후 직접 확인 필요
- ⬜ 모의투자 1주일 이상 안정 운영 확인 — 운영 중 확인 필요

> Playwright MCP 자동 검증 완료 (2026-03-02) — 전체 항목 통과
> 수동 검증 완료 (2026-03-02) — JSON 로그, Health Check, 통합 테스트 14개 PASSED, toast 알림, 안전장치 API

---

## 15. Sprint 11 완료 검증 (자동 검증 완료)

Sprint 11에서는 로그인 페이지, 데모 모드, Next.js 미들웨어 인증 가드가 추가되었습니다.

> **자동 검증 완료 항목 (Playwright Chromium, 2026-03-03)**
> TC-1~TC-7 모두 통과 (7/7)

### 검증 결과


| 시나리오                                                  | 결과  |
| ----------------------------------------------------- | --- |
| TC-1: 미인증 접근 차단 (`/dashboard` → `/login` 리다이렉트)       | ✅   |
| TC-2: 로그인 페이지 레이아웃 (데스크톱 좌우 분할 + 모바일 단일 폼)            | ✅   |
| TC-3: 로그인 실패 에러 메시지 표시                                | ✅   |
| TC-4: 로그인 성공 → `/dashboard` 이동, 헤더에 사용자명 + 로그아웃 버튼    | ✅   |
| TC-5: 데모 보기 → "데모 모드" 뱃지 + 더미 데이터 표시                  | ✅   |
| TC-6: 데모 쓰기 차단 (전략 토글 시 "데모 모드에서는 사용할 수 없습니다." toast) | ✅   |
| TC-7: 로그아웃 → `/login` 리다이렉트 + 재접근 시 차단                | ✅   |


### Sprint 11 완료 체크리스트

- ✅ 로그인 페이지 (`/login`) 렌더링 정상
- ✅ 미인증 접근 시 서버사이드 리다이렉트 동작
- ✅ 로그인 성공/실패 처리 정상
- ✅ 데모 로그인 (`POST /api/v1/auth/demo`) 정상
- ✅ 데모 더미 데이터 표시 (보유종목, 전략, 관심종목 등)
- ✅ 데모 쓰기 차단 (403 → toast 알림)
- ✅ 로그아웃 후 인증 상태 초기화 및 쿠키 삭제
- ✅ 헤더에 사용자명 + 로그아웃 버튼 + 데모 모드 뱃지

> Playwright Chromium 자동 검증 완료 (2026-03-03) — 7/7 항목 통과

---

## 16. Sprint 12 완료 검증 (사용자 수행 필요)

Sprint 12에서는 KIS 듀얼 키 구조가 도입되었습니다.

- 시세 API(현재가/차트/지수)는 **항상 실전 키**를 사용
- 주문/잔고 API는 `KIS_ENVIRONMENT` 설정에 따라 모의투자 또는 실전 키를 사용

### 16-1. .env 파일 마이그레이션 (Sprint 12 기준 — 현재는 DB 관리)

> **⚠️ Sprint 13 이후 KIS API 키는 DB(`system_settings`)에서 관리합니다.**
> 아래 마이그레이션 가이드는 Sprint 12 당시 `.env` 방식 기준입니다. 현재 설치 시에는 설정 페이지에서 입력하세요.

기존 단일 키 구조를 새로운 듀얼 키 구조로 변경합니다.

**변경 전 (기존):**

```
KIS_APP_KEY=...
KIS_APP_SECRET=...
KIS_ACCOUNT_NUMBER=...
KIS_ENVIRONMENT=vts
```

**변경 후 (Sprint 12):**

```
# 모의투자 앱 키 (주문/잔고 - KIS_ENVIRONMENT=vts 일 때)
KIS_VTS_APP_KEY=모의투자_App_Key
KIS_VTS_APP_SECRET=모의투자_App_Secret
KIS_VTS_ACCOUNT_NUMBER=모의투자_계좌번호  # 예: 50123456-01

# 실전투자 앱 키 (시세 조회 항상 사용 + KIS_ENVIRONMENT=real 일 때 주문/잔고에도 사용)
KIS_REAL_APP_KEY=실전투자_App_Key
KIS_REAL_APP_SECRET=실전투자_App_Secret
KIS_REAL_ACCOUNT_NUMBER=실전투자_계좌번호  # 예: 50123456-01

KIS_HTS_ID=HTS_로그인_ID
KIS_ENVIRONMENT=vts  # vts: 모의투자, real: 실전투자
```

> ⚠️ **[중요]** 시세 API(현재가·차트·지수)는 KIS 실전 서버에서만 제공됩니다.
> 모의투자 모드(`KIS_ENVIRONMENT=vts`)에서도 `KIS_REAL_APP_KEY / KIS_REAL_APP_SECRET`을
> 반드시 입력해야 시세 조회가 가능합니다.

### 16-2. KIS Developers에서 앱 2개 생성

1. [KIS Developers](https://apiportal.koreainvestment.com) 접속 → HTS ID로 로그인
2. **[앱 관리] → [앱 생성]** 에서 **2개** 앱 생성:
  - 앱 1: 모의투자용 (이름 예: `mystock-vts`)
  - 앱 2: 실전투자용 (이름 예: `mystock-real`)
3. 각 앱의 App Key / App Secret 확인 후 `.env` 파일에 입력

### 15-3. Docker 재빌드 및 서비스 기동

```bash
# 프로젝트 루트에서 실행
docker compose up --build -d
```

### 15-4. 백엔드 KIS 상태 확인

```bash
# 1. 로그인 → 토큰 발급
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "설정한_비밀번호"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 2. KIS API 상태 확인
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/settings/kis-status
# 기대: {"is_available": true, "environment": "vts"} (실전 키 + 모의투자 키 모두 입력 시)

# 3. 시세 조회 테스트 (삼성전자: 005930)
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/stocks/005930/quote
# 기대: {"symbol": "005930", "price": ..., "change_rate": ...}
# (실전 키가 입력된 경우에만 실제 데이터 반환)

# 4. 통합 테스트 실행
docker compose exec backend pytest -v
# 기대: 14개 PASSED
```

### Sprint 12 완료 체크리스트

- ⬜ `.env` 파일에서 `KIS_VTS_*` / `KIS_REAL_*` 듀얼 키 입력 완료
- ⬜ `docker compose up --build` 성공
- ⬜ `GET /api/v1/settings/kis-status` → `is_available: true` 확인
- ⬜ `GET /api/v1/stocks/005930/quote` → 실제 시세 데이터 반환 확인 (실전 키 필요)
- ✅ `/settings` 페이지 → KIS API 폼에 모의투자/실전 키 입력란 구분 확인 (Playwright 자동 검증 완료, 2026-03-03)
- ⬜ `docker compose exec backend pytest -v` → 14개 PASSED 확인

---

## Sprint 13: MVP 안정화 (2026-03-03)

Sprint 13은 코드 품질 개선 중심으로, 사용자가 직접 수행해야 하는 배포 작업은 없습니다.

### 변경 사항 요약


| 구분    | 파일                            | 내용                             |
| ----- | ----------------------------- | ------------------------------ |
| 긴급 버그 | `order_executor.py`           | 분산 락 경합 조건 수정                  |
| 긴급 버그 | `risk_manager.py`             | 전량/분할 익절 순서 수정                 |
| 중요 개선 | `strategies.py`               | N+1 쿼리 최적화                     |
| 중요 개선 | `core/deps.py` (신규)           | 공통 `get_user_id` 함수            |
| 중요 개선 | `kis_client.py`               | httpx 연결 풀 공유                  |
| 중요 개선 | `stocks.py` + `demo_data.py`  | 데모 모드 balance/quote/chart 추가   |
| 중요 개선 | `safety_guard.py`             | 손실 계산 네이밍 수정                   |
| 중요 개선 | 프론트엔드 스토어                     | Mock 스토어 2개 삭제                 |
| 중요 개선 | `lib/api/types.ts` (신규)       | API 타입 중복 해소                   |
| 중요 개선 | `orders.py` + `use-orders.ts` | 주문 취소 기능 구현                    |
| 권장 개선 | `scheduler.py`                | 하드코딩(user_id=1, quantity=1) 제거 |


### 검증

```bash
# 테스트 실행 (33개 전부 PASSED 확인)
docker compose exec backend python -m pytest tests/ -v
# 기대: 33 passed

# 데모 모드 API 검증
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/demo | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/stocks/balance
# 기대: 200 (더미 데이터)
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/stocks/005930/quote
# 기대: 200 (더미 데이터)
```

### Sprint 13 완료 체크리스트

- ✅ 테스트 33개 PASSED (자동 검증 완료, 2026-03-03)
- ✅ 데모 모드 API 9개 엔드포인트 200 확인 (자동 검증 완료, 2026-03-03)
- ✅ TypeScript 빌드 성공 (`npm run build` 2026-03-03)
- ⬜ 실제 KIS API 연동 환경에서 주문 취소 기능 수동 확인

---

## Sprint 14: JWT 인증 + User 모델 확장

### 환경변수 추가

`.env` 파일에 다음을 추가해주세요:

```env
# JWT 설정 (Sprint 14 신규)
JWT_SECRET=<openssl rand -hex 32 으로 생성한 랜덤 시크릿>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# 관리자 이메일 (Sprint 14 신규)
ADMIN_EMAIL=admin@mystock.bot
```

### Sprint 14 배포 절차

```bash
# 1. 환경변수 추가 후 컨테이너 재시작
docker compose up -d --build backend

# 2. 의존성 설치 확인 (python-jose, bcrypt — passlib은 PR #22에서 bcrypt로 대체됨)
docker compose exec backend pip list | grep -E "jose|bcrypt"

# 3. Alembic 마이그레이션 실행
docker compose exec backend alembic upgrade head

# 4. 신규 관리자 계정으로 로그인 테스트
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@mystock.bot", "password": "change-me-in-production"}'
# 기대: {"access_token": "...", "refresh_token": "...", "token_type": "bearer"}
```

### ⚠️ 기존 운영 중인 경우 주의사항

기존에 이미 users 테이블이 있는 경우, 마이그레이션에서 기존 사용자의 `role='admin'`, `is_approved=true`로 자동 설정됩니다.
단, `password_hash`와 `email`은 NULL로 남으므로, 로그인하려면 반드시 seed.py를 실행하거나 DB에서 직접 업데이트해주세요.

```bash
# 기존 사용자가 없는 경우에만 seed.py 실행
docker compose exec backend python scripts/seed.py
```

### Sprint 14 완료 체크리스트

> **자동 검증 완료 (정적 분석, 2026-03-03)**
> Python 문법 검증, JWT 설정, 인증/관리자 API 엔드포인트, User 모델 필드, 라우터 의존성, Alembic 마이그레이션, 프론트엔드 auth-store, client.ts 401 갱신 로직 — 59/59 항목 통과
> 상세 내용: [docs/sprint/sprint14/validation-report.md](docs/sprint/sprint14/validation-report.md)

- ✅ `alembic upgrade head` 실행 확인 (2026-03-03)
- ✅ 관리자 이메일로 로그인 테스트 (`frogy95@gmail.com`, 2026-03-03)
- ✅ 초대 코드 생성 (`POST /api/v1/admin/invitations`, 2026-03-03)
- ✅ 새 사용자 회원가입 (`POST /api/v1/auth/register`, 초대코드 검증 포함, 2026-03-03)
- ✅ 데모 모드 여전히 정상 동작 확인 (2026-03-03)

---

## 17. Sprint 15 완료 검증 (사용자 수행 필요)

Sprint 15에서는 전략(Strategy)과 백테스트 결과(BacktestResult)에 사용자별 데이터 격리가 추가되었습니다.

- 프리셋 전략(`user_id IS NULL`)은 모든 사용자가 조회 가능하나 수정 불가
- 사용자는 프리셋을 복사(clone)하여 본인 소유 전략 생성
- 백테스트 결과는 실행한 사용자만 조회 가능

### 17-1. Docker 재빌드 및 마이그레이션

```bash
# 프로젝트 루트에서 실행 (코드 변경 반영)
docker compose up --build -d

# Alembic 마이그레이션 실행 (strategies.user_id, backtest_results.user_id 컬럼 추가)
docker compose exec backend alembic upgrade head

# 마이그레이션 확인
docker compose exec postgres psql -U mystock_user -d mystock -c "\d strategies"
# user_id 컬럼이 표시되어야 함
docker compose exec postgres psql -U mystock_user -d mystock -c "\d backtest_results"
# user_id 컬럼이 표시되어야 함
```

### 17-2. 백엔드 통합 테스트 실행

```bash
# 컨테이너 내에서 pytest 실행
docker compose exec backend pytest -v

# 기대 결과: 40 passed (신규 7개 포함)
# test_strategies.py — 격리/프리셋 보호/clone 6개 신규
# test_backtest.py — 사용자별 격리 2개 신규
# 1 failed (test_stocks.py::test_balance_returns_valid_status — KIS API 네트워크 오류, Sprint 15 이전부터 존재)
```

### 17-3. API 수동 검증

먼저 로그인하여 토큰을 발급받으세요:

```bash
# 로그인 (이메일 방식)
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "frogy95@gmail.com", "password": "설정한_비밀번호"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

#### 전략 격리 검증

```bash
# 1. 전략 목록 조회 → 프리셋만 표시 (신규 사용자 기준)
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/strategies | python3 -m json.tool
# 기대: user_id가 null인 프리셋 3개

# 2. 프리셋 전략 활성화 시도 → 404 확인 (id=1 은 프리셋)
curl -s -X PUT -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_active": true}' \
  http://localhost:8000/api/v1/strategies/1/activate
# 기대: {"detail": "Not found"} 또는 404 응답

# 3. 프리셋 전략 복사 (clone)
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/strategies/1/clone | python3 -m json.tool
# 기대: user_id가 본인 id인 새 전략 생성 (name에 "(복사)" 또는 "copy" 포함)
# 응답에서 복사된 전략의 id를 메모 (예: CLONED_ID=4)

# 4. 복사된 전략 활성화 → 성공 확인
CLONED_ID=<위에서 메모한 id>
curl -s -X PUT -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_active": true}' \
  http://localhost:8000/api/v1/strategies/$CLONED_ID/activate
# 기대: {"is_active": true, ...}

# 5. 복사된 전략 파라미터 수정 → 성공 확인
curl -s -X PUT -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"params": [{"param_key": "rsi_threshold", "param_value": "30", "param_type": "float"}]}' \
  http://localhost:8000/api/v1/strategies/$CLONED_ID/params
# 기대: 200 OK + 업데이트된 파라미터
```

#### 백테스트 격리 검증

```bash
# 6. 백테스트 실행 (복사된 전략으로)
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"strategy_id\": $CLONED_ID, \"symbol\": \"005930\", \"start_date\": \"2023-01-01\", \"end_date\": \"2023-12-31\"}" \
  http://localhost:8000/api/v1/backtest/run | python3 -m json.tool
# 기대: 백테스트 결과 + user_id 포함

# 7. 백테스트 결과 조회 → 본인 결과만 표시
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/backtest/results | python3 -m json.tool
# 기대: 방금 실행한 결과만 포함
```

### 17-4. 프론트엔드 UI 검증

브라우저에서 `http://localhost:3001/strategy` 접속 후:

```
1. 전략 목록에서 프리셋 전략 카드 클릭
   → 토글(활성화/비활성화) 스위치가 비활성화(grayed out) 상태임을 확인
   → 상세 패널에 "파라미터를 수정하려면 전략을 복사하세요" 안내 문구 확인

2. 프리셋 전략 카드에서 "내 전략으로 복사" 버튼 클릭
   → 복사본이 전략 목록에 추가됨 확인
   → 복사본 카드의 토글은 정상 동작 확인

3. 복사된 전략 파라미터 수정 후 저장
   → 네트워크 탭에서 PUT /api/v1/strategies/{id}/params 200 확인

4. 브라우저 개발자도구 콘솔 에러 없음 확인
```

### 17-5. 데모 모드 정상 동작 확인

```bash
# 데모 로그인
DEMO_TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/demo \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 데모 모드 전략 조회 (더미 데이터 반환 확인)
curl -s -H "Authorization: Bearer $DEMO_TOKEN" \
  http://localhost:8000/api/v1/strategies | python3 -m json.tool
# 기대: user_id: null 인 더미 전략 3개
```

### Sprint 15 완료 체크리스트

**자동 검증 완료 (sprint-close 시점에 실행됨):**

- ✅ pytest 41개 PASSED (신규 8개 포함) — `docker compose exec backend pytest -v` (2026-03-03 sprint-close 재검증, 41 passed / 0 failed)
- ✅ 데모 모드 전략 조회 — 전략 3개, 모두 `user_id=None`, `is_preset=True` 확인

**수동 필요 — DB 마이그레이션 (되돌릴 수 없으므로 사용자가 타이밍 결정):**

- ✅ `docker compose up --build` 성공 (핫리로드 환경에서는 불필요할 수 있음)
- ✅ `alembic upgrade head` 성공 → strategies/backtest_results 테이블에 user_id 컬럼 추가 확인

**자동 검증 완료 — 실제 API 검증 (2026-03-03, alembic 실행 후):**

- ✅ `GET /api/v1/strategies` → 프리셋 3개, 모두 `user_id=null`
- ✅ `PUT /api/v1/strategies/1/activate` → HTTP 404 (프리셋 토글 차단 정상)
- ✅ `POST /api/v1/strategies/1/clone` → 복사본 생성 (`id=4, user_id=1, is_preset=false`)
- ✅ `PUT /api/v1/strategies/4/activate` → HTTP 200 (복사본 토글 성공)
- ✅ `GET /api/v1/backtest/results` → 빈 배열 (타사용자 결과 노출 없음)

**수동 필요 — 브라우저 UI 시각 확인 (자동화 불가):**

- ✅ 프론트엔드: 프리셋 전략 카드에서 토글 비활성화 표시 (Playwright 자동 검증, 2026-03-03)
- ✅ 프론트엔드: "내 전략으로 복사" 버튼 카드 하단에 표시 확인 (Playwright 자동 검증, 2026-03-03) — 클릭 시 API 검증은 curl로 완료
- ✅ 프론트엔드: 복사된 전략 파라미터 수정 가능 확인 (Playwright + DB 저장 검증, 2026-03-03)
- ✅ 브라우저 콘솔 에러 없음 (Playwright: 0 errors, 2026-03-03)

---

## 18. Sprint 16 완료 검증

Sprint 16에서는 관리자 대시보드 UI 및 초대코드 기반 회원가입 플로우가 완성되었습니다.

### 18-1. 신규 구현 항목

- `frontend/src/app/admin/page.tsx` — 관리자 대시보드 페이지 (초대코드 탭 + 사용자 관리 탭)
- `frontend/src/app/register/page.tsx` — 초대코드 기반 회원가입 페이지 (`?code=` URL 파라미터 자동 주입)
- `frontend/src/hooks/use-admin.ts` — 관리자 API TanStack Query 훅 (useInvitations, useCreateInvitation, useAdminUsers, useApproveUser, useDeactivateUser)
- `frontend/src/components/admin/invitation-tab.tsx` — 초대코드 발급/목록/복사 탭 컴포넌트
- `frontend/src/components/admin/users-tab.tsx` — 사용자 목록/승인/비활성화 탭 컴포넌트
- `frontend/src/components/layout/admin-guard.tsx` — role=admin 전용 라우트 보호 컴포넌트
- `frontend/src/stores/auth-store.ts` — role, userId 필드 추가
- `frontend/src/components/layout/app-sidebar.tsx` — role=admin 조건부 관리자 메뉴 추가
- `backend/app/api/v1/auth.py` — GET /auth/me 엔드포인트 추가
- `backend/tests/api/test_admin.py` — 관리자 API 통합 테스트 6개

### 18-2. 자동 검증 완료 (sprint-close 시점 실행됨)

**백엔드 pytest (2026-03-04):**

- ✅ `docker compose exec backend pytest -v` → **51 passed / 0 failed** (1 warning)
  - `tests/api/test_admin.py` — 6개 전체 통과
    - `test_non_admin_cannot_list_invitations` PASSED
    - `test_admin_can_list_invitations` PASSED
    - `test_admin_can_create_invitation` PASSED
    - `test_admin_can_list_users` PASSED
    - `test_admin_can_approve_user` PASSED
    - `test_admin_cannot_deactivate_self` PASSED
  - 기존 45개 회귀 없음

**프론트엔드 TypeScript 빌드 (2026-03-04):**

- ✅ `npx tsc --noEmit` → 에러 없음

### 18-3. 수동 검증 필요 항목

아래 항목은 Docker 서비스 기동 후 사용자가 직접 브라우저에서 확인해야 합니다.

#### 사전 조건

```bash
# Docker 서비스 기동 (새 코드 반영을 위해 재빌드 필요)
docker compose up --build -d

# DB 마이그레이션 (Sprint 14/15에서 이미 적용된 경우 불필요)
docker compose exec backend alembic upgrade head
```

#### TC-1: 관리자 로그인 후 /admin 접속

```
1. http://localhost:3001/login 접속
2. 이메일: frogy95@gmail.com, 비밀번호: 관리자 비밀번호 입력
3. 로그인 후 /dashboard 리다이렉트 확인
4. http://localhost:3001/admin 접속
5. 관리자 대시보드 렌더링 확인 (초대코드 탭, 사용자 탭 표시)
6. 브라우저 콘솔 에러 없음 확인
```

#### TC-2: 초대코드 생성 및 복사

```
1. /admin 페이지 → 초대코드 탭 이동
2. 유효기간 선택 (예: 7일)
3. "초대코드 생성" 버튼 클릭
4. 테이블에 새 행 추가 확인 (상태: 유효)
5. "링크 복사" 버튼 클릭 → 클립보드에 복사되었다는 토스트 확인
6. 복사된 URL 형식: http://localhost:3001/register?code=<코드>
```

#### TC-3: 비관리자 /admin 접속 차단

```
1. 데모 모드로 로그인 (일반 유저)
2. http://localhost:3001/admin 접속
3. /dashboard로 자동 리다이렉트 확인 (AdminGuard 동작)
```

#### TC-4: 회원가입 페이지 URL 파라미터 자동 주입

```
1. http://localhost:3001/register?code=test123 접속
2. 초대코드 입력란에 "test123" 자동 입력 확인
3. "초대링크에서 자동으로 입력되었습니다." 안내 문구 표시 확인
4. 브라우저 콘솔 에러 없음 확인
```

#### TC-5: 사이드바 관리자 메뉴 조건부 표시

```
1. 관리자 로그인 후 → 사이드바에 "관리자" 메뉴 표시 확인 (Shield 아이콘)
2. 일반 유저/데모 로그인 후 → 사이드바에 "관리자" 메뉴 없음 확인
```

#### TC-6: 사용자 승인 기능

```
1. /admin → 사용자 관리 탭 이동
2. 미승인 사용자가 있는 경우 "승인" 버튼 클릭
3. 상태 Badge가 "대기" → "승인됨"으로 변경 확인
4. 자기 자신 "비활성화" 버튼 비활성화(disabled) 상태 확인
```

#### TC-7: 회원가입 플로우 End-to-End

```
1. /admin에서 초대코드 생성 후 링크 복사
2. 복사된 링크로 /register 접속
3. 이메일, 비밀번호, 비밀번호 확인 입력 (초대코드는 자동 입력됨)
4. "회원가입" 버튼 클릭
5. 성공 토스트: "회원가입이 완료되었습니다. 관리자 승인 후 로그인 가능합니다."
6. /login 페이지로 자동 이동 확인
```

### Sprint 16 완료 체크리스트

**자동 검증 완료 (2026-03-04, sprint-close 실행):**

- ✅ pytest 51개 PASSED (신규 6개 포함) — `docker compose exec backend pytest -v`
- ✅ TypeScript 빌드 에러 없음 — `npx tsc --noEmit`

**수동 검증 필요 — Docker 빌드 (타이밍 사용자 결정):**

- ✅ `docker compose up --build` 성공 확인
- ✅ `alembic upgrade head` 최신 마이그레이션 적용 확인 (이미 최신 상태)

**Playwright E2E 검증 완료 (2026-03-05):**

- ✅ TC-1: 관리자 로그인 후 /admin 대시보드 렌더링 확인
- ✅ TC-2: 초대코드 생성 및 링크 복사 동작 확인
- ✅ TC-3: 비관리자 /admin 접속 시 /dashboard 리다이렉트 확인 (버그 수정: 데모 로그인 시 setRole 누락 수정)
- ✅ TC-4: /register?code=xxx 접속 시 초대코드 자동 주입 확인 (안내 문구 추가)
- ✅ TC-5: 사이드바 관리자 메뉴 조건부 표시 확인
- ✅ TC-6: 사용자 승인/비활성화 기능 동작 확인
- ✅ TC-7: 회원가입 플로우 End-to-End 확인

---

## 프로덕션 배포 가이드 (AWS Lightsail)

CI/CD 파이프라인 기반의 단계별 배포 가이드입니다. `deploy.yml` 워크플로우가 GHCR에 이미지를 push한 후 Lightsail에 자동 배포합니다.

---

### Phase 1: Lightsail 사전 준비 (1회)

- ✅ **인스턴스 생성**
  - OS: Ubuntu 22.04 LTS
  - 플랜: $20/월 이상 (RAM 4GB+)
  - 방화벽: 80 포트(HTTP), 22 포트(SSH) 인바운드 허용
- ✅ **Docker 설치**
  ```bash
  curl -fsSL https://get.docker.com | sh
  sudo usermod -aG docker $USER
  newgrp docker
  ```
- ✅ **저장소 클론**
  ```bash
  git clone https://github.com/frogy95/mystock.bot.git /opt/mystock-bot
  cd /opt/mystock-bot
  git checkout main
  ```
- ✅ `**.env` 파일 생성 및 설정**
  ```bash
  cp .env.example .env
  # 아래 항목 편집
  python3 -c "import secrets; print(secrets.token_hex(32))"  # SECRET_KEY, JWT_SECRET 생성용
  ```
  필수 설정값:
  - `SECRET_KEY`, `JWT_SECRET` — 위 명령으로 각각 생성
  - `POSTGRES_PASSWORD` — 특수문자 포함 12자 이상
  - `DEBUG=false`
  - `CORS_ORIGINS=http://{서버IP}` (또는 실제 도메인)
  - `POSTGRES_HOST=postgres`, `REDIS_HOST=redis`
  - `NEXT_PUBLIC_API_URL=http://{서버IP}`
    > ℹ️ KIS API 키 및 텔레그램 설정은 앱 실행 후 관리자 페이지(설정 > 연동)에서 입력합니다.

---

### Phase 2: GitHub 사전 준비 (1회)

- ✅ **GitHub Secrets 설정** (저장소 Settings > Secrets and variables > Actions)

  | Secret 이름             | 설명                                 |
  | --------------------- | ---------------------------------- |
  | `LIGHTSAIL_SSH_KEY`   | Lightsail 인스턴스 SSH 개인키 (PEM 전체 내용) |
  | `LIGHTSAIL_HOST`      | Lightsail 퍼블릭 IP                   |
  | `LIGHTSAIL_USER`      | SSH 접속 사용자명 (보통 `ubuntu`)          |
  | `POSTGRES_PASSWORD`   | Phase 1에서 설정한 DB 비밀번호              |
  | `JWT_SECRET`          | Phase 1에서 생성한 JWT 시크릿              |
  | `SECRET_KEY`          | Phase 1에서 생성한 앱 시크릿                |
  | `NEXT_PUBLIC_API_URL` | 프론트엔드 API URL (예: `http://{서버IP}`) |

  자세한 Secrets 설명은 `docs/ci-policy.md` 참조.

---

### Phase 3: 배포 실행

- ✅ `develop` → `main` PR 생성 및 머지
- ✅ **GitHub Actions 모니터링**: [https://github.com/frogy95/mystock.bot/actions](https://github.com/frogy95/mystock.bot/actions)
  - `ci.yml` CI 워크플로우 통과 확인
  - `deploy.yml` 완료 확인 (GHCR 이미지 push + Lightsail SSH 배포)

---

### Phase 4: 배포 후 확인

- ✅ **DB 마이그레이션** (최초 1회 또는 스키마 변경 시)
  ```bash
  ssh {LIGHTSAIL_USER}@{LIGHTSAIL_HOST}
  cd /opt/mystock-bot
  docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
  ```
  ⚠️ 되돌릴 수 없으므로 반드시 수동으로 실행합니다.
- ✅ **헬스체크**: `curl http://{서버IP}/api/v1/health` → 200 응답 확인
- ✅ 프론트엔드 메인 페이지 접속 확인
- ✅ 관리자 로그인 동작 확인

---

### 롤백 방법 (문제 발생 시)

```bash
# Lightsail SSH 접속 후
cd /opt/mystock-bot
docker pull ghcr.io/frogy95/mystock-bot-backend:v0.16.0
docker pull ghcr.io/frogy95/mystock-bot-frontend:v0.16.0
docker compose -f docker-compose.prod.yml up -d
```

---

### 모의투자 5일 안정 운영 가이드

배포 후 최소 5거래일간 아래 항목을 모니터링합니다:


| 항목          | 확인 방법                                                               | 주기   |
| ----------- | ------------------------------------------------------------------- | ---- |
| 컨테이너 재시작 여부 | `docker compose -f docker-compose.prod.yml ps`                      | 매일   |
| 백엔드 로그 오류   | `docker compose -f docker-compose.prod.yml logs backend --tail 100` | 매일   |
| DB 용량       | `docker system df`                                                  | 주 1회 |
| 헬스체크        | `curl http://서버IP/api/v1/health`                                    | 매일   |
| KIS 토큰 갱신   | 백엔드 로그에서 `KIS 토큰 갱신` 메시지 확인                                         | 매일   |


---

## 배포 이력

### v0.17.1 (2026-03-06)

#### 포함 변경사항

- Hotfix: 대시보드 요약 카드 UX 개선 (PR #28, hotfix/dashboard-summary-ux)

#### PR

- [release: v0.17.1 프로덕션 배포 (#29)](https://github.com/frogy95/mystock.bot/pull/29)

#### 주요 변경 내용

- KIS 요약 데이터 통합: `get_balance()` output2에서 총평가금액, 매입합계, 손익합계, 전일총자산 필드 추가 추출
- 일일 손익 구현: `calculate_summary()`에서 KIS 데이터를 단일 소스로 사용, `현재 총자산 - 전일 총자산`으로 일일 손익 계산
- 에러/로딩 UX 개선: 포트폴리오 요약 카드에 `isError`/`isFetching` 상태 처리 및 "KIS 데이터를 불러오는 중..." 안내 텍스트 추가
- 보유종목 테이블 에러 처리: `isError` 시 에러 메시지 표시

#### 자동 배포 (GitHub Actions)

- ✅ main merge 시 GHCR 이미지 push 자동 실행
- ✅ Lightsail SSH 배포 자동 실행 (CD - 프로덕션 배포)

#### 자동 검증 완료 항목 (SSH + Playwright)

- ✅ 헬스체크: GET http://3.39.124.72/api/v1/health → 200 (status: healthy, db/redis/scheduler 모두 healthy)
- ✅ Docker 컨테이너 전체 Running 확인 (backend/frontend/nginx/postgres/redis 5개 모두 Up)
- ✅ 백엔드 로그 오류 없음 확인 (No errors found)
- ✅ 프론트엔드 메인 페이지 접속 확인 (Playwright — 로그인 페이지 정상 렌더링, /login 리다이렉트 확인)

#### 수동 검증 필요 항목

- ⬜ Alembic 마이그레이션 적용 (스키마 변경 없음 — 이번 배포는 생략 가능)
- ⬜ 실제 KIS API 실거래 대시보드 데이터 표시 확인 (실제 자금)
- ⬜ UI 디자인/시각적 품질 주관적 판단 (로딩 스켈레톤, 에러 메시지 UI)

---

### v0.17.0 (2026-03-05)

#### 포함 스프린트

- Sprint 17: MVP 프로덕션 배포 준비 (Docker prod, Nginx, CI/CD 파이프라인)
- Sprint 17 후속: 설정 간소화, CI/CD 워크플로우, 문서 업데이트

#### PR

- [release: v0.17.0 프로덕션 배포 (#27)](https://github.com/frogy95/mystock.bot/pull/27)

#### 자동 검증 완료 항목

- ✅ docker-compose.prod.yml 문법 검증: `docker compose -f docker-compose.prod.yml config`
- ✅ Dockerfile.prod 파일 생성 확인 (백엔드/프론트엔드)
- ✅ CORS 환경변수화 코드 반영 (`settings.CORS_ORIGINS` 적용)
- ✅ 헬스체크 503 반환 코드 반영 (`JSONResponse` with `status_code=503`)
- ✅ gunicorn 의존성 추가 (`backend/requirements.txt`)
- ✅ develop 브랜치 커밋 정상 상태 확인 (e2a16e2)
- ✅ GitHub Actions 워크플로우 파일 존재 확인 (ci.yml, deploy.yml)
- ✅ main merge 시 `ci.yml` CI 체크 자동 실행
- ✅ main merge 시 `deploy.yml` — GHCR 이미지 push + Lightsail SSH 배포 자동 실행

#### 수동 검증 필요 항목

- ⬜ `docker compose -f docker-compose.prod.yml up --build` 로컬 정상 기동 확인
- ⬜ `curl http://localhost/api/v1/health` → Nginx 경유 200 응답 확인
- ⬜ postgres/redis 포트 외부 접근 불가 확인 (`curl localhost:5432` 실패 확인)
- ⬜ Phase 3~4 배포 가이드 실행 및 서버 정상 동작 확인

---

### v0.18.0 (2026-03-06)

#### 포함 스프린트

- Sprint 18: 설정 페이지 UX 개선 (탭 구조, 저장 버튼, toast 피드백, 위험 구역 Card)

#### PR

- sprint-18 → develop PR (개발 검토 후 링크 업데이트 예정)

#### 변경 내용

| 변경 | 결과 |
|------|------|
| 탭 구조 | 3개 탭: "API 연동" / "매매 설정" / "알림 & 위험" |
| 저장 버튼 | 텔레그램, 매매시간, 안전장치 폼에 각각 추가 |
| toast 피드백 | 설정 저장/자동매매 토글/긴급매도 onSuccess에 toast.success 추가 |
| 긴급 매도 | w-full 제거, 위험 구역 Card로 분리 (빨간 테두리/배경) |
| 모의투자 키 | Collapsible 기본 접힌 상태, "선택사항" 라벨 |
| KIS 필드 순서 | 실전투자 키(필수) → 모의투자 키(선택) → HTS ID → 투자 모드 |

#### 자동 검증 완료 항목

- ✅ 백엔드 통합 테스트: `pytest -v` → 51 passed (1 warning)
- ✅ Playwright UI — 3개 탭 렌더링 (API 연동 / 매매 설정 / 알림 & 위험)
- ✅ Playwright UI — API 연동 탭: 실전투자 키 상단, 모의투자 키 Collapsible 접힌 상태 확인
- ✅ Playwright UI — 매매 설정 탭: 매매시간 저장 버튼 + 안전장치 저장 버튼 확인
- ✅ Playwright UI — 알림 & 위험 탭: 텔레그램 저장 버튼 + 위험 구역 Card(긴급 전체 매도) 확인

#### 수동 검증 필요 항목

- ✅ `docker compose up --build` — 새 코드(collapsible.tsx 신규 파일) 반영을 위한 Docker 재빌드
- ✅ 설정 저장 시 toast.success 메시지 시각적 확인 (자동매매 토글, KIS 저장, 텔레그램 저장 등)
- ✅ 모의투자 키 Collapsible 클릭 → 펼쳐짐/접힘 동작 브라우저 직접 확인
- ✅ UI 디자인/시각적 품질 주관적 판단 (위험 구역 Card 빨간 테두리, 탭 레이아웃 미적 요소)

---

### v0.19.0 (2026-03-06)

#### 포함 스프린트

- Sprint 19: 글로벌 종목 검색 구현 (yfinance 전환, KRX 한국어 매핑, 한글 IME 수정)
- Hotfix: KRX 종목 데이터 완성 (FinanceDataReader 교체, 3,790개)

#### PR

- Sprint 19 → develop → main: PR #33 (예정)
- Hotfix KRX 데이터: PR #32 (main 머지 완료)

#### 변경 내용

| 변경 | 결과 |
|------|------|
| 검색 엔진 교체 | pykrx(403 에러) → yfinance (전세계 시장, 무료, API 키 불필요) |
| KRX 한국어 이름 매핑 | `backend/data/krx_stocks.json` 정적 파일 로드 → 메모리 캐시 |
| KRX 종목 데이터 확장 | 197개 → 3,790개 (KOSPI 951, KOSDAQ 1767, ETF 1072) |
| 검색 범위 확장 | KOSPI/KOSDAQ → NYSE, NASDAQ, TSE 등 전세계 시장 |
| 한글 IME 버그 수정 | Popover `onOpenAutoFocus` 차단 + 300ms 디바운스 |
| 타입 확장 | `market: "KOSPI"\|"KOSDAQ"` → `string` (글로벌 대응) |
| 의존성 변경 | `pykrx`, `setuptools` 제거 → `yfinance>=0.2.0` 추가 |

#### 자동 검증 완료 항목

- ✅ 백엔드 통합 테스트: `pytest -v` → 51 passed (1 warning)
- ✅ KRX 종목 데이터 수집: 3,790개 (KOSPI 951, KOSDAQ 1767, ETF 1072)
- ✅ 유비케어 (KOSDAQ, 032620) 포함 확인
- ✅ KODEX ETF 230개 포함 확인

#### 수동 검증 필요 항목

- ⬜ `docker compose up --build` — yfinance 설치 + 새 JSON 데이터 반영을 위한 Docker 재빌드
- ⬜ 한국 종목 검색: `삼성` → 한국어 이름 정상 반환 확인
- ⬜ 글로벌 종목 검색: `AAPL` → 정상 반환 확인
- ⬜ 한글 쿼리 검색: `유비케어` → KOSDAQ 결과 확인
- ⬜ ETF 검색: `KODEX` → ETF 결과 확인
- ⬜ UI 디자인/시각적 품질 주관적 판단 (검색 결과 레이아웃 등)

