---
name: landing-gen-skill
description: 새 마케팅 랜딩페이지, 전환 중심 HTML 페이지, Tailwind CDN 기반 단일 HTML 랜딩 산출물을 만들어야 할 때 사용한다. 사용자가 랜딩페이지, 서비스 소개 페이지, 제품 페이지, 캠페인 페이지, 사전예약 페이지를 요청하면 사용한다.
---

# Aegis 랜딩페이지 생성 스킬

## 기본 설정

- `DESIGN_VARIANCE`: 8. 대칭 템플릿보다 과감한 변주를 우선한다.
- `MOTION_INTENSITY`: 6. 의미 있는 모션을 쓰되 성능을 해치지 않는다.
- `VISUAL_DENSITY`: 3. 여백과 집중도를 우선한다.
- `LANDING_PURPOSE`: conversion. 사용자가 별도 목적을 주면 brand, portfolio, saas, ecommerce로 조정한다.

사용자 요청이 위 설정과 충돌하면 사용자 요청을 우선한다. 단, 금지 패턴과 완성도 기준은 유지한다.

## 출력 아키텍처

모든 결과물은 브라우저에서 바로 열 수 있는 단일 HTML 파일이다. 빌드 도구, 번들러, 프레임워크를 요구하지 않는다.

- 스타일: Tailwind CSS CDN
- 폰트: Pretendard CDN 필수. 영문 display에는 Geist, Outfit, Cabinet Grotesk, Satoshi 중 하나를 조합할 수 있다.
- 아이콘: Iconify Solar 세트 우선
- placeholder 이미지: `https://picsum.photos/seed/{name}/{width}/{height}` 사용. Unsplash URL 금지.
- avatar: `https://i.pravatar.cc/150?u={unique_name}` 사용 가능
- 모션: 강한 모션에는 Motion One, 단순 모션에는 CSS keyframes와 Tailwind utility 사용
- 이모지 금지. 보이는 장식은 아이콘이나 SVG로 대체한다.
- 한국어 기본. heading, CTA, testimonial, 설명 문구는 자연스러운 한국어로 작성한다.

## 필수 HTML 골격

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>페이지 제목</title>
  <meta name="description" content="페이지 설명">
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.min.css">
  <script src="https://code.iconify.design/iconify-icon/2.3.0/iconify-icon.min.js"></script>
  <script>
    tailwind.config = {
      theme: {
        extend: {
          fontFamily: {
            sans: ['Pretendard', 'system-ui', 'sans-serif'],
          },
        },
      },
    }
  </script>
</head>
```

## 디자인 규칙

### 타이포그래피

- 한국어 headline: `text-4xl md:text-5xl lg:text-6xl tracking-tight leading-tight font-bold`
- 한국어에는 `leading-none`을 쓰지 않는다. `leading-tight` 또는 `leading-snug`를 사용한다.
- 한국어 텍스트 블록에는 `word-break: keep-all` 또는 Tailwind `break-keep-all`을 적용한다.
- 본문: `text-base md:text-lg text-gray-600 leading-relaxed max-w-[65ch]`
- 금지 폰트: Inter, Noto Sans KR, Roboto, Arial, Open Sans

### 색상

- 한 페이지의 accent color는 1개만 사용한다.
- 보라/파랑 AI gradient, 네온 glow, 과포화 색상을 금지한다.
- neutral base는 Zinc-900, Slate-950, Stone-100 계열 중 하나로 통일한다.
- warm gray와 cool gray를 섞지 않는다.

### 레이아웃

- `DESIGN_VARIANCE > 4`면 중앙정렬 hero만 쓰는 구조를 피한다.
- split screen, left-aligned content/right asset, asymmetric whitespace, full-bleed media hero 중 하나를 선택한다.
- 인접 섹션은 서로 다른 패턴을 사용한다.
- 복잡한 flex 비율 계산보다 CSS Grid를 우선한다.
- iOS Safari 흔들림 방지를 위해 `h-screen` 대신 `min-h-[100dvh]`를 쓴다.
- 모든 page container는 `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8`을 기본으로 한다.

### 깊이감과 표면

- 카드는 계층이 필요할 때만 사용한다.
- glass 효과는 `backdrop-blur`만 쓰지 말고 `border-white/10`, inset highlight, 약한 shadow를 함께 쓴다.
- noise overlay는 fixed, `pointer-events-none`, 높은 z-index에만 둔다.
- 그림자는 배경 hue에 맞게 tint 처리한다.

### 전환 UI

- CTA는 `px-8 py-4 text-lg` 이상, 모바일 touch target 최소 48px를 만족한다.
- CTA에는 hover, active, focus 상태를 모두 구현한다.
- social proof 숫자는 47,200+, 4.87/5.0처럼 실제처럼 보이는 값을 쓴다.
- testimonial에는 한국어 이름, 역할, 회사명을 넣는다.
- conversion 목적이면 limited spots, 현재 조회 수, 미묘한 countdown 같은 긴급 요소를 과하지 않게 넣을 수 있다.

## 섹션 라이브러리

필수 순서:

1. Navigation: floating glass pill 또는 minimal top bar
2. Hero: 첫 화면에서 가장 강한 섹션
3. Social Proof: logo cloud, metrics bar, press mention 중 하나
4. Features: Bento grid 또는 zig-zag 구성의 3-5개 핵심 기능
5. Testimonials: 실제 같은 한국어 후기
6. CTA: full-bleed 전환 섹션
7. Footer: essential links만 담은 간결한 footer

선택 패턴:

- Hero: split hero, full-bleed media hero, minimal statement hero, interactive hero
- Features: bento grid, zig-zag alternating, icon strip, comparison table
- Social proof: logo cloud, testimonial masonry, metrics bar, case study cards
- CTA: full-bleed CTA, sticky bottom CTA, inline CTA

## 콘텐츠 기준

- 번역투 금지. 한국인이 한국 사용자를 위해 쓴 문장처럼 작성한다.
- 존댓말 수준을 섞지 않는다. 기본은 `합니다/하세요` 체.
- 금지 문구: "혁신적인", "획기적인", "차세대", "게임 체인저", "원활한"
- CTA 예시: "무료로 시작하기", "3분 만에 만들어보기", "지금 바로 체험하기"
- 이름 예시: 하윤서, 박도현, 이서진, 김하늘
- 회사명 예시: 스텔라랩스, 베리파이, 루미너스, 브릿지웍스
- Lorem Ipsum, John Doe, Acme Corp, 김철수 금지

## 성능 기준

- 애니메이션은 `transform`과 `opacity`만 대상으로 한다.
- below-fold 이미지는 `loading="lazy"`와 `decoding="async"`를 사용한다.
- 외부 CDN 스크립트는 5개 이하로 제한한다.
- z-index는 nav `z-40`, overlay `z-50`, noise `z-[60]` 수준으로 절제한다.

## 출력 전 점검

- 단일 HTML 파일이며 브라우저에서 바로 열리는가?
- Pretendard가 로드되고 primary font로 지정됐는가?
- 모든 아이콘이 Iconify Solar 세트인가?
- 보이는 모든 텍스트가 자연스러운 한국어인가?
- 한국어 텍스트에 `break-keep-all`이 적용됐는가?
- `min-h-[100dvh]`를 사용하고 `h-screen`을 피했는가?
- 모바일 layout이 모든 섹션에서 깨지지 않는가?
- CTA가 모바일 터치 크기를 만족하는가?
- 인접 섹션의 레이아웃 패턴이 서로 다른가?
- 금지 폰트, 이모지, Unsplash URL이 없는가?
- 결과물이 템플릿이 아니라 프리미엄 랜딩처럼 보이는가?
