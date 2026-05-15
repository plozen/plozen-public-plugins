---
name: verification-branch-finish-hook-harness
description: 완료, fixed, ready, merge, cleanup을 말하기 전 마지막 변경 이후 fresh verification evidence를 확보하고, 종료 자동화가 필요하면 `finish-flow-harness`로 넘겨야 할 때 사용한다.
---

# Verification / Branch Finish Hook Harness

## 역할

완료 선언 전에는 마지막 변경 이후 fresh verification evidence를 확보한다. 이 스킬은 "작업이 검증됐는가"를 판정하는 gate이고, commit/push/PR checks 자동화는 `finish-flow-harness`가 담당한다.

분리 원칙:

- 이 스킬: fresh local evidence 수집, gate 판정, 완료 가능 여부 판단.
- `finish-flow-harness`: `local-preflight -> commit -> push -> pr-gate` 종료 자동화.
- local verification이 실패했거나 실행되지 않았으면 완료가 아니라 `UNVERIFIED` 또는 `FAIL`로 보고한다.
- push 이후 remote checks가 필요하면 `finish-flow-harness`를 호출한다. checks 없음은 `NO_CHECKS`로 분리 보고한다.

## 사용 시점

다음 말을 하기 전에 적용한다.

- 완료, fixed, ready, 통과, 해결됨
- merge 가능, cleanup 가능
- commit/push/PR로 넘겨도 됨
- 작업 브랜치 종료, worktree 정리

사용자가 `push까지`, `PR까지`, `종료 루틴`, `finish flow`를 요청하면 이 gate로 fresh evidence를 확인한 뒤 `finish-flow-harness`를 이어서 적용한다.

## Fresh evidence 기준

fresh evidence는 아래 조건을 모두 만족해야 한다.

1. 마지막 파일 변경 이후 실행됐다.
2. 현재 branch/HEAD/worktree에서 실행됐다.
3. 변경 범위와 직접 연결된다.
4. exit code, 실패 수, 확인한 artifact가 보고됐다.
5. 실패 또는 skip 이유가 숨겨지지 않았다.

예:

- 문서/스킬 변경: frontmatter validation, markdown/content assertion, `git diff --check`.
- 코드 변경: 관련 unit/integration test, lint/typecheck/build.
- UI 변경: screenshot/browser smoke, responsive/overflow/accessibility checks.
- auth/secret/infra 변경: secret scan, permission/config validation, security gate.
- workflow/CI 변경: local syntax validation, dry-run 가능 여부, remote check 계획.

## 실행 절차

```text
scope -> evidence-plan -> run-verification -> inspect-results -> gate-decision -> finish-route
```

### 1. scope

- 현재 branch와 작업 트리를 확인한다.
- 변경 파일을 확인한다: `git status --short`, `git diff --name-only`, 필요 시 `git diff --cached --name-only`.
- 변경 성격을 분류한다: docs/skill, code, UI, config, infra, auth/secret, dependency.
- 소유자가 불명확한 dirty change는 완료 판정에 섞지 않는다.

### 2. evidence-plan

변경 성격에 맞는 최소 fresh evidence를 정한다.

- docs/skill only: `git diff --check`, frontmatter/schema/content assertion.
- package/app code: lint + relevant tests + build/typecheck 중 프로젝트가 제공하는 명령.
- bug fix: 재현 실패/성공 증거 또는 regression test.
- UI/browser-facing: browser smoke 또는 screenshot 기반 evidence.
- security/secret/auth: secret scan + security review/gate.

명령을 찾을 수 없으면 파일 구조와 README/package scripts를 확인한다. 그래도 없으면 `UNVERIFIED`로 보고하고, 어떤 evidence가 비었는지 적는다.

### 3. run-verification

- 명령을 실제로 실행한다.
- subagent가 검증했다면 self-report만 믿지 말고 로그, 파일, exit code, artifact를 확인한다.
- 오래 걸리는 검증은 background process를 사용해 완료까지 기다린다.
- 실패 명령을 성공처럼 요약하지 않는다.

### 4. inspect-results

각 evidence를 아래 형식으로 정리한다.

```text
- <command or procedure>: <PASS|FAIL|SKIP|UNAVAILABLE>, exit=<code>, artifact=<path/url/count>, note=<짧은 설명>
```

실패 수, warning, skipped test가 있으면 그대로 남긴다. `exit 0`이어도 실제 출력이 오류를 말하면 PASS로 판정하지 않는다.

### 5. gate-decision

판정값:

- `PASS`: 필요한 fresh evidence가 모두 통과했다.
- `FAIL`: 필수 검증이 실패했다.
- `UNVERIFIED`: 필수 검증을 실행하지 못했거나 evidence가 부족하다.
- `PARTIAL`: 선택 검증 일부만 생략됐고 필수 evidence는 통과했다. 남은 위험을 명시한다.

완료 선언은 `PASS` 또는 사용자가 위험을 알고 승인한 `PARTIAL`에서만 가능하다. `UNVERIFIED`는 완료가 아니다.

### 6. finish-route

검증 후 branch 종료 경로를 선택한다.

- 사용자가 commit/push/PR을 요청했거나 저장소 정책이 있으면 `finish-flow-harness`로 넘긴다.
- 아직 local 수정만 확인하면 되는 상황이면 commit/push 없이 evidence만 보고한다.
- merge/cleanup 전이면 `finish-flow-harness`의 PR remote gate 결과까지 확인한 뒤 cleanup 여부를 판단한다.
- worktree cleanup은 clean + merged/pushed 상태가 확인된 뒤에만 진행한다.

## 완료 보고 포맷

```text
VERIFICATION_GATE: <PASS|FAIL|UNVERIFIED|PARTIAL>
branch: <branch>
head: <short-sha>
changed_scope: <docs|code|ui|config|infra|mixed>

evidence:
- <name>: <PASS|FAIL|SKIP|UNAVAILABLE>, exit=<code>, artifact=<...>, note=<...>

finish_route:
- <none|finish-flow-harness|manual-followup>

remaining_risk:
- <없으면 none>
```

## 실패/미검증 보고 포맷

```text
VERIFICATION_GATE: <FAIL|UNVERIFIED>
blocked_reason:
- <실패/미검증 이유>

failed_or_missing_evidence:
- <command/procedure>: <FAIL|UNAVAILABLE>, detail=<짧게>

required_action:
- <다음에 해야 할 액션 1-3개>
```

## 하드 규칙

- fresh evidence 없이 `완료`, `fixed`, `ready`, `merge 가능`이라고 말하지 않는다.
- 오래된 테스트 결과를 현재 변경의 근거로 쓰지 않는다.
- 검증을 실행할 수 없으면 `UNVERIFIED`라고 말한다.
- commit/push/PR checks까지 필요한 종료 루틴은 `finish-flow-harness`로 분리한다.
- `NO_CHECKS`는 PASS가 아니다. remote check evidence가 없다는 별도 상태다.
- secret/auth/infra 변경은 security gate 없이는 `PASS`로 닫지 않는다.
