# Sprint 23~25 코드 리뷰 보고서

- **PR**: https://github.com/frogy95/mystock.bot/pull/46
- **검토 범위**: sprint25 브랜치 전체 (Sprint 23~25 구현)
- **검토 일자**: 2026-03-08
- **검토자**: sprint-close agent (Claude Sonnet 4.6)

---

## 요약

| 심각도 | 건수 |
|--------|------|
| Critical | 0 |
| High | 0 |
| Medium | 3 |
| Low/Info | 4 |

**Critical/High 이슈 없음 — 머지 진행 가능**

---

## Medium 이슈

### M-01: ai_advisor.py — `text` 변수 참조 가능성
- **파일**: `backend/app/services/ai_advisor.py`, 104번째 줄
- **내용**: `json.JSONDecodeError` 핸들러에서 `text`를 참조하지만, `response.content[0].text.strip()` 실행 이전에 예외가 발생하면 `text`가 미정의 상태일 수 있음.
  ```python
  except json.JSONDecodeError as e:
      logger.warning(f"AI 추천 JSON 파싱 실패: {e}, 응답: {text}")  # text 미정의 가능성
  ```
- **권장 조치**: `text = ""` 초기화 후 할당하거나, except 블록에서 `e.doc`를 대신 참조.

### M-02: DynamicStrategy — 최신 시점 단일 행 평가
- **파일**: `backend/app/services/strategy_engine.py`
- **내용**: `_evaluate_condition()`이 DataFrame 마지막 행(`iloc[-1]`)만 평가함. 백테스트는 전체 시계열에서 신호를 생성해야 하는데, 이 방식은 "현재 시점"만 반환하므로 백테스트 엔진에서 슬라이딩 윈도우 방식으로 루프를 돌아야 함. 현재 구현에서 이 부분이 어떻게 연동되는지 명확히 문서화 필요.
- **권장 조치**: `generate_signals()` 내에서 전체 시계열 반복 여부 확인 및 주석 추가.

### M-03: run_backtest_multi — 동시성 제한 없음
- **파일**: `backend/app/api/v1/backtest.py`
- **내용**: `asyncio.gather(*tasks)`로 선택된 전략 수만큼 동시 백테스트를 실행함. 전략이 다수(예: 10개 이상)인 경우 I/O 및 CPU 부하가 집중될 수 있음.
- **권장 조치**: `asyncio.Semaphore`로 동시 실행 수를 제한(예: 최대 5개). 단, 현재 MVP 규모에서는 실질적 문제 없음.

---

## Low/Info 이슈

### L-01: backtest.py 내 지연 임포트 (`from app.models.watchlist import WatchlistGroup`)
- **파일**: `backend/app/api/v1/backtest.py`, `get_stock_status()` 내부
- **내용**: `WatchlistGroup`을 함수 내부에서 지연 임포트함. 파일 상단 임포트로 이동하면 일관성 향상.

### L-02: ai_advisor.py — 싱글톤 클라이언트와 ANTHROPIC_API_KEY 재로드
- **파일**: `backend/app/services/ai_advisor.py`
- **내용**: `_client` 싱글톤이 최초 호출 시 생성되므로, 환경변수가 나중에 설정되어도 반영되지 않음. 현재 Docker 환경에서는 문제없으나 동적 키 교체 불가.

### L-03: `WatchlistStatusItem` 미사용 임포트 가능성
- **파일**: `backend/app/api/v1/backtest.py`
- **내용**: `WatchlistStatusItem`이 임포트되어 있고 `get_stock_status()`에서 사용되므로 문제없음. 정상.

### L-04: BacktestAIRecommendation — stock_name을 symbol로 대체
- **파일**: `frontend/src/components/backtest/backtest-ai-recommendation.tsx`, 43번째 줄
- **내용**: `stock_name: symbol`로 종목명 대신 심볼 코드를 전달함. AI 분석 품질에 영향을 줄 수 있으나 기능적으로는 동작함. 향후 종목명 API 연동 시 개선 권장.

---

## 긍정적 사항

- **에러 처리**: `ai_advisor.py`에서 JSON 파싱 실패 시 폴백 로직, API 오류 시 예외 전파를 분리하여 처리.
- **데모 모드 분기**: 신규 엔드포인트(`run-multi`, `ai-recommend`) 모두 데모 모드 차단 처리됨.
- **인증/권한**: `get_stock_status()` 포함 모든 신규 엔드포인트에서 `get_current_user` 의존성 주입 일관 적용.
- **랭킹 스코어**: 가중치 설계가 퀀트 관점에서 합리적 (수익률 30%, 샤프 25%, 승률 20%, MDD 역수 15%, CAGR 10%).
- **AI 프롬프트**: 시스템 프롬프트에서 응답 형식(JSON)을 명확히 지정하여 파싱 안정성 확보.
- **타입 안전성**: Pydantic 스키마(`AIRecommendRequest`, `AIRecommendationResponse`)를 통한 입출력 검증.
