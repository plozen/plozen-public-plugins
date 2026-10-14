---
name: worktree-hook-harness
description: 저장소 변경이 있는 표준/보호 작업에서 branch, remote, dirty file 상태를 확인하거나 repo 내부 `.worktrees/` 기반 독립 worktree 생성과 cleanup 기준을 적용해야 할 때 사용한다.
---
# Worktree / Git Safety Hook Harness

이 스킬은 branch, remote, dirty file, worktree 생성·정리만 담당한다. 작업 분류, dispatch, 내용 검증, commit·push·PR 관문은 다른 canonical skill의 책임이다.

## Orca lifecycle reconciliation

- Orca가 실행 중인 세션에서는 먼저 `orca-ide status --json`, `orca-ide worktree current --json`, `orca-ide worktree list --json`, 필요 시 `orca-ide terminal list --worktree <full-id> --json`으로 Orca 등록 상태와 Git 상태를 대조한다.
- Orca에 등록된 child worktree는 raw `git worktree remove`만으로 정리하지 않는다. terminal을 먼저 닫거나 종료를 확인한 뒤, 목록에서 반환된 전체 `<repoId>::<worktreePath>`를 사용해 `orca-ide worktree rm`으로 Orca metadata와 checkout을 함께 정리한다.
- `isMainWorktree: true`인 active/main checkout은 완료 cleanup 대상 child로 간주하지 않는다. 저장소 checkout과 현재 agent terminal을 끊을 수 있으므로 제거하지 말고, 필요하면 `worktree set --workspace-status`와 짧은 comment로 상태만 갱신한다.
- 브라우저/UI 검증을 수행한 작업은 종료 전에 browser engine과 fresh evidence를 worktree comment 또는 최종 보고에 남긴다.

- 보호 작업, 충돌 위험이 있는 작업, PR 대상 작업은 task branch를 가진 독립 worktree에서 진행한다.
- agent/task worktree는 해당 저장소 폴더 안의 `.worktrees/` 아래에 만든다.
- worktree 경로는 `<repo-root>/.worktrees/<task-slug>` 형식으로 둔다. 예: `/mnt/data/workspace/plozen-console/.worktrees/console-live-tab`.
- repo root의 `.gitignore`에는 `.worktrees/`를 추가해 GitHub 저장소에 worktree 파일이 push되지 않게 한다.
- worktree는 가능한 한 새 task branch에 붙여 만든다: `git worktree add <repo-root>/.worktrees/<task-slug> -b <task-branch> <base-branch>`.
- detached HEAD, base branch 직접 수정, 소유자가 불명확한 dirty worktree에서는 구현을 시작하지 않는다.
- 사용자가 만든 dirty change는 되돌리지 않고, 의도한 파일만 commit에 포함한다.
## 병합 후 자동 정리

- PR이 base branch에 병합된 것이 확인되면 task의 원격 feature branch, 로컬 feature branch, task worktree를 기본적으로 정리한다. 별도 정리 요청을 기다리지 않는다. `finish-flow-harness`의 `cleanup_remote_branch`, `cleanup_local_branch`, `cleanup_worktree` 기본값은 모두 `true`다.
- 병합 전에 branch/worktree를 삭제하지 않는다. 병합 증거, 대상 SHA, worktree 소유권 중 하나라도 확인할 수 없으면 그대로 보존하고 `WORKTREE_CLEANUP_BLOCKED` 사유를 보고한다.

삭제 전 확인:

1. PR이 `state=MERGED`이고 `baseRefName`이 의도한 base branch인지 확인한다. `headRefName`, `headRefOid`, `mergeCommit.oid`, `mergedAt`도 기록한다.
2. `mergeCommit.oid`가 `origin/<base>`에 포함됐는지 확인한다. squash/rebase merge는 원래 feature HEAD가 base의 조상인지 검사하지 않는다.
3. 로컬 feature branch HEAD와 원격 feature ref(존재할 경우)가 PR `headRefOid`와 일치하는지 확인한다. SHA가 다르면 병합 이후 추가 commit이 있으므로 삭제하지 않는다.
4. `git worktree list --porcelain`에서 정확한 대상 경로와 branch를 확인하고, 대상 worktree의 `git status --porcelain`가 비어 있는지 확인한다. main/active worktree는 삭제하지 않는다.
5. Orca에 등록된 worktree라면 full id로 terminal 목록을 확인한다. 병합과 readback이 끝난 뒤 남은 terminal은 정확한 worktree에 한해 `orca-ide terminal close --worktree <full-id> --all --json`으로 닫고, 모든 PTY가 종료됐다는 결과를 확인한다. close가 실패하거나 종료를 검증할 수 없으면 정리를 멈춘다.

정리 순서:

1. `cleanup_remote_branch = true`이고 원격 feature ref가 남아 있으면 PR `headRefOid`와 일치할 때 `git push origin --delete <branch>`로 제거한다. GitHub가 이미 삭제했으면 건너뛴다. SHA가 다르거나 보호 정책이 막으면 worktree와 local branch를 보존하고 보고한다.
2. Orca 등록 worktree는 terminal 종료 후 목록에서 받은 전체 id로 `orca-ide worktree rm --worktree <full-id> --force --json`을 실행한다. 일반 Git worktree는 정확한 경로에 `git worktree remove <path>`를 force 없이 실행한다.
3. worktree 제거 후 local feature branch를 삭제한다. 먼저 `git branch -d <branch>`를 사용한다. squash/rebase로 인해 거부되면, PR 병합 증거와 local HEAD의 `headRefOid` 일치, clean worktree를 다시 확인한 경우에만 `git branch -D <branch>`를 사용한다.
4. `git worktree prune` 후 worktree 목록, 로컬 branch 목록, 원격 branch 존재 여부를 다시 확인한다.

Orca terminal을 닫은 뒤에는 원격 feature ref와 worktree 상태를 한 번 더 읽어 SHA 일치와 clean 상태를 확인한 후 삭제를 진행한다.

- PR 없이 base에 통합하는 final-push 작업은 기존 `git merge-base --is-ancestor HEAD <base-ref>` 증거를 사용한다.
- dirty worktree, 진행 중이거나 종료가 확인되지 않은 agent/terminal, 추가 commit이 있는 branch, 소유자가 불명확한 경로는 강제로 삭제하지 않는다. 사용자가 변경 폐기를 명시적으로 승인한 경우에만 예외를 적용한다.
