# mystock.bot

주식 관련 봇 프로젝트입니다.

## 저장소

- **원격 저장소**: https://github.com/frogy95/mystock.bot.git

## 언어 및 커뮤니케이션 규칙

- 기본 응답 언어: 한국어
- 코드 주석: 한국어로 작성
- 커밋 메시지: 한국어로 작성
- 문서화: 한국어로 작성
- 변수명/함수명: 영어 (코드 표준 준수)

## 개발시 유의해야할 사항

- sprint 개발이 plan 모드로 진행될 때는 다음을 꼭 준수합니다.
  - karpathy-guidelines skill을 준수하세요.
  - sprint 가 새로 시작될 때는 새로 branch를 sprint{n} 이름으로 생성하고 해당 브랜치에서 작업해주세요.
  - 다음과 같이 agent를 활용합니다.
     1. sprint-planner agent가 계획 수립 작업을 수행하도록 해주세요.
     2. 구현/검증 단계에서는 각 task의 내용에 따라 적절한 agent가 있는지 확인 한 후 적극 활용해주세요.

- 사용자가 직접 수행해야 하는 작업은 deploy.md 파일을 생성하거나 기존에 존재하는 deploy.md에 수행해야하는 작업을 자세히 정리해주세요.

- sprint 개발이 진행되는 단계를 ROADMAP.md 에 업데이트 해주세요.

- sprint 브랜치에서 main으로 PR을 생성한 후에는 code-reviewer agent를 사용하여 코드 리뷰를 수행해주세요.

- deploy.md에 기재된 검증 항목 중 자동으로 수행 가능한 항목(Playwright MCP 등)은 직접 수행해주세요.
  - 테스트 결과 보고서와 스크린샷은 `docs/sprint/sprint{n}/` 폴더에 저장해주세요.
  - `docs/sprint/sprint{n}.md`에 검증 보고서 링크를 추가해주세요.
  - deploy.md 체크리스트를 검증 결과에 따라 업데이트해주세요.

