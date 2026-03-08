# Sprint 25: AI 전략 추천

## 개요

- **기간**: 2026-03-08
- **브랜치**: `sprint25`
- **PR**: develop 브랜치로 PR 생성
- **상태**: 완료

## 목표

다중 백테스트 결과를 Claude AI로 분석하여 최적 전략을 자동 추천한다.

## 구현 내용

### 1. AI 어드바이저 서비스 (신규)

- `backend/app/services/ai_advisor.py`: Anthropic claude-haiku-4-5-20251001 모델 사용
  - `get_ai_recommendation()`: 전략별 백테스트 성과 요약 → JSON 추천 반환
  - 퀀트 관점 분석 (수익률, MDD, 샤프지수, 승률 기반)
  - 포지션 상태(보유/관심종목) 반영한 맞춤 조언
  - JSON 파싱 실패 시 샤프지수 기준 폴백 추천
  - API 에러 시 적절한 예외 전파

### 2. AI 추천 API 엔드포인트 (신규)

- `POST /api/v1/backtest/ai-recommend`: AI 전략 추천 실행
  - 요청: `AIRecommendRequest` (symbol, stock_name, results_summary, is_holding, is_watchlist)
  - 응답: `AIRecommendationResponse` (recommended_strategy, confidence, analysis, risk_warning, position_advice)
  - ANTHROPIC_API_KEY 미설정 시 503 반환

### 3. 스키마 추가

- `backend/app/schemas/backtest.py`: `AIRecommendRequest`, `AIRecommendationResponse` 스키마 추가

### 4. 환경변수 추가

- `backend/requirements.txt`: `anthropic` 패키지 추가
- `.env.example`: `ANTHROPIC_API_KEY` 항목 추가

### 5. 프론트엔드 컴포넌트 (신규)

- `frontend/src/components/backtest/backtest-ai-recommendation.tsx`: AI 분석 카드 컴포넌트
  - 추천 전략명 + 신뢰도 뱃지 (높음/보통/낮음)
  - 종목 특성 분석 코멘트
  - 리스크 경고 (MDD 기반)
  - 포지션별 조언 (보유/관심종목/없음)
  - "AI 분석 요청" 버튼 (다중 결과 있을 때만 활성화)

### 6. 프론트엔드 훅 및 페이지 연동 (수정)

- `frontend/src/hooks/use-backtest.ts`: `useAIRecommend()` 훅 추가
- `frontend/src/app/backtest/page.tsx`: 다중 결과 존재 시 `BacktestAIRecommendation` 컴포넌트 표시

## 변경 파일 목록

| 파일 | 유형 | 설명 |
|------|------|------|
| `backend/app/services/ai_advisor.py` | 신규 | Anthropic API 기반 AI 전략 어드바이저 |
| `backend/app/api/v1/backtest.py` | 수정 | POST /backtest/ai-recommend 엔드포인트 추가 |
| `backend/app/schemas/backtest.py` | 수정 | AIRecommendRequest, AIRecommendationResponse 스키마 추가 |
| `backend/requirements.txt` | 수정 | anthropic 패키지 추가 |
| `.env.example` | 수정 | ANTHROPIC_API_KEY 항목 추가 |
| `frontend/src/components/backtest/backtest-ai-recommendation.tsx` | 신규 | AI 분석 카드 UI 컴포넌트 |
| `frontend/src/hooks/use-backtest.ts` | 수정 | useAIRecommend() 훅 추가 |
| `frontend/src/app/backtest/page.tsx` | 수정 | AI 추천 컴포넌트 통합 |

## 검증 결과

### 자동 검증 (2026-03-08)

- ✅ `pytest -v` — 51 passed (기존 테스트 회귀 없음)
- ✅ 헬스체크 (`/api/v1/health`) — DB/Redis/Scheduler 모두 healthy
- ✅ `/backtest/run-multi` 엔드포인트 라우터 등록 확인
- ✅ `/backtest/stock-status/{symbol}` 엔드포인트 라우터 등록 확인
- ✅ `/backtest/ai-recommend` 엔드포인트 라우터 등록 확인
- ✅ `/backtest/stock-status/005930` API 응답 정상 (보유: false, 관심: true)
- ✅ Playwright: 백테스팅 페이지 렌더링 정상
- ✅ Playwright: 체크박스 전략 선택 동작 정상 (골든크로스+RSI, 볼린저밴드반전 선택 → "2개 전략 선택됨" + "2개 전략 백테스트 실행" 버튼 레이블 동적 변경)
- ✅ Playwright: 전략 페이지 커스텀 전략 탭 렌더링 정상 (RSI 과매도 전략 에디터, "업데이트" 버튼 표시)
- ✅ 코드 리뷰: Critical/High 이슈 없음 ([보고서](sprint25/code-review-report.md))
- ✅ checkbox.tsx 누락 컴포넌트 추가 (빌드 오류 수정)

### 수동 검증 필요

- ⬜ `docker compose up --build` — anthropic 패키지 포함 이미지 빌드
- ⬜ `ANTHROPIC_API_KEY` 환경변수 설정 (`.env` 파일)
- ⬜ 다중 전략 선택 → 백테스트 실행 → 랭킹 테이블 확인
- ⬜ "AI 분석 요청" 버튼 클릭 → 추천 카드 표시 확인
- ⬜ ANTHROPIC_API_KEY 미설정 상태에서 503 반환 확인

## 스크린샷

- [백테스팅 페이지](sprint25/playwright-backtest-page.png)
- [체크박스 전략 선택](sprint25/playwright-backtest-strategy-checkbox.png)
- [커스텀 전략 에디터](sprint25/playwright-custom-strategy-editor.png)
