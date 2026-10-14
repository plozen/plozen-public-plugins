---
name: finish-flow-harness
description: local verification evidence가 확보된 뒤 branch 종료를 local-preflight, commit, push, pr-gate, merge, worktree-cleanup 순서로 자동화해야 할 때 사용한다. main 직접 push 차단, secret 파일 차단, repo별 `.plostack/finish.toml` 검증, GitHub PR checks remote gate를 분리한다.
---
# Finish Flow Harness

## 역할

`finish-flow-harness`는 작업이 끝난 뒤 저장소 변경을 안전하게 닫는 종료 자동화 하네스다. 기존 `verification-branch-finish-hook-harness`가 "완료라고 말해도 되는 fresh verification evidence"를 판정하고, 이 스킬은 그 다음 단계인 `local-preflight -> commit -> push -> pr-gate -> merge -> worktree-cleanup`을 담당한다.

분리 원칙:

- `verification-branch-finish-hook-harness`: 마지막 변경 이후 fresh verification evidence를 확보하고 `PASS / FAIL / UNVERIFIED`를 판정한다.
- `finish-flow-harness`: verification이 통과했거나 사용자가 명시적으로 종료 자동화를 요청했을 때 commit, push, PR checks, main 병합, 병합된 branch/worktree 정리까지 한 종료 실행에서 닫는다.
- remote PR checks는 push 이후에만 확인한다. local 검증과 remote gate를 한 덩어리로 섞지 않는다.
- GitHub checks가 없으면 성공이 아니다. `NO_CHECKS`로 보고한다.

## 사용 시점

다음 조건 중 하나가 있으면 사용한다.

- 사용자가 `commit`, `push`, `PR`, `merge 전 체크`, `마무리`, `종료 루틴`, `push까지`를 요청했다.
- 사용자가 `main 병합`, `merge`, `worktree 정리`를 요청했다.
- 표준/보호 작업에서 변경을 커밋하고 원격 브랜치나 PR로 넘겨야 한다.
- 완료 전 local verification은 끝났고, 남은 일이 git 종료 루틴이다.
- repo별 종료 정책(`.plostack/finish.toml`)을 적용해야 한다.

다음이면 먼저 verification-branch-finish-hook-harness로 보낸다.

- 아직 구현/문서 수정이 끝나지 않았다.
- fresh verification evidence가 없고 사용자가 단순 완료 여부만 물었다. 이때는 먼저 `verification-branch-finish-hook-harness`를 적용한다.
- 브랜치/worktree 생성 전 안전 점검만 필요하다. 이때는 `worktree-hook-harness`를 적용한다.

## 입력과 전제

- repo root, 대상 branch, base branch, commit message
- push/PR 필요 여부와 .plostack/finish.toml
- 현재 변경에 대한 VERIFICATION_GATE: PASS 또는 사용자가 위험을 알고 승인한 PARTIAL

검증 결과가 없으면 이 문서에서 테스트를 다시 설계하지 말고 verification으로 돌린다. push와 PR은 사용자 요청 또는 저장소 정책이 있을 때만 진행한다.

선택 입력:

- `.plostack/finish.toml` 경로
- stage allowlist 또는 commit 대상 파일 목록
- PR title/body/base/draft 여부
- `allow_main_push` 명시 옵션
- `merge_after_checks`, `cleanup_remote_branch`, `cleanup_local_branch`, `cleanup_worktree` 여부
- remote checks timeout

`main` 직접 push는 기본 차단이다. 허용하려면 아래 둘 다 필요하다.

1. 사용자가 이번 턴에서 main 직접 push를 명시적으로 승인한다.
2. `.plostack/finish.toml` 또는 실행 옵션에 `allow_main_push = true`가 있다.

둘 중 하나라도 없으면 `MAIN_PUSH_BLOCKED`로 중단한다.

## Same-run branch closeout

- task branch/worktree를 만든 작업은 최종 보고 전에 `branch_disposition`을 `MERGED_CLEANED`, `PRESERVED` 또는 `BLOCKED`로 명시한다.
- 사용자가 main 병합·push를 요청하면 PR 생성·push만으로 종료하지 않는다. merge gate를 통과한 뒤 같은 실행에서 `worktree-cleanup`까지 진행하고, 원격 branch·로컬 branch·task worktree의 제거를 확인한다.
- merge 후 cleanup이 기본 설정인데도 생략되거나 막히면 `PASS` 또는 `NO_CHECKS` 완료로 보고하지 않는다. `WORKTREE_CLEANUP_BLOCKED`로 원인과 다음 액션을 남긴다.
- `PRESERVED`는 병합·정리를 하지 않기로 한 명시적 사유가 있을 때만 허용한다. 이유, 소유자, 후속 액션을 기록한다. 관련 없는 task branch를 자동 병합·삭제하지 않는다.

## 실행 흐름

resolve-config
  -> local-preflight
  -> stage
  -> commit
  -> push
  -> pr-gate
  -> merge-gate (요청 시)
  -> worktree-cleanup (merge 확인 시)
  -> finish-report

### 1. resolve-config

1. repo root, branch, status, remote, upstream을 확인한다. upstream이 없어도 push 전까지는 실패가 아니다.
2. .plostack/finish.toml이 있으면 적용하고, 없으면 templates/finish.toml의 안전 기본값을 따른다.
3. detached HEAD면 DETACHED_HEAD로 중단한다.
4. 기본값은 base_branch = main, allow_main_push = false, require_pr = true, stage_strategy = explicit, secret_scan = auto, merge_after_checks = false, cleanup_remote_branch = true, cleanup_local_branch = true, cleanup_worktree = true다.

## finish.toml contract

```toml
version = 1
base_branch = "main"
allow_main_push = false
require_pr = true
merge_after_checks = false
cleanup_worktree = true
cleanup_local_branch = true
cleanup_remote_branch = true

[local_preflight]
diff_check = true
secret_scan = "auto"
require_clean_after_commit = true

[pr]
checks_watch = true
checks_timeout_minutes = 30
no_checks_status = "NO_CHECKS"
```

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

1. PR 확인 또는 생성
   - 기존 PR: `gh pr view --json number,url,headRefName,baseRefName,state,isDraft`
   - PR이 없고 사용자가 PR 생성을 요청했거나 `require_pr = true`면 `gh pr create`를 실행한다.
   - `gh` 인증이 없으면 PR gate는 `PR_GATE_UNAVAILABLE`로 보고한다.
2. checks watch
   - `gh pr checks --watch`를 사용한다.
   - timeout이 필요하면 wrapper timeout을 적용한다.
   - checks가 실패하면 `REMOTE_CHECKS_FAILED`.
   - checks가 없으면 `NO_CHECKS`. 이것은 PASS가 아니다.
3. checks 결과 보고
   - check name, state/conclusion, URL 또는 run id를 요약한다.
   - checks가 없을 때는 `NO_CHECKS`와 함께 "remote CI evidence 없음"을 명시한다.

### 7. merge-gate

사용자가 `main` 병합을 요청했거나 설정에서 `merge_after_checks = true`인 경우에만 실행한다.

1. PR의 base가 요청된 `main`인지, head branch와 commit SHA가 현재 작업과 일치하는지 확인한다.
2. 필수 remote checks가 `PASS`인지 확인한다. `NO_CHECKS`는 자동 병합하지 않으며, 사용자가 checks 부재를 명시적으로 승인한 경우에만 `gh pr merge`를 실행한다.
3. PR을 병합한다. 기본은 `gh pr merge <number> --squash`이며 저장소 정책이 정한 merge 방식이 있으면 그 방식을 따른다. 원격 feature branch 삭제는 다음 `worktree-cleanup` 단계가 head SHA를 확인한 뒤 처리한다.
4. `gh pr view --json state,mergedAt,mergeCommit,baseRefName,headRefName`와 `git fetch origin <base>`로 병합 사실을 확인한다.
5. merge commit 방식이 commit-preserving이면 `git merge-base --is-ancestor <head-sha> origin/<base>`를 확인한다. 기본 squash merge처럼 원래 head SHA가 보존되지 않는 방식이면 이 검사를 요구하지 말고, `state=MERGED`, `mergedAt`, `mergeCommit.oid`, base 일치를 함께 확인한다. squash merge에 대해 원래 head SHA가 `origin/<base>`의 조상이 아니라는 이유만으로 실패 처리하지 않는다.
6. 사용자가 merge를 요청한 작업은 여기서 종료 보고하지 않고 바로 `worktree-cleanup` 단계로 이어간다.

병합 대상이 이미 닫혔거나 SHA/base가 다르면 `MERGE_BLOCKED`로 중단하고, 다른 PR이나 작업을 임의로 병합하지 않는다.

### 8. worktree-cleanup

`merge-gate`가 통과하면 기본적으로 실행한다. cleanup 플래그는 각 원격 branch, 로컬 branch, worktree에 개별 적용하며 기본값은 모두 `true`다. 세 항목 모두 명시적으로 꺼진 경우에만 단계를 생략한다. 현재 셸이 삭제 대상 worktree 안에 있으면 먼저 repo root 또는 별도 worktree로 이동한다.

1. 삭제 대상을 절대 경로로 확정하고 `git worktree list --porcelain`로 등록 상태를 확인한다.
2. PR의 `state=MERGED`, base, `headRefName`, `headRefOid`, `mergeCommit.oid`를 확인하고 merge commit이 `origin/<base>`에 포함됐는지 확인한다. squash/rebase merge는 원래 feature HEAD의 ancestor 여부를 요구하지 않는다.
3. 로컬 feature HEAD와 원격 feature ref(존재할 경우)가 PR `headRefOid`와 일치하는지 확인한다. SHA가 다르거나 대상 worktree의 `git status --porcelain`가 비어 있지 않으면 cleanup을 중단한다.
4. Orca 등록 worktree에 terminal이 있으면 `worktree-hook-harness` 절차대로 정확한 worktree의 terminal을 닫고 모든 PTY 종료를 확인한다. 종료 후 remote/local SHA와 worktree clean 상태를 다시 확인한다.
5. `cleanup_remote_branch = true`이고 원격 feature ref가 남아 있으면 PR `headRefOid`와 일치할 때 `git push origin --delete <branch>`로 제거한다. GitHub가 이미 삭제했으면 건너뛴다. SHA가 다르거나 보호 정책이 막으면 worktree와 local branch를 보존하고 보고한다.
6. `cleanup_worktree = true`일 때, Orca 등록 worktree는 전체 id로 `worktree-hook-harness`의 Orca 정리 절차를 적용한다. 일반 Git worktree는 정확한 경로에 `git worktree remove <exact-path>`를 force 없이 실행한다. 그 다음 `git worktree prune`을 실행한다.
7. `cleanup_local_branch = true`이면 worktree 제거 후 local feature branch를 삭제한다. 먼저 `git branch -d <branch>`를 사용한다. squash/rebase로 거부되면 병합 증거와 local HEAD의 PR `headRefOid` 일치가 확인된 경우에만 `git branch -D <branch>`를 허용한다.
8. `git worktree list --porcelain`, 로컬·원격 branch 존재 여부를 다시 확인하고 cleanup 결과를 보고한다.

`cleanup_remote_branch`, `cleanup_local_branch`, `cleanup_worktree`가 기본 `true`인 병합 작업은 세 위치 모두 제거가 확인되어야 `MERGED_CLEANED`다. 한 곳이라도 남았거나 안전 조건 때문에 정리하지 못하면 `WORKTREE_CLEANUP_BLOCKED`로 종료하고 `PASS`/`NO_CHECKS`로 포장하지 않는다. 관련 없는 branch와 worktree는 조회 증거를 남기더라도 정리 대상에 추가하지 않는다.

dirty, unmerged, SHA 불일치, 경로 불일치, 진행 중인 agent/terminal, 현재 main worktree 삭제 시도는 `WORKTREE_CLEANUP_BLOCKED`로 중단한다. 확인되지 않은 파일이나 세션을 force로 제거하지 않는다. Orca의 `worktree rm --force`는 위 병합·cleanliness·terminal 확인을 모두 통과한 뒤 정확한 full id에만 사용한다.

## `.plostack/finish.toml` 예시

repo root에 둔다.

```toml
version = 1
base_branch = "main"
allow_main_push = false
require_pr = true
merge_after_checks = false
cleanup_remote_branch = true
cleanup_local_branch = true
cleanup_worktree = true
stage_strategy = "explicit" # explicit | all_safe

[local_preflight]
diff_check = true
secret_scan = "auto" # auto | gitleaks | detect-secrets | fallback | off
require_clean_after_commit = false

secret_file_patterns = [
  ".env",
  ".env.*",
  "*.pem",
  "*.key",
  "*.p12",
  "*.pfx",
  "id_rsa",
  "id_ed25519",
  "credentials.json",
  "service-account*.json",
  "kakao-config.local.js",
]

allowed_secret_templates = [
  ".env.example",
  ".env.sample",
  "*.example",
  "*.template",
]

stage_allow = [
  "plugins/plostack/skills/**",
  "plugins/plostack/README.md",
  "README.md",
]

stage_deny = [
  ".env*",
  "*.pem",
  "*.key",
  "credentials*.json",
  "service-account*.json",
  "kakao-config.local.js",
]

[[local_preflight.commands]]
name = "skill-frontmatter"
command = "python3 scripts/validate-skills.py plugins/plostack/skills"
required = true

[[local_preflight.commands]]
name = "lint"
command = "pnpm lint"
required = false

[[local_preflight.commands]]
name = "test"
command = "pnpm test"
required = false

[[local_preflight.commands]]
name = "build"
command = "pnpm build"
required = false

[pr]
base = "main"
draft = false
checks_watch = true
checks_timeout_minutes = 30
no_checks_status = "NO_CHECKS"
```

## 판정 상태

- `PASS`: 요청된 local-preflight, commit, push, PR remote checks, merge, worktree cleanup이 모두 성공했다.
- `NO_CHECKS`: push/PR은 됐지만 remote checks가 없다. 성공으로 포장하지 않는다.
- `NO_CHANGES`: stage 대상 변경이 없어 commit하지 않았다.
- `UNVERIFIED`: 필요한 local verification evidence가 없거나 실행할 수 없다.
- `LOCAL_PREFLIGHT_FAILED`: diff, lint/test/build/repo-specific check, dirty ownership 중 하나가 실패했다.
- `SECRET_FILE_BLOCKED`: credential 파일이 staged/tracked 상태거나 ignored 확인 없이 포함될 위험이 있다.
- `MAIN_PUSH_BLOCKED`: main/base branch 직접 push 조건을 충족하지 못했다.
- `PUSH_FAILED`: local commit은 됐지만 push가 실패했다.
- `PR_GATE_UNAVAILABLE`: `gh` 인증/권한/네트워크 문제로 PR gate를 확인하지 못했다.
- `REMOTE_CHECKS_FAILED`: PR checks가 실패했다.
- `MERGE_BLOCKED`: 대상 PR, base, head SHA 또는 remote gate가 병합 조건을 충족하지 못했다.
- `WORKTREE_CLEANUP_BLOCKED`: dirty/unmerged/경로 불일치로 worktree를 안전하게 삭제하지 못했다.

## 실패 보고 포맷

```text
FINISH_FLOW: <STATUS>
phase: <local-preflight|stage|commit|push|pr-gate|merge-gate|worktree-cleanup>
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
branch_disposition: <MERGED_CLEANED|PRESERVED(reason, owner, next action)|BLOCKED(reason)>
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

merge:
- state: <MERGED|BLOCKED|SKIP>
- base/head: <refs and SHAs>

cleanup:
- remote branch: <DELETED|KEPT|SKIP>
- worktree: <REMOVED|BLOCKED|SKIP>
- local branch: <DELETED|KEPT|SKIP>

remaining:
- <untracked or skipped risk, 없으면 none>

## 주의사항

- NO_CHECKS는 좋은 상태가 아니라 remote CI evidence가 없는 상태다. 자동 merge나 완료 선언 근거로 쓰지 않는다.
- merge 요청 작업은 cleanup 단계까지 같은 종료 흐름에서 처리한다. cleanup이 기본값인데 남은 항목이 있으면 `MERGED_CLEANED` 또는 성공 상태로 보고하지 않는다.
- secret guard는 파일명과 diff 양쪽을 본다. .env가 ignored여도 staged면 실패다.
- fallback secret scan은 보조 수단이다. gitleaks/detect-secrets가 없으면 secret guard: LIMITED로 보고한다.
- git add .는 편하지만 위험하다. 기본은 explicit stage다.
- 사용자가 만든 dirty change를 되돌리지 않는다. 필요한 파일만 stage하고 나머지는 보고한다.
- PR checks는 push 이후 remote gate다. local-preflight 실패를 PR checks로 덮지 않는다.
