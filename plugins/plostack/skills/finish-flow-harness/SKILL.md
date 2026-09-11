---
name: finish-flow-harness
description: local verification evidence가 확보된 뒤 branch 종료를 local-preflight, commit, push, pr-gate 순서로 자동화해야 할 때 사용한다. main 직접 push 차단, secret 파일 차단, repo별 `.plostack/finish.toml` 검증, GitHub PR checks remote gate를 분리한다.
---
# Finish Flow Harness

## 역할

finish-flow-harness는 local-preflight -> explicit stage -> commit -> 필요 시 push -> 필요 시 PR checks로 branch를 닫는다. fresh local evidence와 완료 판정은 verification-branch-finish-hook-harness의 책임이며, worktree 생성·정리는 worktree-hook-harness의 책임이다.

## 사용 시점

다음 조건 중 하나가 있으면 사용한다.

- 사용자가 commit, push, PR, merge 전 체크, 마무리, 종료 루틴, push까지를 요청했다.
- local verification이 끝났고 남은 일이 Git 종료 루틴이다.
- repo별 종료 정책(.plostack/finish.toml)을 적용해야 한다.

다음이면 먼저 verification-branch-finish-hook-harness로 보낸다.

- 아직 수정이 끝나지 않았다.
- fresh evidence가 없고 단순 완료 여부만 묻는다.
- 작업 branch/worktree 안전성만 확인하면 된다.

## 입력과 전제

- repo root, 대상 branch, base branch, commit message
- push/PR 필요 여부와 .plostack/finish.toml
- 현재 변경에 대한 VERIFICATION_GATE: PASS 또는 사용자가 위험을 알고 승인한 PARTIAL

검증 결과가 없으면 이 문서에서 테스트를 다시 설계하지 말고 verification으로 돌린다. push와 PR은 사용자 요청 또는 저장소 정책이 있을 때만 진행한다.

main/master/base branch 직접 push는 기본 차단한다. 허용에는 이번 턴의 명시적 사용자 승인과 finish 설정의 allow_main_push = true가 모두 필요하다.

## 실행 흐름

resolve-config
  -> local-preflight
  -> stage
  -> commit
  -> optional push
  -> optional pr-gate
  -> finish-report

### 1. resolve-config

1. repo root, branch, status, remote, upstream을 확인한다. upstream이 없어도 push 전까지는 실패가 아니다.
2. .plostack/finish.toml이 있으면 적용하고, 없으면 templates/finish.toml의 안전 기본값을 따른다.
3. detached HEAD면 DETACHED_HEAD로 중단한다.
4. 기본값은 base_branch = main, allow_main_push = false, require_pr = true, stage_strategy = explicit, secret_scan = auto다.

## finish.toml contract

repo별 .plostack/finish.toml은 templates/finish.toml을 기준으로 한다. base branch와 main push 허용, PR 요구, stage 전략, secret scan, clean-after-commit, stage allow/deny, required preflight commands, PR checks timeout/no-checks 상태를 설정할 수 있다.

### 2. local-preflight

commit 전 변경 소유권과 credential 노출만 확인한다. verification의 content/test evidence를 반복하지 않는다. working diff의 git diff --check는 fresh verification evidence로 확인하고, stage 후에는 cached diff를 다시 확인한다.

- git status --short --branch로 staged, unstaged, untracked를 분리한다. 소유자가 불명확하거나 사용자의 변경이 섞이면 중단한다.
- secret file guard를 적용한다. .env, .env.*, *.pem, *.key, *.p12, *.pfx, id_rsa, id_ed25519, credentials.json, credentials*.json, service-account*.json, kakao-config.local.js가 staged/tracked면 SECRET_FILE_BLOCKED다. untracked secret은 git check-ignore -v -- <path>로 ignore 여부를 확인한다. .env.example, .env.sample, *.example, *.template은 허용 가능하지만 내용 scan은 한다.
- gitleaks detect --redact --source .가 있으면 우선 사용하고, 없으면 detect-secrets scan, 둘 다 없으면 working/staged diff에서 api[_-]?key, secret, token, password, private_key, AKIA[0-9A-Z]{16} 패턴을 redacted fallback scan한다. 후보 secret 값은 출력하지 않는다.
- .plostack/finish.toml의 required local_preflight command를 실행한다. 실패하면 push를 막고, 선택 명령 skip도 보고한다.
- commit 대상과 남길 untracked를 분리 보고한다. allowlist 밖 파일은 commit하지 않는다.

### 3. stage

- 기본은 git add <explicit paths>다. git add .는 설정의 all_safe가 허용하고 preflight가 통과한 경우에만 사용한다.
- stage allow/deny와 secret denylist를 다시 확인하고, git diff --cached --name-status와 git diff --cached --check를 실행한다.
- staged diff가 비어 있으면 NO_CHANGES로 종료한다.

### 4. commit

- 사용자 message를 우선하고, 없으면 conventional commit을 사용한다.
- commit 후 git rev-parse --short HEAD와 git status --short --branch를 확인한다.
- 의도하지 않은 unstaged/untracked가 남으면 보고한다. require_clean_after_commit = true면 DIRTY_AFTER_COMMIT으로 push를 막는다.

### 5. push

- push가 요청되지 않으면 commit에서 멈추고 remote 작업을 하지 않는다.
- feature branch는 git push -u origin HEAD를 기본으로 사용한다.
- main/master/base 직접 push 조건이 충족되지 않으면 MAIN_PUSH_BLOCKED로 중단한다.
- push 실패는 PUSH_FAILED로 보고하고 remote error를 요약한다.

### 6. pr-gate

push 이후에만 remote gate를 실행하며 local verification과 섞지 않는다.

1. 기존 PR은 gh pr view --json number,url,headRefName,baseRefName,state,isDraft로 확인한다.
2. PR이 없고 사용자가 요청했거나 require_pr = true면 gh pr create를 실행한다. gh 인증·권한 문제는 PR_GATE_UNAVAILABLE이다.
3. gh pr checks --watch로 checks를 기다린다. 실패는 REMOTE_CHECKS_FAILED, check가 없으면 NO_CHECKS다. NO_CHECKS는 성공이 아니며 remote CI evidence 없음으로 보고한다.

## 판정 상태

- PASS: 선택된 local-preflight·commit과 요청되거나 정책상 필요한 push·PR remote checks가 모두 성공했다.
- NO_CHECKS: push/PR은 됐지만 remote checks가 없다. 성공으로 포장하지 않는다.
- NO_CHANGES: stage 대상 변경이 없어 commit하지 않았다.
- UNVERIFIED: 필요한 verification evidence가 없다. verification으로 돌린다.
- LOCAL_PREFLIGHT_FAILED: diff, required command, dirty ownership, 또는 finish preflight가 실패했다.
- SECRET_FILE_BLOCKED: credential 파일이 staged/tracked거나 ignore 확인 없이 포함될 위험이 있다.
- MAIN_PUSH_BLOCKED: main/base branch 직접 push 조건을 충족하지 못했다.
- PUSH_FAILED: local commit은 됐지만 push가 실패했다.
- PR_GATE_UNAVAILABLE: gh 인증·권한·네트워크 문제로 PR gate를 확인하지 못했다.
- REMOTE_CHECKS_FAILED: PR checks가 실패했다.

## 실패 보고 포맷

FINISH_FLOW: STATUS
phase: <local-preflight|stage|commit|push|pr-gate>
branch: <branch>
base: <base>
commit: <sha or none>
pr: <url or none>

blocked_reason:
- <무엇 때문에 멈췄는지>

evidence:
- git status --short --branch: <요약>
- git diff --cached --check: <exit code / 요약>
- secret guard: <PASS|FAIL|UNAVAILABLE> (<도구명>)
- repo commands: <name=PASS/FAIL/SKIP>
- pr checks: <PASS|FAIL|NO_CHECKS|SKIP>

blocked_files:
- <path> (<staged|tracked|untracked>, <ignored 확인 결과>)

required_action:
- <다음에 해야 할 1-3개 액션>

## 성공/부분 성공 보고 포맷

FINISH_FLOW: PASS / NO_CHECKS
branch: <branch>
commit: <short-sha> <subject>
push: origin/<branch>
pr: <url or none>

local-preflight:
- git status: <clean/dirty summary>
- diff --check: PASS
- secret guard: PASS (<도구명>)
- commands: <name=PASS/SKIP>

remote-gate:
- pr checks: <PASS|NO_CHECKS>
- checks: <check name list or none>

remaining:
- <untracked or skipped risk, 없으면 none>

## 주의사항

- NO_CHECKS는 좋은 상태가 아니라 remote CI evidence가 없는 상태다. 자동 merge나 완료 선언 근거로 쓰지 않는다.
- secret guard는 파일명과 diff 양쪽을 본다. .env가 ignored여도 staged면 실패다.
- fallback secret scan은 보조 수단이다. gitleaks/detect-secrets가 없으면 secret guard: LIMITED로 보고한다.
- git add .는 편하지만 위험하다. 기본은 explicit stage다.
- 사용자가 만든 dirty change를 되돌리지 않는다. 필요한 파일만 stage하고 나머지는 보고한다.
- PR checks는 push 이후 remote gate다. local-preflight 실패를 PR checks로 덮지 않는다.
