---
name: public-orchestration-harness
description: 저장소 변경, 새 기능, 동작 변경, 버그 수정, 테스트 실패, 다단계 작업, 작업 범위 분류, 스킬 라우팅, planning, worktree, debugging/TDD, 리뷰/QA/security gate, verification, PR/merge/cleanup 통합이 필요할 때 사용한다. 사용자가 Plostack을 명시하지 않아도 작업 성격상 필요하면 경량/표준/보호를 먼저 분류한다. background subagent 디스패치는 `background-dispatch` 스킬로 처리한다.
---

# Plostack 오케스트레이션 하네스

## 적용 범위

사용자가 `Plostack`을 명시하지 않아도, 작업이 저장소 변경/동작 변경/다단계 실행/검증/위임을 포함하면 먼저 이 하네스로 경량/표준/보호 작업을 분류한다. Plostack 작업 흐름은 모든 작업에 강제하지 않고 필요한 만큼만 적용한다.

사용자는 짧은 작업 지시만 남겨도 된다. 팀장이 경량/표준/보호를 분류하고 [Workflow By Scope](#workflow-by-scope)를 선택한 뒤, 필요한 hook, subagent, gate, 검증 절차를 작업 성격에 맞게 조합한다.

- 경량 작업: 질문 답변, 범위 분류, 설계 대화, 상태 확인처럼 실행 산출물이 없는 작업이다. [Workflow By Scope](#workflow-by-scope)의 Lightweight 흐름으로 처리하고, Brainstorming, 작업 트리, 위임, PR을 강제하지 않는다.
- 표준 작업: 일반 기능 수정, 버그 수정, 테스트 추가, 문서 수정처럼 실행 산출물이 생기지만 위험이 낮은 작업이다. [Workflow By Scope](#workflow-by-scope)의 Standard 흐름으로 처리하고, `background-dispatch`, 작업 트리, 커밋, 푸시, PR은 필요한 경우에만 적용한다.
- 보호 작업: 새 기능, 동작 변경, 대규모 리팩터링, 릴리스, 보안/인증/데이터/마이그레이션, 여러 하위 시스템이 섞인 작업이다. [Workflow By Scope](#workflow-by-scope)의 Protected 흐름을 기본 적용한다.

사용자가 명시적으로 `Plostack으로 진행`, `PR까지`, `팀장 모드`, `서브에이전트로 병렬 진행`처럼 요청하면 한 단계 높은 흐름으로 올릴 수 있다. 입력 끝의 `-bd`는 `background-dispatch` 스킬 호출 신호로 본다. Plostack 명시는 필수 트리거가 아니며 작업 성격이 조건에 맞으면 자동 적용한다.

## Workflow By Scope

위 [적용 범위](#적용-범위)에서 정한 경량/표준/보호 분류를 그대로 받아서 해당 등급의 최소 워크플로우만 적용한다. 모든 작업에 보호 작업 전체 절차를 강제하지 않는다.

### Lightweight

```text
분류 -> 바로 답변/상태 확인 -> 필요한 근거 표시
```

### Standard

```text
분류 -> git/worktree 상태 확인 -> 수정/실행 -> 검증 -> 보고
```

선택 단계:

- `-bd`가 있거나 독립 실행 단위가 2개 이상이면 `background-dispatch` 스킬을 적용한다.
- 회귀 위험이 있으면 reviewer 또는 QA gate를 적용한다.
- 사용자 요청 또는 저장소 정책이 있으면 `verification-branch-finish-hook-harness`로 fresh evidence를 확인한 뒤 `finish-flow-harness`로 commit/push/PR gate를 적용한다.

### Protected

보호 작업의 기본 흐름:

```text
Brainstorming -> Planning -> 라우팅 -> 작업 트리 -> 위임 -> 구현/디버깅 -> 리뷰 -> QA/Security -> 검증 -> finish-flow(local-preflight/commit/push/PR gate) -> 팀장 확인 -> 병합/정리 -> 보고
```

보호 작업에서 팀장은 라우터, gate 판정자, 통합자 역할을 우선한다. 실행은 작업 규모와 런타임 정책에 따라 현재 세션, 역할 에이전트, 독립 실행 컨텍스트 중 적절한 경로가 맡는다. 최종 저장소 통합, 병합, 최종 푸시, 깨끗한 작업 트리 정리는 팀장이 책임진다.

단계별 hook skill 연결:

- Brainstorming: 새 기능, 디자인, 동작 변경, 불명확한 요구사항이면 `brainstorming`을 먼저 사용한다.
- Output Artifact Routing: HTML/PDF/PPTX/디자인 산출물은 먼저 최종 형태를 판정한다. 새 문서형 standalone HTML 작성은 `exportable-html-document`, 이미 있는 HTML을 PDF로 변환만 하면 `html-to-pdf`, 이미 있는 HTML page/slide를 PPTX로 변환하거나 PPTX 다운로드 버튼/경로를 구현하면 `html-to-pptx`, 새 발표자료/피치덱 작성은 `pptx-generator`, Excalidraw/whiteboard/와이어프레임으로 화면 구조만 먼저 잡는 작업은 `design-gate-hook-harness`의 Visual Planning Gate와 `design-quality`, 새 랜딩/웹앱/모바일 UI mock은 `design-gate-hook-harness`와 해당 디자인 스킬로 보낸다.
- Design Gate: 새 앱/SaaS/SPA/랜딩/관리자 UI/포트폴리오용 UI screenshot처럼 디자인이 제품 성공과 판매 전환에 영향을 주는 작업은 실제 구현 전에 `design-gate-hook-harness`를 적용한다. Excalidraw/draw/whiteboard/와이어프레임은 pub mock 이전의 visual planning으로 다루고, frame/page 분리, common vs page-specific layout 구분, 제한된 palette, clean font, 짧은 slot label, route arrow, 짧은 handoff를 `design-quality`로 점검한다. 보고서, 제안서 문서, 포트폴리오 본문, 경력기술서처럼 PDF/PPTX export가 최종물인 HTML은 design gate 대신 `exportable-html-document`로 분기한다. 이 gate에서 `Output Format Gate -> Marketing Brief -> DESIGN.md -> pub mock -> screenshots -> design review -> implementation handoff` 흐름과 `design-lab/pub/`, `design-lab/screenshots/`, 필요 시 `design-lab/handoff.md` 산출물 여부를 확인한다. Confirmed `DESIGN.md`와 승인된 `design-kit/` 또는 `design-lab/pub/`을 source of truth로 두고, 없는 UX는 planning으로 되돌린 뒤 design/pub을 먼저 갱신하고 service/API sync를 진행한다. `-bd`는 design gate 우회 사유가 아니다. 모바일/포트폴리오 mock은 `design-lab/pub/`를 raw publishing/artboard 원본으로 유지하고, 디바이스 mockup·크몽 썸네일·composite page는 별도 경로로 분리했는지 확인한다. 요청 폭이 없으면 390px, Z Fold 5 folded/344px 요청이면 344px 기준 screenshot과 blocker 수치를 요구한다.
- Planning: Brainstorming 및 필요한 Design Gate 승인이 끝난 보호 작업은 `planning-hook-harness`를 적용한다.
- 작업 트리: 저장소 수정 전에는 `worktree-hook-harness`를 적용한다.
- 위임: 독립 실행 단위가 여러 개이거나, 전문 역할 gate가 필요하거나, 사용자가 명시적으로 요청했거나, 장시간 작업을 분리하는 편이 안전하면 `background-dispatch` 스킬을 적용한다. 이때 새 subagent를 바로 만들지 말고 같은 역할/같은 작업 라인의 기존 agent를 `send_input` 또는 `resume_agent`로 재사용할 수 있는지 먼저 확인한다.
- 구현/디버깅: 버그, 테스트 실패, 동작 변경은 `debugging-hook-harness`를 적용한다.
- 리뷰: 피드백 처리에는 `review-reception-hook-harness`를 적용한다.
- QA/Security: 변경 성격에 맞춰 reviewer, qa, breaker, security gate를 적용한다.
- 검증/완료: 완료, fixed, ready, merge, cleanup 전에는 `verification-branch-finish-hook-harness`를 적용해 마지막 변경 이후 fresh verification evidence를 확보한다.
- 종료 자동화: commit, push, PR, remote checks까지 닫아야 하면 fresh verification 후 `finish-flow-harness`를 적용한다. 이 단계는 `local-preflight -> commit -> push -> pr-gate`를 담당하고, `main` 직접 push 기본 차단, secret 파일 차단, `NO_CHECKS` 별도 보고를 강제한다.

## 역할 위임 경계

역할 위임은 표준/보호 작업에서 선택 가능한 실행 경로다. 독립 실행 단위가 여러 개이거나, reviewer/qa/security 같은 분리 gate가 필요하거나, 사용자가 명시적으로 위임을 요청한 경우 우선 검토한다. 단일 경량 실행 단위는 현재 세션에서 처리할 수 있다. 상위 지침, 도구 정책, 실행 환경이 위임을 금지하면 로컬 실행 계획으로 전환하고 생략 이유를 남긴다.

팀장이 직접 맡는 일:

- 질문 답변, 상태 확인, 범위 분류, 라우팅, 설계, 작업 방향 제시
- 위임 준비를 위한 최소 파일 읽기와 작업 트리/브랜치/커밋/푸시/PR/병합/정리 같은 통합 작업
- 위임 결과 검토, gate 판정, 최종 보고

subagent lifecycle 기본값:

- 동일 역할과 동일 작업 라인의 후속 작업은 기존 agent 재사용을 우선한다.
- 새 agent 생성 전 `send_input`으로 이어갈 수 있는지 확인하고, 이미 닫은 agent라도 맥락을 이어갈 가치가 있으면 `resume_agent`를 먼저 시도한다.
- `completed`는 결과 수신 상태일 뿐 자동 종료 신호가 아니다. 후속 피드백 가능성이 있으면 agent를 유지한다.
- `close_agent`는 작업 라인 종료, 취소, 컨텍스트 폐기, 또는 세션 유지가 더 위험한 경우에만 사용한다.
- 역할별로 `designer`, `developer`, `qa`, `reviewer` 같은 장기 작업 슬롯을 유지할 수 있다. 단, 파일 ownership이 겹치거나 역할이 달라 충돌 위험이 있으면 새 agent를 만들 수 있다.

역할별 우선 호출 기준:

| 역할 | 호출 기준 |
|---|---|
| `developer-senior` | 새 기능, 복잡한 구현, 아키텍처, 다중 파일 리팩터링, 어려운 디버깅 |
| `developer-mid` | 버그 수정, 단순 CRUD, 집중 테스트 추가, 단일/소규모 파일 변경 |
| `developer-junior` | 문구, 오타, 주석, import 정리, 포맷팅, 상수 변경처럼 로직 없는 수정 |
| `designer` | 앱 UI, 랜딩페이지, 대시보드, 디자인 시스템, 시각 구현 |
| `design-reviewer` | 디자인 일관성, 접근성, 타이포그래피, 간격, 색상 감사 |
| `reviewer` | 코드, schema, API, LLM trust boundary, 구조 위험 리뷰 |
| `qa` | 테스트 실행, 회귀 확인, 재현 절차, 검증 리포트 |
| `breaker` | 브라우저 흐름, 사용자 관점 edge case, 비직관적 UX 검증 |
| `security` | secrets, auth, infra, dependency, supply-chain 위험 |
| `documenter` | 문서, spec, README, 릴리스 노트, Markdown 변환 |
| `researcher` | 외부/기술 조사, 라이브러리/API 확인, 출처 기반 비교 |

파일 수정, 코드/문서 작성, 조사, 테스트, 검증, 정리처럼 실행 산출물이 생기는 작업은 현재 실행 환경과 상위 지침이 허용하면 위임을 검토한다. 경량 단일 작업은 현재 세션에서 직접 처리할 수 있고, 위임을 생략하면 이유와 남은 위험을 보고한다.

## 완료 기준

보호 작업은 필요한 gate가 통과하거나, 생략 이유와 남은 위험이 기록되어야 완료할 수 있다. 완료 선언 전에는 `verification-branch-finish-hook-harness`를 적용한다. commit/push/PR까지 요청된 작업은 verification gate 통과 후 `finish-flow-harness`의 local-preflight, secret guard, push, PR remote gate 결과까지 보고되어야 한다.

- 코드, schema, API, auth, data 변경: `reviewer` gate
- 동작 변경, 테스트 추가, 회귀 위험: `qa` gate
- UI 또는 browser-facing 변경: `breaker` 또는 `qa` browser gate
- 새 앱/SaaS/SPA/랜딩/관리자 UI/포트폴리오 화면: `design-gate-hook-harness` + `design-reviewer` gate. 승인된 `DESIGN.md`, raw `design-lab/pub/` mock, `design-lab/screenshots/` 캡처 없이 실제 구현으로 바로 들어가면 완료를 막는다. 모바일 화면은 root tab/back 규칙, bottom tab fixed/anchored, overlap 0px, 최소 좌우 여백 16px 이상, text overflow 없음 같은 수치 기준이 handoff에 있어야 한다. 구현 handoff가 필요하면 `design-lab/handoff.md`를 확인한다.
- secrets, auth, infra, dependency 변경: `security` gate
- `reviewer` BLOCK, `qa` FAIL, `security` Critical, 핵심 사용자 흐름 실패는 완료를 막는다.
- gate를 생략하면 최종 보고에 생략 이유와 남은 위험을 남긴다.
