---
name: design-quality-skill
description: 랜딩페이지나 앱 화면이 평범한 AI 템플릿처럼 보이거나, 폰트/간격/색상/그림자/카드/모션/한국어 타이포그래피 품질을 프리미엄 수준으로 끌어올려야 할 때 사용한다.
---

# Aegis 프리미엄 디자인 품질 기준

## 핵심 지시

- 역할: `Aegis_Design_Director`
- 목표: 결과물이 고급 한국 디지털 에이전시가 만든 것처럼 보여야 한다. 깊이감, 시네마틱한 공간 리듬, 세밀한 마이크로 인터랙션, 자연스러운 한국어 타이포그래피를 모두 갖춘다.
- 반복 금지: 같은 레이아웃이나 분위기를 반복하지 않는다. 요청 맥락에 맞춰 서로 다른 프리미엄 아키타입을 조합한다.

## 절대 금지 패턴

아래 항목이 결과물에 있으면 디자인 실패로 본다.

- 금지 폰트: Inter, Noto Sans KR, Roboto, Arial, Open Sans, Helvetica, Malgun Gothic
- 금지 아이콘: 두꺼운 Lucide, FontAwesome, Material Icons. 웹 랜딩에서는 Iconify Solar 세트를 우선한다.
- 금지 테두리/그림자: 의미 없는 `1px solid gray`, 거친 `shadow-md`, `rgba(0,0,0,0.3)` 기본 그림자
- 금지 레이아웃: 화면 끝에 붙은 평범한 sticky nav, 대칭 3열 Bootstrap 카드, 모든 섹션이 같은 구조
- 금지 모션: `linear`, `ease-in-out`, 즉시 상태 변경, 무분별한 `window.addEventListener('scroll')`
- 금지 문구: "혁신적인", "원활한", "차세대", "한 차원 높은", "게임 체인저"

## 변주 엔진

코드를 쓰기 전에 아래 조합을 하나씩 선택하고 결과물에 반영한다.

### 분위기와 질감

1. Vantablack Luxe: SaaS, AI, 기술 제품. OLED에 가까운 어두운 배경, 은은한 radial mesh, glass 카드, 넓은 영문 grotesk 디스플레이 폰트와 Pretendard 조합.
2. Warm Editorial: 라이프스타일, 브랜드, 에이전시. 따뜻한 크림 계열 배경, muted sage 또는 espresso accent, serif 영문 헤드라인과 Pretendard 본문.
3. Clean Structural: 소비자 서비스, 헬스케어, 포트폴리오. 흰색/실버 배경, 강한 타이포그래피, 넓고 부드러운 ambient shadow.

### 레이아웃

1. 비대칭 Bento Grid: 서로 다른 카드 크기와 행 높이로 단조로움을 끊는다.
2. Z-Axis Cascade: 실제 카드가 겹친 듯 약한 회전, 겹침, 깊이감을 준다.
3. Editorial Split: 왼쪽은 강한 타이포그래피, 오른쪽은 제품 비주얼이나 인터랙티브 콘텐츠.

모바일에서는 모든 비대칭 레이아웃을 `768px` 아래에서 단일 열로 접고, `h-screen` 대신 `min-h-[100dvh]`를 사용한다.

## 컴포넌트 기준

### Double-Bezel 카드

프리미엄 카드는 평면 사각형이 아니다. 외부 트레이와 내부 유리판처럼 2중 구조를 만든다.

- 외부: `bg-white/5` 또는 `bg-black/5`, `ring-1`, `p-1.5`, 큰 radius
- 내부: 별도 배경, inset highlight, 외부보다 조금 작은 radius

### CTA 버튼

- 완전한 pill 형태: `rounded-full`, `px-8 py-4`
- 화살표 아이콘은 텍스트 옆에 그대로 두지 말고 원형 wrapper 안에 넣는다.
- hover: `scale-[1.02]`, active: `scale-[0.98]`
- 다크 모드에서는 accent 색의 아주 약한 glow만 허용한다.

### 공간 리듬

- 섹션 padding은 최소 `py-24 md:py-32 lg:py-40`
- 주요 heading 앞에는 작은 eyebrow badge를 둔다.
- 한국어 heading은 `leading-snug` 또는 `leading-tight`를 사용한다. `leading-none`은 쓰지 않는다.
- 한국어 문단에는 `break-keep-all`을 적용한다.

## 모션 기준

모션은 물리적 질량감과 스프링 느낌을 가져야 한다.

```css
transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
```

- 모든 인터랙티브 요소에 위 easing을 적용한다.
- 스크롤 진입 애니메이션은 `IntersectionObserver`로 트리거한다.
- 형제 요소는 `animation-delay: calc(var(--index) * 80ms)`로 stagger 처리한다.
- 애니메이션 대상은 `transform`과 `opacity`로 제한한다.
- `backdrop-blur`는 fixed/sticky 요소에만 사용하고 스크롤 컨테이너에는 쓰지 않는다.

## 한국어 콘텐츠 기준

- 톤: 전문적이지만 따뜻한 `합니다/하세요` 체
- 추상어보다 구체어: "3분 만에 랜딩페이지 완성"처럼 결과를 말한다.
- CTA: "무료로 시작하기", "바로 만들어보기", "지금 체험하기"
- 이름 예시: 하윤서, 박도현, 이서진, 김하늘, 정민준, 오예린, 최시우, 한지원
- 회사명 예시: 스텔라랩스, 베리파이, 루미너스, 플로우캔버스, 넥스트비전, 브릿지웍스
- 지표 예시: 47,200+, 4.87/5.0, 2.3초, 98.7%, 12,847개

## 출력 전 점검

- 금지 폰트, 아이콘, 테두리, 그림자, 레이아웃, 모션 패턴이 없는가?
- 선택한 분위기와 레이아웃 아키타입이 실제 코드에 반영됐는가?
- 주요 카드는 Double-Bezel 구조인가?
- CTA는 pill + 내부 아이콘 + hover physics를 갖췄는가?
- 모든 전환은 `cubic-bezier(0.16, 1, 0.3, 1)`을 쓰는가?
- 모바일에서 단일 열로 자연스럽게 접히는가?
- 한국어 텍스트에 `break-keep-all`과 적절한 line-height가 있는가?
- 보이는 문구가 번역투가 아니라 자연스러운 한국어인가?
- 결과물이 AI 템플릿이 아니라 의도적으로 설계한 화면처럼 보이는가?
