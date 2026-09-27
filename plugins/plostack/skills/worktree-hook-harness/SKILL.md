---
name: worktree-hook-harness
description: 저장소 변경이 있는 표준/보호 작업에서 branch, remote, dirty file 상태를 확인하거나 repo 내부 `.worktrees/` 기반 독립 worktree 생성과 cleanup 기준을 적용해야 할 때 사용한다.
---

# Worktree / Git Safety Hook Harness

저장소 변경이 있는 표준/보호 작업은 수정 전에 branch, remote, dirty file 상태를 확인한다.

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
- 작업 완료 후 branch push, PR/merge 또는 final push, gate 증거 확인이 끝나고 worktree가 clean하면 `git worktree remove <path>`와 `git worktree prune`으로 정리한다.
- cleanup 전에는 `git worktree list`, `git status --porcelain`, 그리고 merge 방식에 맞는 병합 증거(commit-preserving merge의 `git merge-base --is-ancestor HEAD <base-ref>` 또는 squash merge PR의 `MERGED`/`mergedAt`/`mergeCommit.oid`/base 일치)를 확인한다.
- `finish-flow-harness`의 `merge-gate`가 통과한 뒤에도 worktree 등록·dirty 여부·병합 증거를 다시 실행하고, 정확한 worktree 경로에만 non-force `git worktree remove`를 적용한다.
- dirty worktree, unmerged branch, 소유자가 불명확한 worktree는 삭제하지 않는다. 사용자가 명시적으로 폐기를 승인한 경우에만 `git worktree remove --force <path>`를 사용한다.
