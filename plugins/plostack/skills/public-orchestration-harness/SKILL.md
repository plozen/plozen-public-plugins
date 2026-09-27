---
name: public-orchestration-harness
description: 복잡하거나 고위험인 저장소 작업 또는 사용자가 명시적으로 Plostack 오케스트레이션을 요청한 경우에만 선택해 위험을 분류하고 필요한 하네스를 라우팅한다. 저위험 작업에는 강제하지 않는다.
---

# Plostack 오케스트레이션 하네스

## 호환 역할

이 문서는 글로벌 지침 위에 놓이는 얇은 호환용 라우터다. 작업 위험을 분류하고, 필요한 고위험 하네스만 선택한다. 저위험 작업에 Plostack 흐름을 강제하지 않는다. 브라우저에 영향을 주는 변경도 중간 구현 단계에서는 검증을 유예하고, 최종 배포·릴리스 gate에서만 UI·통합 검증을 요구한다.

## 위험 기반 최소 경로

| 등급 | 판단 기준 | 최소 경로 |
|---|---|---|
| Lightweight | 읽기, 질문, 상태 확인, 단순 문구처럼 실행 산출물이 없음 | 하네스 없이 처리 |
| Standard | 작은 로컬 문서·코드 변경 | 직접 수행하고 변경에 맞는 targeted verification만 선택 |
| Protected | 새 동작, 대규모 리팩터링, 보안·인증·데이터·인프라, 릴리스, 다중 시스템 | 필요한 primary 1개와 risk-required verifier만 선택. 격리가 필요할 때 worktree, 종료 요청 때 finish-flow 추가 |

일반 작업에는 자동 cascade가 없다. browser-facing 변경도 중간 구현 단계에서는 `browser-change-verification`과 QA 서브에이전트를 자동 호출하지 않는다. 사용자가 브라우저 검증을 명시하거나 최종 배포·릴리스 gate에 도달한 경우에만 해당 하네스를 선택한다.

## 검증 모드

- `INTERMEDIATE`(기본): 기능을 구현·수정·정리하는 단계다. 변경 범위에 맞는 lint, typecheck, build, diff-check, 정적/API/readback 확인만 수행하고 browser QA는 `DEFERRED`로 기록한다.
- `RELEASE`: 사용자가 배포·publish·release·production·ship을 요청했거나 최종 배포 전 검증을 요청한 단계다. `browser-change-verification`을 선택하고 전용 test-only 서브에이전트의 실제 UI·통합 evidence를 확보한다.
- 사용자가 “브라우저로 확인”, “디자인 검수”, “QA”처럼 브라우저 검증을 명시하면 해당 요청 범위는 `RELEASE` 모드로 취급한다.

## 선택형 라우팅

- 독립성·병렬 이득·역할 분리가 실제로 있을 때만 background-dispatch를 선택한다.
- branch/worktree/Git 격리가 필요할 때만 worktree-hook-harness를 선택한다.
- 마지막 변경의 local evidence가 필요할 때 verification-branch-finish-hook-harness를 선택한다.
- commit·push·PR 종료가 요청되거나 정책상 필요할 때만 finish-flow-harness를 선택한다.
- 중간 작업에서 UI, route, client interaction, 또는 UI가 소비하는 API/RPC/server action/data boundary를 변경하면 browser QA를 자동 호출하지 않는다. 변경에 맞는 정적·read-only/API evidence를 확보하고 browser gate를 `DEFERRED`로 기록한다.
- `RELEASE` 모드에서만 `browser-change-verification`을 선택한다. 전용 test-only 서브에이전트가 실제 브라우저 UI와 통합 경계를 검증하고 메인 에이전트가 결과를 통합해야 한다.
- 최종 배포·릴리스 전에는 서브에이전트 기록과 UI·통합 evidence가 모두 필요하다. 어느 하나가 `FAIL`/`UNVERIFIED`면 배포를 통과시키지 않는다. 중간 작업의 `DEFERRED`는 실패가 아니다.
- 관리자 UI와 export 산출물은 설치된 해당 non-harness skill로 직접 라우팅한다.
- 계획·버그·리뷰의 공통 판단은 글로벌 지침에 따르며 별도 hook을 자동으로 붙이지 않는다.

각 선택형 하네스가 자신의 concern 절차와 판정값을 소유한다. 이 라우터는 그 내용을 재서술하거나 완료를 대신 판정하지 않는다.
