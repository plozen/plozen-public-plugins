---
name: verification-branch-finish-hook-harness
description: 완료, fixed, ready, merge, cleanup을 말하기 전 마지막 변경 이후 fresh verification evidence를 확보하고, 종료 자동화가 필요하면 `finish-flow-harness`로 넘겨야 할 때 사용한다.
---
# Verification / Branch Finish Hook Harness

## 역할

이 스킬은 마지막 변경 이후의 fresh local evidence와 PASS / FAIL / UNVERIFIED / PARTIAL gate 판정만 담당한다. commit·push·PR은 finish-flow-harness가 담당하며, branch/worktree 안전은 worktree-hook-harness가 담당한다.

## 사용 시점

다음과 같이 말하기 전에 적용한다.

- 완료, fixed, ready, 통과, 해결됨
- merge 가능, cleanup 가능
- commit/push/PR로 넘겨도 됨
- 작업 브랜치 종료, worktree 정리

## Fresh evidence

fresh evidence는 아래 조건을 모두 만족해야 한다.

1. 마지막 파일 변경 이후 실행됐다.
2. 현재 branch/HEAD/worktree에서 실행됐다.
3. 변경 범위와 직접 연결된다.
4. exit code, 실패 수, 확인한 artifact가 보고됐다.
5. 실패 또는 skip 이유가 숨겨지지 않았다.

변경 범위에 맞는 최소 증거만 선택한다.

| 변경 범위 | 최소 evidence |
|---|---|
| docs/skill | frontmatter·schema·content assertion와 git diff --check |
| package/app code | 관련 lint, test, typecheck, build 중 필요한 명령 |
| bug/behavior change | 동일 재현 절차 또는 regression test |
| UI/browser-facing | browser smoke, 실제 UI action, screenshot, responsive·overflow·accessibility, API/RPC/server action/network/readback 통합 evidence, 전용 verifier subagent 기록 |
| auth/secret/infra/dependency | secret scan과 해당 보안·권한·설정 검증 |
| workflow/CI | local syntax validation과 가능한 dry-run |

명령을 찾을 수 없으면 저장소의 README와 package scripts 등 제공된 경로를 확인한다. 그래도 실행할 수 없거나 필요한 verifier가 없으면 UNVERIFIED로 보고하고 누락된 evidence를 적는다. 변경과 무관한 전체 회귀 절차는 자동으로 붙이지 않는다.

## 실행 절차

scope -> evidence-plan -> run-verification -> inspect-results -> gate-decision

### 1. scope와 evidence-plan

- 현재 branch와 작업 트리를 확인한다.
- 변경 파일을 확인한다: git status --short, git diff --name-only, 필요 시 git diff --cached --name-only.
- 변경 성격을 분류한다: docs/skill, code, UI, config, infra, auth/secret, dependency.
- 소유자가 불명확한 dirty change는 완료 판정에 섞지 않는다.

### 2. run과 inspect

- 명령을 실제로 실행하고 결과를 다음처럼 기록한다: command/procedure, PASS·FAIL·SKIP·UNAVAILABLE, exit code, artifact, note.
- subagent가 실행한 검증도 로그·파일·exit code·artifact를 확인한다.
- warning, skipped test, 실패 수를 숨기지 않는다. exit 0이어도 실제 오류가 있으면 PASS가 아니다.
- 오래 걸리는 명령은 완료까지 기다리며, 실패를 성공으로 요약하지 않는다.
- browser-facing 변경이면 검증 서브에이전트가 실제 UI와 통합 경계를 수행했는지 확인하고, 그 결과·로그·screenshot·network/readback evidence를 메인이 통합한다.

### 3. gate decision

- PASS: 필요한 fresh evidence가 모두 통과했다.
- FAIL: 필수 검증이 실패했다.
- UNVERIFIED: 필수 검증을 실행하지 못했거나 evidence가 부족하다.
- PARTIAL: 필수 evidence는 통과했지만 선택 검증을 생략했고 남은 위험을 보고했다.

완료·fixed·ready·merge 가능 선언은 PASS 또는 사용자가 위험을 알고 승인한 PARTIAL에서만 가능하다. local 수정만 확인하면 commit/push 없이 evidence를 보고하고, commit/push/PR 요청이 있으면 이 결과를 finish-flow-harness에 전달한다. cleanup은 worktree-hook-harness와 finish-flow의 조건을 모두 따른다.

## 완료 보고 포맷

VERIFICATION_GATE: PASS / FAIL / UNVERIFIED / PARTIAL
branch: <branch>
head: <short-sha>
changed_scope: <docs|code|ui|config|infra|mixed>
verifier_subagent: <id/name/status/result>
ui_gate: PASS / FAIL / UNVERIFIED
integration_gate: PASS / FAIL / UNVERIFIED

evidence:
- <name>: <PASS|FAIL|SKIP|UNAVAILABLE>, exit=<code>, artifact=<...>, note=<...>

finish_route: none / finish-flow-harness / manual-followup

remaining_risk:
- <없으면 none>

blocked_reason:
- FAIL 또는 UNVERIFIED인 경우 원인을 적는다.

required_action:
- 누락·실패 evidence를 해소할 다음 액션을 적는다.

## 하드 규칙

- fresh evidence 없이 완료, fixed, ready, merge 가능이라고 말하지 않는다.
- 오래된 테스트나 다른 branch의 결과를 현재 변경의 근거로 쓰지 않는다.
- 검증을 실행할 수 없으면 UNVERIFIED라고 말한다.
- secret/auth/infra 변경은 필요한 보안·권한 gate 없이는 PASS로 닫지 않는다.
- browser-facing 변경은 verifier subagent 기록과 `ui_gate=PASS`, `integration_gate=PASS`가 모두 있어야 PASS다. 하나라도 누락되거나 `FAIL`/`UNVERIFIED`면 gate는 `UNVERIFIED`이며 완료·fixed·ready·배포를 선언하지 않는다.
