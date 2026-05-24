---
name: design-quality
description: 랜딩페이지, 웹앱, 모바일 앱 화면, Excalidraw/와이어프레임 레이아웃 보드가 평범한 AI 템플릿처럼 보이거나 폰트, 간격, 색상, 카드, 모션, 한국어 타이포그래피 품질을 프리미엄 수준으로 끌어올려야 할 때 사용한다. 디자인 리뷰, 품질 게이트, DESIGN.md 정리, 긴 디자인 산출물의 생략 없는 완성 기준에도 사용한다.
---

# Plostack 디자인 품질 기준

## 역할

`design-quality`는 산출물 유형별 스킬의 공통 품질 게이트다. 새 화면을 직접 만들기보다, 이미 만들었거나 만들 예정인 디자인이 전문적인 제품 품질을 갖추도록 기준을 제공한다.

## 연결 스킬

- `landing-page-design`: 새 랜딩페이지 생성 또는 기존 HTML/CSS 랜딩 개선.
- `web-app-design`: React/Next/Tailwind 기반 웹앱, 관리자, 대시보드, 반복 업무 UI.
- `mobile-app-design`: React Native/Expo/NativeWind 기반 모바일 앱 UI.
- `exportable-html-document`: PDF/PPTX export를 전제로 새 HTML 문서를 설계.
- `html-to-pdf`: 이미 있는 HTML 파일을 PDF로 변환.
- `html-to-pptx`: 이미 있는 HTML page/slide를 PPTX로 변환.
- `pptx-generator`: 새 발표자료/피치덱을 기획하고 PptxGenJS 기반 HTML preview와 PPTX 생성기를 작성.

작업 대상이 명확하면 해당 산출물 스킬을 먼저 적용하고, 이 스킬은 품질 기준과 점검에 사용한다.

## Excalidraw / Wireframe 품질 기준

Excalidraw, draw, whiteboard, low-fi wireframe은 구현물이 아니라 구조 합의 도구다. 그래도 결과가 이후 구현 방향을 결정하므로 `design-gate-hook-harness`의 Visual Planning Gate를 적용하고 아래 기준으로 점검한다.

- frame은 실제 route/page/screen 단위로 나눈다. 예: blog main entry, portfolio main, detail template.
- 공통 layout과 전용 layout을 구분한다. 예: common footer, page-specific hero.
- 긴 기획 문장을 쓰지 말고 slot label과 짧은 CTA만 둔다. 예: `Case Index`, `Problem 2 lines`, `Evidence links`.
- 색은 2~3개 neutral과 1개 accent를 기본으로 한다. 의미 없는 rainbow card, 프로젝트마다 다른 강한 배경색, 단색 계열 도배를 피한다.
- 손글씨/rough 느낌 폰트가 의사결정을 흐리면 clean sans 기준으로 바꾼다.
- 카드 벽을 만들지 말고 row, strip, band, diagram slot, proof block을 섞는다.
- 운영/구조/아키텍처 다이어그램은 표/카드벽으로 검토하지 않고 node -> arrow -> state/output 흐름으로 검토한다. 예: `request -> agents -> shared memory -> recorded output`. 에이전트/모듈/저장소/산출물은 node, 책임은 짧은 label, 관계는 방향 arrow로 둔다.
- 이동 흐름은 arrow로 표시한다. 예: `/` hero CTA -> `/portfolio/` -> `/portfolio/{case}/`.
- 보드 옆에는 route, approved layout, content source, implementation notes를 10줄 안팎의 handoff로 남긴다.
- Excalidraw 보드는 pub mock이나 screenshot gate를 대체하지 않는다. 구현 전에는 필요 수준에 따라 `DESIGN.md`, `design-lab/pub/`, `design-lab/screenshots/`로 승격한다.

## DESIGN.md 원칙

프로젝트 저장소 안에서 디자인 작업을 하면 `DESIGN.md`를 디자인 원본으로 둔다. 새 앱/SaaS/SPA/랜딩/관리자 UI/포트폴리오 화면처럼 디자인이 제품 성공이나 판매 전환에 영향을 주는 작업은 실제 구현 전에 `design-gate-hook-harness`를 적용한다. 기본 퍼블리싱 원본은 `design-lab/pub/`, 캡처 산출물은 `design-lab/screenshots/`, 실제 구현 handoff 문서는 필요 시 `design-lab/handoff.md`다.

`design-lab/pub/`는 raw publishing/artboard 원본이다. 개발 참조용 화면 구조, 토큰, 상태, 레이아웃을 그대로 보여줘야 하며 디바이스 목업/손 mockup/배경 합성/크몽 썸네일용 composite를 포함하지 않는다. 썸네일·포트폴리오 합성은 `kmong-thumbnail/` 또는 `design-lab/composite/` 같은 별도 경로로 분리한다.

보고서, 제안서 문서, 포트폴리오 본문, 이력서, 경력기술서처럼 PDF/PPTX export가 최종 목표인 HTML은 랜딩/웹앱 mock이 아니다. 이 경우 `exportable-html-document`를 먼저 적용하고, 디자인 품질은 page canvas, print/export fidelity, 읽기 구조를 중심으로 점검한다.

- 기존 `DESIGN.md` 또는 `design.md`가 있으면 먼저 읽고 코드와 문구를 맞춘다.
- 둘 다 없고 단발 산출물이 아닌 프로젝트 변경이면 `DESIGN.md`를 만든다.
- 새 `DESIGN.md`에는 브랜드 톤, 폰트, 색상 토큰, spacing, 컴포넌트 상태, 레이아웃 원칙, 접근성, 금지 패턴, 검증 기준을 간결하게 기록한다.
- 구현 중 디자인 결정이 바뀌면 `DESIGN.md`도 함께 갱신한다.
- `DESIGN.md`와 실제 화면이 충돌하면 화면을 임의로 밀어붙이지 말고, 근거 있는 변경으로 둘을 맞춘다.

## 절대 금지 패턴

아래 항목이 결과물에 있으면 디자인 실패로 본다.

- 금지 출력: `TODO`, `...`, "나머지도 같은 패턴", skeleton-only, wireframe-only, placeholder 설명으로 끝나는 결과물.
- 금지 폰트: Inter, Noto Sans KR, Roboto, Arial, Open Sans, Helvetica, Malgun Gothic.
- 금지 아이콘: 두꺼운 Lucide, FontAwesome, Material Icons 남용. 랜딩은 Iconify Solar, 앱은 프로젝트 아이콘 시스템을 우선한다.
- 금지 테두리/그림자: 의미 없는 `1px solid gray`, 거친 `shadow-md`, `rgba(0,0,0,0.3)` 기본 그림자.
- 금지 레이아웃: 평범한 sticky nav, 대칭 3열 카드 반복, 모든 섹션이 같은 구조, 카드 안의 카드, 모바일 화면 전체를 동일 카드 패턴으로 도배하는 구조.
- 금지 모션: `linear`, 무분별한 `ease-in-out`, 즉시 상태 변경, 과도한 scroll listener.
- 금지 문구: "혁신적인", "원활한", "차세대", "한 차원 높은", "게임 체인저".

## 생략 없는 산출물 기준

랜딩페이지, 웹앱, 모바일 앱 화면을 만들 때 결과물은 실행 가능한 파일/컴포넌트 단위로 완성한다. 예시 일부만 만들고 나머지를 설명으로 넘기지 않는다.

- 코드 주석이나 본문에 `<!-- ... -->`, `// ...`, `TODO`, 단독 `...`, "add more as needed"를 남기지 않는다.
- 요청된 섹션, 상태, 반복 항목은 실제 데이터와 UI로 채운다.
- 랜딩페이지는 nav, hero, social proof, features, testimonials/case studies, CTA, footer를 생략 없이 채운다.
- 앱 UI는 default, loading, empty, error, disabled 등 필요한 상태를 실제 화면 요소로 구현한다.
- 출력이 길어져 한 번에 끝낼 수 없으면 안전한 섹션/컴포넌트 경계에서만 멈추고, 다음에 이어 쓸 정확한 위치를 남긴다.

## 프리미엄 아키타입

코드를 쓰기 전에 요청 맥락에 맞는 조합을 하나 고른다.

분위기:

- Vantablack Luxe: SaaS, AI, 기술 제품. OLED에 가까운 어두운 배경, 절제된 glass, 선명한 데이터 계층.
- Warm Editorial: 라이프스타일, 브랜드, 에이전시. 따뜻한 배경, muted accent, 자연스러운 한국어 리듬.
- Clean Structural: 소비자 서비스, 헬스케어, 포트폴리오. 밝은 neutral, 강한 타이포그래피, 정돈된 shadow.

레이아웃:

- 비대칭 Bento Grid: 서로 다른 카드 크기와 행 높이로 단조로움을 끊는다.
- Z-Axis Cascade: 겹침, 약한 회전, 깊이감으로 화면에 층을 만든다.
- Editorial Split: 강한 타이포그래피와 제품 비주얼/인터랙티브 영역을 나눈다.

모바일에서는 비대칭 레이아웃을 `768px` 아래에서 단일 열로 접고, `h-screen` 대신 `min-h-[100dvh]`를 사용한다.

## 컴포넌트 기준

- 주요 카드는 외부 tray와 내부 content를 분리한 Double-Bezel 구조를 우선한다.
- CTA는 pill 또는 명확한 버튼 형태, 48px 이상 touch target, hover/active/focus 상태를 갖춘다.
- 아이콘 버튼에는 tooltip 또는 `aria-label`을 둔다.
- 폼은 label, hint, error, focused, disabled 상태를 가진다.
- 테이블/리스트는 loading, empty, pagination 또는 scroll 상태를 고려한다.
- 상태 없는 버튼, 입력, 토글, 모달은 납품하지 않는다.

## Surface / Card 기준

카드는 독립 데이터 묶음, 결과, 입력, 선택지를 담는 surface다. 모든 section을 카드로 감싸면 정보 구조가 무너진다.

- 카드 사용: 개별 task/장소/프로그램 항목, 신청 결과 요약, 입력 form group, 견적/분석 결과, 상태 알림 묶음.
- 카드 비사용: hero/header, section title, 설명 band, navigation, timeline/list wrapper, sticky action area, 단순 메타/라벨.
- 카드 유형은 최소 2~3개로 분화한다. 예: filled surface, outline card, compact row, statistic chip, media tile, full-width functional surface.
- 리스트는 row density와 scan speed를 우선한다. 모든 row를 큰 카드로 만들지 말고 divider, band, grouped section, inline action을 섞는다.
- 모바일에서는 기능 surface, list, section, detail panel의 역할을 이름 붙여 구분한 뒤 시각 스타일을 다르게 준다.

## 모바일 검증 기준

- 기준 폭은 요청값을 따른다. 없으면 390px, `Z Fold 5 folded`/`folded`/`344px` 요청이면 344px을 blocker 기준으로 삼는다.
- root tab 화면은 back button이 없어야 한다. task/detail/modal/secondary flow는 back button이 있어야 한다.
- bottom tab은 fixed/anchored 상태여야 하며 콘텐츠를 가리면 fail이다.
- hero panel, status band, card/list, bottom tab 간 overlap은 0px이어야 한다.
- 좌우 최소 여백은 16px 이상, touch target은 44px 이상, 주요 CTA는 48px 이상을 기본으로 본다.
- 텍스트 overflow, 잘림, 줄바꿈 깨짐, safe-area 침범은 blocker다.

## 문서형 Export 품질 기준

PDF/PPTX 제출물을 전제로 만든 HTML은 웹페이지처럼 보이는 것이 목표가 아니다. 브라우저 preview는 원본 확인용이고, 최종 품질은 export 결과에서 판정한다.

- `.page` 또는 `.slide` 단위의 고정 canvas를 쓰고 `@page` 크기와 일치시킨다.
- print media에서 레이아웃, 타이포그래피, spacing을 새로 설계하지 않는다.
- toolbar, preview-only control, debug label은 PDF/PPTX에 포함하지 않는다.
- screen preview와 PDF/PPTX 산출물의 page count, 주요 여백, 제목 위치, 링크 상태가 일치해야 한다.
- 포트폴리오/제안서/경력기술서 문서는 과한 랜딩 hero, 반복 카드, 앱 대시보드 스타일로 흐르지 않게 본문 읽기와 증빙 흐름을 우선한다.
- PDF는 텍스트 추출과 hyperlink annotation을 확인한다. PPTX는 slide count와 편집성/시각 fidelity tradeoff를 보고한다.

## 모션 기준

모션은 `transform`과 `opacity`를 중심으로 제한한다.

```css
transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
```

- 모든 인터랙티브 요소는 일관된 easing을 사용한다.
- 스크롤 진입 애니메이션은 `IntersectionObserver`로 트리거한다.
- 형제 요소는 `animation-delay: calc(var(--index) * 80ms)`로 stagger 처리한다.
- `backdrop-blur`는 fixed/sticky 요소나 작은 표면에 제한적으로 사용한다.

## 한국어 콘텐츠 기준

- 톤은 전문적이지만 자연스러운 `합니다/하세요` 체를 기본으로 한다.
- 추상어보다 구체적인 결과를 말한다. 예: "3분 만에 랜딩페이지 완성".
- 한국어 heading은 `leading-tight` 또는 `leading-snug`를 사용하고 `leading-none`은 피한다.
- 한국어 문단에는 `break-keep-all` 또는 `word-break: keep-all`을 적용한다.
- 이름 예시: 하윤서, 박도현, 이서진, 김하늘, 정민준, 오예린.
- 회사명 예시: 스텔라랩스, 베리파이, 루미너스, 플로우캔버스, 브릿지웍스.
- 지표 예시: 47,200+, 4.87/5.0, 2.3초, 98.7%, 12,847개.

## 출력 전 점검

- `design-gate-hook-harness` 적용 대상이면 `Output Format Gate -> Marketing Brief -> DESIGN.md -> pub mock -> screenshots -> design review -> implementation handoff` 흐름과 `design-lab/pub/`, `design-lab/screenshots/`, 필요 시 `design-lab/handoff.md` 산출물이 완료됐는가?
- Excalidraw/whiteboard/와이어프레임 단계라면 Visual Planning Gate를 적용했고, frame/page 분리, common vs page-specific layout 구분, 제한된 palette, clean font, 짧은 slot label, route arrow, 운영/구조 다이어그램의 node-flow 검토, 10줄 안팎 handoff가 있는가?
- 작업이 문서형 HTML/PDF/PPTX 산출물이라면 랜딩/웹앱 gate 대신 `exportable-html-document`로 라우팅했는가?
- 이미 있는 HTML의 PDF/PPTX 변환 요청이라면 각각 `html-to-pdf`, `html-to-pptx`로 분리했는가?
- 문서형 export 산출물에서 `.page`/`.slide` canvas, `@page`, toolbar 숨김, PDF text/link, PPTX slide count를 확인했는가?
- `design-lab/pub/`가 디바이스 목업/썸네일 합성이 아니라 raw publishing/artboard 원본인가? composite/thumbnail이 필요하면 별도 경로로 분리했는가?
- 단일 repo/단일 포트폴리오 작업에서 `design-lab/pub/<project-slug>/` 중첩을 불필요하게 만들지 않았는가? 여러 디자인 실험이 동시에 있을 때만 `pub/<slug>/`를 예외로 썼는가?
- `DESIGN.md`가 필요하면 생성/갱신됐는가?
- 선택한 분위기와 레이아웃 아키타입이 실제 코드에 반영됐는가?
- 금지 폰트, 아이콘, 테두리, 그림자, 레이아웃, 모션 패턴이 없는가?
- 주요 CTA와 입력/버튼에 hover, active, focus, disabled/loading 상태가 있는가?
- 모바일에서 요청 폭 또는 기본 390px 기준으로 텍스트, 카드, nav, 버튼이 겹치지 않는가? Z Fold 5 folded 요청이면 344px에서 통과했는가?
- root tab/back button 규칙, bottom tab fixed/anchored, overlap 0px, 최소 좌우 여백 16px 이상, text overflow 없음이 확인됐는가?
- 카드가 필요한 데이터 묶음/결과/입력과 카드가 아닌 header/band/list/functional surface가 구분됐는가?
- 한국어 문구가 번역투가 아니라 자연스러운가?
- 결과물이 AI 템플릿이 아니라 의도적으로 설계한 제품 화면처럼 보이는가?
