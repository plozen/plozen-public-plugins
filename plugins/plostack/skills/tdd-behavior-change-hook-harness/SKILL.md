---
name: tdd-behavior-change-hook-harness
description: 동작 변경, 버그 수정, 리팩터링을 구현하기 전에 테스트 또는 수동 검증 기준을 먼저 세워야 할 때 사용한다.
---

# TDD / Behavior Change Hook Harness

동작 변경, 버그 수정, 리팩터링은 구현 전에 검증 기준을 먼저 만든다.

- 가능한 경우 실패하는 테스트를 먼저 작성하고 실패를 확인한다.
- 테스트가 부적절한 작업은 수동 검증 절차와 기대 결과를 먼저 적는다.
- 문서, 설정, throwaway prototype은 예외가 될 수 있지만 예외 이유를 남긴다.
- 구현은 검증 기준을 통과시키는 최소 변경부터 시작한다.
