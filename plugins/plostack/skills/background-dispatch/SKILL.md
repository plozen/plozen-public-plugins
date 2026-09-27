---
name: background-dispatch
description: 메인 에이전트가 작업의 독립성, 병렬 처리 이점, 역할 분리, 지연과 충돌 위험을 평가해 background subagent가 유용하다고 판단하거나 사용자가 명시적으로 위임을 요청했을 때 사용한다. 스폰 이후 lifecycle과 결과 통합을 관리한다.
---
# Background Dispatch Skill

이 스킬은 background subagent의 dispatch 판단, prompt contract, lifecycle만 담당한다. 구현·조사·검증 자체와 전체 작업 라우팅은 다른 canonical skill의 책임이다.

## 사용 시점

다음 중 하나일 때만 사용한다.

- 독립 실행 단위, 병렬 처리, 장시간 작업, 역할 분리가 실질적으로 유리하다.
- 사용자가 background 또는 subagent 활용을 명시했다.
- 이미 시작한 agent의 lifecycle이나 결과를 관리한다.

## Dispatch 판단

- 단순·강결합 작업과 write set이 겹치는 작업은 직접 수행한다.
- 호출 여부, 역할, 개수, 병렬화는 메인 에이전트가 독립성·지연·충돌 위험을 보고 자율 결정한다.
- 사용하더라도 결과 통합, 검증, 사용자 보고 책임은 메인 에이전트에 남는다.

## Prompt contract

spawn prompt에는 반드시 다음을 포함한다.

- 미션 1줄, 범위·금지 범위, 파일 ownership
- 수정 권한과 산출물 형식
- 종료 기준 또는 시간 한도
- 다른 작업자의 변경을 되돌리거나 흡수하지 말라는 지시
- UI/browser 작업이면 허용되는 screenshot, viewport, 저장 경로
- commit·push·PR 허용 여부
- 별도 mock 산출물은 기본 요구사항이 아니며, 생성이 허용된 경우에만 저장한다.

## Lifecycle

1. 같은 역할·작업 라인의 agent가 있으면 새로 만들기 전에 send_input으로 재사용한다. 닫힌 agent를 이어갈 가치가 있으면 resume_agent를 먼저 시도한다.
2. 재사용이 부적합하거나 역할·ownership·위험이 다를 때만 spawn_agent를 호출한다. 단순 작업과 겹치는 write set에는 호출하지 않는다.
3. spawn 직후에는 짧게 dispatch 사실만 알리고, wait_agent로 기본 대기하지 않는다. 결과가 즉시 critical path를 막을 때만 기다린다. 같은 주제의 긴 foreground 조사도 이어가지 않는다.
4. completed는 결과 도착이지 자동 종료가 아니다. 후속 피드백이 있으면 세션을 유지한다.
5. Esc, turn abort, 새 질문, 상태 질문만으로 취소로 해석하지 않는다. 명시적 취소, 작업 라인 종료, 또는 통합 완료 후에만 close_agent를 사용한다.
6. 상태·관련 질문은 메인 에이전트가 답하되 충돌이 없으면 agent를 유지한다. 충돌 요청은 우선순위를 확인하거나 충돌 없는 최소 조치만 한다.
7. 결과가 오면 산출물·로그·검증을 메인 에이전트가 확인하고 통합한다. 실패는 원인과 unblock path를 보고한다.
8. agent 상태 확인 불가나 agent가 많다는 이유만으로 완료·취소·일괄 종료를 추정하지 않는다.
