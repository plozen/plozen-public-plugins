---
name: design-gate-hook-harness
description: 새 앱, SaaS, SPA, 랜딩, 관리자 UI, 포트폴리오용 UI screenshot, Excalidraw/와이어프레임 레이아웃 기획처럼 디자인이 제품 성공과 판매 전환에 영향을 주는 작업에서 실제 구현 전에 output format gate, visual planning, marketing brief, DESIGN.md, design-lab/pub mock, screenshot, design review gate를 강제한다. 문서형 HTML/PDF/PPTX 산출물은 exportable-html-document로 분기한다.
---

# Plostack Design Gate Hook Harness

## 역할

이 스킬은 앱/SaaS/SPA/랜딩/관리자 UI/포트폴리오용 UI screenshot 작업이 바로 실제 구현으로 튀지 않게 막는 디자인 게이트다. 목적은 기능 명세보다 먼저 팔릴 이유, 클릭 훅, 사용자 심리, 유통 각도, 시각 시스템, 퍼블리싱 mock을 확정한 뒤 실제 개발로 승격하는 것이다.

단, 보고서, 제안서 문서, 포트폴리오 본문, 이력서, 경력기술서처럼 HTML 자체가 PDF/PPTX export 원본이면 이 스킬로 웹페이지 mock을 만들지 않고 `exportable-html-document`로 라우팅한다.

팀장은 디자인 산출물을 직접 만드는 사람이 아니라 gate owner다. 팀장은 `DESIGN.md`와 mock 산출물의 존재, 품질, 검증 상태를 확인하고 통과/보류를 판정한다.

## 적용 시점

다음 중 하나라도 해당하면 적용한다.

- 새 앱, SaaS, SPA, 웹앱, 모바일 앱, 랜딩페이지를 시작한다.
- 기존 제품에 주요 화면, 대시보드, 관리자, 온보딩, 가격/전환 화면을 추가한다.
- 포트폴리오/크몽/제안서에 넣을 제품 UI screenshot 또는 UI mock을 만들거나 개선한다.
- 사용자가 “마케팅 먼저”, “클릭하게”, “궁금증”, “퍼블리싱 mock”, “DESIGN.md”, “디자인 게이트”를 언급한다.
- 사용자가 Excalidraw, draw, whiteboard, 와이어프레임, 레이아웃 보드로 화면/페이지 구조를 먼저 잡자고 한다.
- 에이전트가 바로 `src/`, `app/`, 실제 운영 앱 코드 구현으로 들어갈 위험이 있다.

보고서, 제안서 문서, 포트폴리오 본문 HTML, PDF/PPTX 제출물, 다운로드 버튼이 있는 문서형 HTML은 `exportable-html-document`로 먼저 분기한다.

단순 버그 수정, 문구 수정, 기존 디자인 토큰을 따르는 작은 컴포넌트 수정에는 생략할 수 있다. 생략하면 이유를 보고한다.

## Gate Flow

Design gate 흐름은 항상 `Output Format Gate -> Marketing Brief -> DESIGN.md -> pub mock -> screenshots -> design review -> implementation handoff` 순서를 유지한다. Output Format Gate에서 문서형 export 산출물로 판정되면 여기서 멈추고 `exportable-html-document`로 넘긴다.

```text
Output Format Gate
  -> Marketing Brief
  -> DESIGN.md
  -> pub mock
  -> screenshots
  -> design review
  -> implementation handoff
```

Design-to-Service Sync rule: confirmed `DESIGN.md`와 승인된 `design-kit/` 또는 `design-lab/pub/`이 구현의 source of truth다. 필요한 UX/state/slot이 여기에 없으면 구현하지 말고 planning meeting 안건으로 보고한다. design/pub을 먼저 갱신한 뒤 service code를 sync하며, API wiring은 승인된 design slot 안에서만 허용한다. `-bd`나 subagent dispatch도 이 gate를 우회하지 못한다.

### 0. Output Format Gate

구현 전에 최종 산출물 형태를 먼저 판정한다. “포트폴리오 페이지”라는 표현만으로 웹페이지 작업이라고 단정하지 않는다. 제출, 공유, PDF, PPTX, 다운로드 버튼이 핵심이면 문서형 export 작업이다.

| 최종 산출물 | 라우팅 |
|---|---|
| 마케팅 웹페이지, 제품 소개 랜딩 | `landing-page-design` |
| 앱, 관리자, 대시보드, 반복 업무 UI | `web-app-design` |
| React Native/Expo 모바일 앱 화면 | `mobile-app-design` |
| PDF/PPTX export를 전제로 새 HTML 문서를 작성 | `exportable-html-document` |
| 이미 있는 HTML 파일을 PDF로 변환만 함 | `html-to-pdf` |
| 이미 있는 HTML page/slide를 PPTX로 변환하거나 PPTX 다운로드 버튼/경로를 구현 | `html-to-pptx` |
| 새 발표자료/피치덱을 기획하고 PPTX 생성 | `pptx-generator` |
| Excalidraw/whiteboard/와이어프레임으로 화면 구조만 먼저 판단 | 이 design gate의 Visual Planning Gate + `design-quality` |

포트폴리오/제안서 작업은 두 갈래로 나눈다.

- 포트폴리오나 제안서에 넣을 제품 UI screenshot/mock: 이 design gate를 적용한다.
- 포트폴리오 본문, 제안서 문서, 경력기술서, 보고서 HTML: `exportable-html-document`를 적용한다.

### 0-1. Visual Planning Gate

Excalidraw, whiteboard, rough wireframe은 `design-lab/pub/` mock 이전의 빠른 구조 판단 단계다. 이 단계는 긴 문서 대신 route, section, surface, CTA, evidence slot, data boundary를 눈으로 확인하는 용도이며, 승인된 퍼블리싱 mock이나 screenshot을 대체하지 않는다.

Visual planning을 요청받으면 아래를 먼저 고정한다.

- 페이지/화면 단위 frame을 분리한다. 예: blog main entry, portfolio main, case detail.
- 각 frame에는 긴 문단이 아니라 slot label만 둔다. 예: `Problem 2 lines`, `Evidence links`, `Architecture slot`.
- entry route와 CTA 흐름을 선으로 표시한다. 예: `/` hero CTA -> `/portfolio/` -> `/portfolio/{case}/`.
- `Architecture slot`, 운영 구조, 멀티 에이전트 구조는 표/카드벽이 아니라 `design-quality`의 node-arrow flow 기준으로 판단한다. 최소한 `입력/요청 -> 처리 노드 -> 공유 상태/메모리 -> 기록/출력` 방향성이 보여야 한다.
- 공통 layout과 전용 layout을 구분한다. 예: common footer, page-specific hero.
- 색상은 2~3개 neutral + 1 accent로 제한하고, 의미 없는 rainbow card를 쓰지 않는다.
- 손글씨/rough 폰트 느낌이 판단을 흐리면 clean sans 기준으로 바꾼다.
- `design-quality`로 폰트, 색, 카드 반복, 정보량, 한국어 라벨을 점검한다.

이 단계의 산출물은 `layout decision board`와 짧은 handoff다. 실제 UI 구현이 필요해지면 이후 `DESIGN.md -> design-lab/pub mock -> screenshots -> design review`로 승격한다.

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
- 모바일 화면이면 기준 폭, navigation 규칙, bottom tab 규칙, card/surface 사용 기준, 수치 검증 기준을 `DESIGN.md`에 기록한다. 요청 폭이 없으면 390px을 기본값으로 두고, `Z Fold 5 folded`/`folded`/`344px` 요청이 있으면 344px을 blocker 기준으로 둔다.
- Google `design.md` CLI 호환이 필요한 경우 YAML front matter를 포함하고 `npx -y @google/design.md lint DESIGN.md`를 통과시킨다.
- 기존 프로젝트의 `DESIGN.md`가 prose-only 문서일 수 있다. 이 경우 lint warning 자체가 blocker는 아니지만, “CLI 호환 DESIGN.md가 아님”을 명시하고 필요 시 별도 보강 작업으로 분리한다.

### 3. Publishing Mock Gate

실제 앱 코드에 바로 들어가지 말고 별도 mock 공간을 우선 만든다.

표준 구조:

```text
project/
  DESIGN.md
  docs/
    marketing-brief.md          # 선택
  design-lab/
    pub/                         # 기본 퍼블리싱 원본
      index.html 또는 src/
    screenshots/                 # 캡처 산출물
      desktop-main.png
      desktop-detail.png
      mobile.png
    handoff.md                   # 실제 구현 handoff가 필요할 때만 작성
  app/ 또는 src/                 # 실제 앱 코드, gate 전에는 건드리지 않음
```

규칙:

- 기본 퍼블리싱 원본은 `design-lab/pub/`에 둔다.
- `design-lab/pub/`는 raw publishing/artboard 원본이다. 디바이스 프레임, 휴대폰 mockup, 손에 든 폰 합성, 배경 장식, 크몽 썸네일용 composite를 넣지 않는다.
- 문서형 export HTML은 `design-lab/pub/` UI mock 흐름의 기본 대상이 아니다. PDF/PPTX 원본 HTML은 `exportable-html-document`의 page canvas 규칙을 따른다.
- 썸네일/포트폴리오 합성이 필요하면 `kmong-thumbnail/`, `design-lab/composite/`, 또는 별도 composite page로 분리한다. composite는 `pub` 원본을 참조할 수 있지만 `pub` 원본을 대체하지 않는다.
- 캡처 산출물은 `design-lab/screenshots/`에 둔다.
- 실제 구현 handoff 문서가 필요하면 `design-lab/handoff.md`에 둔다.
- 단일 repo 또는 단일 포트폴리오 작업에서는 `design-lab/pub/<project-slug>/` 중첩을 기본값으로 쓰지 않는다.
- 여러 디자인 실험이 동시에 존재해 산출물 충돌이 날 때만 `design-lab/pub/<slug>/` 예외를 허용한다. 이 경우 screenshot 파일명이나 하위 폴더에도 같은 slug를 반영한다.
- 실제 운영 앱 코드, DB, API, auth, routing을 수정하지 않는다. 필요하면 사용자 승인 후 Implementation Handoff에서 별도 작업으로 승격한다.
- 단일 HTML, Tailwind, React/Vite, Next static route 중 프로젝트에 맞는 최소 스택을 쓴다.
- TODO, lorem ipsum, placeholder-only, wireframe-only 산출물은 gate fail이다.

### 3-1. Mobile Navigation / Surface Gate

모바일 앱 mock이면 아래 규칙을 먼저 고정한다.

- 기준 폭은 사용자 요청값을 따른다. 요청이 없으면 390px, `Z Fold 5 folded`/`folded`/`344px` 요청이면 344px이다.
- bottom tab root 화면은 back button이 없다. task/detail/modal/secondary flow 화면은 back button이 필수다.
- bottom tab은 fixed 또는 safe-area anchored 상태여야 하며, scroll content가 tab 아래로 가려지지 않게 하단 padding을 둔다.
- 카드 사용 여부를 먼저 분류한다. 독립 데이터 묶음/결과/입력은 카드가 맞고, header/hero/band/list wrapper/navigation/sticky action은 카드가 아니다.
- 화면 안에 surface 유형을 최소 2~3개 섞는다. 예: hero band, compact list row, filled card, outline panel, sticky action.

### 4. Screenshot / Browser Verification Gate

최소 검증:

- 데스크톱 1440px 폭 screenshot
- 모바일 screenshot은 요청 폭을 따른다. 요청이 없으면 390px, Z Fold 5 folded/344px 요청이면 344px screenshot을 blocker 기준으로 저장한다.
- screenshot 파일은 기본적으로 `design-lab/screenshots/`에 저장
- 텍스트/카드/nav/table/form 겹침 없음
- hero/header/status panel/list/bottom tab overlap 0px
- 좌우 최소 여백 16px 이상, touch target 44px 이상, 주요 CTA 48px 이상
- bottom tab fixed/anchored, root tab back 없음, task/detail/modal back 있음
- text overflow, clipped copy, safe-area 침범 없음
- 한국어 문구 자연스러움
- 사용자가 요청한 화면 수를 실제 이미지로 생성

브라우저 검증이 가능하면 Playwright를 우선 사용한다. 불가능하면 수동 브라우저 확인 방법과 남은 위험을 보고한다.

### 5. Design Review Gate

`design-quality` 기준으로 판정한다.

Fail 조건:

- AI 템플릿 느낌, 과한 보라/파랑 gradient, 의미 없는 neon/glass 남용
- 금지 폰트 또는 프로젝트 DESIGN.md와 다른 폰트
- 카드 반복만 있는 평범한 3열 레이아웃 또는 모바일 전체가 같은 카드 UI로 수렴한 구조
- 카드가 아닌 header/band/list/functional surface까지 전부 카드로 감싼 구조
- TODO, `...`, lorem ipsum, generic placeholder
- 모바일 깨짐, 텍스트 overflow, overlap, bottom tab 미고정, navigation back 규칙 불일치, 클릭 가능한 요소의 상태 부재
- 마케팅 훅과 실제 화면이 연결되지 않음

통과하면 실제 구현으로 넘길 수 있는 “승인된 mock”으로 표시한다.

### 6. Implementation Handoff Gate

실제 개발은 별도 작업으로 승격한다. 구현 handoff가 필요하면 `design-lab/handoff.md`를 작성한다.

handoff에는 아래를 포함한다.

- 승인된 `DESIGN.md` 경로
- 승인된 mock 경로(`design-lab/pub/` 또는 예외적으로 `design-lab/pub/<slug>/`)
- pub/composite 목적 분리 여부(`design-lab/pub/`는 raw 원본, thumbnail/composite는 별도 경로)
- screenshot 경로(`design-lab/screenshots/`)
- 검증 폭과 blocker 수치(예: 390px 또는 344px, overlap 0px, 최소 좌우 여백 16px 이상, bottom tab fixed/anchored, text overflow 없음)
- navigation 판정(root tab back 없음, task/detail/modal back 있음)
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
- Mock: [design-lab/pub/ 경로]
- Screenshots: [design-lab/screenshots/ 경로]
- Handoff: [design-lab/handoff.md 또는 생략 사유]

검증한 것:
- Desktop/mobile 폭과 요청 폭 기준
- overlap 0px / 최소 좌우 여백 16px 이상 / bottom tab fixed·anchored / text overflow 없음
- root tab back 없음 / task-detail-modal back 있음
- design-quality 기준
- 실제 앱 미수정 여부

남은 것:
- [보류/리스크]

다음 액션:
- 실제 구현 승격 / 크몽 업로드 / 문구 정리 중 하나
```

## Pitfalls

- DESIGN.md를 만들었다고 디자인이 끝난 게 아니다. screenshot으로 실제 화면을 봐야 한다.
- Excalidraw/whiteboard는 디자인 방향을 빠르게 합의하는 도구일 뿐이다. 실제 구현 승인에는 DESIGN.md, pub mock, screenshot gate가 필요하다.
- design-lab이 실제 앱과 너무 멀어져도 문제다. 토큰, 폰트, 정보 구조는 실제 구현 가능성을 유지한다.
- `design-lab/pub/`를 디바이스 mockup/썸네일 합성용 페이지로 쓰지 않는다. raw 원본과 composite 목적을 섞으면 reviewer와 developer handoff가 깨진다.
- 단일 repo/단일 포트폴리오 작업에서 습관적으로 `design-lab/pub/<project-slug>/`를 만들지 않는다. 중첩은 여러 실험이 동시에 있을 때만 쓴다.
- 포트폴리오용 mock은 과장하면 안 된다. “포트폴리오 표현을 위해 재구성한 고도화 UI 예시”처럼 실제 운영 사실과 표현용 재구성을 구분한다.
- “포트폴리오 페이지”, “제안서”, “PDF” 같은 단어만 보고 랜딩/웹앱 mock으로 라우팅하지 않는다. 최종 산출물이 문서면 `exportable-html-document`, 기존 HTML 변환이면 `html-to-pdf` 또는 `html-to-pptx`다.
- 오케스트레이션 프롬프트에 긴 디자인 규칙을 복붙하지 말고 이 스킬로 라우팅한다.
