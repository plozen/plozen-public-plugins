---
name: finish-flow-harness
description: local verification evidence가 확보된 뒤 branch 종료를 local-preflight, commit, push, pr-gate 순서로 자동화해야 할 때 사용한다. main 직접 push 차단, secret 파일 차단, repo별 `.plostack/finish.toml` 검증, GitHub PR checks remote gate를 분리한다.
---

# Finish Flow Harness

## 역할

`finish-flow-harness`는 작업이 끝난 뒤 저장소 변경을 안전하게 닫는 종료 자동화 하네스다. 기존 `verification-branch-finish-hook-harness`가 "완료라고 말해도 되는 fresh verification evidence"를 판정하고, 이 스킬은 그 다음 단계인 `local-preflight -> commit -> push -> pr-gate`를 담당한다.

분리 원칙:

- `verification-branch-finish-hook-harness`: 마지막 변경 이후 fresh verification evidence를 확보하고 `PASS / FAIL / UNVERIFIED`를 판정한다.
- `finish-flow-harness`: verification이 통과했거나 사용자가 명시적으로 종료 자동화를 요청했을 때 commit, push, PR checks까지 닫는다.
- remote PR checks는 push 이후에만 확인한다. local 검증과 remote gate를 한 덩어리로 섞지 않는다.
- GitHub checks가 없으면 성공이 아니다. `NO_CHECKS`로 보고한다.

## 사용 시점

다음 조건 중 하나가 있으면 사용한다.

- 사용자가 `commit`, `push`, `PR`, `merge 전 체크`, `마무리`, `종료 루틴`, `push까지`를 요청했다.
- 표준/보호 작업에서 변경을 커밋하고 원격 브랜치나 PR로 넘겨야 한다.
- 완료 전 local verification은 끝났고, 남은 일이 git 종료 루틴이다.
- repo별 종료 정책(`.plostack/finish.toml`)을 적용해야 한다.

사용하지 않는 경우:

- 아직 구현/문서 수정이 끝나지 않았다.
- fresh verification evidence가 없고 사용자가 단순 완료 여부만 물었다. 이때는 먼저 `verification-branch-finish-hook-harness`를 적용한다.
- 리뷰 피드백 수용 여부 판단이 먼저다. 이때는 `review-reception-hook-harness`를 적용한다.
- 브랜치/worktree 생성 전 안전 점검만 필요하다. 이때는 `worktree-hook-harness`를 적용한다.

## 입력값

최소 입력:

- repo root 또는 현재 작업 디렉터리
- 종료 대상 branch
- base branch(default: `main`)
- commit message 또는 commit message를 만들 수 있는 변경 요약
- push/PR 필요 여부

선택 입력:

- `.plostack/finish.toml` 경로
- stage allowlist 또는 commit 대상 파일 목록
- PR title/body/base/draft 여부
- `allow_main_push` 명시 옵션
- remote checks timeout

`main` 직접 push는 기본 차단이다. 허용하려면 아래 둘 다 필요하다.

1. 사용자가 이번 턴에서 main 직접 push를 명시적으로 승인한다.
2. `.plostack/finish.toml` 또는 실행 옵션에 `allow_main_push = true`가 있다.

둘 중 하나라도 없으면 `MAIN_PUSH_BLOCKED`로 중단한다.

## 실행 흐름

```text
resolve-config
  -> local-preflight
  -> stage
  -> commit
  -> push
  -> pr-gate
  -> finish-report
```

### 1. resolve-config

1. repo root를 확인한다: `git rev-parse --show-toplevel`.
2. branch 상태를 확인한다: `git status --short --branch`, `git branch --show-current`.
3. remote와 upstream을 확인한다: `git remote -v`, `git rev-parse --abbrev-ref --symbolic-full-name @{u}`. upstream이 없어도 push 전까지는 실패가 아니다.
4. `.plostack/finish.toml`이 있으면 읽고 적용한다. 없으면 안전 기본값을 사용한다.
5. detached HEAD면 중단한다: `DETACHED_HEAD`.

안전 기본값:

```toml
version = 1
base_branch = "main"
allow_main_push = false
require_pr = true

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

commit/push 전에 로컬에서 반드시 확인한다.

필수 체크:

1. `git status --short --branch`
   - staged, unstaged, untracked를 분리해 요약한다.
   - 소유자가 불명확한 변경이나 사용자 변경이 섞이면 stage 전에 멈추고 범위를 좁힌다.
2. `git diff --check`와 `git diff --cached --check`
   - trailing whitespace, conflict marker, whitespace error를 막는다.
3. secret file guard
   - `.env`, `.env.*`, `*.pem`, `*.key`, `*.p12`, `*.pfx`, `id_rsa`, `id_ed25519`, `credentials.json`, `service-account*.json`, `kakao-config.local.js` 등 credential 파일이 staged/tracked/untracked 상태인지 확인한다.
   - secret 파일이 untracked면 `git check-ignore -v -- <path>`로 ignored 여부를 확인한다.
   - secret 파일이 staged거나 tracked면 `SECRET_FILE_BLOCKED`로 중단한다. `.env.example`, `.env.sample`, `*.example`, `*.template`은 허용 가능하지만 내용 스캔은 계속한다.
4. secret content scan
   - `gitleaks detect --redact --source .`가 있으면 우선 사용한다.
   - 없으면 `detect-secrets scan`을 사용한다.
   - 둘 다 없으면 fallback으로 staged diff와 working diff에서 `api[_-]?key`, `secret`, `token`, `password`, `private_key`, `AKIA[0-9A-Z]{16}` 같은 고위험 패턴을 redacted grep으로 확인한다.
   - secret 후보 문자열은 그대로 출력하지 않는다. 파일명, 라인, 패턴명만 보고한다.
5. repo별 commands
   - `.plostack/finish.toml`의 `[[local_preflight.commands]]`를 순서대로 실행한다.
   - 일반 예: lint, test, build, repo-specific check.
   - `required = true` 명령 실패는 push를 막는다.
6. staged/untracked summary
   - commit에 들어갈 파일과 들어가지 않는 파일을 따로 보여준다.
   - untracked가 남아 있으면 `UNTRACKED_REMAINING`으로 보고하되, allowlist 밖이면 commit하지 않는다.

### 3. stage

- 기본은 명시 파일만 stage한다: `git add <file...>`.
- `git add .`는 repo 설정에서 허용했고 local-preflight가 staged/untracked summary를 통과한 경우에만 사용한다.
- denylist 파일은 절대 stage하지 않는다.
- stage 후 `git diff --cached --name-status`로 commit 대상 파일을 다시 확인한다.
- staged diff가 비어 있으면 `NO_CHANGES`로 종료한다.

### 4. commit

- commit message는 사용자가 준 메시지를 우선한다.
- 없으면 conventional commit 형식으로 만든다. 예: `docs: add finish flow harness`.
- commit 후 `git rev-parse --short HEAD`와 `git status --short --branch`를 확인한다.
- commit 이후에도 의도하지 않은 unstaged/untracked가 남아 있으면 최종 보고에 남긴다. `require_clean_after_commit = true`면 `DIRTY_AFTER_COMMIT`으로 push 전 중단한다.

### 5. push

- 현재 branch가 `main`, `master`, base branch와 같으면 기본 차단한다.
- main 직접 push 허용 조건이 충족되지 않으면 `MAIN_PUSH_BLOCKED`로 중단한다.
- feature branch는 `git push -u origin HEAD`를 기본으로 사용한다.
- push 실패는 `PUSH_FAILED`로 보고하고 remote error를 요약한다.

### 6. pr-gate

push 이후 remote gate를 분리해서 실행한다.

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

## `.plostack/finish.toml` 예시

repo root에 둔다.

```toml
version = 1
base_branch = "main"
allow_main_push = false
require_pr = true
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

- `PASS`: local-preflight, commit, push, PR remote checks가 모두 성공했다.
- `NO_CHECKS`: push/PR은 됐지만 remote checks가 없다. 성공으로 포장하지 않는다.
- `NO_CHANGES`: stage 대상 변경이 없어 commit하지 않았다.
- `UNVERIFIED`: 필요한 local verification evidence가 없거나 실행할 수 없다.
- `LOCAL_PREFLIGHT_FAILED`: diff, lint/test/build/repo-specific check, dirty ownership 중 하나가 실패했다.
- `SECRET_FILE_BLOCKED`: credential 파일이 staged/tracked 상태거나 ignored 확인 없이 포함될 위험이 있다.
- `MAIN_PUSH_BLOCKED`: main/base branch 직접 push 조건을 충족하지 못했다.
- `PUSH_FAILED`: local commit은 됐지만 push가 실패했다.
- `PR_GATE_UNAVAILABLE`: `gh` 인증/권한/네트워크 문제로 PR gate를 확인하지 못했다.
- `REMOTE_CHECKS_FAILED`: PR checks가 실패했다.

## 실패 보고 포맷

```text
FINISH_FLOW: <STATUS>
phase: <local-preflight|stage|commit|push|pr-gate>
branch: <branch>
base: <base>
commit: <sha or none>
pr: <url or none>

blocked_reason:
- <무엇 때문에 멈췄는지>

evidence:
- git status --short --branch: <요약>
- git diff --check: <exit code / 요약>
- secret guard: <PASS|FAIL|UNAVAILABLE> (<도구명>)
- repo commands: <name=PASS/FAIL/SKIP>
- pr checks: <PASS|FAIL|NO_CHECKS|SKIP>

blocked_files:
- <path> (<staged|tracked|untracked>, <ignored 확인 결과>)

required_action:
- <다음에 해야 할 1-3개 액션>
```

## 성공/부분 성공 보고 포맷

```text
FINISH_FLOW: <PASS|NO_CHECKS>
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
```

## 주의사항

- `NO_CHECKS`는 좋은 상태가 아니라 remote CI evidence가 없는 상태다. 자동 merge나 완료 선언 근거로 쓰지 않는다.
- secret guard는 파일명과 diff 양쪽을 본다. `.env`가 ignored여도 staged면 실패다.
- fallback secret scan은 보조 수단이다. gitleaks/detect-secrets가 없으면 `secret guard: LIMITED`로 보고한다.
- `git add .`는 편하지만 위험하다. 기본은 explicit stage다.
- 사용자가 만든 dirty change를 되돌리지 않는다. 필요한 파일만 stage하고 나머지는 보고한다.
- PR checks는 push 이후 remote gate다. local-preflight 실패를 PR checks로 덮지 않는다.
