---
name: public-orchestration-harness
description: 저장소 변경, 새 기능, 동작 변경, 버그 수정, 테스트 실패, 다단계 작업, 작업 범위 분류, 스킬 라우팅, planning, worktree, debugging/TDD, 리뷰/QA/security gate, verification, PR/merge/cleanup 통합이 필요할 때 사용한다. 사용자가 Plostack을 명시하지 않아도 작업 성격상 필요하면 경량/표준/보호를 먼저 분류하고 subagent 활용 여부를 자율 판단한다.
---

# Plostack 오케스트레이션 하네스

## 적용 범위

이 하네스는 작업을 경량/표준/보호로 분류하고 필요한 hook skill만 연결하는 라우터다. 사용자가 `Plostack`을 명시하지 않아도 아래 조건 중 하나가 있으면 먼저 적용한다.

- 저장소 변경, 코드/문서/설정 수정
- 새 기능, 동작 변경, 버그 수정, 테스트 실패
- 다단계 실행, 검증, 위임, 리뷰/QA/security 판단
- commit, push, PR, merge, cleanup 판단
- 사용자가 `Plostack으로 진행`, `PR까지`, `팀장 모드`, `서브에이전트로 병렬 진행`처럼 요청

적용 범위에서는 등급만 판정한다. 실제 흐름은 [Workflow By Scope](#workflow-by-scope)를 따른다. Plostack 작업 흐름은 모든 작업에 강제하지 않고 필요한 만큼만 적용한다.

- subagent 사용 여부와 구성은 메인 에이전트가 자율 판단한다. 별도 사용자 플래그를 요구하지 않는다.
- 명시 요청이 있으면 한 단계 높은 흐름으로 올릴 수 있다.

UI 화면 작업 기본 규칙:

- 페이지 섹션, 프로필 헤더, 통계, 탭, 내비게이션, 폼 전체를 각각 독립 카드 컨테이너로 반복해서 감싸지 않는다.
- 카드는 반복 항목, 모달, 실제 프레임이 필요한 도구처럼 경계가 기능적으로 필요한 곳에만 사용한다.
- 사용자가 특정 제품의 디자인을 그대로 구현하라고 요청하면 해당 제품의 정보 구조, 배치, 크기 관계, 반응형 전환을 먼저 일치시킨다. 앱 고유 문구, 데이터, 브랜드 요소는 그 구조 안에서만 조정한다.
- 사용자가 카드형 UI를 명시적으로 요청한 경우에만 위 카드 제한의 예외로 처리한다.

## Workflow By Scope

위 [적용 범위](#적용-범위)에서 정한 등급별 최소 워크플로우만 적용한다. 모든 작업에 보호 작업 전체 절차를 강제하지 않는다.

| 등급 | 기준 | 기본 흐름 |
|---|---|---|
| Lightweight | 질문 답변, 범위 분류, 설계 대화, 상태 확인처럼 실행 산출물이 없는 작업 | 분류 -> 바로 답변/상태 확인 -> 필요한 근거 표시 |
| Standard | 일반 기능 수정, 버그 수정, 테스트 추가, 문서 수정처럼 실행 산출물이 생기지만 위험이 낮은 작업 | 분류 -> git/worktree 상태 확인 -> 수정/실행 -> 검증 -> 보고 |
| Protected | 새 기능, 동작 변경, 대규모 리팩터링, 릴리스, 보안/인증/데이터/마이그레이션, 여러 하위 시스템이 섞인 작업 | Brainstorming -> Planning -> 라우팅 -> 작업 트리 -> 구현/디버깅 -> 리뷰 -> QA/Security -> 검증 -> finish-flow -> 팀장 확인 -> 병합/정리 -> 보고 |

### Lightweight

Brainstorming, 작업 트리, 위임, PR을 강제하지 않는다.

### Standard

선택 단계:

- subagent가 유용하다고 판단한 경우 `background-dispatch` 스킬을 적용한다.
- 회귀 위험이 있으면 reviewer 또는 QA gate를 적용한다.
- 사용자 요청 또는 저장소 정책이 있으면 `verification-branch-finish-hook-harness`로 fresh evidence를 확인한 뒤 `finish-flow-harness`로 commit/push/PR gate를 적용한다.

### Protected

보호 작업에서 subagent 사용 여부는 메인 에이전트가 작업 성격에 따라 자율 판단한다. 최종 저장소 통합, 병합, 최종 푸시, 깨끗한 작업 트리 정리는 메인 에이전트가 책임진다.

단계별 hook skill 연결:

이 목록은 라우팅 인덱스다. 적용 조건, 세부 절차, 완료 기준은 링크된 skill prompt를 따른다.

| 단계 | 연결 skill |
|---|---|
| Brainstorming | `brainstorming` |
| Output Artifact Routing | `exportable-html-document`, `html-to-pdf`, `html-to-pptx`, `pptx-generator` |
| 작업 트리 | `worktree-hook-harness` |
| Background dispatch | `background-dispatch` |
| 검증/완료 | `verification-branch-finish-hook-harness` |
| 종료 자동화 | `finish-flow-harness` |

## Subagent decision

- 메인 에이전트가 작업의 독립성, 병렬 처리 이점, 예상 지연, 역할 분리 가치, write conflict를 평가해 subagent 사용 여부를 결정한다.
- 사용자가 별도 플래그를 붙일 필요가 없으며, 단일 작업이거나 현재 에이전트가 더 효율적이면 직접 수행한다.
- subagent를 사용하면 역할과 파일 ownership을 분리하고 결과 통합과 최종 검증은 메인 에이전트가 맡는다.
- 스폰, 재사용, lifecycle, 보고 세부 규칙은 `background-dispatch` 한 곳에서만 정의한다.
- 보호 작업은 구현 전에 작고 검증 가능한 task로 나누고, 각 task의 수정 파일, owner, 금지 범위, 검증 명령을 정한다. 여러 하위 시스템은 독립 task group으로 나눠 write conflict를 막는다.
- 계획이 불명확하면 구현으로 넘어가지 않고 사용자 확인을 받는다.

역할별 우선 호출 기준:

| 역할 | 호출 기준 |
|---|---|
| `developer` | 작업 범위에 맞는 최소권한 구현·수정 |
| `reviewer` | 코드, schema, API, LLM trust boundary, 구조 위험 리뷰 |
| `qa` | 테스트 실행, 회귀 확인, 재현 절차, 검증 리포트 |
| `security` | secrets, auth, infra, dependency, supply-chain 위험 |
| `documenter` | 문서, spec, README, 릴리스 노트, Markdown 변환 |
| `researcher` | 외부/기술 조사, 라이브러리/API 확인, 출처 기반 비교 |

역할별 gate는 검증 책임을 뜻하며 subagent 자동 호출을 뜻하지 않는다.

## 완료 기준

이 섹션은 완료 선언 전 필요한 gate만 정한다. fresh evidence 수집과 완료 판정은 `verification-branch-finish-hook-harness`, commit/push/PR 종료 자동화는 `finish-flow-harness`를 따른다.

| 변경 성격 | 필요한 gate |
|---|---|
| 코드, schema, API, auth, data | reviewer |
| 동작 변경, 테스트 추가, 회귀 위험 | qa |
| UI 또는 browser-facing 변경 | qa |
| secrets, auth, infra, dependency | security |
| commit, push, PR, merge, cleanup | `verification-branch-finish-hook-harness` -> `finish-flow-harness` |

완료 가능 조건:

- 필요한 gate가 통과했다.
- reviewer/qa/security gate의 실행 주체도 메인 에이전트가 작업 위험과 독립성을 보고 결정한다.
- 생략한 gate가 있으면 생략 이유와 남은 위험을 보고했다.
- BLOCK, FAIL, Critical, UNVERIFIED 상태가 남아 있으면 완료로 말하지 않는다.
