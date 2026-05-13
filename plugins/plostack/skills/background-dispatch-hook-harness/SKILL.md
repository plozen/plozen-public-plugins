---
name: background-dispatch-hook-harness
description: 경량/표준/보호 분류 후 `-bd`, 독립 실행 단위, 역할 분리, 장시간 작업 조건 때문에 `background-dispatch` 스킬 호출 여부를 판단해야 할 때 사용한다.
---

# Background Dispatch Hook Harness

Background dispatch의 세부 실행, 대화 양보, subagent lifecycle은 `background-dispatch` 스킬을 단일 기준으로 따른다. 이 하네스에서는 경량/표준/보호 분류 후 해당 스킬을 호출할지만 판단한다.
