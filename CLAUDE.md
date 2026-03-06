# mystock.bot

주식 관련 봇 프로젝트입니다.

## 저장소

- **원격 저장소**: [https://github.com/frogy95/mystock.bot.git](https://github.com/frogy95/mystock.bot.git)

## 언어 및 커뮤니케이션 규칙

- 기본 응답 언어: 한국어
- 코드 주석: 한국어로 작성
- 커밋 메시지: 한국어로 작성
- 문서화: 한국어로 작성
- 변수명/함수명: 영어 (코드 표준 준수)

## Git 브랜치 전략

### Sprint 흐름 (기능 개발)
```
sprint{n}  →  PR to develop  →  로컬 Docker 스테이징 검증  →  PR to main  →  Lightsail 자동 배포
```

### Hotfix 흐름 (긴급 패치)
```
hotfix/*  →  PR to main  →  Lightsail 자동 배포  →  main을 develop에 역머지
```

- `sprint{n}`: 스프린트 단위 개발 브랜치
- `develop`: 스테이징 통합 브랜치 (로컬 Docker로 검증)
- `main`: 프로덕션 브랜치 (GitHub Actions → AWS Lightsail 자동 배포)
- `hotfix/*`: 긴급 운영 패치 (main 기반 분기, main PR 후 develop 역머지)

자세한 CI/CD 정책은 `docs/ci-policy.md` 참조.

## 개발시 유의해야할 사항

- **plan 모드에서 수정사항을 받으면 반드시 Hotfix vs Sprint 의사결정을 먼저 수행합니다:**
  1. 수정사항의 긴급도, 변경 범위, DB 변경 여부, 의존성 추가 여부를 분석합니다.
  2. 아래 기준에 따라 Hotfix 또는 Sprint를 추천합니다.
  3. 사용자의 최종 결정을 받은 후 해당 프로세스를 따릅니다.

  **Hotfix 추천 기준** (모두 충족 시):
  - 프로덕션 장애/버그이거나, 변경 범위가 파일 3개 이하 & 코드 50줄 이하
  - DB 스키마 변경 없음
  - 새 의존성(pip/npm) 추가 없음

  **Sprint 추천 기준** (하나라도 해당 시):
  - 새 기능 추가 또는 여러 모듈에 걸친 작업
  - DB 스키마 변경 필요
  - 새 의존성 추가 필요
  - 파일 4개 이상 또는 코드 50줄 초과 변경

- sprint 관련 문서 구조:
  - 스프린트 계획/완료 문서: `docs/sprint/sprint{n}.md`
  - 스프린트 첨부 파일 (스크린샷, 보고서 등): `docs/sprint/sprint{n}/`
- sprint 개발이 plan 모드로 진행될 때는 다음을 꼭 준수합니다.
  - karpathy-guidelines skill을 준수하세요.
  - sprint 가 새로 시작될 때는 새로 branch를 sprint{n} 이름으로 생성하고 해당 브랜치에서 작업해주세요. (worktree 사용하지 말아주세요)
  - 다음과 같이 agent를 활용합니다.
    1. sprint-planner agent가 계획 수립 작업을 수행하도록 해주세요.
    2. 구현/검증 단계에서는 각 task의 내용에 따라 적절한 agent가 있는지 확인 한 후 적극 활용해주세요.
    3. 스프린트 구현이 완료되면 sprint-close agent를 사용하여 마무리 작업(ROADMAP 업데이트, PR 생성, 코드 리뷰, 자동 검증)을 수행해주세요.
    4. sprint-close agent는 **`develop` 브랜치로 PR**을 생성합니다. (main이 아닌 develop)
    5. `develop` → `main` merge는 별도 QA 통과 후 deploy-prod agent를 사용합니다.

- hotfix 개발이 plan 모드로 진행될 때는 다음을 꼭 준수합니다.
  - karpathy-guidelines skill을 준수하세요.
  - `main` 기반으로 `hotfix/{설명}` 브랜치를 생성합니다. (worktree 사용하지 말아주세요)
  - sprint-planner agent는 사용하지 않습니다. (계획 수립 불필요)
  - 구현 완료 후 hotfix-close agent를 사용하여 마무리 작업(PR to main, 경량 검증, deploy.md 기록, develop 역머지 안내)을 수행합니다.
  - ROADMAP.md 업데이트나 sprint 문서 작성은 불필요합니다.
  - 프로덕션 배포는 main merge 시 GitHub Actions가 자동 수행합니다.
  - 배포 후 실서버 검증이 필요하면 deploy-prod agent의 5단계(실서버 자동 검증)를 참조합니다.

- 스프린트 검증 원칙 — **자동화 가능한 항목은 sprint-close 시점에 직접 실행**:
  - ✅ **자동 실행**: `docker compose exec backend pytest -v` — 백엔드 통합 테스트
  - ✅ **자동 실행**: API 동작 검증 (curl/httpx) — Docker 컨테이너가 실행 중인 경우 sprint-close agent가 직접 실행
  - ✅ **자동 실행**: 데모 모드 API 검증 — 마찬가지로 서버 실행 중이면 자동 실행
  - ✅ **자동 실행**: Playwright UI 검증 — 페이지 렌더링, 버튼 동작, 폼 제출 등 자동화 가능한 UI 시나리오는 서버 실행 중이면 sprint-close agent가 직접 실행
  - ❌ **수동 필요**: `docker compose up --build` — 새 코드 반영을 위한 Docker 재빌드 (타이밍을 사용자가 결정)
  - ❌ **수동 필요**: `alembic upgrade head` — prod DB 스키마 변경 (되돌릴 수 없으므로 사용자가 직접 실행)
  - ❌ **수동 필요**: 실제 KIS API 실거래 확인 (실제 자금이 사용되므로 사용자가 직접 확인)
  - ❌ **수동 필요**: UI 디자인/시각적 품질 주관적 판단 (색상, 레이아웃 미적 요소 등 Playwright로 측정 불가한 항목)
  - sprint-close agent는 자동 실행 항목을 실행하고 결과를 deploy.md에 기록해야 합니다.
  - deploy.md에는 "자동 검증 완료" 항목과 "수동 검증 필요" 항목을 명확히 구분하여 기재합니다.

- 핫픽스 검증 원칙 — **sprint보다 경량화된 검증**:
  - ✅ **자동 실행**: `docker compose exec backend pytest -v` — 백엔드 통합 테스트
  - ✅ **자동 실행**: 해당 변경사항과 관련된 페이지/API만 Playwright/curl로 타겟 검증
  - ❌ **수동 필요**: sprint 검증의 수동 항목과 동일
  - hotfix-close agent는 자동 실행 항목을 실행하고 결과를 deploy.md에 기록합니다.

- deploy-prod 실서버 검증 원칙 — **배포 후 SSH로 자동 실행**:
  - SSH 키: `./mystock-bot-ssh-key.pem` (프로젝트 루트), 서버: `ubuntu@3.39.124.72`
  - ✅ **자동 실행**: 헬스체크 (`curl http://3.39.124.72/api/v1/health`)
  - ✅ **자동 실행**: Docker 컨테이너 상태 확인 (`docker compose ps`)
  - ✅ **자동 실행**: 백엔드 로그 오류 확인 (`docker compose logs backend --tail 30`)
  - ✅ **자동 실행**: Playwright 프론트엔드 접속 확인 (메인 페이지, 로그인 페이지)
  - ❌ **수동 필요**: `alembic upgrade head` — prod DB 스키마 변경 (되돌릴 수 없음)
  - ❌ **수동 필요**: 실제 KIS API 실거래 확인 (실제 자금)
  - ❌ **수동 필요**: UI 디자인/시각적 품질 주관적 판단

- 사용자가 직접 수행해야 하는 작업은 deploy.md 파일을 생성하거나 기존에 존재하는 deploy.md에 수행해야하는 작업을 자세히 정리해주세요.
- 체크리스트 작성 형식:
  - 완료 항목: `- ✅ 항목 내용`
  - 미완료 항목: `- ⬜ 항목 내용`
  - GFM `[x]`/`[ ]` 대신 이모지를 사용하여 마크다운 미리보기에서 시각적 구분을 보장합니다.
