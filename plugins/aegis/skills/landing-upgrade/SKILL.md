---
name: landing-upgrade
description: 기존 HTML/CSS 랜딩페이지가 밋밋하거나 AI 템플릿처럼 보일 때, 구조를 크게 망가뜨리지 않고 프리미엄 한국어 랜딩페이지 품질로 개선해야 할 때 사용한다.
---

# Aegis 랜딩페이지 업그레이드 스킬

## 작업 순서

1. 스캔: HTML/CSS를 읽고 스타일 방식, 폰트, 색상, 레이아웃, 섹션 구조를 파악한다.
2. 진단: 아래 audit 기준으로 AI 패턴, 약점, 누락 상태를 기록한다.
3. 수정: 전체 재작성보다 기존 구조를 살린 targeted upgrade를 우선한다.

## Audit 기준

### 타이포그래피

- 브라우저 기본 폰트, Inter, Noto Sans KR은 Pretendard와 premium 영문 display font로 교체한다.
- headline은 존재감이 있어야 한다. 한국어 headline에는 `text-4xl md:text-6xl tracking-tight leading-tight font-bold` 계열을 사용한다.
- 한국어 텍스트에는 `word-break: keep-all`을 적용한다.
- 본문 폭은 약 65자 안팎으로 제한하고 line-height를 넉넉히 둔다.
- Regular/Bold만 쓰지 말고 Medium(500), SemiBold(600)로 계층을 만든다.
- 지표와 가격 숫자는 `tabular-nums` 또는 monospace 계열을 사용한다.
- heading에는 필요 시 `text-wrap: balance`를 적용한다.

### 색상과 표면

- 순수 `#000000` 배경은 `#0a0a0a`, `#09090b`, zinc-950 계열로 바꾼다.
- accent는 1개로 줄이고 과포화 색을 낮춘다.
- 보라/파랑 AI gradient는 제거한다.
- generic shadow 대신 배경 hue가 묻은 그림자를 사용한다.
- 완전히 평평한 섹션에는 약한 noise, mesh gradient, pattern overlay를 추가한다.
- light page 중간에 뜬금없는 dark section을 넣지 않는다.

### 레이아웃

- 모든 요소가 중앙정렬이고 대칭이면 offset, split screen, mixed aspect ratio로 균형을 깬다.
- 3열 동일 카드 feature는 bento grid, zig-zag, horizontal scroll로 바꾼다.
- 인접 섹션은 서로 다른 구조를 써야 한다.
- `height: 100vh`는 `min-height: 100dvh`로 교체한다.
- page container는 `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8`를 기본으로 한다.
- landing section padding은 최소 `py-20 md:py-32`로 늘린다.
- CTA는 `px-8 py-4 text-lg` 이상으로 눈에 띄게 만든다.

### 인터랙션

- 버튼 hover, active, focus 상태를 추가한다.
- 인터랙션 전환에는 `transition-all duration-300 ease-out` 또는 Aegis easing을 적용한다.
- scroll reveal은 CSS keyframes와 `IntersectionObserver`로 구현한다.
- static logo strip은 필요 시 CSS marquee로 바꾼다.
- `href="#"` dead link는 제거하거나 비활성 처리한다.
- `html { scroll-behavior: smooth; }`를 추가한다.

### 한국어 콘텐츠

- 번역투를 자연스러운 한국어로 고친다.
- 존댓말 수준을 한 가지로 통일한다.
- "혁신적인", "원활한", "차세대", "게임 체인저", "한 차원 높은" 같은 AI 문구를 제거한다.
- 김철수/이영희 같은 generic 이름은 하윤서, 박도현, 이서진처럼 현실적인 이름으로 교체한다.
- `50,000+`, `5.0/5.0` 같은 둥근 지표는 `47,200+`, `4.87/5.0`처럼 실제처럼 조정한다.
- Lorem Ipsum과 영어 자리표시 문구는 즉시 한국어 초안 문구로 바꾼다.

### 코드 품질

- div soup는 `<nav>`, `<main>`, `<section>`, `<article>`, `<footer>`로 정리한다.
- `<html lang="ko">`, `<title>`, description, viewport, OG meta를 확인한다.
- 이미지에는 한국어 `alt`와 below-fold `loading="lazy"`를 추가한다.
- z-index는 nav 40, overlay 50, decorative 60 수준으로 체계화한다.

## 업그레이드 기법

- Pretendard 전환: 한국어 페이지의 고급감을 가장 빠르게 올린다.
- 색상 팔레트 정리: AI purple 제거, accent 단일화, neutral tone 통일
- 콘텐츠 재작성: 자연스러운 한국어, 실제 같은 이름과 지표
- hover/active 상태 추가: 인터페이스가 살아있는 느낌을 만든다.
- 레이아웃 변주: 반복 섹션 구조를 깨고 hierarchy를 만든다.
- staggered reveal: `animation-delay: calc(var(--index) * 80ms)` 사용
- true glass: `backdrop-blur-xl`, `border-white/10`, inset shadow 조합

## 우선순위

1. Pretendard 적용
2. 색상 팔레트 정리
3. 한국어 콘텐츠 개선
4. hover/active/focus 상태 추가
5. 레이아웃 다양화
6. scroll reveal과 모션 추가
7. spacing과 typography polish

## 규칙

- 기존 페이지 구조를 불필요하게 깨지 않는다.
- 결과물은 단일 standalone HTML 파일이어야 한다.
- CDN을 추가하기 전에 신뢰 가능한 URL인지 확인한다.
- 변경은 집중적이고 review 가능해야 한다.
- 보이는 콘텐츠는 자연스러운 한국어 품질을 유지한다.
