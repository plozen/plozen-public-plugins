---
name: worktree-hook-harness
description: 저장소 변경이 있는 표준/보호 작업에서 branch, remote, dirty file 상태를 확인하거나 repo 내부 `.worktrees/` 기반 독립 worktree 생성과 cleanup 기준을 적용해야 할 때 사용한다.
---
# Worktree / Git Safety Hook Harness

이 스킬은 branch, remote, dirty file, worktree 생성·정리만 담당한다. 작업 분류, dispatch, 내용 검증, commit·push·PR 관문은 다른 canonical skill의 책임이다.

## Orca lifecycle reconciliation

- Orca가 실행 중인 세션에서는 먼저 `orca-ide status --json`, `orca-ide worktree current --json`, `orca-ide worktree list --json`, 필요 시 `orca-ide terminal list --worktree <full-id> --json`으로 Orca 등록 상태와 Git 상태를 대조한다.
- Orca에 등록된 child worktree는 raw `git worktree remove`만으로 정리하지 않는다. terminal을 먼저 닫거나 종료를 확인한 뒤, 목록에서 반환된 전체 `<repoId>::<worktreePath>`를 사용해 `orca-ide worktree rm`으로 Orca metadata와 checkout을 함께 정리한다.
- `isMainWorktree: true`인 active/main checkout은 완료 cleanup 대상 child로 간주하지 않는다. 저장소 checkout과 현재 agent terminal을 끊을 수 있으므로 제거하지 말고, 필요하면 `worktree set --workspace-status`와 짧은 comment로 상태만 갱신하거나 사용자에게 범위를 확인한다.
- 브라우저/UI 검증을 수행한 작업은 종료 전에 browser engine(Orca 내장 브라우저 또는 외부 fallback)과 fresh evidence를 worktree comment/최종 보고에 남긴다.

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

Orca 등록 worktree의 cleanup은 위 Orca lifecycle reconciliation을 먼저 적용한 뒤 raw Git 정리를 수행한다.
