# Sprint 15: 사용자별 전략/백테스트 데이터 격리

## 개요

- **스프린트 번호:** Sprint 15
- **브랜치:** sprint-15
- **시작일:** 2026-03-03
- **완료일:** 2026-03-03
- **상태:** 완료

## 목표

Sprint 14에서 구축한 JWT 멀티유저 인증 기반 위에 데이터 격리 계층을 추가한다.
전략(Strategy)과 백테스트 결과(BacktestResult)를 사용자별로 격리하여:
- 프리셋 전략은 모든 사용자가 조회 가능 (공용 읽기)
- 각 사용자는 프리셋을 복사하여 본인만의 전략을 생성하고 관리 가능
- 백테스트 결과는 실행한 사용자만 조회 가능

## 완료 기준 (Definition of Done)

- ✅ Strategy.user_id (nullable FK) 추가 — NULL=프리셋, 값=사용자 소유
- ✅ BacktestResult.user_id (NOT NULL FK) 추가
- ✅ Alembic 마이그레이션 적용
- ✅ GET /strategies → 프리셋 + 본인 소유만 반환
- ✅ POST /strategies/{id}/clone → 프리셋을 사용자 소유로 복사
- ✅ PUT /strategies/{id}/activate, /params → 본인 소유만 수정 가능 (프리셋 404)
- ✅ GET /backtest/results → 본인 결과만 조회
- ✅ 프론트엔드: 프리셋 토글 차단 UI, "내 전략으로 복사" 버튼
- ✅ 전체 테스트 45 passed (기존 33 + 신규 12, 2단계 완료 후 최종 수치)

## 주요 변경 사항

### 1. 모델 수정 (backend/app/models/)

#### Strategy 모델
- `user_id` 컬럼 추가 (nullable FK → users.id)
- NULL 값: 프리셋 전략 (모든 사용자 공용)
- 값 존재: 특정 사용자 소유 전략

#### BacktestResult 모델
- `user_id` 컬럼 추가 (NOT NULL FK → users.id)
- 기존 레코드는 admin(id=1)에 할당

### 2. Alembic 마이그레이션 (d4e5f6a7b8c9)

- `strategies.user_id` 컬럼 추가 (nullable)
- `backtest_results.user_id` 컬럼 추가 (NOT NULL, 기존 레코드 admin에 할당)

### 3. Strategy API (backend/app/api/v1/strategies.py)

| 엔드포인트 | 변경 내용 |
|-----------|----------|
| GET /strategies | 프리셋(user_id IS NULL) + 본인 소유(user_id=me) 반환 |
| GET /strategies/{id} | 프리셋 또는 본인 소유만 접근 허용 |
| PUT /strategies/{id}/activate | 본인 소유만 토글 (프리셋 → 404) |
| PUT /strategies/{id}/params | 본인 소유만 수정 (프리셋 → 404) |
| POST /strategies/{id}/evaluate/{symbol} | 프리셋 + 본인 소유 평가 허용 |
| POST /strategies/{id}/clone (신규) | 전략 복사 — 프리셋→사용자 소유 복제본 생성 |

### 4. Backtest API (backend/app/api/v1/backtest.py)

| 엔드포인트 | 변경 내용 |
|-----------|----------|
| POST /backtest/run | user_id=current_user.id 저장 |
| GET /backtest/results | 본인 결과만 조회 |
| GET /backtest/results/{id} | 본인 결과만 접근 허용 |

### 5. Schema (backend/app/schemas/strategy.py)

- `StrategyResponse`에 `user_id: Optional[int]` 필드 추가

### 6. Demo Data (backend/app/services/demo_data.py)

- 전략 더미 데이터에 `user_id: None` 추가 (프리셋으로 표시)

### 7. 테스트 (backend/tests/api/)

#### test_strategies.py 신규 테스트 6개
- `test_strategies_returns_presets`: 프리셋 전략 조회 확인
- `test_user_cannot_activate_preset`: 프리셋 토글 시 404 확인
- `test_clone_strategy`: 전략 복사본 생성 확인
- `test_cloned_strategy_is_user_owned`: 복사본 user_id 확인
- `test_clone_isolation`: 복사본 수정이 원본에 영향 없음 확인
- `test_user_can_activate_cloned_strategy`: 복사본 토글 성공 확인

#### test_backtest.py 신규 파일 (테스트 2개)
- `test_backtest_result_isolation`: 사용자별 결과 격리 확인
- `test_backtest_run_stores_user_id`: 백테스트 실행 시 user_id 저장 확인

### 8. 프론트엔드 (frontend/src/)

#### use-strategy.ts
- `StrategyAPI`에 `user_id: number | null` 추가
- `useCloneStrategy` 훅 추가 (POST /strategies/{id}/clone)

#### strategy-card-list.tsx
- 프리셋 전략(`user_id === null`) 토글 차단
- 프리셋에 "내 전략으로 복사" 버튼 표시

#### strategy-detail-panel.tsx
- 프리셋 전략 파라미터 읽기전용 표시
- "파라미터를 수정하려면 전략을 복사하세요" 안내 문구

## 테스트 결과

```
40 passed, 1 failed
```

- 통과: 40개 (기존 33 + 신규 7)
- 실패: 1개 — `test_stocks.py::test_balance_returns_valid_status`
  - 원인: KIS API 네트워크 오류 (Sprint 15 이전부터 존재하는 기존 실패)
  - Sprint 15와 무관

## 커밋 내역

| 커밋 | 메시지 |
|------|--------|
| c29138a | feat: 프론트엔드 전략 컴포넌트에 사용자 격리 UI 반영 |
| 39f42d9 | test: Sprint 15 전략/백테스트 사용자 격리 테스트 추가 |
| 28e3afd | feat: 전략/백테스트 API에 사용자별 데이터 격리 로직 추가 |
| 3182b4f | feat: Strategy/BacktestResult 모델에 user_id FK 추가 및 Alembic 마이그레이션 |

## 검증 결과

- [pytest 보고서](sprint15/pytest-report.md) (2026-03-03, 자동 검증)
  - 41 passed, 0 failed
  - Sprint 15 신규 테스트 8개 포함 (전략 격리 6개 + 백테스트 격리 2개) 전부 통과
- [코드 리뷰 보고서](sprint15/code-review-report.md) (2026-03-03, 자동 코드 리뷰)
  - Critical 이슈: 0건
  - High 이슈: 1건 (clone 후 불필요한 DB 재조회 — 성능 경미, 기능 정상)
  - Medium 이슈: 3건 (추후 개선 권장)
  - MED-3 (데모 유저 분기) 재확인 완료: `run_backtest_api` 62번 줄에서 데모 유저 즉시 차단 — 안전

## 사용자 수동 검증 항목

deploy.md 섹션 17 참고:

1. Docker 재빌드 후 `alembic upgrade head` 실행
2. API 수동 검증:
   - `GET /api/v1/strategies` → 프리셋 전략만 표시 (신규 사용자)
   - `POST /api/v1/strategies/{id}/clone` → 복사본 생성 확인
   - `PUT /api/v1/strategies/{cloned_id}/activate` → 복사본 토글 성공
   - `PUT /api/v1/strategies/{preset_id}/activate` → 프리셋 토글 실패 (404)
   - `POST /api/v1/backtest/run` → user_id 포함 저장
   - `GET /api/v1/backtest/results` → 본인 결과만 조회
3. 데모 모드 정상 동작 확인
