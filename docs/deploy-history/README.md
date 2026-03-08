# 배포/검증 기록 아카이브

날짜별 스프린트/핫픽스 검증 기록을 보관합니다.
sprint-close, hotfix-close, deploy-prod agent가 완료된 기록을 이 디렉토리로 이동합니다.

## 네이밍 규칙

- `YYYY-MM-DD.md` — 해당 날짜의 모든 검증/배포 기록 (최신 기록이 파일 상단)

## 현재 아카이브 목록

| 파일 | 포함 기록 |
|------|---------|
| `2026-03-08.md` | Sprint 22, Sprint 23~25, 핫픽스 7건 (BacktestRunRequest, 드롭다운, confidence, 날짜형식, 신호인덱스, 날짜필터, 프리셋중복) |
| `2026-03-07.md` | 프로덕션 배포 v0.21.0, Sprint 21, 핫픽스 2건 (SSH timeout, compose write permission) |
| `2026-03-06.md` | 프로덕션 배포 v0.20.0, v0.19.0, Sprint 17~20, 핫픽스 krx-fulldata |

> Sprint 0~16 (2026-02-28 ~ 2026-03-05)의 검증 기록은 아카이브 미생성 상태입니다.
> 원본 기록은 `deploy.md`의 git history (`git log --all -- deploy.md`)에서 확인 가능합니다.
