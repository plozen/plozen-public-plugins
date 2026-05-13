---
name: review-reception-hook-harness
description: 코드 리뷰나 reviewer 피드백을 받은 뒤 바로 수용/반박하지 않고 맥락, 타당성, 검증 필요성을 판정해야 할 때 사용한다.
---

# Review Reception Hook Harness

리뷰 피드백은 바로 수용하거나 반박하지 않고 기술적으로 검증한다.

- 피드백을 전체 맥락에서 읽고 요구사항을 재진술한다.
- 코드베이스 현실과 대조해 맞는 지적인지 확인한다.
- 맞으면 수정하고 관련 검증을 실행한다.
- 애매하거나 틀린 피드백은 근거를 들어 질문하거나 반박한다.
- reviewer BLOCK은 해결 또는 명시적 override 전까지 완료를 막는다.
