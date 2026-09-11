---
name: worktree-hook-harness
description: 저장소 변경이 있는 표준/보호 작업에서 branch, remote, dirty file 상태를 확인하거나 repo 내부 `.worktrees/` 기반 독립 worktree 생성과 cleanup 기준을 적용해야 할 때 사용한다.
---
# Worktree / Git Safety Hook Harness

이 스킬은 branch, remote, dirty file, worktree 생성·정리만 담당한다. 작업 분류, dispatch, 내용 검증, commit·push·PR 관문은 다른 canonical skill의 책임이다.

## 수정 전 preflight

- branch, remote, worktree 목록, dirty 상태를 확인한다. detached HEAD와 base branch 직접 수정은 중단한다.
- 보호 작업, 충돌 위험, PR 대상 작업은 task branch를 가진 독립 worktree에서 진행한다.
- 경로는 repo 내부 .worktrees/<task-slug>로 두고, 가능한 경우 다음 형식을 사용한다: git worktree add <repo-root>/.worktrees/<task-slug> -b <task-branch> <base-branch>
- repo root의 .gitignore에는 .worktrees/를 추가해 worktree 파일이 저장소에 포함되지 않게 한다.
- 소유자가 불명확한 dirty worktree에서는 시작하지 않는다. 사용자가 만든 변경은 되돌리거나 흡수하지 않고, 소유 파일만 명시적으로 stage한다.

## 정리

branch push, PR/merge 또는 final push와 필요한 gate 증거가 확인되고 worktree가 clean할 때만 정리한다. 정리 전 다음을 확인한다.

- git worktree list
- git status --porcelain
- git merge-base --is-ancestor HEAD <base-ref>

확인 후 git worktree remove <path>와 git worktree prune을 사용한다. dirty, unmerged, 소유자 불명확 상태에서는 삭제하지 않으며, --force는 사용자가 폐기를 명시적으로 승인한 경우에만 허용한다.
