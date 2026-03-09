# 수동 작업 가이드 (deploy.md)

> 초기 환경 설정: [docs/setup-guide.md](docs/setup-guide.md) 참조
> 과거 검증/배포 기록: [docs/deploy-history/](docs/deploy-history/) 참조
> 개발 프로세스 가이드: [docs/dev-process.md](docs/dev-process.md) 참조

---

## Hotfix: 모의투자 모드 전환 시 holdings 정리 및 auto-sync 조건 수정 (2026-03-09)

### 브랜치 및 PR
- 브랜치: `sprint26` (hotfix 작업)
- PR: https://github.com/frogy95/mystock.bot/pull/50 (sprint26 → main)

### 문제 원인
모의투자(VTS)↔실거래(REAL) 환경 전환 시 복합 버그 3건:
1. `kis_mode` 변경 시 DB holdings 미삭제 → 구환경 종목 잔존
2. holdings auto-sync 조건(`holdings?.length === 0`)으로 인해 종목 있으면 동기화 스킵
3. 전략 목록 로드 실패 시 `isError` 미처리 → 스켈레톤 무한 표시

### 수정 내용
- `backend/app/api/v1/system_settings.py`: `kis_mode` 변경 시 해당 유저의 holdings 전체 삭제
- `frontend/src/components/dashboard/holdings-table.tsx`: auto-sync 조건에서 `holdings?.length === 0` 제거
- `frontend/src/components/strategy/strategy-card-list.tsx`: `isError` 추출 후 에러 메시지 표시

### 검증 결과
- ✅ 자동 검증 완료 항목:
  - pytest: 51 passed (docker compose exec backend pytest tests/ -q)
  - 코드 리뷰: Critical/High 이슈 없음
  - 변경 범위: 3개 파일, +20줄/-3줄 (hotfix 기준 충족)

- ⬜ 수동 검증 필요 항목:
  - `docker compose up --build` — 백엔드/프론트엔드 코드 변경 반영 (이미지 재빌드)
  - 모의→실거래 모드 전환 후 보유종목 화면이 초기화되는지 확인
  - 전환 후 보유종목 자동 동기화가 즉시 시작되는지 확인
  - develop 역머지: main merge 후 `git checkout develop && git pull origin main && git push origin develop`

---

## 현재 미완료 수동 검증 항목

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
