---
name: skill-routing-hook-harness
description: 저장소 변경, 동작 변경, 검증, 위임, 리뷰, QA, PR이 필요한 작업을 시작할 때 관련 Plostack skill과 하네스 적용 여부를 판단해야 하면 사용한다.
---

# Skill Routing Hook Harness

작업 시작 전에 관련 Plostack skill이 있는지 판단한다. 사용자가 Plostack을 말하지 않아도 저장소 변경, 동작 변경, 검증, 위임, 리뷰, QA, PR이 필요한 작업이면 먼저 이 하네스로 범위를 분류한다.

- 새 기능, 디자인, 동작 변경, 불명확한 요구사항은 `brainstorming`을 먼저 사용한다.
- 저장소 변경, 버그 수정, 테스트 실패, 다단계 실행, 검증/위임/리뷰/QA/PR이 필요한 작업은 이 orchestration harness로 경량/표준/보호를 먼저 분류한다.
- 구현, PR, 리뷰, QA, 위임이 필요하면 이 orchestration harness를 적용한다.
- 버그, 테스트 실패, 예상 밖 동작은 수정 전에 Debugging Hook을 적용한다.
- 완료, 성공, 통과, fixed를 말하기 전에는 Verification Hook을 적용한다.
- 경량 작업에는 skill 흐름을 강제하지 않는다. 관련 skill을 생략하면 이유와 남은 위험을 짧게 남긴다.
