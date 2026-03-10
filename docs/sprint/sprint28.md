# Sprint 28: 전략 알고리즘 보강 — 기존 전략 3종 개선 + 신규 전략 3종 추가

- **브랜치**: `sprint28`
- **기간**: 2026-03-10
- **PR**: (진행 중)
- **상태**: 구현 완료, 검증 완료

---

## 목표

기존 프리셋 전략 3종의 신호 품질을 개선하고, `docs/algorithm.md` 기반의 퀀트 이론을 적용한 신규 프리셋 전략 3종을 추가한다. 전략 레지스트리를 3개 → 6개로 확장하고, 백테스팅 엔진에 시장 데이터 주입 파이프라인을 구축한다.

---

## 배경 및 동기

Sprint 27까지 백테스팅 인프라(SSE 스트리밍, UX 개선)가 완성되었다. 이제 실제로 백테스트할 전략의 품질을 높여야 한다.

- **기존 전략 3종**: 단순 신호 조건으로 인해 Falling Knife 진입, 과열 매도 미실행 등 실전 한계가 존재
- **신규 전략 3종**: `docs/algorithm.md`에 설계된 BAB(Betting Against Beta), Dual Momentum 이론을 KOSPI 단일 종목 롱온리 방식으로 구현

---

## 스프린트 범위

### 포함 항목

- 기존 전략 3종 (GoldenCrossRSI, BollingerReversal, ValueMomentum) 신호 로직 강화
- 신규 전략 3종 (MACDTrend, LowBetaMomentum, MomentumRiskSwitch) 구현
- 전략 레지스트리 3 → 6 확장
- `indicators.py` 신규 지표 함수 추가 (MOMENTUM_20/60, SMA60_SLOPE, calculate_beta, get_market_returns)
- `backtest_engine.py` 시장 의존 전략을 위한 KOSPI 데이터 사전 로딩 파이프라인
- `seed.py` / `demo_data.py` 신규 전략 데이터 동기화
- 프론트엔드 전략 카드 카테고리 분류 표시 (기본 전략 / 퀀트 전략)

### 제외 항목

- 공매도(Short) 포지션 구현 — KOSPI 현물 롱온리 제약
- BAB 풀 포트폴리오 구성 (횡단면 롱/숏) — MVP 범위 초과
- Piotroski F-Score 스크리닝 — 재무 데이터 API 미연동 (향후 Sprint 예정)
- 실전 자동매매 연동 — 백테스팅 검증 단계

---

## Task 목록

### Task 1: indicators.py — 신규 지표 함수 추가

**파일**: `backend/app/services/indicators.py`

- `MOMENTUM_20(df)`: 20일 모멘텀 (현재가 / 20일 전 종가 - 1)
- `MOMENTUM_60(df)`: 60일 모멘텀 (현재가 / 60일 전 종가 - 1)
- `SMA60_SLOPE(df)`: SMA(60) 5일 기울기 (현재 SMA60 - 5일 전 SMA60)
- `calculate_beta(df, market_returns, window=252)`: Vasicek 수축 베타 산출
  - Dimson 방법론 적용 (당기 + 1일 시차 시장 수익률)
  - Vasicek 수축 가중치 w=0.5 적용
- `get_market_returns(market_df)`: KOSPI 지수 일간 수익률 산출

### Task 2: strategy_engine.py — 기존 전략 3종 개선

**파일**: `backend/app/services/strategy_engine.py`

#### GoldenCrossRSI 개선

| 항목 | 기존 | 변경 후 |
|------|------|---------|
| 매수 조건 | SMA5 > SMA20 AND RSI < 70 | SMA5 > SMA20 AND RSI < 70 **AND MACD_hist > 0** |
| 매도 조건 | SMA5 < SMA20 OR RSI > 70 | SMA5 < SMA20 OR **RSI > 75** |

- MACD 히스토그램 양수 조건 추가 → 골든크로스 직후 모멘텀 확인으로 허위 신호 감소
- 매도 RSI 임계값 70→75 상향 → 과열 구간에서 더 명확한 신호에만 매도

#### BollingerReversal 개선

| 항목 | 기존 | 변경 후 |
|------|------|---------|
| 매수 조건 | 종가 < BB_lower AND RSI < 30 | 종가 < BB_lower AND RSI < 35 **AND SMA60_SLOPE > 0** |
| 매도 조건 | 종가 > BB_upper OR RSI > 70 | (동일) |

- SMA(60) 5일 기울기 양수 조건 → 하락 추세 중 Falling Knife 진입 방지
- RSI 매수 임계값 30→35 완화 → 진입 기회 확대 (SMA 조건이 방어)

#### ValueMomentum 개선

| 항목 | 기존 | 변경 후 |
|------|------|---------|
| 매수 조건 | MOMENTUM_20 > 0 AND PER 하위 30% | **MOMENTUM_60 > 0 AND MOMENTUM_20 > 0** AND PER 하위 30% |
| 매도 조건 | MOMENTUM_20 < 0 OR PER 상위 70% | **MOMENTUM_60 < 0** OR PER 상위 70% |

- Gary Antonacci Dual Momentum 차용
- 20일 단일 모멘텀 → 60일+20일 이중 모멘텀 필터 (장기 추세 확인 후 단기 진입)
- 매도는 장기 모멘텀(60일) 기준으로 전환하여 잦은 매도 감소

### Task 3: strategy_engine.py — 신규 전략 3종 추가

**파일**: `backend/app/services/strategy_engine.py`

#### MACDTrend (MACD 추세추종)

- `strategy_type`: `technical`
- **매수 조건**: MACD > Signal (교차 발생) AND MACD_hist 가 전 2일 연속 증가 (히스토그램 증가 추세)
- **매도 조건**: MACD < Signal (데드크로스 발생) OR MACD_hist < 0

```
설계 근거: 단순 MACD 교차만으로는 허위 신호가 많음. 히스토그램 증가 추세를 추가로 요구하여
추세 강도가 확인된 시점에만 진입.
```

#### LowBetaMomentum (저베타 모멘텀)

- `strategy_type`: `quantitative`
- **지표**: Vasicek 수축 베타 (w=0.5, 252일 롤링)
- **매수 조건**: 베타 < 0.8 AND MOMENTUM_60 > 0
  - 저베타 종목 (시장 민감도 낮음) + 장기 모멘텀 양수 = BAB 전략 롱 레그 근사
- **매도 조건**: 베타 > 1.0 OR MOMENTUM_60 < 0
- **시장 의존성**: KOSPI 지수 수익률 필요 (backtest_engine에서 주입)

```
설계 근거: algorithm.md 섹션 2 BAB 전략. 공매도 없이 롱온리로 저베타 알파만 취득.
Frazzini & Pedersen (2010) 저베타 포트폴리오 우월한 샤프 비율 검증.
```

#### MomentumRiskSwitch (모멘텀 리스크 스위치)

- `strategy_type`: `quantitative`
- **로직**: Gary Antonacci Dual Momentum의 절대 모멘텀(Risk-Off Switch) 적용
- **매수 조건 (Risk-On)**: MOMENTUM_60 > 0 (절대 모멘텀 양수 = 무위험 수익률 초과)
- **매도 조건 (Risk-Off)**: MOMENTUM_60 < 0 (절대 모멘텀 음수 = 채권/현금으로 전환 신호)
- **시장 의존성**: KOSPI 지수 MOMENTUM_60 교차 확인용

```
설계 근거: algorithm.md 섹션 3 Dual Momentum. 단순하지만 강력한 리스크온/오프 스위치.
시장 전반이 하락할 때 자동으로 현금 보유 신호 발생 → 드로우다운 방어.
```

### Task 4: backtest_engine.py — 시장 데이터 주입 파이프라인

**파일**: `backend/app/services/backtest_engine.py`

- 백테스트 실행 전 KOSPI 지수 OHLCV 데이터 사전 로딩
- `LowBetaMomentum`, `MomentumRiskSwitch` 등 `requires_market_data=True` 전략 감지
- 전략 인스턴스에 `market_df` 주입 → `calculate_beta`, `get_market_returns` 활용

### Task 5: seed.py / demo_data.py — 신규 전략 시드 데이터

**파일**: `backend/scripts/seed.py`, `backend/app/services/demo_data.py`

신규 프리셋 전략 3종 DB 시드 레코드:

| name | display_name | strategy_type |
|------|-------------|---------------|
| MACDTrend | MACD 추세추종 | technical |
| LowBetaMomentum | 저베타 모멘텀 | quantitative |
| MomentumRiskSwitch | 모멘텀 리스크 스위치 | quantitative |

### Task 6: strategy-card-list.tsx — 프론트엔드 카테고리 분류

**파일**: `frontend/src/components/strategy/strategy-card-list.tsx`

- `strategy_type` 필드 기반으로 전략 카드 섹션 분리
- "기본 전략" 섹션: `technical` 유형 (GoldenCrossRSI, BollingerReversal, MACDTrend)
- "퀀트 전략" 섹션: `quantitative` 유형 (ValueMomentum, LowBetaMomentum, MomentumRiskSwitch)
- 섹션 헤더 및 배지(badge) UI 추가

---

## 기술적 접근 방법

### 베타 산출 알고리즘 (Vasicek 수축)

```
1. 종목 일간 수익률 = pct_change(종가)
2. KOSPI 지수 일간 수익률 = get_market_returns(market_df)
3. Dimson 베타: 현재일 + 1일 시차 시장 수익률로 OLS 회귀
   β_TS = cov(종목, 시장) / var(시장)
4. Vasicek 수축: β_Vasicek = 0.5 * β_TS + 0.5 * 1.0
   (횡단면 평균 β^XS = 1 방향으로 수축, w=0.5)
```

### Dual Momentum 이중 필터 구조

```
Long 진입 조건 (AND):
  MOMENTUM_60 > 0  → 장기 추세 확인 (절대 모멘텀)
  MOMENTUM_20 > 0  → 단기 모멘텀 확인 (상대 모멘텀 근사)

Exit 조건:
  MOMENTUM_60 < 0  → 장기 추세 반전 = Risk-Off
```

### 전략 레지스트리 구조

```python
STRATEGY_REGISTRY = {
    "GoldenCrossRSI":       GoldenCrossRSI,
    "BollingerReversal":    BollingerReversal,
    "ValueMomentum":        ValueMomentum,
    "MACDTrend":            MACDTrend,           # 신규
    "LowBetaMomentum":      LowBetaMomentum,     # 신규
    "MomentumRiskSwitch":   MomentumRiskSwitch,  # 신규
}
```

---

## 의존성 및 리스크

| 리스크 | 내용 | 대응 방안 |
|--------|------|-----------|
| KOSPI 지수 데이터 부재 | LowBetaMomentum, MomentumRiskSwitch가 KOSPI 수익률 필요 | backtest_engine에서 시장 데이터 사전 로딩, 실패 시 해당 전략 graceful skip |
| 베타 계산 분모 0 | 시장 수익률 분산이 0인 경우 ZeroDivisionError | np.where로 방어, 분모 epsilon 처리 |
| 252일 롤링 윈도우 초기 구간 | 데이터 부족 시 베타 NaN | dropna 처리, NaN 구간 신호 미발생으로 처리 |
| 신규 전략 DB 미주입 | seed.py 재실행 없이 배포 시 전략 목록에 표시 안 됨 | 배포 후 `python scripts/seed.py` 수행 필수 |

---

## 완료 기준 (Definition of Done)

- ✅ 기존 51개 pytest 전부 통과 (회귀 없음)
- ✅ 전략 레지스트리 6개 정상 로드 확인
- ✅ 신규 지표 (MOMENTUM_20/60, SMA60_SLOPE, calculate_beta) 정상 계산
- ✅ MACDTrend 백테스트 실행 → 결과 반환 (에러 없음)
- ✅ LowBetaMomentum 백테스트 실행 → 베타 계산 포함 결과 반환
- ✅ MomentumRiskSwitch 백테스트 실행 → 리스크 스위치 신호 포함 결과 반환
- ✅ 프론트엔드 전략 카드 "기본 전략 / 퀀트 전략" 섹션 분리 표시

---

## 변경 파일

| 파일 | 유형 | 변경 내용 |
|------|------|-----------|
| `backend/app/services/indicators.py` | 수정 | MOMENTUM_20/60, SMA60_SLOPE 지표 추가, calculate_beta/get_market_returns 함수 추가 |
| `backend/app/services/strategy_engine.py` | 수정 | 기존 3개 전략 신호 개선 + 신규 3개 전략 클래스 + 레지스트리 3→6 확장 |
| `backend/app/services/backtest_engine.py` | 수정 | 시장 의존 전략 KOSPI 데이터 사전 로딩 및 주입 파이프라인 |
| `backend/scripts/seed.py` | 수정 | 신규 3개 프리셋 전략 시드 데이터 추가 |
| `backend/app/services/demo_data.py` | 수정 | 신규 전략 더미 데이터 동기화 |
| `frontend/src/components/strategy/strategy-card-list.tsx` | 수정 | 전략 카테고리 분류 표시 (기본 전략 / 퀀트 전략) |

---

## 검증 결과

- ✅ pytest: 51 passed (기존 테스트 회귀 없음)
- ✅ 전략 레지스트리 6개 정상 로드
- ✅ MOMENTUM_20/60, SMA60_SLOPE 지표 정상 계산
- ✅ calculate_beta (Vasicek 수축) 정상 동작
- ✅ MACDTrend 백테스트 결과 반환
- ✅ LowBetaMomentum 백테스트 결과 반환 (KOSPI 데이터 주입 포함)
- ✅ MomentumRiskSwitch 백테스트 결과 반환
- ✅ 프론트엔드 카테고리 분류 UI 표시

---

## 예상 산출물

1. 전략 레지스트리 6종 (기존 3 + 신규 3) — 모두 백테스트 가능
2. 프론트엔드 전략 목록 페이지 카테고리 분류 (기본 전략 / 퀀트 전략)
3. algorithm.md 이론 → 실제 구현 연결 (BAB 롱 레그, Dual Momentum 적용 사례)

---

## 참고 문서

- `docs/algorithm.md`: BAB 전략, Dual Momentum 설계 원본
- `docs/sprint/sprint27.md`: 이전 스프린트 (백테스팅 인프라 완성)
- Frazzini & Pedersen (2010): Betting Against Beta
- Gary Antonacci: Dual Momentum Investing
