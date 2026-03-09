# Sprint 27: 관심종목 시세 표시 + 백테스팅 UX 개선

- **브랜치**: `sprint27`
- **기간**: 2026-03-09
- **PR**: https://github.com/frogy95/mystock.bot/pull/53 (sprint27 → develop)
- **상태**: 완료

## 목표

관심종목 추가 시 현재가 0원으로 표시되는 버그를 수정하고, 백테스팅 UX를 전반적으로 개선한다. nginx 타임아웃으로 인해 장기 실행 시 실패하는 문제를 SSE 스트리밍 방식으로 해결한다.

## Task 목록

### Task 1: 백테스팅 종료일 기본값 오늘
- `frontend/src/components/backtest/backtest-config-form.tsx`
- `useState("")` → `useState(new Date().toISOString().slice(0, 10))`

### Task 2: 관심종목 현재가 0원 버그 수정
- `frontend/src/stores/watchlist-store.ts`: `updateItemQuote(symbol, quote)` 액션 추가
- `frontend/src/components/watchlist/stock-search.tsx`: 종목 추가 후 `/api/v1/stocks/{symbol}/quote` REST API 호출
- `frontend/src/app/watchlist/page.tsx`: `useRealtimeQuotes` WebSocket 구독 + `updateItemQuote` 연동

### Task 3: 백테스팅 종목선택 탭 추가
- `frontend/src/components/backtest/backtest-config-form.tsx`: "검색 | 보유종목 | 관심종목" 3탭
- `useHoldings()`, `useWatchlistGroups()` 훅 연동

### Task 4: 백테스팅 엔진 O(n²) → O(n) 최적화
- `backend/app/services/backtest_engine.py`: `_build_signals()` 루프에서 chart_list 증분 구축

### Task 5: SSE 스트리밍 백테스트
- `backend/app/api/v1/backtest.py`: `POST /backtest/run-multi-stream` 엔드포인트 추가
- `docker/nginx/nginx.conf`: SSE 전용 location 추가 (proxy_buffering off, timeout 600s)
- `frontend/src/hooks/use-backtest.ts`: `useBacktestRunMultiSSE()` 훅 추가
- `frontend/src/components/backtest/backtest-progress.tsx`: 진행상황 표시 컴포넌트 신규
- `frontend/src/app/backtest/page.tsx`: SSE 방식으로 변경, 프로그레스 UI 표시

## 변경 파일

| 파일 | 유형 |
|------|------|
| `frontend/src/components/backtest/backtest-config-form.tsx` | 수정 |
| `frontend/src/stores/watchlist-store.ts` | 수정 |
| `frontend/src/components/watchlist/stock-search.tsx` | 수정 |
| `frontend/src/app/watchlist/page.tsx` | 수정 |
| `backend/app/services/backtest_engine.py` | 수정 |
| `backend/app/api/v1/backtest.py` | 수정 |
| `docker/nginx/nginx.conf` | 수정 |
| `frontend/src/hooks/use-backtest.ts` | 수정 |
| `frontend/src/components/backtest/backtest-progress.tsx` | 신규 |
| `frontend/src/app/backtest/page.tsx` | 수정 |

## 검증 결과

검증 보고서: [docs/deploy-history/2026-03-09.md](../deploy-history/2026-03-09.md)

- ✅ TypeScript tsc --noEmit: 오류 없음
- ✅ Python 구문 검사: 오류 없음
- ✅ pytest: 51 passed
- ✅ API 검증: health, backtest results, watchlist 정상
- ✅ 데모 모드 API: 정상
- ✅ Playwright: 로그인 → 관심종목 → 백테스팅 페이지 검증 통과
- ✅ 콘솔 에러: 0건
- 스크린샷: [backtest-page-sprint27.png](sprint27/backtest-page-sprint27.png)
