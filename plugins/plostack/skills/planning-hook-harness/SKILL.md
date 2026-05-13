---
name: planning-hook-harness
description: Brainstorming 승인이 끝난 보호 작업에서 구현 전 실행 계획, task 분해, 파일 ownership, 검증 명령을 정해야 할 때 사용한다.
---

# Planning Hook Harness

Brainstorming 승인이 끝난 보호 작업은 구현 전에 실행 계획을 만든다.

- 작업을 작고 검증 가능한 task로 나눈다.
- 각 task에는 수정 대상 파일, owner, 금지 범위, 검증 명령을 둔다.
- 여러 하위 시스템이 섞이면 하위 프로젝트나 독립 task group으로 나눈다.
- 파일 ownership을 나눠 subagent 간 write conflict를 막는다.
- 계획이 불명확하면 구현으로 넘어가지 않고 사용자 확인을 받는다.
