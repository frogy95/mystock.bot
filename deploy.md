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
6. `.env` 파일에 입력:
   ```
   KIS_APP_KEY=발급받은_App_Key
   KIS_APP_SECRET=발급받은_App_Secret
   KIS_ACCOUNT_NUMBER=계좌번호 (하이픈 포함, 예: 50123456-01)
   ```

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

- [ ] 한국투자증권 계좌 개설 완료
- [ ] KIS App Key / App Secret 발급 완료
- [ ] 모의투자 신청 완료
- [ ] 텔레그램 봇 생성 및 Bot Token 발급 완료
- [ ] Telegram Chat ID 확인 완료
- [ ] Python 3.12+ 설치 확인
- [ ] Node.js 22+ 설치 확인
- [ ] Docker Desktop 설치 및 실행 확인
- [ ] `.env` 파일 생성 및 모든 값 입력 완료

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
# http://localhost:3000
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

- [ ] `docker compose up --build` 성공
- [ ] 4개 서비스 모두 Up 상태
- [ ] `curl http://localhost:8000/api/v1/health` → 200 OK
- [ ] `http://localhost:3000` → "AutoTrader KR" 표시
- [ ] `alembic upgrade head` 성공
- [ ] 10개 테이블 확인
- [ ] seed 데이터 삽입 완료
