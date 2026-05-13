---
name: verification-branch-finish-hook-harness
description: 완료, fixed, ready, merge, cleanup을 말하기 전 fresh verification evidence를 확보하고 branch 종료 경로를 선택해야 할 때 사용한다.
---

# Verification / Branch Finish Hook Harness

완료 선언 전에는 fresh verification evidence를 확보한다.

- 완료, fixed, 통과, ready를 말하기 전에 증명할 명령이나 절차를 실행 단위로 만든다. 검증 책임을 분리할 필요가 있으면 subagent에 위임한다.
- 실행 결과, exit code, 실패 수, 확인한 artifact를 읽고 gate를 판정한다.
- 검증을 실행할 수 없으면 완료가 아니라 미검증 상태로 보고한다.
- branch 작업 완료 후에는 PR 생성, 병합, branch 유지, 폐기, worktree cleanup 중 하나를 선택한다.
- 선택한 경로와 남은 위험을 최종 보고에 남긴다.
