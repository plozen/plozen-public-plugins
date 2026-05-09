---
name: orchestration-harness-skill
description: 저장소 변경, 새 기능, 동작 변경, 버그 수정, 테스트 실패, 다단계 작업, 작업 범위 분류, 스킬 라우팅, planning, worktree, 허용된 경우 background subagent 병렬 디스패치, debugging/TDD, 리뷰/QA/security gate, verification, PR/merge/cleanup 통합이 필요할 때 사용한다. 사용자가 Aegis를 명시하지 않아도 경량 답변을 넘어서면 먼저 적용 범위를 분류한다.
---

# Aegis 오케스트레이션 하네스

## 적용 범위

사용자가 `Aegis`를 명시하지 않아도, 작업이 저장소 변경/동작 변경/다단계 실행/검증/위임을 포함하면 먼저 이 하네스로 경량/표준/보호 작업을 분류한다. Aegis 작업 흐름은 모든 작업에 강제하지 않고 필요한 만큼만 적용한다.

- 경량 작업: 질문 답변, 읽기 전용 조사, 단일 명령 실행, 상태 확인, 작은 문구 수정은 현재 세션에서 바로 처리한다. Brainstorming, 작업 트리, 위임, PR을 강제하지 않는다.
- 표준 작업: 일반 기능 수정, 버그 수정, 테스트 추가, 문서 수정처럼 저장소 변경이 있지만 위험이 낮은 작업은 필요한 검증까지만 수행한다. 작업 트리, 커밋, 푸시, PR은 사용자 요청이나 저장소 정책이 있을 때 사용한다.
- 보호 작업: 새 기능, 동작 변경, 대규모 리팩터링, 릴리스, 보안/인증/데이터/마이그레이션, 여러 하위 시스템이 섞인 작업은 아래 작업 흐름을 적용한다.

사용자가 명시적으로 `Aegis로 진행`, `PR까지`, `팀장 모드`, `서브에이전트로 병렬 진행`처럼 요청하면 한 단계 높은 흐름으로 올릴 수 있다. 단, Aegis 명시는 필수 트리거가 아니며 작업 성격이 조건에 맞으면 자동 적용한다.

## 작업 흐름

보호 작업의 기본 흐름은 아래와 같다.

```text
Brainstorming -> Planning -> 라우팅 -> 작업 트리 -> 위임 -> 구현/디버깅 -> 리뷰 -> QA/Security -> 검증 -> 커밋/푸시/PR -> 팀장 확인 -> 병합/정리 -> 보고
```

팀장은 실행자가 아니라 라우터, 검증자, 통합자다. 실행은 가능한 역할 에이전트나 독립 실행 컨텍스트가 맡는다. 최종 저장소 통합, 병합, 최종 푸시, 깨끗한 작업 트리 정리는 팀장이 책임진다.

단계별 hook 연결:

- Brainstorming: 새 기능, 디자인, 동작 변경, 불명확한 요구사항이면 [Skill Routing Hook](#skill-routing-hook)을 거쳐 `brainstorming-skill`을 먼저 사용한다.
- Planning: Brainstorming 승인이 끝난 보호 작업은 [Planning Hook](#planning-hook)을 적용한다.
- 작업 트리: 저장소 수정 전에는 [Worktree / Git Safety Hook](#worktree--git-safety-hook)을 적용한다.
- 위임: 독립 실행 단위가 2개 이상이면 [Background Dispatch Hook](#background-dispatch-hook)을 적용해 작업을 분해하고, 상위 지침과 런타임이 허용할 때만 실제 하위 에이전트로 위임한다.
- 구현/디버깅: 버그, 테스트 실패, 동작 변경은 [Debugging Hook](#debugging-hook)과 [TDD / Behavior Change Hook](#tdd--behavior-change-hook)을 적용한다.
- 리뷰: 피드백 처리에는 [Review Reception Hook](#review-reception-hook)을 적용한다.
- QA/Security: 변경 성격에 맞춰 reviewer, qa, breaker, security gate를 적용한다.
- 검증/완료: 완료, fixed, ready, merge, cleanup 전에는 [Verification / Branch Finish Hook](#verification--branch-finish-hook)을 적용한다.

## 역할 위임 경계

역할 위임은 보호 작업에서 우선 고려한다. 경량 작업에는 강제하지 않고, 표준 작업은 전문 검증이나 병렬 실행이 실제로 도움이 될 때만 위임한다. 사용자 요청, 상위 지침, 도구 정책, 실행 환경이 위임을 허용하지 않으면 작업을 분해한 뒤 로컬 실행 계획으로 전환하고 생략 이유를 남긴다.

팀장이 직접 맡는 일:

- 질문 답변, 상태 확인, 파일 읽기, 범위 분류, 라우팅
- 작업 트리/브랜치/커밋/푸시/PR/병합/정리 같은 통합 작업
- 위임 결과 검증, gate 판정, 최종 보고

역할별 우선 호출 기준:

| 역할 | 호출 기준 |
|---|---|
| `developer-senior` | 새 기능, 복잡한 구현, 아키텍처, 다중 파일 리팩터링, 어려운 디버깅 |
| `developer-mid` | 버그 수정, 단순 CRUD, 집중 테스트 추가, 단일/소규모 파일 변경 |
| `developer-junior` | 문구, 오타, 주석, import 정리, 포맷팅, 상수 변경처럼 로직 없는 수정 |
| `designer` | 앱 UI, 랜딩페이지, 대시보드, 디자인 시스템, 시각 구현 |
| `design-reviewer` | 디자인 일관성, 접근성, 타이포그래피, 간격, 색상 감사 |
| `reviewer` | 코드, schema, API, LLM trust boundary, 구조 위험 리뷰 |
| `qa` | 테스트 실행, 회귀 확인, 재현 절차, 검증 리포트 |
| `breaker` | 브라우저 흐름, 사용자 관점 edge case, 비직관적 UX 검증 |
| `security` | secrets, auth, infra, dependency, supply-chain 위험 |
| `documenter` | 문서, spec, README, 릴리스 노트, Markdown 변환 |
| `researcher` | 외부/기술 조사, 라이브러리/API 확인, 출처 기반 비교 |

하위 에이전트 사용은 현재 실행 환경과 상위 지침이 명시적으로 허용할 때만 수행한다. 필요한 역할을 실행할 수 없으면 로컬 검토/검증으로 대체하거나 멈춰야 할 위험을 보고한다.

## 완료 기준

보호 작업은 필요한 gate가 통과하거나, 생략 이유와 남은 위험이 기록되어야 완료할 수 있다. 완료 선언 전에는 [Verification / Branch Finish Hook](#verification--branch-finish-hook)을 적용한다.

- 코드, schema, API, auth, data 변경: `reviewer` gate
- 동작 변경, 테스트 추가, 회귀 위험: `qa` gate
- UI 또는 browser-facing 변경: `breaker` 또는 `qa` browser gate
- secrets, auth, infra, dependency 변경: `security` gate
- `reviewer` BLOCK, `qa` FAIL, `security` Critical, 핵심 사용자 흐름 실패는 완료를 막는다.
- gate를 생략하면 최종 보고에 생략 이유와 남은 위험을 남긴다.

# Hooks

## Skill Routing Hook

작업 시작 전에 관련 Aegis skill이 있는지 판단한다. 사용자가 Aegis를 말하지 않아도 경량 답변을 넘어서면 먼저 이 하네스로 범위를 분류한다.

- 새 기능, 디자인, 동작 변경, 불명확한 요구사항은 `brainstorming-skill`을 먼저 사용한다.
- 저장소 변경, 버그 수정, 테스트 실패, 다단계 실행, 검증/위임/리뷰/QA/PR이 필요한 작업은 이 orchestration harness로 경량/표준/보호를 먼저 분류한다.
- 구현, PR, 리뷰, QA, 병렬 위임이 필요하면 이 orchestration harness를 적용한다.
- 버그, 테스트 실패, 예상 밖 동작은 수정 전에 Debugging Hook을 적용한다.
- 완료, 성공, 통과, fixed를 말하기 전에는 Verification Hook을 적용한다.
- 경량 작업에는 skill 흐름을 강제하지 않는다. 관련 skill을 생략하면 이유와 남은 위험을 짧게 남긴다.

## Planning Hook

Brainstorming 승인이 끝난 보호 작업은 구현 전에 실행 계획을 만든다.

- 작업을 작고 검증 가능한 task로 나눈다.
- 각 task에는 수정 대상 파일, owner, 금지 범위, 검증 명령을 둔다.
- 여러 하위 시스템이 섞이면 하위 프로젝트나 독립 task group으로 나눈다.
- 파일 ownership을 나눠 subagent 간 write conflict를 막는다.
- 계획이 불명확하면 구현으로 넘어가지 않고 사용자 확인을 받는다.

## Background Dispatch Hook

보호 작업이나 여러 실행 단위가 있는 표준 작업은 팀장이 직접 구현하기 전에 작업을 분해한다. background subagent 또는 동등한 실행 컨텍스트 위임은 사용자 요청, 상위 지침, 도구 정책, 현재 런타임이 허용할 때만 수행한다.

- 팀장은 설계, 범위 분류, 작업 분해, 역할 선택, 위임, 통합, gate 판정을 맡는다.
- 독립 실행 단위가 2개 이상이면 병렬 디스패치 계획을 먼저 제시한다. 실제 subagent 실행은 사용자가 `병렬`, `서브에이전트`, `디스패치`, `위임`을 명시하고, 상위 지침과 현재 런타임이 허용할 때만 수행한다.
- 구현, 문서 작성, 조사, QA, 리뷰, 보안 점검, 브라우저 검증은 허용된 경우 적절한 역할 에이전트에 디스패치한다.
- 독립적인 sidecar 작업은 위임이 허용되면 병렬로 디스패치하고, 팀장은 기다리는 동안 다른 설계/통합 작업을 계속한다.
- 즉시 다음 판단이 막히는 critical path 작업만 직접 처리하거나 foreground로 기다린다.
- 각 하위 에이전트에는 명확한 owner, 작업 범위, 파일 소유권, 산출물 형식을 준다.
- 같은 파일을 여러 하위 에이전트가 동시에 수정하지 않도록 write scope를 분리한다.
- 하위 에이전트 결과가 돌아오면 팀장은 재작업하지 않고 검토, 통합, 보완, gate 판정을 수행한다.
- 하위 에이전트 실행이 불가능하면 로컬 실행/검증으로 대체할지 판단하고, 생략 이유와 남은 위험을 보고한다.

## Debugging Hook

버그, 테스트 실패, 빌드 실패, 예상 밖 동작은 수정 전에 원인을 좁힌다.

- 먼저 재현 절차와 관찰된 증상을 기록한다.
- root cause를 확인하기 전에는 임시 수정이나 추측성 패치를 하지 않는다.
- 원인 후보를 나누고 증거로 하나씩 제거한다.
- 수정 후 같은 재현 절차로 문제가 사라졌는지 확인한다.
- 가능하면 회귀 테스트나 재발 방지 검증을 추가한다.

## TDD / Behavior Change Hook

동작 변경, 버그 수정, 리팩터링은 구현 전에 검증 기준을 먼저 만든다.

- 가능한 경우 실패하는 테스트를 먼저 작성하고 실패를 확인한다.
- 테스트가 부적절한 작업은 수동 검증 절차와 기대 결과를 먼저 적는다.
- 문서, 설정, throwaway prototype은 예외가 될 수 있지만 예외 이유를 남긴다.
- 구현은 검증 기준을 통과시키는 최소 변경부터 시작한다.

## Worktree / Git Safety Hook

저장소 변경이 있는 표준/보호 작업은 수정 전에 branch, remote, dirty file 상태를 확인한다.

- 보호 작업, 충돌 위험이 있는 작업, PR 대상 작업은 task branch를 가진 독립 worktree에서 진행한다.
- worktree는 가능한 한 새 task branch에 붙여 만든다: `git worktree add <path> -b <task-branch> <base-branch>`.
- detached HEAD, base branch 직접 수정, 소유자가 불명확한 dirty worktree에서는 구현을 시작하지 않는다.
- 사용자가 만든 dirty change는 되돌리지 않고, 의도한 파일만 commit에 포함한다.
- 작업 완료 후 branch push, PR/merge 또는 final push, gate 증거 확인이 끝나고 worktree가 clean하면 worktree를 삭제하고 prune으로 정리한다.
- dirty worktree, unmerged branch, 소유자가 불명확한 worktree는 삭제하지 않는다.

## Review Reception Hook

리뷰 피드백은 바로 수용하거나 반박하지 않고 기술적으로 검증한다.

- 피드백을 전체 맥락에서 읽고 요구사항을 재진술한다.
- 코드베이스 현실과 대조해 맞는 지적인지 확인한다.
- 맞으면 수정하고 관련 검증을 실행한다.
- 애매하거나 틀린 피드백은 근거를 들어 질문하거나 반박한다.
- reviewer BLOCK은 해결 또는 명시적 override 전까지 완료를 막는다.

## Verification / Branch Finish Hook

완료 선언 전에는 fresh verification evidence를 확보한다.

- 완료, fixed, 통과, ready를 말하기 전에 증명할 명령이나 절차를 실행한다.
- 실행 결과, exit code, 실패 수, 확인한 artifact를 읽고 판단한다.
- 검증을 실행할 수 없으면 완료가 아니라 미검증 상태로 보고한다.
- branch 작업 완료 후에는 PR 생성, 병합, branch 유지, 폐기, worktree cleanup 중 하나를 선택한다.
- 선택한 경로와 남은 위험을 최종 보고에 남긴다.
