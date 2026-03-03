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

## 개발시 유의해야할 사항

- sprint 관련 문서 구조:
  - 스프린트 계획/완료 문서: `docs/sprint/sprint{n}.md`
  - 스프린트 첨부 파일 (스크린샷, 보고서 등): `docs/sprint/sprint{n}/`
- sprint 개발이 plan 모드로 진행될 때는 다음을 꼭 준수합니다.
  - karpathy-guidelines skill을 준수하세요.
  - sprint 가 새로 시작될 때는 새로 branch를 sprint{n} 이름으로 생성하고 해당 브랜치에서 작업해주세요.
  - 다음과 같이 agent를 활용합니다.
    1. sprint-planner agent가 계획 수립 작업을 수행하도록 해주세요.
    2. 구현/검증 단계에서는 각 task의 내용에 따라 적절한 agent가 있는지 확인 한 후 적극 활용해주세요.
    3. 스프린트 구현이 완료되면 sprint-close agent를 사용하여 마무리 작업(ROADMAP 업데이트, PR 생성, 코드 리뷰, 자동 검증)을 수행해주세요.
- 사용자가 직접 수행해야 하는 작업은 deploy.md 파일을 생성하거나 기존에 존재하는 deploy.md에 수행해야하는 작업을 자세히 정리해주세요.
- 체크리스트 작성 형식:
  - 완료 항목: `- ✅ 항목 내용`
  - 미완료 항목: `- ⬜ 항목 내용`
  - GFM `[x]`/`[ ]` 대신 이모지를 사용하여 마크다운 미리보기에서 시각적 구분을 보장합니다.

