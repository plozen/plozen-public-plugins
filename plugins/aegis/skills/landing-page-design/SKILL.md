---
name: landing-page-design
description: 새 마케팅 랜딩페이지를 만들거나 기존 HTML/CSS 랜딩페이지를 개선할 때 사용한다. 서비스 소개, 제품 페이지, 캠페인, 사전예약, 전환 중심 단일 HTML 랜딩 산출물에 사용하며, 랜딩이 아닌 대시보드/관리자/앱 UI는 web-app-design 또는 mobile-app-design을 사용한다.
---

# Aegis 랜딩페이지 디자인 스킬

## 역할

전환 중심 랜딩페이지를 생성하거나 개선한다. 새 페이지는 브라우저에서 바로 열 수 있는 단일 HTML 파일로 만들고, 기존 페이지는 구조를 불필요하게 갈아엎지 않고 targeted upgrade를 우선한다.

## 연결 스킬

- `design-quality`: 프리미엄 품질 기준, 금지 패턴, 한국어 타이포그래피, 모션/표면감 점검이 필요할 때 함께 사용한다.
- `web-app-design`: 사용자가 반복 조작하는 웹앱, 관리자, 대시보드, 설정, 테이블 UI는 이 스킬로 넘긴다.
- `mobile-app-design`: React Native/Expo 기반 모바일 앱 UI는 이 스킬로 넘긴다.

## 모드 선택

- `new`: 사용자가 새 랜딩페이지, 서비스 소개 페이지, 캠페인 페이지, 사전예약 페이지를 요청한 경우.
- `upgrade`: 사용자가 기존 HTML/CSS/랜딩페이지를 개선, 고급화, 리디자인, polish 해달라고 요청한 경우.

요청이 불분명하면 입력 파일이 있으면 `upgrade`, 없으면 `new`로 본다.

## 프로젝트 디자인 원본

프로젝트 저장소 안에서 작업 중이면 `DESIGN.md`를 디자인 원본으로 사용한다.

- 기존 `DESIGN.md` 또는 `design.md`가 있으면 먼저 읽고, 랜딩의 색상/타이포/컴포넌트 규칙을 맞춘다.
- 둘 다 없고 작업이 단발 HTML 산출물이 아니라 프로젝트에 남는 변경이면 `DESIGN.md`를 만든다.
- 새 `DESIGN.md`에는 브랜드 톤, 폰트, 색상 토큰, 레이아웃 원칙, 컴포넌트 규칙, 금지 패턴, 검증 기준을 간결하게 기록한다.
- 랜딩 수정 후 디자인 결정이 바뀌면 `DESIGN.md`도 함께 갱신한다.

## 공통 품질 기준

- 기본 언어는 한국어이며, 번역투와 과장 문구를 피한다.
- 폰트는 Pretendard를 기본으로 한다. 영문 display에는 Geist, Outfit, Cabinet Grotesk, Satoshi 중 하나를 조합할 수 있다.
- 금지 폰트: Inter, Noto Sans KR, Roboto, Arial, Open Sans, Helvetica, Malgun Gothic.
- 아이콘은 Iconify Solar 세트를 우선한다. 이모지는 쓰지 않는다.
- `h-screen` 대신 `min-h-[100dvh]`를 사용한다.
- 한국어 텍스트에는 `break-keep-all` 또는 `word-break: keep-all`을 적용한다.
- 보라/파랑 AI gradient, 네온 glow, 과포화 색상, 의미 없는 회색 테두리와 기본 그림자를 피한다.
- CTA는 hover, active, focus 상태와 모바일 48px 이상 touch target을 갖춘다.
- 이미지에는 의미 있는 `alt`를 넣고 below-fold 이미지는 `loading="lazy"`와 `decoding="async"`를 사용한다.

## 새 랜딩 생성

출력은 단일 standalone HTML이다.

- Tailwind CSS CDN을 사용한다.
- Pretendard CDN을 로드하고 primary font로 지정한다.
- 외부 CDN 스크립트는 5개 이하로 제한한다.
- 임시 이미지는 `https://picsum.photos/seed/{name}/{width}/{height}`를 사용한다. Unsplash URL은 쓰지 않는다.
- avatar가 필요하면 `https://i.pravatar.cc/150?u={unique_name}`를 사용할 수 있다.

필수 섹션:

1. Navigation: floating glass pill 또는 minimal top bar
2. Hero: 첫 화면에서 브랜드/제품/제안이 즉시 보이는 가장 강한 섹션
3. Social Proof: logo cloud, metrics bar, press mention 중 하나
4. Features: bento grid, zig-zag, comparison 중 하나
5. Testimonials: 실제 같은 한국어 후기
6. CTA: full-bleed 또는 sticky bottom CTA
7. Footer: essential links만 담은 간결한 footer

HTML 기본 골격:

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
</head>
```

## 기존 랜딩 개선

작업 순서:

1. HTML/CSS 구조, 폰트, 색상, 섹션, CTA, 모바일 상태를 스캔한다.
2. 가장 큰 품질 저하 원인 3-5개를 진단한다.
3. 기존 정보 구조를 보존하면서 집중적으로 수정한다.

우선순위:

1. Pretendard 적용과 한국어 타이포그래피 정리
2. 색상 팔레트 단일화와 AI 템플릿 패턴 제거
3. 자연스러운 한국어 콘텐츠로 교체
4. CTA와 인터랙션 상태 보강
5. 반복적인 3열 카드 구조를 bento, zig-zag, media split로 변주
6. 모바일 레이아웃과 접근성 보정

Dead link인 `href="#"`는 제거하거나 명확한 비활성 상태로 바꾼다.

## 콘텐츠 기준

- 금지 문구: "혁신적인", "획기적인", "차세대", "게임 체인저", "원활한", "한 차원 높은".
- CTA 예시: "무료로 시작하기", "3분 만에 만들어보기", "지금 바로 체험하기".
- 이름 예시: 하윤서, 박도현, 이서진, 김하늘, 정민준, 오예린.
- 회사명 예시: 스텔라랩스, 베리파이, 루미너스, 플로우캔버스, 브릿지웍스.
- 지표 예시: 47,200+, 4.87/5.0, 2.3초, 98.7%, 12,847개.
- Lorem Ipsum, John Doe, Acme Corp, 김철수 같은 generic placeholder를 쓰지 않는다.

## 검증

- 단일 HTML 파일이 브라우저에서 바로 열리는지 확인한다.
- 모바일 폭에서 hero, CTA, 카드, nav가 겹치지 않는지 확인한다.
- 금지 폰트, 이모지, Unsplash URL, `h-screen`, dead link가 없는지 확인한다.
- 주요 CTA와 입력/링크의 hover, active, focus 상태를 확인한다.
- 큰 디자인 변경은 `design-quality` 기준으로 독립 점검한다.
