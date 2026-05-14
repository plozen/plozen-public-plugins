---
name: design-gate-hook-harness
description: 새 앱, SaaS, SPA, 랜딩, 관리자 UI, 포트폴리오 화면처럼 디자인이 제품 성공과 판매 전환에 영향을 주는 작업에서 실제 구현 전에 marketing brief, DESIGN.md, 별도 design-lab 퍼블리싱 mock, screenshot, design review gate를 강제한다.
---

# Plostack Design Gate Hook Harness

## 역할

이 스킬은 앱/SaaS/SPA/랜딩/관리자 UI/포트폴리오 화면 작업이 바로 실제 구현으로 튀지 않게 막는 디자인 게이트다. 목적은 기능 명세보다 먼저 팔릴 이유, 클릭 훅, 사용자 심리, 유통 각도, 시각 시스템, 퍼블리싱 mock을 확정한 뒤 실제 개발로 승격하는 것이다.

팀장은 디자인 산출물을 직접 만드는 사람이 아니라 gate owner다. 팀장은 `DESIGN.md`와 mock 산출물의 존재, 품질, 검증 상태를 확인하고 통과/보류를 판정한다.

## 적용 시점

다음 중 하나라도 해당하면 적용한다.

- 새 앱, SaaS, SPA, 웹앱, 모바일 앱, 랜딩페이지를 시작한다.
- 기존 제품에 주요 화면, 대시보드, 관리자, 온보딩, 가격/전환 화면을 추가한다.
- 포트폴리오/크몽/제안서용 UI screenshot을 만들거나 개선한다.
- 사용자가 “마케팅 먼저”, “클릭하게”, “궁금증”, “퍼블리싱 mock”, “DESIGN.md”, “디자인 게이트”를 언급한다.
- 에이전트가 바로 `src/`, `app/`, 실제 운영 앱 코드 구현으로 들어갈 위험이 있다.

단순 버그 수정, 문구 수정, 기존 디자인 토큰을 따르는 작은 컴포넌트 수정에는 생략할 수 있다. 생략하면 이유를 보고한다.

## Gate Flow

```text
Marketing Brief Gate
  -> DESIGN.md Gate
  -> Publishing Mock Gate
  -> Screenshot / Browser Verification Gate
  -> Design Review Gate
  -> Implementation Handoff Gate
```

### 1. Marketing Brief Gate

구현 전에 아래를 1페이지 이내로 정리한다.

- 클릭 훅: 사용자가 왜 눌러보는가?
- Curiosity gap: 어떤 궁금증이 다음 행동을 만든다?
- 사용자 심리: 불안, 욕망, 비용, 신뢰 장벽은 무엇인가?
- 유통/판매 각도: 어디에 보여주고 어떤 문장으로 팔 것인가?
- 성공 기준: screenshot, 신청, 문의, 구매, 포트폴리오 신뢰 중 무엇을 올릴 것인가?

필요하면 `docs/marketing-brief.md`에 둔다. 단, 사용자가 빠른 방향 판단만 원하면 대화 내 결정 브리프로 충분하다.

### 2. DESIGN.md Gate

프로젝트 루트에서 `DESIGN.md` 또는 `design.md`를 먼저 확인한다.

- 있으면 먼저 읽고 mock/구현이 그 규칙을 따르게 한다.
- 없고 프로젝트에 남는 화면/컴포넌트/디자인 시스템 변경이면 `DESIGN.md`를 만든다.
- `DESIGN.md`에는 제품 톤, 폰트, 색상 토큰, spacing, 컴포넌트 상태, 레이아웃 원칙, 접근성, 금지 패턴, 검증 기준을 포함한다.
- Google `design.md` CLI 호환이 필요한 경우 YAML front matter를 포함하고 `npx -y @google/design.md lint DESIGN.md`를 통과시킨다.
- 기존 프로젝트의 `DESIGN.md`가 prose-only 문서일 수 있다. 이 경우 lint warning 자체가 blocker는 아니지만, “CLI 호환 DESIGN.md가 아님”을 명시하고 필요 시 별도 보강 작업으로 분리한다.

### 3. Publishing Mock Gate

실제 앱 코드에 바로 들어가지 말고 별도 mock 공간을 우선 만든다.

권장 구조:

```text
project/
  DESIGN.md
  docs/
    marketing-brief.md          # 선택
  design-lab/
    <feature-or-page>/
      README.md
      index.html 또는 src/
      screenshots/
        desktop-main.png
        desktop-detail.png
        mobile.png
  app/ 또는 src/                 # 실제 앱 코드, gate 전에는 건드리지 않음
```

규칙:

- 포트폴리오/제안/초기 제품 화면은 `design-lab/`, `publishing/`, `mockups/` 같은 분리 폴더에서 먼저 만든다.
- 실제 운영 앱 코드, DB, API, auth, routing을 수정하지 않는다. 필요하면 사용자 승인 후 Implementation Handoff에서 별도 작업으로 승격한다.
- 단일 HTML, Tailwind, React/Vite, Next static route 중 프로젝트에 맞는 최소 스택을 쓴다.
- TODO, lorem ipsum, placeholder-only, wireframe-only 산출물은 gate fail이다.

### 4. Screenshot / Browser Verification Gate

최소 검증:

- 데스크톱 1440px 폭 screenshot
- 모바일 390px 폭 screenshot
- 텍스트/카드/nav/table/form 겹침 없음
- 한국어 문구 자연스러움
- 사용자가 요청한 화면 수를 실제 이미지로 생성

브라우저 검증이 가능하면 Playwright를 우선 사용한다. 불가능하면 수동 브라우저 확인 방법과 남은 위험을 보고한다.

### 5. Design Review Gate

`design-quality` 기준으로 판정한다.

Fail 조건:

- AI 템플릿 느낌, 과한 보라/파랑 gradient, 의미 없는 neon/glass 남용
- 금지 폰트 또는 프로젝트 DESIGN.md와 다른 폰트
- 카드 반복만 있는 평범한 3열 레이아웃
- TODO, `...`, lorem ipsum, generic placeholder
- 모바일 깨짐, 텍스트 overflow, 클릭 가능한 요소의 상태 부재
- 마케팅 훅과 실제 화면이 연결되지 않음

통과하면 실제 구현으로 넘길 수 있는 “승인된 mock”으로 표시한다.

### 6. Implementation Handoff Gate

실제 개발은 별도 작업으로 승격한다.

handoff에는 아래를 포함한다.

- 승인된 `DESIGN.md` 경로
- 승인된 mock 경로
- screenshot 경로
- 실제 구현 대상 화면/컴포넌트
- 실제 앱 코드에서 수정 허용되는 파일 범위
- 구현하지 않을 범위(DB/API/auth/운영 데이터 등)
- review/QA/browser gate 계획

## 역할 분리

- 팀장: 범위 분류, gate 적용 여부, 승인/보류 판정, 실제 구현 승격 여부 결정
- designer: DESIGN.md와 mock 제작
- design-reviewer: 디자인 품질, 접근성, 타이포, spacing, visual consistency 점검
- qa/breaker: 브라우저 screenshot, 모바일 깨짐, 사용 흐름 검증
- developer: gate 통과 후 실제 앱 구현

## 보고 형식

완료 보고는 짧게 아래 순서로 한다.

```text
완료한 것:
- DESIGN.md: [경로/상태]
- Mock: [경로]
- Screenshots: [경로]

검증한 것:
- Desktop/mobile 폭
- design-quality 기준
- 실제 앱 미수정 여부

남은 것:
- [보류/리스크]

다음 액션:
- 실제 구현 승격 / 크몽 업로드 / 문구 정리 중 하나
```

## Pitfalls

- DESIGN.md를 만들었다고 디자인이 끝난 게 아니다. screenshot으로 실제 화면을 봐야 한다.
- design-lab이 실제 앱과 너무 멀어져도 문제다. 토큰, 폰트, 정보 구조는 실제 구현 가능성을 유지한다.
- 포트폴리오용 mock은 과장하면 안 된다. “포트폴리오 표현을 위해 재구성한 고도화 UI 예시”처럼 실제 운영 사실과 표현용 재구성을 구분한다.
- 오케스트레이션 프롬프트에 긴 디자인 규칙을 복붙하지 말고 이 스킬로 라우팅한다.
