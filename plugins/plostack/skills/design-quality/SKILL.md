---
name: design-quality
description: 랜딩페이지, 웹앱, 모바일 앱 화면이 평범한 AI 템플릿처럼 보이거나 폰트, 간격, 색상, 카드, 모션, 한국어 타이포그래피 품질을 프리미엄 수준으로 끌어올려야 할 때 사용한다. 디자인 리뷰, 품질 게이트, DESIGN.md 정리, 긴 디자인 산출물의 생략 없는 완성 기준에도 사용한다.
---

# Plostack 디자인 품질 기준

## 역할

`design-quality`는 산출물 유형별 스킬의 공통 품질 게이트다. 새 화면을 직접 만들기보다, 이미 만들었거나 만들 예정인 디자인이 전문적인 제품 품질을 갖추도록 기준을 제공한다.

## 연결 스킬

- `landing-page-design`: 새 랜딩페이지 생성 또는 기존 HTML/CSS 랜딩 개선.
- `web-app-design`: React/Next/Tailwind 기반 웹앱, 관리자, 대시보드, 반복 업무 UI.
- `mobile-app-design`: React Native/Expo/NativeWind 기반 모바일 앱 UI.

작업 대상이 명확하면 해당 산출물 스킬을 먼저 적용하고, 이 스킬은 품질 기준과 점검에 사용한다.

## DESIGN.md 원칙

프로젝트 저장소 안에서 디자인 작업을 하면 `DESIGN.md`를 디자인 원본으로 둔다. 새 앱/SaaS/SPA/랜딩/관리자 UI/포트폴리오 화면처럼 디자인이 제품 성공이나 판매 전환에 영향을 주는 작업은 실제 구현 전에 `design-gate-hook-harness`를 적용한다.

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
- 금지 레이아웃: 평범한 sticky nav, 대칭 3열 카드 반복, 모든 섹션이 같은 구조, 카드 안의 카드.
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

- `design-gate-hook-harness` 적용 대상이면 marketing brief, `DESIGN.md`, 별도 `design-lab/` mock, desktop/mobile screenshot, design review gate가 완료됐는가?
- `DESIGN.md`가 필요하면 생성/갱신됐는가?
- 선택한 분위기와 레이아웃 아키타입이 실제 코드에 반영됐는가?
- 금지 폰트, 아이콘, 테두리, 그림자, 레이아웃, 모션 패턴이 없는가?
- 주요 CTA와 입력/버튼에 hover, active, focus, disabled/loading 상태가 있는가?
- 모바일에서 텍스트, 카드, nav, 버튼이 겹치지 않는가?
- 한국어 문구가 번역투가 아니라 자연스러운가?
- 결과물이 AI 템플릿이 아니라 의도적으로 설계한 제품 화면처럼 보이는가?
