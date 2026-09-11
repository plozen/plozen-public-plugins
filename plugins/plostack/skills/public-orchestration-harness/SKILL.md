---
name: public-orchestration-harness
description: 저장소 변경, 새 기능, 동작 변경, 버그 수정, 테스트 실패, 다단계 작업, 작업 범위 분류, 스킬 라우팅, planning, worktree, debugging/TDD, 리뷰/QA/security gate, verification, PR/merge/cleanup 통합이 필요할 때 사용한다. 사용자가 Plostack을 명시하지 않아도 작업 성격상 필요하면 경량/표준/보호를 먼저 분류하고 subagent 활용 여부를 자율 판단한다.
---

# Plostack 오케스트레이션 하네스

## 호환 역할

이 문서는 글로벌 지침 위에 놓이는 얇은 호환용 라우터다. 작업 위험을 분류하고, 필요한 고위험 하네스만 선택한다. 저위험 작업에 Plostack 흐름을 강제하지 않는다.

## 위험 기반 최소 경로

| 등급 | 판단 기준 | 최소 경로 |
|---|---|---|
| Lightweight | 읽기, 질문, 상태 확인, 단순 문구처럼 실행 산출물이 없음 | 하네스 없이 처리 |
| Standard | 작은 로컬 문서·코드 변경 | 직접 수행하고 변경에 맞는 targeted verification만 선택 |
| Protected | 새 동작, 대규모 리팩터링, 보안·인증·데이터·인프라, 릴리스, 다중 시스템 | 필요한 primary 1개와 risk-required verifier만 선택. 격리가 필요할 때 worktree, 종료 요청 때 finish-flow 추가 |

자동 cascade는 없다. 여러 primary 하네스나 전체 보호 흐름을 기본으로 붙이지 않으며, 사용자의 명시 요청이나 저장소 정책이 있을 때만 등급을 올린다.

## 선택형 라우팅

- 독립성·병렬 이득·역할 분리가 실제로 있을 때만 background-dispatch를 선택한다.
- branch/worktree/Git 격리가 필요할 때만 worktree-hook-harness를 선택한다.
- 마지막 변경의 local evidence가 필요할 때 verification-branch-finish-hook-harness를 선택한다.
- commit·push·PR 종료가 요청되거나 정책상 필요할 때만 finish-flow-harness를 선택한다.
- 관리자 UI와 export 산출물은 설치된 해당 non-harness skill로 직접 라우팅한다.
- 계획·버그·리뷰의 공통 판단은 글로벌 지침에 따르며 별도 hook을 자동으로 붙이지 않는다.

각 선택형 하네스가 자신의 concern 절차와 판정값을 소유한다. 이 라우터는 그 내용을 재서술하거나 완료를 대신 판정하지 않는다.
