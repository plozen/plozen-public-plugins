---
name: public-orchestration-harness
description: 저장소 변경, 새 기능, 동작 변경, 버그 수정, 테스트 실패, 다단계 작업, 작업 범위 분류, 스킬 라우팅, planning, worktree, debugging/TDD, 리뷰/QA/security gate, verification, PR/merge/cleanup 통합이 필요할 때 사용한다. 사용자가 Plostack을 명시하지 않아도 작업 성격상 필요하면 경량/표준/보호를 먼저 분류한다. background subagent 디스패치는 `background-dispatch` 스킬로 처리한다.
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

특수 라우팅:

- 관리자웹 공통 UI 패턴은 `admin-ui-consistency-harness`로 보낸다.
- 입력 끝의 `-bd`는 `background-dispatch` 스킬 호출 신호로 본다.
- 명시 요청이 있으면 한 단계 높은 흐름으로 올릴 수 있다.

## Workflow By Scope

위 [적용 범위](#적용-범위)에서 정한 등급별 최소 워크플로우만 적용한다. 모든 작업에 보호 작업 전체 절차를 강제하지 않는다.

| 등급 | 기준 | 기본 흐름 |
|---|---|---|
| Lightweight | 질문 답변, 범위 분류, 설계 대화, 상태 확인처럼 실행 산출물이 없는 작업 | 분류 -> 바로 답변/상태 확인 -> 필요한 근거 표시 |
| Standard | 일반 기능 수정, 버그 수정, 테스트 추가, 문서 수정처럼 실행 산출물이 생기지만 위험이 낮은 작업 | 분류 -> git/worktree 상태 확인 -> 수정/실행 -> 검증 -> 보고 |
| Protected | 새 기능, 동작 변경, 대규모 리팩터링, 릴리스, 보안/인증/데이터/마이그레이션, 여러 하위 시스템이 섞인 작업 | Brainstorming -> Planning -> 라우팅 -> 작업 트리 -> 위임 -> 구현/디버깅 -> 리뷰 -> QA/Security -> 검증 -> finish-flow -> 팀장 확인 -> 병합/정리 -> 보고 |

### Lightweight

Brainstorming, 작업 트리, 위임, PR을 강제하지 않는다.

### Standard

선택 단계:

- `-bd`가 있거나 독립 실행 단위가 2개 이상이면 `background-dispatch` 스킬을 적용한다.
- 회귀 위험이 있으면 reviewer 또는 QA gate를 적용한다.
- 관리자웹 공통 UI 패턴을 바꾸거나 한 페이지 수정사항을 다른 페이지에도 맞춰야 하면 `admin-ui-consistency-harness`를 적용한다.
- 사용자 요청 또는 저장소 정책이 있으면 `verification-branch-finish-hook-harness`로 fresh evidence를 확인한 뒤 `finish-flow-harness`로 commit/push/PR gate를 적용한다.

### Protected

보호 작업에서 팀장은 라우터, gate 판정자, 통합자 역할을 우선한다. 실행은 작업 규모와 런타임 정책에 따라 현재 세션, 역할 에이전트, 독립 실행 컨텍스트 중 적절한 경로가 맡는다. 최종 저장소 통합, 병합, 최종 푸시, 깨끗한 작업 트리 정리는 팀장이 책임진다.

단계별 hook skill 연결:

이 목록은 라우팅 인덱스다. 적용 조건, 세부 절차, 완료 기준은 링크된 skill prompt를 따른다.

| 단계 | 연결 skill |
|---|---|
| Brainstorming | `brainstorming` |
| Output Artifact Routing | `exportable-html-document`, `html-to-pdf`, `html-to-pptx`, `pptx-generator` |
| Admin UI Common Gate | `admin-ui-consistency-harness` |
| Planning | `planning-hook-harness` |
| 작업 트리 | `worktree-hook-harness` |
| 위임 | `background-dispatch` |
| 구현/디버깅 | `debugging-hook-harness` |
| 리뷰/피드백 | `review-reception-hook-harness` |
| 검증/완료 | `verification-branch-finish-hook-harness` |
| 종료 자동화 | `finish-flow-harness` |

## 역할 위임 경계

이 섹션은 위임 여부와 역할 선택만 정한다. subagent 스폰, 재사용, 종료, 보고 방식은 `background-dispatch`를 따른다.

위임을 검토하는 경우:

- 독립 실행 단위가 2개 이상이다.
- reviewer, qa, breaker, security처럼 분리 판단이 필요하다.
- 장시간 조사, 검증, 구현을 분리하는 편이 안전하다.
- 사용자가 위임, 병렬, `-bd`를 명시했다.

현재 세션에서 직접 처리하는 경우:

- 질문 답변, 상태 확인, 범위 분류, 라우팅.
- 경량 단일 수정, 단일 명령, 단일 검증.
- 위임 결과 통합, gate 판정, 최종 보고.

역할별 우선 호출 기준:

| 역할 | 호출 기준 |
|---|---|
| `developer-senior` | 새 기능, 복잡한 구현, 아키텍처, 다중 파일 리팩터링, 어려운 디버깅 |
| `developer-mid` | 버그 수정, 단순 CRUD, 집중 테스트 추가, 단일/소규모 파일 변경 |
| `developer-junior` | 문구, 오타, 주석, import 정리, 포맷팅, 상수 변경처럼 로직 없는 수정 |
| `reviewer` | 코드, schema, API, LLM trust boundary, 구조 위험 리뷰 |
| `qa` | 테스트 실행, 회귀 확인, 재현 절차, 검증 리포트 |
| `breaker` | 브라우저 흐름, 사용자 관점 edge case, 비직관적 UX 검증 |
| `security` | secrets, auth, infra, dependency, supply-chain 위험 |
| `documenter` | 문서, spec, README, 릴리스 노트, Markdown 변환 |
| `researcher` | 외부/기술 조사, 라이브러리/API 확인, 출처 기반 비교 |

위임이 불가하거나 생략되면 로컬 실행 경로와 남은 위험만 보고한다.

## 완료 기준

이 섹션은 완료 선언 전 필요한 gate만 정한다. fresh evidence 수집과 완료 판정은 `verification-branch-finish-hook-harness`, commit/push/PR 종료 자동화는 `finish-flow-harness`를 따른다.

| 변경 성격 | 필요한 gate |
|---|---|
| 코드, schema, API, auth, data | reviewer |
| 동작 변경, 테스트 추가, 회귀 위험 | qa |
| 관리자웹 공통 UI | `admin-ui-consistency-harness` |
| UI 또는 browser-facing 변경 | qa 또는 breaker browser gate |
| secrets, auth, infra, dependency | security |
| commit, push, PR, merge, cleanup | `verification-branch-finish-hook-harness` -> `finish-flow-harness` |

완료 가능 조건:

- 필요한 gate가 통과했다.
- 생략한 gate가 있으면 생략 이유와 남은 위험을 보고했다.
- BLOCK, FAIL, Critical, UNVERIFIED 상태가 남아 있으면 완료로 말하지 않는다.
