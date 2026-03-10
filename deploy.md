# 수동 작업 가이드 (deploy.md)

> 초기 환경 설정: [docs/setup-guide.md](docs/setup-guide.md) 참조
> 과거 검증/배포 기록: [docs/deploy-history/](docs/deploy-history/) 참조
> 개발 프로세스 가이드: [docs/dev-process.md](docs/dev-process.md) 참조

---

## Sprint 28: 전략 알고리즘 보강 — 기존 3종 개선 + 신규 3종 추가 (2026-03-10)

PR: https://github.com/frogy95/mystock.bot/pull/54 (sprint28 → develop)

- ✅ 자동 검증 완료 항목:
  - 코드 리뷰: Critical/High 이슈 없음
  - pytest: 51 passed (회귀 없음)
  - API 검증: `/api/v1/health` 정상 (database/redis/scheduler healthy)
  - 데모 모드 API 검증: 전략 목록 6개 정상 반환
  - Playwright 검증: 로그인 → 대시보드 → 전략("기본 전략" 섹션 헤더 정상) → 백테스팅 정상 로드
  - 콘솔 에러: 0건

- ⬜ 수동 검증 필요 항목:
  - `docker compose up --build` — 신규 전략 포함 이미지 재빌드
  - `docker compose exec backend python3 scripts/seed.py` — 신규 프리셋 전략 3종 DB 주입
  - 전략 목록에서 MACDTrend / 저베타모멘텀 / 모멘텀리스크스위치 카드 표시 확인
  - "퀀트 전략" 섹션 헤더 및 카드 렌더링 확인 (seed 후)
  - 신규 전략으로 백테스트 실행 → 결과 정상 반환 확인

---

## 현재 미완료 수동 검증 항목

### Hotfix: KIS 토큰 상태 기반 대시보드 동기화 UX 개선 (2026-03-09)

PR: https://github.com/frogy95/mystock.bot/pull/52

- ⬜ `docker compose up --build` — 변경 파일 반영 (이미지 재빌드)
- ⬜ KIS 토큰 미발급 상태에서 대시보드 진입 시 "KIS 토큰 발급 대기 중..." 인라인 메시지 확인
- ⬜ 토큰 유효 상태에서 자동 동기화 silent 동작 (에러 토스트 미노출) 확인
- ⬜ develop 역머지: main merge 후 `git checkout develop && git pull origin main && git push origin develop`

### Sprint 23~25 — Phase 15: 전략 테스팅 업그레이드 (2026-03-08)

PR: https://github.com/frogy95/mystock.bot/pull/46 (sprint25 → develop)

- ⬜ `docker compose up --build` — anthropic 패키지 포함 이미지 재빌드
- ⬜ `docker compose exec backend alembic upgrade head` — JSONB 컬럼 마이그레이션 적용
- ⬜ `.env`에 `ANTHROPIC_API_KEY=sk-ant-...` 설정
- ⬜ 다중 전략 선택(2개 이상) → 백테스트 실행 → 랭킹 테이블 렌더링 확인
- ⬜ 랭킹 테이블에서 "적용" 버튼 클릭 → 단일 결과 표시 전환 확인
- ⬜ "AI 분석 요청" 버튼 클릭 → 추천 전략/신뢰도/리스크/포지션 조언 카드 표시 확인
- ⬜ 커스텀 전략 "업데이트" 버튼 클릭 → 서버 저장 성공 토스트 확인
- ⬜ ANTHROPIC_API_KEY 미설정 상태에서 AI 분석 요청 → 503 오류 처리 확인

### Hotfix: BacktestRunRequest 타입 불일치 (2026-03-08)

PR: https://github.com/frogy95/mystock.bot/pull/48 (sprint25 → main)

- ⬜ `docker compose up --build` — 프론트엔드 코드 변경 반영 (이미지 재빌드)
- ⬜ develop 역머지: main merge 후 `git checkout develop && git pull origin main && git push origin develop`

### Hotfix: 백테스트 종목검색 드롭다운 오버플로우 (2026-03-08)

PR: https://github.com/frogy95/mystock.bot/pull/47 (sprint25 → main)

- ⬜ `docker compose up --build` — 프론트엔드 코드 변경 반영 (이미지 재빌드)
