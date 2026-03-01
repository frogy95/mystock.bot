# Sprint 4.1 Playwright 자동 검증 보고서

**검증 일시:** 2026-03-01
**대상 URL:** http://localhost:3000
**브랜치:** sprint4 (커밋 dcd401e)
**검증 도구:** Playwright MCP

---

## 검증 요약

| 항목 | 결과 |
|------|------|
| 총 검증 항목 | 8개 |
| 통과 | 8개 |
| 실패 | 0개 |
| 콘솔 에러 | 0건 |

---

## 검증 항목 상세

### 1. 커스텀 전략 탭 전환

- **시나리오:** `/strategy` 접속 후 "커스텀 전략" 탭 클릭
- **결과:** 통과
- **확인 내용:** 프리셋/커스텀 탭 전환 정상 동작, 커스텀 빌더 UI 렌더링 확인
- **스크린샷:** [playwright-custom-strategy-tab.png](playwright-custom-strategy-tab.png)

### 2. 전략 생성 및 자동 선택

- **시나리오:** "새 전략 만들기" 클릭 → 이름 입력("골든크로스 테스트") → Enter 제출
- **결과:** 통과
- **확인 내용:** 전략 목록에 추가되고 편집기가 자동으로 새 전략을 선택함. 조건 섹션에 "조건을 추가하세요" 안내 메시지 표시

### 3. 조건 행 추가

- **시나리오:** 매수 조건 "조건 추가" 버튼 클릭 (2회)
- **결과:** 통과
- **확인 내용:**
  - 첫 번째 조건 추가 후 조건 행 렌더링 (지표/기간/조건/우변종류/값 입력 필드)
  - 두 번째 조건 추가 후 AND 토글 자동 삽입
  - 전략 목록 카드의 "매수 2개 / 매도 0개 조건" 카운트 실시간 업데이트
- **스크린샷:** [playwright-custom-strategy-editor.png](playwright-custom-strategy-editor.png)

### 4. AND/OR 토글 동작

- **시나리오:** 조건 사이 "AND" 배지 클릭
- **결과:** 통과
- **확인 내용:** AND → OR 전환 확인, 전략 미리보기 텍스트 "SMA(20) > 0 OR SMA(20) > 0"으로 즉시 업데이트

### 5. 전략 미리보기 실시간 업데이트

- **시나리오:** 조건 추가 및 AND/OR 토글 후 미리보기 섹션 확인
- **결과:** 통과
- **확인 내용:**
  - 매수 조건: "SMA(20) > 0 OR SMA(20) > 0" 표시
  - 매도 조건: "(조건 없음)" 표시
  - 조건 변경 시 즉시 미리보기 텍스트 업데이트
- **스크린샷:** [playwright-strategy-preview-full.png](playwright-strategy-preview-full.png)

### 6. localStorage persist 동작

- **시나리오:** 전략 생성 후 페이지 재방문
- **결과:** 통과
- **확인 내용:** 모바일 뷰 재방문 시 이전에 생성한 RSI 전략, RSI 전략 (복사본), 골든크로스 테스트 전략이 localStorage에서 정상 복원됨

### 7. 모바일 반응형 (375px)

- **시나리오:** 뷰포트 375x812 설정 후 `/strategy` 접속
- **결과:** 통과
- **확인 내용:**
  - 사이드바 숨김, 햄버거 메뉴(≡) 헤더 좌측 표시
  - 프리셋/커스텀 탭 탭 정상 표시
  - 커스텀 전략 탭 전환 후 전략 목록, 편집기, 조건 행이 모바일 레이아웃으로 렌더링
  - 조건 행 입력 필드 가로 wrap 처리로 모바일에서 접근 가능
- **스크린샷:** [playwright-mobile-375px.png](playwright-mobile-375px.png), [playwright-mobile-custom-tab.png](playwright-mobile-custom-tab.png)

### 8. 콘솔 에러 없음

- **시나리오:** 전체 검증 과정 중 콘솔 에러 메시지 수집
- **결과:** 통과 (Error 0건, Warning 0건)

---

## 스크린샷 목록

| 파일명 | 설명 |
|--------|------|
| [playwright-custom-strategy-tab.png](playwright-custom-strategy-tab.png) | 커스텀 전략 탭 전환 후 전략 목록 + 편집기 (데스크톱) |
| [playwright-custom-strategy-editor.png](playwright-custom-strategy-editor.png) | 조건 2개 추가 + OR 토글 동작 확인 (데스크톱) |
| [playwright-strategy-preview-full.png](playwright-strategy-preview-full.png) | 전략 미리보기 섹션 - 매수/매도 조건 텍스트 변환 확인 |
| [playwright-mobile-375px.png](playwright-mobile-375px.png) | 모바일 375px - 프리셋 전략 탭 (햄버거 메뉴 확인) |
| [playwright-mobile-custom-tab.png](playwright-mobile-custom-tab.png) | 모바일 375px - 커스텀 전략 탭 + 편집기 렌더링 |

---

## 수동 검증 필요 항목

| 항목 | 이유 |
|------|------|
| 지표 선택 드롭다운 전체 8종 동작 확인 | MACD 특수 처리(빈 onValueChange), BB position Select 등 복잡한 케이스의 실제 UX 확인 필요 |
| 데스크톱 1920px 전체 레이아웃 | 자동 검증 범위 외 |
| 전략 복제 후 조건 ID 독립성 확인 | 복제된 전략의 조건을 수정했을 때 원본에 영향이 없는지 수동 확인 권장 |
